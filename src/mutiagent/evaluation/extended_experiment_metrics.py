"""
实验扩展指标：变更行 / 新增函数 / 跨模块用例 / 压缩率 / Bug detection / 执行时间缩减等。

环境变量（可选）::
  CHANGED_FILES                 逗号分隔相对路径，缺省使 WorkflowState.changed_files
  CHANGED_FUNCS                 ``name`` 或 ``path/to.py:name``
  FAILING_TESTS                 逗号分隔失败 nodeid（与 selected_tests 做集合交）
  MUTIAGENT_FULL_SUITE_PYTEST_ARGS      测全量耗时时的附加 pytest 参数（shlex 分词）
  MUTIAGENT_MEASURE_FULL_SUITE_TIME      若为 1/true：无缓存时对数据集跑完整 pytest 并写入缓存（可能很慢）
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
from mutiagent.graph.state import WorkflowState


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


def _load_cov_files_map(cov_path: Path) -> dict[str, Any]:
    if not cov_path.is_file():
        return {}
    try:
        data = json.loads(cov_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    fm = data.get("files")
    return fm if isinstance(fm, dict) else {}


def _executed_lines_for_file(files_map: dict[str, Any], rel: str) -> set[int]:
    fd = _lookup_fd(files_map, rel)
    if fd is None:
        return set()
    ex: set[int] = set()
    for el in fd.get("executed_lines") or fd.get("covered_lines") or []:
        if isinstance(el, int):
            ex.add(el)
    if not ex and isinstance(fd.get("line_data"), list):
        for i, row in enumerate(fd["line_data"], 1):
            if isinstance(row, dict) and row.get("hits", 0) > 0:
                ex.add(i)
    return ex


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
                    rels_py = [_norm_rel(r) for r in sorted(state.changed_files or []) if str(r).endswith(".py")]
                for rel in rels_py:
                    specs.append((rel, tok))
    else:
        for rel, nms in by_file_defs.items():
            for nm in nms:
                specs.append((rel, nm))

    if not specs:
        return {
            "added_function_coverage_pct": None,
            "added_function_total": 0,
            "added_function_covered": 0,
            "note": "无 CHANGED_FUNCS 且 diff 中无 +def 可解析",
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
            exe = _executed_lines_for_file(files_map, rel)
            exe_cache[rel] = exe
        if any(line in exe for line in range(lo, hi + 1)):
            covered += 1

    pct = _safe_div(100.0 * float(covered), float(total))
    return {
        "added_function_coverage_pct": None if pct is None else round(pct, 3),
        "added_function_total": total,
        "added_function_covered": covered,
    }


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
        elif isinstance(sub, ast.ImportFrom) and sub.module:
            r = dotted_to_rel(sub.module)
            if r and r in changed:
                touched.add(r)

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
            if len(touched) >= 2:
                count += 1

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
    python_exe: str,
    mutiagent_repo_root: Path,
    generated_test_function_count: int,
) -> dict[str, Any]:
    notes: list[str] = []
    covp: Path | None = None
    for cand in (cov_json_primary, cov_json_fallback):
        if cand is not None and Path(cand).is_file():
            covp = Path(cand)
            break

    changed_lines_block: dict[str, Any] = {}
    if covp:
        changed_lines_block = change_line_coverage_from_diff_and_cov_paths(
            state.diff or "",
            covp,
            preferred_rels=state.changed_files if state.changed_files else None,
        )
    frac = changed_lines_block.get("recall_frac")
    tp = int(changed_lines_block.get("change_plus_lines") or 0)
    hit = int(changed_lines_block.get("covered_plus_lines") or 0)
    ch_cov_pct = round(float(frac) * 100.0, 3) if isinstance(frac, (int, float)) else None

    missed = None
    if tp > 0:
        missed = tp - hit

    fn_cov = compute_added_function_coverage_pct(state, dataset_repo, covp)

    changed_for_cross = list(state.changed_files or [])
    ef = _env_csv("CHANGED_FILES")
    if ef:
        changed_for_cross = [_norm_rel(x) for x in ef]
    cross = compute_cross_module_test_cases(state, dataset_repo, changed_for_cross)

    collected, cerr = _pytest_collect_test_count(dataset_repo, python_exe)
    if collected is None and cerr:
        notes.append(f"pytest_collect_only: {cerr}")
    compression = None
    if collected is not None and collected > 0 and generated_test_function_count >= 0:
        compression = round((1.0 - generated_test_function_count / float(collected)) * 100.0, 3)

    failing_env = _env_csv("FAILING_TESTS")
    bdr_pct: float | None = None
    bdr_note: str | None = None
    if not failing_env:
        bdr_note = "N/A: FAILING_TESTS 未设置"
    else:
        sel_set = {_norm_casefold_id(x) for x in (selected_tests or []) if str(x).strip()}
        inter = sum(1 for fe in failing_env if _norm_casefold_id(fe) in sel_set)
        r = _safe_div(100.0 * float(inter), float(len(failing_env)))
        bdr_pct = None if r is None else round(r, 3)

    selected_sec = _parse_pytest_duration_seconds(combined_pytest_output)
    if selected_sec is None and junit_summary.get("time"):
        parts = re.findall(r"\d+(?:\.\d+)?", str(junit_summary.get("time") or ""))
        if parts:
            selected_sec = sum(float(x) for x in parts)

    full_sec = measure_full_suite_wall_seconds(dataset_repo, python_exe, mutiagent_repo_root)
    time_red = None
    if selected_sec is not None and full_sec is not None and full_sec > 0:
        time_red = round((1.0 - selected_sec / full_sec) * 100.0, 3)
    elif full_sec is None and _read_cached_full_seconds(dataset_repo, mutiagent_repo_root) is None:
        notes.append(
            "exec_time_reduction: 无全量耗时缓存；设置 MUTIAGENT_MEASURE_FULL_SUITE_TIME=1 可首次测量并缓存"
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
