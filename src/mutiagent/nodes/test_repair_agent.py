from __future__ import annotations

from mutiagent.graph.state import WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_text


def _syntax_check(py_code: str) -> str | None:
    try:
        compile(py_code, "<generated_test>", "exec")
        return None
    except SyntaxError as e:
        return f"SyntaxError: {e}"


def test_repair_agent(state: WorkflowState) -> WorkflowState:
    """
    图中 TestRepairAgent 在执行前做一次“可运行性修复”。
    MVP：只做语法检查；若失败且有LLM则修复一次。
    """
    if not state.generated_tests:
        return state

    code = state.generated_tests[0].content
    err = _syntax_check(code)
    state.debug["test_repair_agent"] = {"attempted": False, "fixed": False, "syntax_error": err}

    if err is None or not llm_available():
        return state

    system = (
        "你是资深Python测试工程师。给定一份pytest测试文件，存在语法错误。"
        "请修复语法错误并保持测试意图不变。只输出修复后的完整Python文件内容（不要markdown，不要解释）。"
    )
    user = (
        f"repo_path: {state.repo_path}\n"
        f"changed_files: {state.changed_files}\n\n"
        f"syntax_error: {err}\n\n"
        "current_test_file:\n"
        f"{code}\n"
    )
    fixed = chat_text(system, user, temperature=0.2)
    state.debug["test_repair_agent"]["attempted"] = True
    if fixed and "def test_" in fixed:
        state.generated_tests[0].content = fixed.strip() + "\n"
        state.debug["test_repair_agent"]["fixed"] = True
    return state

