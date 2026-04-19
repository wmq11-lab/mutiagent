from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
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

_log = logging.getLogger("mutiagent.workflow")

# 与图中节点顺序一致（用于进度 total）
WORKFLOW_NODE_ORDER: tuple[str, ...] = (
    "CodeChangeAgent",
    "ImpactAnalysisAgent",
    "BugPatternAgent",
    "TestPlanningAgent",
    "TestPrioritizationAgent",
    "RetrievalAgent",
    "TestGenAgent",
    "TestRepairAgent",
    "ExecutionAgent",
    "EvaluationAgent",
    "FeedbackAgent",
)

WORKFLOW_NODE_LABELS: dict[str, str] = {
    "CodeChangeAgent": "代码变更解析",
    "ImpactAnalysisAgent": "影响分析",
    "BugPatternAgent": "缺陷模式",
    "TestPlanningAgent": "测试规划",
    "TestPrioritizationAgent": "用例优先级",
    "RetrievalAgent": "上下文检索",
    "TestGenAgent": "生成测试代码",
    "TestRepairAgent": "测试修复",
    "ExecutionAgent": "执行 pytest",
    "EvaluationAgent": "结果评估",
    "FeedbackAgent": "反馈汇总",
}


def build_workflow():
    g = StateGraph(WorkflowState)
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

    g.set_entry_point("CodeChangeAgent")
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
    return g.compile()


_APP = None


def _compiled_graph():
    global _APP
    if _APP is None:
        _APP = build_workflow()
    return _APP


def _workflow_result_dict(out: WorkflowState) -> dict[str, Any]:
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
        "test_plan": out.structured_test_plan.model_dump(mode="json"),
        "test_plan_items": [p.model_dump() for p in out.test_plan],
        "generated_tests": out.generated_tests,
        "evaluation": out.evaluation,
        "debug": out.debug,
    }


def _execute_workflow(
    state: WorkflowState,
    progress_sink: Callable[[dict[str, Any]], None] | None,
    *,
    progress_log: bool = True,
) -> WorkflowState:
    """stream 执行 LangGraph，可选将进度写入 sink（dict 含 type/node/current/total/label）。"""
    g = _compiled_graph()
    total = len(WORKFLOW_NODE_ORDER)
    last_values: dict[str, Any] | WorkflowState | None = None
    done_updates = 0

    for mode, payload in g.stream(state, stream_mode=["updates", "values"]):
        if mode == "updates":
            node = next(iter(payload.keys()))
            done_updates += 1
            label = WORKFLOW_NODE_LABELS.get(node, node)
            if progress_log:
                _log.info("步骤 %s/%s 完成: %s — %s", done_updates, total, node, label)
            if progress_sink is not None:
                progress_sink(
                    {
                        "type": "progress",
                        "node": node,
                        "current": done_updates,
                        "total": total,
                        "label": label,
                    }
                )
        elif mode == "values":
            last_values = payload

    if last_values is None:
        raise RuntimeError("工作流未产生有效状态")
    if isinstance(last_values, WorkflowState):
        return last_values
    return WorkflowState.model_validate(last_values)


def run_workflow(
    repo_path: str,
    diff: str,
    run_eval: bool = True,
    *,
    auto_venv: bool = False,
    progress_callback: Callable[[str, int, int, str], None] | None = None,
) -> dict[str, Any]:
    state = WorkflowState(repo_path=repo_path, diff=diff, run_eval=run_eval, auto_venv=auto_venv)

    def _sink(ev: dict[str, Any]) -> None:
        if progress_callback is not None:
            progress_callback(ev["node"], ev["current"], ev["total"], ev["label"])

    out = _execute_workflow(state, _sink if progress_callback else None)
    return _workflow_result_dict(out)


def iter_workflow_events(
    repo_path: str,
    diff: str,
    run_eval: bool = True,
    *,
    auto_venv: bool = False,
) -> Iterator[dict[str, Any]]:
    """
    供流式 API：按顺序产生 progress，最后一条为 complete；异常时为 error。
    """
    state = WorkflowState(repo_path=repo_path, diff=diff, run_eval=run_eval, auto_venv=auto_venv)
    buf: list[dict[str, Any]] = []

    try:
        out = _execute_workflow(state, buf.append)
    except Exception as exc:
        _log.exception("工作流失败: %s", exc)
        yield {"type": "error", "message": str(exc)}
        return

    for ev in buf:
        yield ev
    yield {"type": "complete", "result": _workflow_result_dict(out)}
