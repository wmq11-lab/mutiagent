from mutiagent.graph.state import WorkflowState
from mutiagent.nodes.feedback_agent import _should_mark_degraded_pass
from mutiagent.nodes.impact_analysis_agent import analyze_impact


def test_analyze_impact_disabled_by_state_clears_outputs():
    state = WorkflowState(repo_path="/tmp/r", diff="", impact_analysis_enabled=False)
    state.changed_files = ["src/foo.py"]
    state.debug["code_change"] = {"analysis_degraded": False}
    out = analyze_impact(state)
    assert out.impact_graph == []
    assert out.semantic_units_catalog == []
    assert out.impacted_ranked == []
    assert out.debug.get("impact", {}).get("disabled_by_switch") is True
    assert out.debug["impact"]["mode"] == "disabled"


def test_degraded_pass_not_when_impact_disabled_by_switch():
    st = WorkflowState(repo_path="/tmp/r", diff="")
    st.debug["code_change"] = {"analysis_degraded": True}
    st.debug["impact"] = {"disabled_by_switch": True, "semantic_unit_catalog_count": 0}
    assert _should_mark_degraded_pass(st) is False
