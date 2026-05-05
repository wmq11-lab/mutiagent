"""execution_agent 评测用例子集（precision 友好）行为。"""

from __future__ import annotations

from mutiagent.graph.state import ChangeRecord, FileChangeSummary, TestPlanItem, WorkflowState
from mutiagent.nodes.execution_agent import _scoped_selected_tests_for_eval


def test_scoped_selected_keeps_failures_and_matching_passes() -> None:
    st = WorkflowState(repo_path="/tmp/r", diff="", run_eval=True)
    st.prioritized_plan = [TestPlanItem(target="m:parse_boolean_env_var", intent="u", priority="high")]
    st.changed_files = ["typer/utils.py"]
    st.change_analysis = [
        FileChangeSummary(
            file="typer/utils.py",
            summary="",
            risk="low",
            intent="FEATURE",
            tags=[],
            entities=[],
            changes=[
                ChangeRecord(entity="parse_boolean_env_var", type="function", change_type="ADD"),
            ],
        )
    ]
    rows = [
        {"classname": "tests.t.TestParseBooleanEnvVar", "name": "test_ok", "status": "passed"},
        {"classname": "tests.unrelated", "name": "test_x", "status": "passed"},
        {"classname": "tests.t.TestParseBooleanEnvVar", "name": "test_bad", "status": "failed"},
    ]
    sel = _scoped_selected_tests_for_eval(st, rows)
    assert sel is not None
    assert len(sel) == 2
    assert "tests.t.TestParseBooleanEnvVar::test_bad" in sel
    assert "tests.t.TestParseBooleanEnvVar::test_ok" in sel
    assert "tests.unrelated::test_x" not in sel
