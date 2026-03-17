from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph

from mutiagent.graph.state import WorkflowState
from mutiagent.nodes.bug_pattern_agent import bug_pattern_agent
from mutiagent.nodes.code_change_agent import ingest_change
from mutiagent.nodes.code_change_graph_agent import code_change_graph_agent
from mutiagent.nodes.code_graph_builder import build_code_graph
from mutiagent.nodes.execution_agent import execution_agent
from mutiagent.nodes.feedback_agent import feedback_agent
from mutiagent.nodes.impact_analysis_agent import analyze_impact
from mutiagent.nodes.retrieval_agent import retrieval_agent
from mutiagent.nodes.evaluation_agent import evaluation_agent
from mutiagent.nodes.test_gen_agent import generate_tests
from mutiagent.nodes.test_planning_agent import plan_tests
from mutiagent.nodes.test_prioritization_agent import test_prioritization_agent
from mutiagent.nodes.test_repair_agent import test_repair_agent


def build_workflow():
    g = StateGraph(WorkflowState)
    # align with diagram node naming
    g.add_node("CodeChangeAgent", ingest_change)
    g.add_node("CodeGraphBuilder", build_code_graph)
    g.add_node("CodeChangeGraphAgent", code_change_graph_agent)
    g.add_node("ImpactAnalysisAgent", analyze_impact)
    g.add_node("BugPatternAgent", bug_pattern_agent)
    g.add_node("TestPlanningAgent", plan_tests)
    g.add_node("TestPrioritizationAgent", test_prioritization_agent)
    g.add_node("RetrievalAgent", retrieval_agent)
    g.add_node("TestGenAgent", generate_tests)
    g.add_node("TestRepairAgent", test_repair_agent)
    g.add_node("ExecutionAgent", execution_agent)
    g.add_node("EvaluationAgent", evaluation_agent)
    g.add_node("FeedbackAgent", feedback_agent)

    g.set_entry_point("CodeChangeAgent")
    g.add_edge("CodeChangeAgent", "CodeGraphBuilder")
    g.add_edge("CodeGraphBuilder", "CodeChangeGraphAgent")
    g.add_edge("CodeChangeGraphAgent", "ImpactAnalysisAgent")
    g.add_edge("ImpactAnalysisAgent", "BugPatternAgent")
    g.add_edge("BugPatternAgent", "TestPlanningAgent")
    g.add_edge("TestPlanningAgent", "TestPrioritizationAgent")
    g.add_edge("TestPrioritizationAgent", "RetrievalAgent")
    g.add_edge("RetrievalAgent", "TestGenAgent")
    g.add_edge("TestGenAgent", "TestRepairAgent")
    g.add_edge("TestRepairAgent", "ExecutionAgent")
    g.add_edge("ExecutionAgent", "EvaluationAgent")
    g.add_edge("EvaluationAgent", "FeedbackAgent")
    g.add_edge("FeedbackAgent", END)
    return g.compile()


_APP = None


def run_workflow(repo_path: str, diff: str, run_eval: bool = False) -> dict[str, Any]:
    global _APP
    if _APP is None:
        _APP = build_workflow()

    state = WorkflowState(repo_path=repo_path, diff=diff, run_eval=run_eval)
    out_raw = _APP.invoke(state)
    out = out_raw if isinstance(out_raw, WorkflowState) else WorkflowState(**out_raw)

    return {
        "changed_files": out.changed_files,
        "impacted": out.impacted_ranked,
        "test_plan": out.test_plan,
        "generated_tests": out.generated_tests,
        "evaluation": out.evaluation,
        "debug": out.debug,
    }
