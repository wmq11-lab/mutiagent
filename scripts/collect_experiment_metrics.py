#!/usr/bin/env python3
"""
收集多智能体实验指标。

与 mutiagent 主流程一致的核心指标（evaluation / metrics.py）：
  precision（通过率或可覆盖为 pytest passed/total）、recall（变更 + 行覆盖或旧选测 recall）、
  f1（2PR/(P+R)）、reduction、time_reduction、redundancy。
  若 supplementary 中含 pytest passed/total 与 change_vs_coverage.recall_frac，将覆盖写入 metrics。

基于 test 文件 / coverage.json / diff / pytest 输出的统计作为 supplementary，避免与核心 6 项混淆。

与 Pynguin 风格实验脚本对齐的字段：生成质量（test_file_exists, syntax_correct, test_count）、
执行结果（parse_pytest_output）、覆盖率（line_coverage, branch_coverage, covered_lines, total_lines 等）；
同时保留 cov_* 前缀的覆盖率键以兼容旧用法。
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# 项目根：scripts/ -> parents[1]
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from mutiagent.evaluation.change_line_coverage import change_line_coverage_from_diff_and_cov_paths
from mutiagent.evaluation.coverage_json import parse_coverage_json
from mutiagent.evaluation.metrics import compute_all_metrics
from mutiagent.evaluation.pytest_parsing import parse_pytest_output


def count_test_functions(test_file: str) -> int:
    with open(test_file, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    n = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            n += 1
    return n


def check_syntax(test_file: str) -> bool:
    try:
        with open(test_file, "r", encoding="utf-8") as f:
            ast.parse(f.read())
        return True
    except SyntaxError:
        return False


def run_tests_and_collect_results(
    test_file: str,
    coverage_json: str,
    cov_module: str,
    cwd: Path,
) -> dict[str, Any]:
    """
    运行 pytest（含 coverage json 报告），并解析输出；与 Pynguin 参考脚本行为一致。
    完整日志写入 ``{coverage_stem}_pytest_output.txt``。
    """
    os.makedirs(os.path.dirname(coverage_json) or ".", exist_ok=True)

    cmd = [
        "pytest",
        test_file,
        "-v",
        "--tb=short",
        f"--cov={cov_module}",
        "--cov-branch",
        f"--cov-report=json:{coverage_json}",
    ]
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    exec_results = parse_pytest_output(output)

    log_path = coverage_json.replace(".json", "_pytest_output.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(output)

    exec_results = dict(exec_results)
    exec_results["pytest_log_path"] = log_path
    return exec_results


def parse_diff_simple(diff_path: str) -> dict[str, Any]:
    """从 unified diff 粗统计 + 新增 def 名（不保证与真实 AST 一致）。"""
    with open(diff_path, "r", encoding="utf-8") as f:
        text = f.read()
    added = sum(1 for line in text.splitlines() if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in text.splitlines() if line.startswith("-") and not line.startswith("---"))
    names: set[str] = set()
    for m in re.finditer(r"^\+\s*def\s+(\w+)\s*\(", text, re.MULTILINE):
        names.add(m.group(1))
    return {
        "total_added_lines": added,
        "total_removed_lines": removed,
        "added_function_names": sorted(names),
    }


def change_line_coverage_from_diff(
    diff_path: str, cov_path: str, rel_path_in_cov: str | None
) -> dict[str, Any]:
    """
    将 diff 中变更 ``+`` 行与 coverage.json 对齐，得到 recall_frac（0~1）及百分数 change_line_hit_rate。
    ``rel_path_in_cov``：优先只聚合该路径对应 chunk；不传则对所有 ``diff --git`` 块与 coverage 能匹配的文件聚合。
    """
    if not os.path.exists(diff_path) or not os.path.exists(cov_path):
        return {
            "recall_frac": None,
            "change_plus_lines": 0,
            "covered_plus_lines": 0,
            "change_line_hit_rate": 0.0,
            "note": "缺少 diff 或 coverage",
        }
    diff_text = Path(diff_path).read_text(encoding="utf-8")
    preferred = [rel_path_in_cov] if rel_path_in_cov else None
    base = change_line_coverage_from_diff_and_cov_paths(diff_text, cov_path, preferred_rels=preferred)
    frac = base.get("recall_frac")
    hit_pct = round(float(frac) * 100.0, 2) if isinstance(frac, (int, float)) else 0.0
    out = dict(base)
    out["change_line_hit_rate"] = hit_pct
    return out
def build_payload_from_args(ns: argparse.Namespace) -> dict[str, Any]:
    """与 evaluation_agent 入参一致：由 CLI 或 JSON 提供。"""
    if getattr(ns, "metrics_json", None) and Path(ns.metrics_json).is_file():
        with open(ns.metrics_json, "r", encoding="utf-8") as f:
            raw = json.load(f)
    else:
        raw = {
            "selected_tests": _read_lines(getattr(ns, "selected_list", None)) or [],
            "all_tests": _read_lines(getattr(ns, "all_list", None)) or [],
            "failing_tests": _read_lines(getattr(ns, "failing_list", None)) or [],
            "execution_time": float(getattr(ns, "exec_time", 0.0) or 0.0),
            "full_time": float(getattr(ns, "full_time", 0.0) or 0.0),
        }
    st = list(raw.get("selected_tests") or [])
    at = list(raw.get("all_tests") or st)
    return {
        "selected_tests": st,
        "all_tests": at,
        "failing_tests": list(raw.get("failing_tests") or []),
        "execution_time": float(raw.get("execution_time") or 0.0),
        "full_time": float(raw.get("full_time") or raw.get("execution_time") or 0.0),
    }


def _read_lines(p: str | None) -> list[str]:
    if not p or not Path(p).is_file():
        return []
    return [ln.strip() for ln in Path(p).read_text(encoding="utf-8").splitlines() if ln.strip()]


def _merge_coverage_dict(sup: dict[str, Any], cov: dict[str, Any]) -> None:
    for k, v in cov.items():
        sup[k] = v
        sup[f"cov_{k}"] = v


def _zero_pytest_exec() -> dict[str, Any]:
    return {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "deselected": 0,
        "xfailed": 0,
        "xpassed": 0,
        "pass_rate": 0.0,
        "execution_success": False,
    }


def collect(
    test_file: str | None,
    coverage_json: str | None,
    diff_file: str | None,
    source_file: str | None,
    rel_in_cov: str | None,
    payload: dict[str, Any],
    *,
    pytest_output: str | None = None,
    run_pytest: bool = False,
    cov_module: str | None = None,
    pytest_cwd: Path | None = None,
) -> dict[str, Any]:
    core = compute_all_metrics(
        selected_tests=payload["selected_tests"],
        all_tests=payload["all_tests"] or list(payload["selected_tests"]),
        failing_tests=payload["failing_tests"],
        execution_time=payload["execution_time"],
        full_time=payload["full_time"] or payload["execution_time"],
    )
    out: dict[str, Any] = {
        "metrics": core,
    }
    sup: dict[str, Any] = {}
    if test_file:
        p = Path(test_file)
        sup["test_file"] = str(p)
        if p.is_file():
            sup["test_file_exists"] = True
            sup["syntax_ok"] = check_syntax(str(p))
            sup["syntax_correct"] = sup["syntax_ok"]
            n_fn = count_test_functions(str(p))
            sup["test_function_count"] = n_fn
            sup["test_count"] = n_fn
        else:
            sup["test_file_exists"] = False
            sup["syntax_ok"] = False
            sup["syntax_correct"] = False
            sup["test_function_count"] = 0
            sup["test_count"] = 0

    if test_file and not Path(test_file).is_file():
        sup.update(_zero_pytest_exec())
    if run_pytest and test_file and coverage_json and cov_module:
        cwd = pytest_cwd or Path.cwd()
        if Path(test_file).is_file():
            ex = run_tests_and_collect_results(str(test_file), coverage_json, cov_module, cwd)
            for k, v in ex.items():
                if k == "pytest_log_path":
                    sup["pytest_log_path"] = v
                else:
                    sup[k] = v
    if pytest_output and os.path.exists(pytest_output):
        with open(pytest_output, "r", encoding="utf-8") as f:
            po = f.read()
        sup["pytest_output_file"] = pytest_output
        sup.update(parse_pytest_output(po))

    if coverage_json and os.path.exists(coverage_json):
        sup["coverage_file"] = coverage_json
        _merge_coverage_dict(sup, parse_coverage_json(coverage_json))
    if diff_file and os.path.exists(diff_file):
        sup["diff"] = parse_diff_simple(diff_file)
    if source_file and os.path.exists(source_file):
        sup["source_file"] = source_file
    if diff_file and coverage_json and os.path.exists(diff_file) and os.path.exists(coverage_json):
        sup["change_vs_coverage"] = change_line_coverage_from_diff(diff_file, coverage_json, rel_in_cov)

    pr_sup: float | None = None
    tt_raw = sup.get("total_tests")
    ps_raw = sup.get("passed")
    try:
        tt_f = float(tt_raw) if tt_raw is not None else 0.0
        if tt_f > 0 and ps_raw is not None:
            pr_sup = float(ps_raw) / tt_f
    except (TypeError, ValueError):
        pr_sup = None

    rr_sup: float | None = None
    cv = sup.get("change_vs_coverage")
    if isinstance(cv, dict):
        rf = cv.get("recall_frac")
        if isinstance(rf, (int, float)):
            rr_sup = float(rf)

    if pr_sup is not None or rr_sup is not None:
        out["metrics"] = compute_all_metrics(
            selected_tests=payload["selected_tests"],
            all_tests=payload["all_tests"] or list(payload["selected_tests"]),
            failing_tests=payload["failing_tests"],
            execution_time=payload["execution_time"],
            full_time=payload["full_time"] or payload["execution_time"],
            precision_pass_rate=pr_sup,
            recall_change_line=rr_sup,
        )

    if sup:
        out["supplementary"] = sup
    return out


def _print_supplementary_pretty(sup: dict[str, Any]) -> None:
    """按 Pynguin 参考脚本的分块打印（生成质量 / 执行结果 / 覆盖率 / 其它）。"""
    gq_keys = (
        "test_file",
        "test_file_exists",
        "syntax_ok",
        "syntax_correct",
        "test_function_count",
        "test_count",
    )
    ex_keys = (
        "total_tests",
        "passed",
        "failed",
        "errors",
        "skipped",
        "deselected",
        "xfailed",
        "xpassed",
        "pass_rate",
        "execution_success",
        "pytest_log_path",
        "pytest_output_file",
    )
    cov_keys = (
        "coverage_file",
        "line_coverage",
        "branch_coverage",
        "covered_lines",
        "total_statements",
        "total_lines",
    )

    def _sub(title: str, keys: tuple[str, ...]) -> None:
        chunk = {k: sup[k] for k in keys if k in sup}
        if not chunk:
            return
        print(title)
        for k, v in chunk.items():
            if k in ("line_coverage", "branch_coverage") and isinstance(v, (int, float)):
                print(f"  {k}: {float(v):.2f}")
            else:
                print(f"  {k}: {v}")
        print()

    _sub("【生成质量】", gq_keys)
    _sub("【执行结果】", ex_keys)
    _sub("【覆盖率】", cov_keys)

    used = set(gq_keys + ex_keys + cov_keys + tuple(k for k in sup if k.startswith("cov_")))
    rest = {k: v for k, v in sup.items() if k not in used}
    if rest:
        print("【其它】")

        def _p(d: Any, indent: int = 0) -> None:
            p2 = "  " * indent
            if isinstance(d, dict):
                for k, v in d.items():
                    if isinstance(v, (dict, list)):
                        print(f"{p2}{k}:")
                        _p(v, indent + 1)
                    else:
                        print(f"{p2}{k}: {v}")
            else:
                print(f"{p2}{d}")

        _p(rest)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="计算与 mutiagent EvaluationAgent 一致的核心 6 项指标，可选附加覆盖率/diff/pytest 执行统计。",
    )
    ap.add_argument(
        "--metrics-json",
        help="含 selected_tests, all_tests, failing_tests, execution_time, full_time 的 JSON（列表或路径）",
    )
    ap.add_argument("--selected-list", help="每行一个用例 id，对应 selected_tests")
    ap.add_argument("--all-list", help="全量用例 id，对应 all_tests")
    ap.add_argument("--failing-list", help="失败用例 id，对应 failing_tests")
    ap.add_argument("--exec-time", type=float, default=0.0, help="执行耗时（秒）")
    ap.add_argument("--full-time", type=float, default=0.0, help="全量基线耗时（秒），默认同 exec-time")
    ap.add_argument("--test-file", help="被统计的测试文件（辅助）")
    ap.add_argument("--coverage-json", help="coverage 工具产出的 .json")
    ap.add_argument("--diff-file", help="unified diff 文件（辅助）")
    ap.add_argument("--source-file", help="与 coverage 对应的一份源文件路径（仅记录）")
    ap.add_argument(
        "--source-rel-for-cov",
        help="coverage.json 里 files 键中的相对路径，用于变更行与覆盖行对齐；多文件时必填",
    )
    ap.add_argument(
        "--pytest-output",
        help="pytest 的 stdout+stderr 文本文件，解析 passed/failed/...（与 run-pytest 二选一或叠加）",
    )
    ap.add_argument(
        "--run-pytest",
        action="store_true",
        help="在本机执行 pytest --cov=... 并写 coverage json，同时解析终端输出",
    )
    ap.add_argument(
        "--cov-module",
        help="--run-pytest 时传给 pytest 的 --cov= 模块/包路径",
    )
    ap.add_argument(
        "--pytest-cwd",
        type=Path,
        help="执行 pytest 时的工作目录，默认当前工作目录",
    )
    ap.add_argument("-o", "--output", help="输出 JSON 路径，默认 当前目录 experiment_metrics_out.json")
    args = ap.parse_args()

    payload = build_payload_from_args(args)
    pytest_cwd = args.pytest_cwd
    if args.run_pytest:
        if not args.cov_module:
            ap.error("--run-pytest 需要同时指定 --cov-module")
        if not args.test_file or not args.coverage_json:
            ap.error("--run-pytest 需要同时指定 --test-file 与 --coverage-json")

    out = collect(
        test_file=args.test_file,
        coverage_json=args.coverage_json,
        diff_file=args.diff_file,
        source_file=args.source_file,
        rel_in_cov=args.source_rel_for_cov,
        payload=payload,
        pytest_output=args.pytest_output,
        run_pytest=bool(args.run_pytest),
        cov_module=args.cov_module,
        pytest_cwd=pytest_cwd,
    )

    print("=" * 60)
    print("核心指标（与 mutiagent.evaluation.metrics 一致）")
    print("=" * 60)
    for k, v in out["metrics"].items():
        print(f"  {k}: {v}")
    if "supplementary" in out:
        print()
        print("辅助统计（非核心 6 项，含 Pynguin 风格字段）")
        print("=" * 60)
        _print_supplementary_pretty(out["supplementary"])

    out_path = Path(args.output) if args.output else Path.cwd() / "experiment_metrics_out.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print(f"已写入 {out_path}")


if __name__ == "__main__":
    main()
