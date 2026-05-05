from __future__ import annotations

import logging
import re
from pathlib import Path

from mutiagent.evaluation.change_line_coverage import change_line_coverage_from_diff_and_cov_paths
from mutiagent.evaluation.coverage_json import parse_coverage_json
from mutiagent.evaluation.metrics import compute_all_metrics
from mutiagent.graph.state import EvalSummary, PytestCaseResult, WorkflowState

_log = logging.getLogger("mutiagent.workflow")


def _extract_coverage(stdout: str, stderr: str = "") -> float | None:
    blob = "\n".join([stdout or "", stderr or ""])
    m = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", blob)
    if not m:
        return None
    try:
        return float(m.group(1)) / 100.0
    except Exception:
        return None


def _coverage_from_report_dir(report_dir: str | None) -> float | None:
    if not report_dir:
        return None
    path = Path(report_dir) / "coverage.json"
    if not path.is_file():
        return None
    data = parse_coverage_json(str(path))
    lc = data.get("line_coverage")
    if lc is None:
        return None
    try:
        return float(lc) / 100.0
    except (TypeError, ValueError):
        return None


def _case_id(item: dict[str, str]) -> str:
    cls = (item.get("classname") or "").strip()
    name = (item.get("name") or "").strip()
    if cls and name:
        return f"{cls}::{name}"
    if name:
        return name
    return cls


def _safe_float(v: object, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _junit_passed_and_total(jsum: dict[str, str], case_rows: list[dict[str, str]]) -> tuple[int, int]:
    """从 junit 聚合或逐条用例得到 (passed, total)。"""
    if case_rows:
        total = len(case_rows)
        passed = sum(1 for row in case_rows if str(row.get("status", "")).lower() == "passed")
        return passed, total
    try:
        total = int(str(jsum.get("tests") or "0").strip() or "0")
    except (TypeError, ValueError):
        total = 0
    if total <= 0:
        return 0, 0
    try:
        failures = int(str(jsum.get("failures") or "0").strip() or "0")
        errors = int(str(jsum.get("errors") or "0").strip() or "0")
        skipped = int(str(jsum.get("skipped") or "0").strip() or "0")
    except (TypeError, ValueError):
        failures = errors = skipped = 0
    passed = max(0, min(total, total - failures - errors - skipped))
    return passed, total


def evaluation_agent(state: WorkflowState) -> WorkflowState:
    if not state.run_eval:
        state.evaluation = EvalSummary(ran=False)
        return state

    ex = state.execution or {}
    code = ex.get("exit_code")
    stdout = ex.get("stdout", "") or ""
    stderr = ex.get("stderr", "") or ""
    report_dir = ex.get("report_dir")
    if report_dir is not None:
        report_dir = str(report_dir)
    cov = _extract_coverage(stdout, stderr)
    if cov is None:
        cov = _coverage_from_report_dir(report_dir)

    jsum = ex.get("junit_summary") if isinstance(ex.get("junit_summary"), dict) else {}
    jraw = ex.get("junit_cases")
    pytest_cases: list[PytestCaseResult] = []
    case_rows: list[dict[str, str]] = []
    if isinstance(jraw, list):
        for item in jraw:
            if isinstance(item, dict):
                pytest_cases.append(PytestCaseResult.model_validate(item))
                case_rows.append(item)

    selected_tests = ex.get("selected_tests")
    if not isinstance(selected_tests, list):
        selected_tests = [_case_id(row) for row in case_rows if _case_id(row)]

    all_tests = ex.get("all_tests")
    if not isinstance(all_tests, list):
        # 默认回退为已执行测试集合；若上游提供全量集合可覆盖该字段用于更准确消融评估。
        all_tests = list(selected_tests)

    failing_tests = ex.get("failing_tests")
    if not isinstance(failing_tests, list):
        failing_tests = [
            _case_id(row)
            for row in case_rows
            if str(row.get("status", "")).lower() in {"failed", "error"}
        ]

    execution_time = _safe_float(ex.get("execution_time"), default=0.0)
    if execution_time <= 0:
        execution_time = _safe_float(jsum.get("time"), default=0.0)
    explicit_full_raw = ex.get("full_time")
    full_time = _safe_float(explicit_full_raw, default=0.0)
    has_explicit_full_time = explicit_full_raw is not None and _safe_float(explicit_full_raw, 0.0) > 0.0
    if full_time <= 0:
        full_time = execution_time

    has_explicit_all_tests = isinstance(ex.get("all_tests"), list)
    passed_n, junit_total = _junit_passed_and_total(jsum, case_rows)
    precision_pass: float | None = None
    if junit_total > 0:
        precision_pass = passed_n / junit_total

    recall_line: float | None = None
    if report_dir:
        cov_json = Path(report_dir) / "coverage.json"
        if cov_json.is_file():
            cov_cl = change_line_coverage_from_diff_and_cov_paths(
                state.diff or "",
                cov_json,
                preferred_rels=state.changed_files if state.changed_files else None,
            )
            recall_line = cov_cl.get("recall_frac")

    use_pr_override = precision_pass is not None or recall_line is not None
    if use_pr_override:
        metrics = compute_all_metrics(
            selected_tests=selected_tests,
            all_tests=all_tests,
            failing_tests=failing_tests,
            execution_time=execution_time,
            full_time=full_time,
            precision_pass_rate=precision_pass,
            recall_change_line=recall_line,
        )
    else:
        metrics = compute_all_metrics(
            selected_tests=selected_tests,
            all_tests=all_tests,
            failing_tests=failing_tests,
            execution_time=execution_time,
            full_time=full_time,
        )

    tf_nonempty = any(str(x).strip() for x in failing_tests if x is not None)
    if use_pr_override:
        precision_meaningful = junit_total > 0
        recall_meaningful = recall_line is not None
        f1_meaningful = precision_meaningful and recall_meaningful
        pr_f1_redundancy_meaningful = f1_meaningful
    else:
        precision_meaningful = tf_nonempty
        recall_meaningful = tf_nonempty
        f1_meaningful = tf_nonempty
        pr_f1_redundancy_meaningful = tf_nonempty

    metric_flags = {
        "precision_meaningful": precision_meaningful,
        "recall_meaningful": recall_meaningful,
        "f1_meaningful": f1_meaningful,
        "pr_f1_redundancy_meaningful": pr_f1_redundancy_meaningful,
        "redundancy_meaningful": precision_meaningful if use_pr_override else tf_nonempty,
        "test_reduction_meaningful": has_explicit_all_tests,
        "time_reduction_meaningful": has_explicit_full_time,
    }

    state.evaluation = EvalSummary(
        ran=bool(ex.get("ran", False)),
        exit_code=int(code) if code is not None else None,
        stdout=stdout,
        stderr=stderr,
        coverage=cov,
        report_dir=report_dir,
        pytest_summary=dict(jsum),
        pytest_cases=pytest_cases,
        metrics=metrics,
        metric_flags=metric_flags,
    )
    _log.info(
        "EvaluationAgent: 指标 precision=%.4f recall=%.4f f1=%.4f reduction=%.4f time_reduction=%.4f redundancy=%.4f",
        metrics.get("precision", 0.0),
        metrics.get("recall", 0.0),
        metrics.get("f1", 0.0),
        metrics.get("reduction", 0.0),
        metrics.get("time_reduction", 0.0),
        metrics.get("redundancy", 0.0),
    )
    return state

