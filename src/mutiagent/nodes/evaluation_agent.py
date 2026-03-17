from __future__ import annotations

import re

from mutiagent.graph.state import EvalSummary, WorkflowState


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

    state.evaluation = EvalSummary(
        ran=bool(ex.get("ran", False)),
        exit_code=int(code) if code is not None else None,
        stdout=stdout,
        stderr=stderr,
        coverage=cov,
    )
    return state

