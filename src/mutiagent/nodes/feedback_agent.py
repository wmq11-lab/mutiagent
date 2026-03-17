from __future__ import annotations

from mutiagent.graph.state import WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_text


def feedback_agent(state: WorkflowState) -> WorkflowState:
    """
    图中 FeedbackAgent：根据执行/评估结果给出下一轮测试规划建议（MVP：返回建议，不做自动回路改写plan）。
    """
    if not state.run_eval or state.evaluation is None:
        state.feedback = {"enabled": False}
        return state

    if state.evaluation.exit_code == 0:
        state.feedback = {"enabled": True, "status": "pass", "suggestions": ["可扩大受影响范围或增加边界/异常用例以提升覆盖率"]}
        return state

    base = {
        "enabled": True,
        "status": "fail",
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
    user = (
        f"changed_files: {state.changed_files}\n"
        f"top_impacted: {[i.id for i in state.impacted_ranked[:8]]}\n"
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

