from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mutiagent.graph.state import WorkflowState
from mutiagent.utils.dataset_venv import ensure_dataset_venv
from mutiagent.utils.pip_infer import write_inferred_pip_requirements
from mutiagent.utils.paths import production_changed_files
from mutiagent.utils.venv_flags import effective_auto_venv

_log = logging.getLogger("mutiagent.workflow")
_MAX_SYMBOLS = 40
_MAX_DEPS = 40
_CACHE_MAX_AGE_SECONDS = 24 * 3600


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _cache_path() -> Path:
    p = _repo_root() / "log" / "project_profile_memory.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _load_cache() -> dict[str, Any]:
    p = _cache_path()
    if not p.exists():
        return {}
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _save_cache(cache: dict[str, Any]) -> None:
    _cache_path().write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _is_cache_fresh(ts: str) -> bool:
    try:
        t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return False
    now = datetime.now(timezone.utc)
    return (now - t).total_seconds() <= _CACHE_MAX_AGE_SECONDS


def _detect_language_and_framework(repo: Path) -> tuple[str, str]:
    has_pkg_json = (repo / "package.json").exists()
    has_pyproject = (repo / "pyproject.toml").exists()
    has_requirements = (repo / "requirements.txt").exists()
    py_files = list(repo.rglob("*.py"))[:1]
    js_files = list(repo.rglob("*.js"))[:1] + list(repo.rglob("*.ts"))[:1]

    if has_pkg_json and not (has_pyproject or has_requirements or py_files):
        return "javascript", "node"
    if (has_pyproject or has_requirements or py_files) and not has_pkg_json:
        return "python", "pytest"
    if has_pkg_json and (has_pyproject or has_requirements or py_files):
        return "mixed", "hybrid"
    if js_files and not py_files:
        return "javascript", "node"
    return "python", "pytest"


def _detect_module_roots(repo: Path) -> list[str]:
    roots: list[str] = []
    if (repo / "src").is_dir():
        roots.append("src")
    if (repo / "app").is_dir():
        roots.append("app")
    if (repo / "lib").is_dir():
        roots.append("lib")
    if (repo / "tests").is_dir():
        roots.append("tests")
    for child in repo.iterdir():
        if child.is_dir() and (child / "__init__.py").exists():
            roots.append(child.name)
    dedup: list[str] = []
    seen: set[str] = set()
    for r in roots:
        if r not in seen:
            seen.add(r)
            dedup.append(r)
    return dedup[:12]


def _read_deps(repo: Path) -> list[str]:
    deps: list[str] = []
    for f in ("requirements.txt", "requirements-dev.txt"):
        p = repo / f
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            deps.append(s)
    return deps[:_MAX_DEPS]


def _probe_symbols(repo: Path, changed_files: list[str]) -> list[str]:
    out: list[str] = []
    for rel in changed_files[:20]:
        p = repo / rel
        if not p.exists() or p.suffix != ".py":
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("def "):
                name = s[4:].split("(", 1)[0].strip()
                if name:
                    out.append(name)
            elif s.startswith("class "):
                name = s[6:].split("(", 1)[0].split(":", 1)[0].strip()
                if name:
                    out.append(name)
            if len(out) >= _MAX_SYMBOLS:
                return out
    return out


def _module_name_from_path(repo: Path, file_path: Path) -> str:
    rel = file_path.resolve().relative_to(repo.resolve())
    no_ext = str(rel.with_suffix(""))
    return no_ext.replace("/", ".").replace("\\", ".")


def _probe_import_candidates(repo: Path, changed_files: list[str]) -> list[str]:
    """
    产出 `module.path:Symbol` 形式的候选导入项，供 TestGen 优先使用，减少首轮猜错导入路径。
    """
    out: list[str] = []
    seen: set[str] = set()
    for rel in changed_files[:30]:
        p = (repo / rel).resolve()
        if not p.exists() or p.suffix != ".py":
            continue
        mod = _module_name_from_path(repo, p)
        text = p.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            s = line.strip()
            sym = ""
            if s.startswith("def "):
                sym = s[4:].split("(", 1)[0].strip()
            elif s.startswith("class "):
                sym = s[6:].split("(", 1)[0].split(":", 1)[0].strip()
            if not sym:
                continue
            cand = f"{mod}:{sym}"
            if cand in seen:
                continue
            seen.add(cand)
            out.append(cand)
            if len(out) >= _MAX_SYMBOLS:
                return out
    return out


