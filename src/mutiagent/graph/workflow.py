from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable, Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from langgraph.graph import END, StateGraph

from mutiagent.graph.state import WorkflowState
from mutiagent.nodes.bug_pattern_agent import bug_pattern_agent
from mutiagent.nodes.code_change_agent import ingest_change
from mutiagent.nodes.execution_agent import execution_agent
from mutiagent.nodes.feedback_agent import feedback_agent
from mutiagent.nodes.impact_analysis_agent import analyze_impact
from mutiagent.nodes.project_probe_agent import project_probe_agent
from mutiagent.nodes.retrieval_agent import retrieval_agent
from mutiagent.nodes.evaluation_agent import evaluation_agent
from mutiagent.nodes.test_gen_agent import generate_tests
from mutiagent.nodes.test_planning_agent import plan_tests
from mutiagent.nodes.test_prioritization_agent import test_prioritization_agent
from mutiagent.nodes.test_repair_agent import test_repair_agent
from mutiagent.evaluation.experiment_run_log import merge_workflow_total_time_into_experiment_record
from mutiagent.utils.run_db import finish_workflow_run
from mutiagent.utils.run_db import start_workflow_run
from mutiagent.utils.run_db import write_workflow_step

_log = logging.getLogger("mutiagent.workflow")

# 与图中节点顺序一致（用于进度 total）
WORKFLOW_NODE_ORDER: tuple[str, ...] = (
    "CodeChangeAgent",
    "ProjectProbeAgent",
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
    "ProjectProbeAgent": "项目探测 / 环境准备",
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


def _app_repo_root() -> Path:
    # src/mutiagent/graph/workflow.py -> parents[3] = 项目根
    return Path(__file__).resolve().parents[3]


def _jsonable(obj: Any) -> Any:
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_jsonable(v) for v in obj]
    if hasattr(obj, "model_dump"):
        try:
            return _jsonable(obj.model_dump(mode="json"))
        except TypeError:
            return _jsonable(obj.model_dump())
    return repr(obj)


def build_workflow():
    g = StateGraph(WorkflowState)
    g.add_node("CodeChangeAgent", ingest_change)
    g.add_node("ProjectProbeAgent", project_probe_agent)
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
    g.add_edge("CodeChangeAgent", "ProjectProbeAgent")
    g.add_edge("ProjectProbeAgent", "ImpactAnalysisAgent")
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
    code_dbg = out.debug.get("code_change", {}) if isinstance(out.debug, dict) else {}
    impact_dbg = out.debug.get("impact", {}) if isinstance(out.debug, dict) else {}
    dwc = out.debug.get("diff_worktree_check") if isinstance(out.debug, dict) else None
    impact_disabled = bool(impact_dbg.get("disabled_by_switch"))
    degraded_gate = (
        bool(code_dbg.get("analysis_degraded", False))
        and int(impact_dbg.get("semantic_unit_catalog_count", 0) or 0) == 0
        and not impact_disabled
    )
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
        "project_profile": out.project_profile,
        "test_plan": out.structured_test_plan.model_dump(mode="json"),
        "test_plan_items": [p.model_dump() for p in out.test_plan],
        "generated_tests": out.generated_tests,
        "evaluation": out.evaluation.model_dump(mode="json") if out.evaluation is not None else None,
        "debug": out.debug,
        "diff_worktree_check": dwc,
        "quality_gates": {
            "degraded_pass_gate": degraded_gate,
            "reason": "CodeChangeAgent degraded + ImpactAnalysisAgent empty" if degraded_gate else "OK",
            "diff_worktree_mismatch": bool(
                isinstance(dwc, dict) and dwc.get("ok") is False and dwc.get("modified_paths_missing_in_worktree")
            ),
        },
    }


