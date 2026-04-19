from __future__ import annotations

import re

from mutiagent.graph.state import EvalSummary, PytestCaseResult, WorkflowState


def _extract_coverage(stdout: str) -> float | None:
    m = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", stdout)
    if not m:
        return None
    try:
        return float(m.group(1)) / 100.0
    except Exception:
        return None


def evaluation_agent(state: WorkflowState) -> WorkflowState:
    if not state.run_eval:
        state.evaluation = EvalSummary(ran=False)
        return state

    ex = state.execution or {}
    code = ex.get("exit_code")
    stdout = ex.get("stdout", "") or ""
    stderr = ex.get("stderr", "") or ""
    cov = _extract_coverage(stdout)

    report_dir = ex.get("report_dir")
    if report_dir is not None:
        report_dir = str(report_dir)

    jsum = ex.get("junit_summary") if isinstance(ex.get("junit_summary"), dict) else {}
    jraw = ex.get("junit_cases")
    pytest_cases: list[PytestCaseResult] = []
    if isinstance(jraw, list):
        for item in jraw:
            if isinstance(item, dict):
                pytest_cases.append(PytestCaseResult.model_validate(item))

    state.evaluation = EvalSummary(
        ran=bool(ex.get("ran", False)),
        exit_code=int(code) if code is not None else None,
        stdout=stdout,
        stderr=stderr,
        coverage=cov,
        report_dir=report_dir,
        pytest_summary=dict(jsum),
        pytest_cases=pytest_cases,
    )
    return state

