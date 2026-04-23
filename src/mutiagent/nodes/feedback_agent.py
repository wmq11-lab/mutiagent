from __future__ import annotations

from mutiagent.graph.state import WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_text


def _quality_metrics(state: WorkflowState) -> dict[str, float]:
    code_dbg = state.debug.get("code_change", {}) if isinstance(state.debug, dict) else {}
    files_analyzed = int(code_dbg.get("files_analyzed", 0) or 0)
    total_changes = int(code_dbg.get("changes", 0) or 0)
    nonempty = 1 if total_changes > 0 else 0
    analysis_nonempty_rate = float(nonempty / files_analyzed) if files_analyzed > 0 else 0.0

    planning_dbg = state.debug.get("test_planning_agent", {}) if isinstance(state.debug, dict) else {}
    fallback_rate = 1.0 if bool(planning_dbg.get("fallback", False)) else 0.0

    first_run_code = None
    if isinstance(state.execution, dict):
        first_run_code = state.execution.get("first_run_exit_code")
    first_run_pass_rate = 1.0 if first_run_code == 0 else 0.0

    bootstrap_phase = ""
    adb = state.debug.get("auto_dep_bootstrap", {}) if isinstance(state.debug, dict) else {}
    if isinstance(adb, dict):
        bootstrap_phase = str(adb.get("phase", ""))
    bootstrap_before_llm_rate = 1.0 if bootstrap_phase.startswith("第1次运行后") else 0.0

    return {
        "analysis_nonempty_rate": round(analysis_nonempty_rate, 4),
        "fallback_rate": round(fallback_rate, 4),
        "first_run_pass_rate": round(first_run_pass_rate, 4),
        "bootstrap_before_llm_rate": round(bootstrap_before_llm_rate, 4),
    }


def _should_mark_degraded_pass(state: WorkflowState) -> bool:
    code_dbg = state.debug.get("code_change", {}) if isinstance(state.debug, dict) else {}
    impact_dbg = state.debug.get("impact", {}) if isinstance(state.debug, dict) else {}
    analysis_degraded = bool(code_dbg.get("analysis_degraded", False))
    impact_empty = int(impact_dbg.get("semantic_unit_catalog_count", 0) or 0) == 0
    return analysis_degraded and impact_empty


def feedback_agent(state: WorkflowState) -> WorkflowState:
    """
    图中 FeedbackAgent：根据执行/评估结果给出下一轮测试规划建议（MVP：返回建议，不做自动回路改写plan）。
    """
    if not state.run_eval or state.evaluation is None:
        state.feedback = {"enabled": False}
        return state

    if state.evaluation.exit_code == 0:
        status = "degraded_pass" if _should_mark_degraded_pass(state) else "pass"
        state.feedback = {
            "enabled": True,
            "status": status,
            "suggestions": ["可扩大受影响范围或增加边界/异常用例以提升覆盖率"],
            "quality_metrics": _quality_metrics(state),
        }
        return state

    base = {
        "enabled": True,
        "status": "fail",
        "quality_metrics": _quality_metrics(state),
        "suggestions": [
            "检查生成测试的import路径是否与项目包结构一致",
            "对外部依赖（网络/DB/文件系统）使用mock/monkeypatch",
            "若失败是断言不稳定，优先断言稳定接口/返回值/异常类型",
        ],
    }

    if not llm_available():
        state.feedback = base
        state.debug["feedback_agent"] = {"used_llm": False, "suggestion_count": len(base["suggestions"])}
        return state

    system = (
        "你是资深Python测试负责人。给定pytest失败输出与当前测试计划，请输出3-6条下一步改进建议。"
        "只输出纯文本要点列表（每行一条），不要markdown。"
    )
    top_sig: list[str] = []
    cmap = {u.semantic_unit_id: u for u in state.semantic_units_catalog}
    if state.impact_graph:
        flat: list[tuple[float, str]] = []
        for igf in state.impact_graph:
            for sym in igf.symbols:
                for uid in sym.semantic_unit_ids:
                    u = cmap.get(uid)
                    if not u:
                        continue
                    flat.append(
                        (u.priority_score, f"{igf.file}::{sym.name}::{u.semantic_unit_id}")
                    )
        flat.sort(key=lambda x: -x[0])
        top_sig = [x[1] for x in flat[:8]]
    else:
        top_sig = [i.id for i in state.impacted_ranked[:8]]

    user = (
        f"changed_files: {state.changed_files}\n"
        f"top_impacted: {top_sig}\n"
        f"test_plan: {[p.model_dump() for p in (state.prioritized_plan or state.test_plan)[:10]]}\n\n"
        f"pytest_stdout:\n{state.evaluation.stdout}\n\npytest_stderr:\n{state.evaluation.stderr}\n"
    )
    text = chat_text(system, user, temperature=0.2)
    suggestions = [ln.strip("- ").strip() for ln in text.splitlines() if ln.strip()]
    if suggestions:
        base["suggestions"] = suggestions[:6]
    state.feedback = base
    state.debug["feedback_agent"] = {"used_llm": True, "suggestion_count": len(base["suggestions"])}
    return state