def _build_profile(repo: Path, state: WorkflowState) -> dict[str, Any]:
    language, framework = _detect_language_and_framework(repo)
    return {
        "repo_path": str(repo),
        "language": language,
        "framework": framework,
        "module_roots": _detect_module_roots(repo),
        "dependencies": _read_deps(repo),
        "importable_symbols": _probe_symbols(repo, production_changed_files(state.changed_files or [])),
        "import_candidates": _probe_import_candidates(repo, production_changed_files(state.changed_files or [])),
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def _infer_pip_and_preflight_venv(repo: Path, state: WorkflowState) -> None:
    """
    每次工作流：根据变更文件推断第三方依赖并落盘 + 在 run_eval 且自动 venv 时预创建/复用 venv。
    避免在 Execution 之前从未安装依赖导致 pytest 与生成阶段脱节。
    """
    inferred: list[str] = []
    try:
        inferred = write_inferred_pip_requirements(repo, state.changed_files or [])
    except OSError as e:
        _log.warning("ProjectProbeAgent: 写入推断 pip 列表失败: %s", e)
    dbg = state.debug.setdefault("env_bootstrap", {})
    dbg["inferred_pip"] = inferred

    if not state.run_eval or not effective_auto_venv(state):
        dbg["preflight_venv"] = "skipped (run_eval off or auto_venv off)"
        return
    try:
        py, msg = ensure_dataset_venv(repo, auto_install_python=bool(state.auto_install_python))
    except Exception as e:  # noqa: BLE001
        _log.warning("ProjectProbeAgent: 预检 venv 失败（后续 Execution 将重试）: %s", e)
        dbg["preflight_venv"] = f"error: {e!s}"
        return
    if py is None:
        _log.warning("ProjectProbeAgent: 预检 venv 未就绪: %s", msg)
        dbg["preflight_venv"] = f"unavailable: {msg}"
        return
    dbg["preflight_venv"] = "ok"
    dbg["python"] = py
    dbg["message"] = msg


def project_probe_agent(state: WorkflowState) -> WorkflowState:
    repo = Path(state.repo_path or "")
    if not repo.exists():
        state.project_profile = {"repo_path": state.repo_path, "status": "repo_not_found"}
        state.debug["project_probe_agent"] = {"status": "repo_not_found"}
        return state

    cache = _load_cache()
    key = str(repo.resolve())
    hit = cache.get(key)
    if (
        isinstance(hit, dict)
        and _is_cache_fresh(str(hit.get("updated_at", "")))
        and isinstance(hit.get("import_candidates"), list)
    ):
        state.project_profile = hit
        state.debug["project_probe_agent"] = {"cache_hit": True, "age_policy_s": _CACHE_MAX_AGE_SECONDS}
        _log.info("ProjectProbeAgent: 命中仓库画像缓存 repo=%s", key)
    else:
        profile = _build_profile(repo.resolve(), state)
        state.project_profile = profile
        cache[key] = profile
        _save_cache(cache)
        state.debug["project_probe_agent"] = {
            "cache_hit": False,
            "language": profile.get("language"),
            "framework": profile.get("framework"),
            "module_roots": profile.get("module_roots", []),
            "symbol_count": len(profile.get("importable_symbols", [])),
        }
        _log.info(
            "ProjectProbeAgent: 探测完成 repo=%s language=%s framework=%s module_roots=%s",
            key,
            profile.get("language"),
            profile.get("framework"),
            profile.get("module_roots"),
        )

    _infer_pip_and_preflight_venv(repo, state)
    return state

