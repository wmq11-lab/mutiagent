import mutiagent.nodes.test_repair_agent as tra_mod
from mutiagent.graph.state import EvalSummary, GeneratedTestFile, WorkflowState
from mutiagent.nodes.feedback_agent import feedback_agent


def test_test_repair_skipped_when_disabled_by_state():
    gt = [GeneratedTestFile(path="t.py", content="def test_ok():\n    assert 1")]
    st = WorkflowState(
        repo_path="/tmp/r",
        diff="",
        run_eval=False,
        test_repair_enabled=False,
        generated_tests=gt,
    )
    out = tra_mod.test_repair_agent(st)
    dbg = out.debug.get("test_repair_agent") or {}
    assert dbg.get("skipped") is True
    assert dbg.get("reason") == "disabled_by_switch"


def test_feedback_skipped_when_disabled_by_state():
    st = WorkflowState(repo_path="/tmp/r", diff="", run_eval=True, feedback_enabled=False)
    st.evaluation = EvalSummary(exit_code=0)
    out = feedback_agent(st)
    assert out.feedback.get("enabled") is False
    assert out.feedback.get("reason") == "disabled_by_switch"
    fa = out.debug.get("feedback_agent") or {}
    assert fa.get("phase") == "disabled"
