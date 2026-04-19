from __future__ import annotations

from mutiagent.graph.state import WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_text
from mutiagent.utils.llm_output import strip_markdown_code_fence
from mutiagent.utils.syntax_guard import exec_syntax_error


def test_repair_agent(state: WorkflowState) -> WorkflowState:
    """
    图中 TestRepairAgent 在执行前做一次“可运行性修复”。
    MVP：只做语法检查；若失败且有LLM则修复一次。
    """
    if not state.generated_tests:
        return state

    code = state.generated_tests[0].content
    err = exec_syntax_error(code, filename="<generated_test>")
    state.debug["test_repair_agent"] = {"attempted": False, "fixed": False, "syntax_error": err}

    if err is None or not llm_available():
        return state

    system = (
        "你是资深Python测试工程师。给定一份pytest测试文件，存在语法错误。"
        "请修复语法错误并保持测试意图不变。不要借机把用例改成整批 pytest.skip 或含糊的“缺模块就跳过”。"
        "unittest.mock.patch / patch.object 的第一个参数（目标路径字符串）必须在一行内写完整："
        "开引号与闭引号、闭括号齐全，禁止在字符串未闭合时换行；过长路径可先赋给变量再 patch(变量)。"
        "Ansible：若报 module ansible has no attribute galaxy，检查 patch 目标；"
        "Display 类在 ansible.utils.display.Display；在 collection 内 mock 时 patch 该模块命名空间下的 Display 或 display，勿编造 ansible.galaxy.collection.display 子模块路径。"
        "只输出修复后的完整Python文件内容（不要markdown，不要解释）。"
    )
    user = (
        f"repo_path: {state.repo_path}\n"
        f"changed_files: {state.changed_files}\n\n"
        f"syntax_error: {err}\n\n"
        "current_test_file:\n"
        f"{code}\n"
    )
    fixed = strip_markdown_code_fence(chat_text(system, user, temperature=0.2))
    state.debug["test_repair_agent"]["attempted"] = True
    if fixed and "def test_" in fixed:
        newc = fixed.strip() + "\n"
        if exec_syntax_error(newc, filename="<generated_test>") is None:
            state.generated_tests[0].content = newc
            state.debug["test_repair_agent"]["fixed"] = True
    return state

