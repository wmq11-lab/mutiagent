"""
实验扩展指标：变更行 / 新增函数 / 跨模块用例 / 压缩率 / Bug detection / 执行时间缩减等。

跨模块用例数：在每个 ``test_*`` 中统计 **import** 与 **函数调用**（``ast.Call``）所解析到的、
落在变更文件集合中的模块路径数是否不少于 2（调用会按属性链与 import 别名还原到可能的包路径）。

环境变量（可选）::
  CHANGED_FILES                 逗号分隔相对路径；与 ``WorkflowState.changed_files`` 的生产文件路径 **并集**（跨模块口径等）。
  CHANGED_FILES_STRICT          若为 1/true：仅使用 ``CHANGED_FILES``，不并入状态中的变更列表（旧版替换语义）。
  CHANGED_FUNCS                 ``name`` 或 ``path/to.py:name``
  FAILING_TESTS                 逗号分隔失败 nodeid（与 selected_tests 做集合交）；未设时若有 junit 失败用例则自动以其为基准
  MUTIAGENT_FULL_SUITE_PYTEST_ARGS      测全量耗时时的附加 pytest 参数（shlex 分词）
  MUTIAGENT_MEASURE_FULL_SUITE_TIME      若为 1/true：无缓存时对数据集跑完整 pytest 并写入缓存（可能很慢）
  MUTIAGENT_EXEC_TIME_REDUCTION_ESTIMATE 若为 0/false/off：关闭「无全量墙钟时」自动粗估；默认开启（无缓存时用
  selected×(project_collected/generated) 估计全量墙钟并给出 exec_time_reduction_pct）
"""

from __future__ import annotations

import ast
import json
import os
import re
import shlex
import subprocess
import time
from pathlib import Path
from typing import Any

from mutiagent.evaluation.change_line_coverage import (
    change_line_coverage_from_diff_and_cov_paths,
    _iter_git_chunks,
    _lookup_fd,
)
from mutiagent.evaluation.coverage_executed_lines import executed_lines_from_file_block
from mutiagent.graph.state import WorkflowState
from mutiagent.utils.paths import is_under_project_tests_tree, production_changed_files


def _env_csv(name: str) -> list[str]:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return []
    return [x.strip() for x in re.split(r"[,;\n]+", raw) if x.strip()]


def _norm_rel(p: str) -> str:
    return (p or "").strip().replace("\\", "/")


def _norm_casefold_id(x: str) -> str:
    return _norm_rel(x).casefold()


def _safe_div(n: float, d: float) -> float | None:
    if d <= 0:
        return None
    return n / d


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _falsy_env(name: str) -> bool:
    """显式关闭：0/false/no/off。"""
    return os.environ.get(name, "").strip().lower() in {"0", "false", "no", "off"}


def _junit_failed_case_ids(rows: list[dict[str, str]] | None) -> list[str]:
    """与 ExecutionAgent._metrics_junit_case_id 一致，便于与 selected_tests 求交。"""
    if not rows:
        return []
    fail_st = {"failed", "error"}
    seen: set[str] = set()
    out: list[str] = []
    for row in rows:
        if str(row.get("status", "")).lower() not in fail_st:
            continue
        cls = (row.get("classname") or "").strip()
        name = (row.get("name") or "").strip()
        cid = f"{cls}::{name}" if cls and name else (name or cls)
        if cid and cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out


def _specs_from_change_analysis_added_funcs(state: WorkflowState) -> list[tuple[str, str]]:
    """change_analysis 中 ADD 的 function/method，补「diff 无 +def」类变更的新增函数覆盖口径。"""
    specs: list[tuple[str, str]] = []
    changed = set(production_changed_files(state.changed_files or []))
    for fc in state.change_analysis or []:
        fn = _norm_rel(getattr(fc, "file", "") or "")
        if fn not in changed:
            continue
        if is_under_project_tests_tree(fn):
            continue
        for ch in getattr(fc, "changes", []) or []:
            if str(getattr(ch, "change_type", "") or "").upper() != "ADD":
                continue
            if str(getattr(ch, "type", "") or "") not in {"function", "method"}:
                continue
            ent = str(getattr(ch, "entity", "") or "").strip()
            if ent:
                specs.append((fn, ent))
    return specs


