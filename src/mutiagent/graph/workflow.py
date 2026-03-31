from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph

from mutiagent.graph.state import WorkflowState
from mutiagent.nodes.bug_pattern_agent import bug_pattern_agent
from mutiagent.nodes.code_change_agent import ingest_change
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
    # 加入agent节点到图中
    g.add_node("CodeChangeAgent", ingest_change)
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

    g.set_entry_point("CodeChangeAgent")#入口节点
    #添加边
    # 说明：LangGraph 默认 state channel 为 last_value，并行分支会触发并发写冲突；
    # 这里先保持顺序执行；CodeChangeAgent 会构建 change_graph 供 Impact / 测试优先级使用。
    g.add_edge("CodeChangeAgent", "ImpactAnalysisAgent")
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
    #返回可执行应用
    return g.compile()


_APP = None


def run_workflow(repo_path: str, diff: str, run_eval: bool = False) -> dict[str, Any]:
    global _APP
    #初始化graph
    if _APP is None:
        #第一次创建，后面复用
        _APP = build_workflow()

    #创建状态对象
    state = WorkflowState(repo_path=repo_path, diff=diff, run_eval=run_eval)
    #执行工作流
    out_raw = _APP.invoke(state)
    out = out_raw if isinstance(out_raw, WorkflowState) else WorkflowState(**out_raw)

    return {
        "changed_files": out.changed_files,
        "change_analysis": out.change_analysis,
        "change_graph": out.change_graph.model_dump() if out.change_graph else None,
        "impact_graph": [g.model_dump(mode="json", by_alias=True) for g in out.impact_graph],
        "semantic_units_catalog": [
            u.model_dump(mode="json", by_alias=True) for u in out.semantic_units_catalog
        ],
        "impact_test_plan": [p.model_dump(mode="json") for p in out.impact_test_plan],
        "top_risks": [r.model_dump(mode="json") for r in out.top_risks],
        "impacted": out.impacted_ranked,
        "test_plan": out.test_plan,
        "generated_tests": out.generated_tests,
        "evaluation": out.evaluation,
        "debug": out.debug,
    }