def _iter_workflow_step_progress(
    state: WorkflowState,
    *,
    progress_log: bool = True,
):
    """执行 LangGraph，每完成一个节点 ``yield`` 一条 progress dict；正常结束时 ``return`` 最终 ``WorkflowState``。"""
    g = _compiled_graph()
    total = len(WORKFLOW_NODE_ORDER)
    last_values: dict[str, Any] | WorkflowState | None = None
    done_updates = 0
    app_root = _app_repo_root()
    run_id = start_workflow_run(
        repo_root=app_root,
        repo_path=state.repo_path,
        diff=state.diff,
        run_eval=bool(state.run_eval),
        auto_venv=bool(state.auto_venv),
        auto_install_python=bool(state.auto_install_python),
    )
    if run_id:
        state.debug["workflow_run_id"] = run_id
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    step_dump_dir = app_root / "log" / "workflow_steps" / stamp
    step_dump_dir.mkdir(parents=True, exist_ok=True)
    state.debug["workflow_steps_stamp"] = stamp
    state.debug["workflow_steps_dir"] = str(step_dump_dir.resolve())
    state.debug["workflow_started_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    state.debug["_workflow_perf_start"] = time.perf_counter()
    _log.info("工作流步骤输出目录: %s", step_dump_dir)
    try:
        for mode, payload in g.stream(state, stream_mode=["updates", "values"]):
            if mode == "updates":
                node = next(iter(payload.keys()))
                done_updates += 1
                label = WORKFLOW_NODE_LABELS.get(node, node)
                node_out = payload.get(node)
                json_out = _jsonable(node_out)
                out_path = step_dump_dir / f"{done_updates:02d}_{node}.json"
                out_path.write_text(
                    json.dumps(json_out, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                write_workflow_step(
                    repo_root=app_root,
                    run_id=run_id,
                    step_index=done_updates,
                    node=node,
                    label=label,
                    payload=json_out,
                    file_path=str(out_path.resolve()),
                )
                if progress_log:
                    _log.info("步骤 %s/%s 完成: %s — %s", done_updates, total, node, label)
                    if isinstance(node_out, dict):
                        _log.info(
                            "步骤 %s 输出已写入: %s（top-level keys=%s）",
                            done_updates,
                            out_path,
                            sorted(node_out.keys()),
                        )
                    else:
                        _log.info("步骤 %s 输出已写入: %s", done_updates, out_path)
                    if done_updates < total:
                        next_node = WORKFLOW_NODE_ORDER[done_updates]
                        next_label = WORKFLOW_NODE_LABELS.get(next_node, next_node)
                        _log.info("步骤 %s/%s 开始: %s — %s", done_updates + 1, total, next_node, next_label)
                next_label_out = ""
                if done_updates < total:
                    nn = WORKFLOW_NODE_ORDER[done_updates]
                    next_label_out = WORKFLOW_NODE_LABELS.get(nn, nn)
                yield {
                    "type": "progress",
                    "node": node,
                    "current": done_updates,
                    "total": total,
                    "label": label,
                    "next_label": next_label_out,
                }
            elif mode == "values":
                last_values = payload
    except Exception as exc:
        finish_workflow_run(
            repo_root=app_root,
            run_id=run_id,
            status="failed",
            error_message=str(exc),
        )
        raise

    if last_values is None:
        finish_workflow_run(
            repo_root=app_root,
            run_id=run_id,
            status="failed",
            error_message="工作流未产生有效状态",
        )
        raise RuntimeError("工作流未产生有效状态")
    finish_workflow_run(
        repo_root=app_root,
        run_id=run_id,
        status="completed",
    )
    if isinstance(last_values, WorkflowState):
        merge_workflow_total_time_into_experiment_record(last_values)
        return last_values
    validated = WorkflowState.model_validate(last_values)
    merge_workflow_total_time_into_experiment_record(validated)
    return validated


def _execute_workflow(
    state: WorkflowState,
    progress_sink: Callable[[dict[str, Any]], None] | None,
    *,
    progress_log: bool = True,
) -> WorkflowState:
    """stream 执行 LangGraph，可选将进度写入 sink（dict 含 type/node/current/total/label）。"""
    gen = _iter_workflow_step_progress(state, progress_log=progress_log)
    while True:
        try:
            ev = next(gen)
        except StopIteration as ex:
            return ex.value
        if progress_sink is not None:
            progress_sink(ev)


def run_workflow(
    repo_path: str,
    diff: str,
    run_eval: bool = True,
    *,
    auto_venv: bool = True,
    auto_install_python: bool = False,
    retrieval_enabled: Optional[bool] = None,
    bug_pattern_enabled: Optional[bool] = None,
    impact_analysis_enabled: Optional[bool] = None,
    test_repair_enabled: Optional[bool] = None,
    feedback_enabled: Optional[bool] = None,
    progress_callback: Callable[[str, int, int, str], None] | None = None,
) -> dict[str, Any]:
    state = WorkflowState(
        repo_path=repo_path,
        diff=diff,
        run_eval=run_eval,
        auto_venv=auto_venv,
        auto_install_python=auto_install_python,
        retrieval_enabled=retrieval_enabled,
        bug_pattern_enabled=bug_pattern_enabled,
        impact_analysis_enabled=impact_analysis_enabled,
        test_repair_enabled=test_repair_enabled,
        feedback_enabled=feedback_enabled,
    )

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
    auto_venv: bool = True,
    auto_install_python: bool = False,
    retrieval_enabled: Optional[bool] = None,
    bug_pattern_enabled: Optional[bool] = None,
    impact_analysis_enabled: Optional[bool] = None,
    test_repair_enabled: Optional[bool] = None,
    feedback_enabled: Optional[bool] = None,
) -> Iterator[dict[str, Any]]:
    """
    供流式 API：按顺序产生 progress，最后一条为 complete；异常时为 error。
    """
    state = WorkflowState(
        repo_path=repo_path,
        diff=diff,
        run_eval=run_eval,
        auto_venv=auto_venv,
        auto_install_python=auto_install_python,
        retrieval_enabled=retrieval_enabled,
        bug_pattern_enabled=bug_pattern_enabled,
        impact_analysis_enabled=impact_analysis_enabled,
        test_repair_enabled=test_repair_enabled,
        feedback_enabled=feedback_enabled,
    )
    try:
        gen = _iter_workflow_step_progress(state, progress_log=True)
        out: WorkflowState | None = None
        while True:
            try:
                ev = next(gen)
            except StopIteration as ex:
                out = ex.value
                break
            yield ev
    except Exception as exc:
        _log.exception("工作流失败: %s", exc)
        yield {"type": "error", "message": str(exc)}
        return

    if out is None:
        _log.error("工作流迭代未返回终止状态（内部错误）")
        yield {"type": "error", "message": "工作流未返回有效状态"}
        return

    yield {"type": "complete", "result": _workflow_result_dict(out)}