def _cross_module_loose_substring_count(state: WorkflowState, changed: set[str]) -> int:
    """AST Strict 未命中时：同一 test_* 源码子串同时出现≥2 个变更模块的 ``a.b.c`` 或 ``path/to.py``。"""
    rels = sorted({_norm_rel(p) for p in changed if str(p).strip()}, key=len, reverse=True)
    rels_py = [r for r in rels if r.endswith(".py")]
    if len(rels_py) < 2:
        return 0
    n = 0
    for gt in state.generated_tests or []:
        raw = gt.content or ""
        try:
            tree = ast.parse(raw)
        except SyntaxError:
            continue
        lines = raw.splitlines()
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            if not node.name.startswith("test_"):
                continue
            lo = max(0, node.lineno - 1)
            hi = getattr(node, "end_lineno", node.lineno) or node.lineno
            chunk = "\n".join(lines[lo:hi])
            touched: set[str] = set()
            for rel in rels_py:
                dotted = rel[:-3].replace("/", ".")
                if dotted in chunk or rel in chunk or _norm_rel(rel) in chunk:
                    touched.add(rel)
            if len(touched) >= 2:
                n += 1
    return n


def _load_cov_files_map(cov_path: Path) -> dict[str, Any]:
    if not cov_path.is_file():
        return {}
    try:
        data = json.loads(cov_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    fm = data.get("files")
    return fm if isinstance(fm, dict) else {}


def _executed_lines_for_file(
    files_map: dict[str, Any], rel: str, *, dataset_repo: Path | None = None
) -> set[int]:
    fd = _lookup_fd(files_map, rel, dataset_repo=dataset_repo)
    if fd is None:
        return set()
    return executed_lines_from_file_block(fd)


def _plus_def_names_per_file(diff_text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for b_path, chunk in _iter_git_chunks(diff_text):
        names: list[str] = []
        for line in chunk.splitlines():
            if not line.startswith("+") or line.startswith("+++"):
                continue
            body = line[1:]
            m = re.match(r"^\s*def\s+(\w+)\s*\(", body)
            if m:
                names.append(m.group(1))
        if names:
            out.setdefault(_norm_rel(b_path), []).extend(names)
    return out


def _func_ranges_in_file(repo: Path, rel: str, want_names: list[str]) -> list[tuple[str, int, int]]:
    path = repo / rel
    if not path.is_file():
        return []
    try:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except (OSError, SyntaxError):
        return []
    want_set = list(dict.fromkeys(want_names))
    got: dict[str, tuple[int, int]] = {}

    def visit_body(body: list[ast.stmt]) -> None:
        for node in body:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                nm = node.name
                if nm in want_set and nm not in got:
                    end = getattr(node, "end_lineno", node.lineno) or node.lineno
                    got[nm] = (node.lineno, max(end, node.lineno))
            if isinstance(node, ast.ClassDef):
                visit_body(node.body)

    visit_body(tree.body)
    return [(nm, got[nm][0], got[nm][1]) for nm in want_names if nm in got]


def compute_added_function_coverage_pct(
    state: WorkflowState,
    dataset_repo: Path,
    cov_json: Path | None,
) -> dict[str, Any]:
    env_funcs = _env_csv("CHANGED_FUNCS")
    by_file_defs = _plus_def_names_per_file(state.diff or "")
    files_map = _load_cov_files_map(Path(cov_json)) if cov_json else {}

    specs: list[tuple[str, str]] = []
    if env_funcs:
        for tok in env_funcs:
            tok = tok.strip()
            if ":" in tok:
                fp, nm = tok.rsplit(":", 1)
                specs.append((_norm_rel(fp), nm.strip()))
            else:
                rels_py = [_norm_rel(r) for r in sorted(by_file_defs.keys())] if by_file_defs else []
                if not rels_py:
                    rels_py = [
                        _norm_rel(r)
                        for r in sorted(production_changed_files(state.changed_files or []))
                        if str(r).endswith(".py")
                    ]
                for rel in rels_py:
                    specs.append((rel, tok))
    else:
        for rel, nms in by_file_defs.items():
            if is_under_project_tests_tree(rel):
                continue
            for nm in nms:
                specs.append((rel, nm))

    if not specs:
        for rel, nm in _specs_from_change_analysis_added_funcs(state):
            specs.append((rel, nm))

    if not specs:
        return {
            "added_function_coverage_pct": None,
            "added_function_total": 0,
            "added_function_covered": 0,
            "note": "无 CHANGED_FUNCS、diff 中无 +def、change_analysis 无 ADD 的 function/method",
        }

    seen: set[tuple[str, str]] = set()
    uniq: list[tuple[str, str]] = []
    for rel, nm in specs:
        if rel and nm:
            k = (rel, nm)
            if k in seen:
                continue
            seen.add(k)
            uniq.append((rel, nm))

    total = covered = 0
    exe_cache: dict[str, set[int]] = {}
    for rel, nm in uniq:
        rngs = _func_ranges_in_file(dataset_repo, rel, [nm])
        if not rngs:
            total += 1
            continue
        _, lo, hi = rngs[0]
        total += 1
        exe = exe_cache.get(rel)
        if exe is None:
            exe = _executed_lines_for_file(files_map, rel, dataset_repo=dataset_repo)
            exe_cache[rel] = exe
        if any(line in exe for line in range(lo, hi + 1)):
            covered += 1

    pct = _safe_div(100.0 * float(covered), float(total))
    return {
        "added_function_coverage_pct": None if pct is None else round(pct, 3),
        "added_function_total": total,
        "added_function_covered": covered,
    }


def _unpack_attribute_chain(expr: ast.expr) -> tuple[str | None, list[str]]:
    """解析 ``a.b.c`` 调用目标为 (``a``, [``b``, ``c``])。"""
    attrs: list[str] = []
    cur: ast.expr = expr
    while isinstance(cur, ast.Attribute):
        attrs.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        return cur.id, list(reversed(attrs))
    return None, []


def _top_level_import_local_to_dotted(imports: list[ast.Import | ast.ImportFrom]) -> dict[str, str]:
    """模块内本地名 -> 用于路径解析的 dotted 前缀（与 ``dotted_to_rel`` 一致）。"""
    out: dict[str, str] = {}
    for im in imports:
        if isinstance(im, ast.Import):
            for alias in im.names:
                parts = alias.name.split(".")
                if not parts:
                    continue
                local = alias.asname or parts[0]
                out[local] = parts[0]
        elif isinstance(im, ast.ImportFrom) and im.module:
            if im.level and im.level > 0:
                continue
            base = im.module
            for alias in im.names:
                if alias.name == "*":
                    continue
                local = alias.asname or alias.name
                out[local] = f"{base}.{alias.name}"
    return out


def compute_cross_module_test_cases(
    state: WorkflowState,
    dataset_repo: Path,
    changed_rels: list[str],
) -> dict[str, Any]:
    changed = {_norm_rel(p) for p in changed_rels if str(p).strip()}
    if len(changed) < 2:
        return {"cross_module_test_case_count": 0, "note": "变更文件少于 2，无法构成跨模块"}

    def dotted_to_rel(mod: str) -> str | None:
        mod = mod.strip()
        rel_py = mod.replace(".", "/") + ".py"
        repo_r = dataset_repo.resolve()
        if (dataset_repo / rel_py).resolve().is_file():
            return _norm_rel(rel_py)
        pkg_init = dataset_repo / mod.replace(".", "/") / "__init__.py"
        if pkg_init.resolve().is_file():
            return _norm_rel(str(pkg_init.relative_to(repo_r)))
        return None

    def register_import_aliases(touched: set[str], sub: ast.AST) -> None:
        if isinstance(sub, ast.Import):
            for alias in sub.names:
                r = dotted_to_rel(alias.name)
                if r and r in changed:
                    touched.add(r)
                parts = alias.name.split(".")
                if parts:
                    r2 = dotted_to_rel(parts[0])
                    if r2 and r2 in changed:
                        touched.add(r2)
        elif isinstance(sub, ast.ImportFrom) and sub.module:
            if not (getattr(sub, "level", 0) or 0):
                r = dotted_to_rel(sub.module)
                if r and r in changed:
                    touched.add(r)
                for alias in sub.names:
                    if alias.name == "*":
                        continue
                    subpath = f"{sub.module}.{alias.name}"
                    r3 = dotted_to_rel(subpath)
                    if r3 and r3 in changed:
                        touched.add(r3)

    def register_dotted_prefixes(touched: set[str], dotted: str) -> None:
        parts = [p for p in dotted.split(".") if p]
        for i in range(len(parts), 0, -1):
            prefix = ".".join(parts[:i])
            rel_h = dotted_to_rel(prefix)
            if rel_h and rel_h in changed:
                touched.add(rel_h)

    def register_call(
        touched: set[str],
        func: ast.expr,
        local_to_dotted: dict[str, str],
    ) -> None:
        if isinstance(func, ast.Name):
            d = local_to_dotted.get(func.id)
            if d:
                register_dotted_prefixes(touched, d)
            register_dotted_prefixes(touched, func.id)
        elif isinstance(func, ast.Attribute):
            base, rest = _unpack_attribute_chain(func)
            if base is None:
                return
            root = local_to_dotted.get(base, base)
            for j in range(len(rest) + 1):
                if j == 0:
                    cand = root
                else:
                    cand = f"{root}.{'.'.join(rest[:j])}"
                register_dotted_prefixes(touched, cand)

    count = 0
    notes: list[str] = []

    for gt in state.generated_tests or []:
        src = gt.content or ""
        try:
            tree = ast.parse(src)
        except SyntaxError:
            notes.append(f"跳过语法错误的生成文件: {getattr(gt, 'path', '?')}")
            continue

        module_aliases: list[ast.Import | ast.ImportFrom] = []
        for bn in tree.body:
            if isinstance(bn, ast.Import | ast.ImportFrom):
                module_aliases.append(bn)

        local_to_dotted = _top_level_import_local_to_dotted(module_aliases)

        for node in tree.body:
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            if not node.name.startswith("test_"):
                continue
            touched: set[str] = set()
            for im in module_aliases:
                register_import_aliases(touched, im)
            for sub in ast.walk(node):
                register_import_aliases(touched, sub)
                if isinstance(sub, ast.Call):
                    register_call(touched, sub.func, local_to_dotted)
            if len(touched) >= 2:
                count += 1

    if count == 0 and len(changed) >= 2:
        loose = _cross_module_loose_substring_count(state, changed)
        if loose > 0:
            count = loose
            notes.append("跨模块：宽松子串模式（同一 test_* 含≥2 个变更 .py 路径或对应 import 点号路径）")

    out: dict[str, Any] = {"cross_module_test_case_count": count}
    if notes:
        out["notes"] = notes
    return out


def _pytest_collect_test_count(repo: Path, python_exe: str) -> tuple[int | None, str]:
    try:
        p = subprocess.run(
            [python_exe, "-m", "pytest", "--collect-only", "-q"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=900,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, str(e)
    text = (p.stdout or "") + "\n" + (p.stderr or "")
    m = re.search(r"(\d+)\s+test(?:s)?\s+collected", text, re.I)
    if not m:
        return None, "无法解析 pytest --collect-only 输出中的 tests collected"
    return int(m.group(1)), ""


def _parse_pytest_duration_seconds(combined_out: str) -> float | None:
    blob = combined_out or ""
    matches = list(re.finditer(r"\bin\s+(\d+(?:\.\d+)?)\s*s\b", blob, re.I))
    if matches:
        return float(matches[-1].group(1))
    return None


def _suite_time_cache_path(mutiagent_root: Path) -> Path:
    return Path(mutiagent_root) / "log" / "full_pytest_suite_time_cache.json"


def _read_cached_full_seconds(repo: Path, mutiagent_root: Path) -> float | None:
    path = _suite_time_cache_path(mutiagent_root)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    key = str(repo.resolve())
    entry = data.get(key)
    if isinstance(entry, dict):
        sec = entry.get("seconds")
        return float(sec) if isinstance(sec, (int, float)) else None
    if isinstance(entry, (int, float)):
        return float(entry)
    return None


def _write_cached_full_seconds(repo: Path, mutiagent_root: Path, seconds: float) -> None:
    path = _suite_time_cache_path(mutiagent_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, Any] = {}
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            data = loaded if isinstance(loaded, dict) else {}
        except (OSError, json.JSONDecodeError):
            data = {}
    key = str(repo.resolve())
    data[key] = {
        "seconds": round(seconds, 3),
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def measure_full_suite_wall_seconds(repo: Path, python_exe: str, mutiagent_root: Path) -> float | None:
    cached = _read_cached_full_seconds(repo, mutiagent_root)
    if cached is not None and cached > 0:
        return cached
    allowed = os.environ.get("MUTIAGENT_MEASURE_FULL_SUITE_TIME", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if not allowed:
        return None
    extra = shlex.split(os.environ.get("MUTIAGENT_FULL_SUITE_PYTEST_ARGS", "").strip())
    cmd = [python_exe, "-m", "pytest", "-q", "--tb=no", *extra]
    t0 = time.monotonic()
    try:
        subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, timeout=3600)
    except (OSError, subprocess.TimeoutExpired):
        return None
    wall = max(1e-6, time.monotonic() - t0)
    _write_cached_full_seconds(repo, mutiagent_root, wall)
    return wall


def compute_extended_experiment_metrics(
    state: WorkflowState,
    dataset_repo: Path,
    *,
    cov_json_primary: Path | None,
    cov_json_fallback: Path | None,
    combined_pytest_output: str,
    selected_tests: list[str] | None,
    junit_summary: dict[str, str],
    junit_cases: list[dict[str, str]] | None = None,
    python_exe: str,
    mutiagent_repo_root: Path,
    generated_test_function_count: int,
    full_suite_wall_seconds: float | None = None,
) -> dict[str, Any]:
    notes: list[str] = []
    covp: Path | None = None
    for cand in (cov_json_fallback, cov_json_primary):
        if cand is not None and Path(cand).is_file():
            covp = Path(cand)
            break

    changed_lines_block: dict[str, Any] = {}
    if covp:
        changed_lines_block = change_line_coverage_from_diff_and_cov_paths(
            state.diff or "",
            covp,
            preferred_rels=(production_changed_files(state.changed_files) if state.changed_files else None),
            dataset_repo=dataset_repo.resolve() if dataset_repo.exists() else dataset_repo,
        )
    frac = changed_lines_block.get("recall_frac")
    tp = int(changed_lines_block.get("change_plus_lines") or 0)
    hit = int(changed_lines_block.get("covered_plus_lines") or 0)
    ch_cov_pct = round(float(frac) * 100.0, 3) if isinstance(frac, (int, float)) else None

    missed = None
    if tp > 0:
        missed = tp - hit

    dbg = state.debug if isinstance(state.debug, dict) else {}
    dwt = dbg.get("diff_worktree_check")
    if (
        tp > 0
        and hit == 0
        and isinstance(dwt, dict)
        and not dwt.get("ok", True)
    ):
        rec = (dwt.get("recommendation_zh") or "").strip()
        notes.append(
            "变更行覆盖率 0% 可能因 diff 与工作区行号不一致（未应用补丁或与 diff 目标版本不同）；"
            + (f"建议: {rec}" if rec else "建议同步工作区与 diff 后再测。")
        )
    fn_cov = compute_added_function_coverage_pct(state, dataset_repo, covp)
    if fn_cov.get("note"):
        notes.append(str(fn_cov["note"]))

    base_prod = [_norm_rel(x) for x in production_changed_files(state.changed_files or [])]
    ef = _env_csv("CHANGED_FILES")
    if ef:
        if _truthy_env("CHANGED_FILES_STRICT"):
            changed_for_cross = [_norm_rel(x) for x in ef]
        else:
            changed_for_cross = sorted(set(base_prod) | {_norm_rel(x) for x in ef})
    else:
        changed_for_cross = base_prod
    cross = compute_cross_module_test_cases(state, dataset_repo, changed_for_cross)
    if cross.get("note"):
        notes.append(str(cross["note"]))
    for x in cross.get("notes") or []:
        if x:
            notes.append(str(x))

    collected, cerr = _pytest_collect_test_count(dataset_repo, python_exe)
    if collected is None and cerr:
        notes.append(f"pytest_collect_only: {cerr}")
    compression = None
    if collected is not None and collected > 0 and generated_test_function_count >= 0:
        compression = round((1.0 - generated_test_function_count / float(collected)) * 100.0, 3)

    failing_env = _env_csv("FAILING_TESTS")
    bdr_src = "FAILING_TESTS"
    if not failing_env:
        failing_env = _junit_failed_case_ids(junit_cases)
        if failing_env:
            bdr_src = "junit_failures"

    bdr_pct: float | None = None
    bdr_note: str | None = None
    if not failing_env:
        bdr_note = "N/A: 未设置 FAILING_TESTS 且 junit 无失败用例"
    else:
        sel_set = {_norm_casefold_id(x) for x in (selected_tests or []) if str(x).strip()}
        inter = sum(1 for fe in failing_env if _norm_casefold_id(fe) in sel_set)
        r = _safe_div(100.0 * float(inter), float(len(failing_env)))
        bdr_pct = None if r is None else round(r, 3)
        bdr_note = f"失败用例命中 selected_tests: {inter}/{len(failing_env)}（来源: {bdr_src}）"

    selected_sec = _parse_pytest_duration_seconds(combined_pytest_output)
    if selected_sec is None and junit_summary.get("time"):
        parts = re.findall(r"\d+(?:\.\d+)?", str(junit_summary.get("time") or ""))
        if parts:
            selected_sec = sum(float(x) for x in parts)

    full_sec: float | None = None
    if full_suite_wall_seconds is not None and float(full_suite_wall_seconds) > 0:
        full_sec = float(full_suite_wall_seconds)
    if full_sec is None:
        full_sec = measure_full_suite_wall_seconds(dataset_repo, python_exe, mutiagent_repo_root)

    time_red: float | None = None
    if selected_sec is not None and full_sec is not None and full_sec > 0:
        time_red = round((1.0 - selected_sec / full_sec) * 100.0, 3)
    elif (
        not _falsy_env("MUTIAGENT_EXEC_TIME_REDUCTION_ESTIMATE")
        and selected_sec is not None
        and selected_sec > 0
        and collected is not None
        and collected > 0
        and generated_test_function_count > 0
        and collected >= generated_test_function_count
    ):
        full_sec = float(selected_sec) * (float(collected) / float(generated_test_function_count))
        time_red = round((1.0 - selected_sec / full_sec) * 100.0, 3)
        notes.append(
            "exec_time_reduction: 无全量墙钟缓存，已用 selected×(project_collected/generated) 粗估全量时间 "
            f"（full≈{round(full_sec, 2)}s）；实测请设 MUTIAGENT_MEASURE_FULL_SUITE_TIME=1；"
            "若不要粗估可设 MUTIAGENT_EXEC_TIME_REDUCTION_ESTIMATE=0"
        )
    elif full_sec is None and _read_cached_full_seconds(dataset_repo, mutiagent_repo_root) is None:
        if _falsy_env("MUTIAGENT_EXEC_TIME_REDUCTION_ESTIMATE"):
            notes.append(
                "exec_time_reduction: 无全量耗时缓存且已关闭粗估（MUTIAGENT_EXEC_TIME_REDUCTION_ESTIMATE=0）；"
                "可设 MUTIAGENT_MEASURE_FULL_SUITE_TIME=1 实测并缓存，或去掉该开关以启用默认粗估"
            )
        elif not (
            selected_sec is not None
            and selected_sec > 0
            and collected is not None
            and collected > 0
            and generated_test_function_count > 0
        ):
            notes.append(
                "exec_time_reduction: 无法粗估（缺选中墙钟或 pytest collect/生成函数计数）；"
                "可设 MUTIAGENT_MEASURE_FULL_SUITE_TIME=1 实测全量"
            )

    return {
        "changed_line_coverage_pct": ch_cov_pct,
        "missed_changed_line_count": missed,
        "changed_plus_line_total_count": tp if tp > 0 else None,
        "changed_plus_line_covered_count": hit if tp > 0 else None,
        "added_function_coverage_pct": fn_cov.get("added_function_coverage_pct"),
        "added_function_total": fn_cov.get("added_function_total"),
        "added_function_covered": fn_cov.get("added_function_covered"),
        "cross_module_test_case_count": cross.get("cross_module_test_case_count"),
        "test_case_compression_pct": compression,
        "project_collected_test_count": collected,
        "generated_selected_test_function_count": generated_test_function_count,
        "bug_detection_rate_pct": bdr_pct,
        "bug_detection_rate_note": bdr_note,
        "selected_pytest_wall_seconds": round(selected_sec, 4) if selected_sec is not None else None,
        "full_suite_cached_wall_seconds": round(full_sec, 4) if full_sec is not None else None,
        "exec_time_reduction_pct": time_red,
        "extended_metrics_notes": notes or None,
    }
