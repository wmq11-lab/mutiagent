from __future__ import annotations

import os

from mutiagent.graph.state import GeneratedTestFile, WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_text
from mutiagent.utils.code_extract import extract_context_by_hunks


def _fallback_tests(state: WorkflowState) -> list[GeneratedTestFile]:
    content = (
        "import importlib\n\n\n"
        "def test_project_import_smoke():\n"
        "    # TODO: 将下面的模块名替换为你的项目主入口模块\n"
        "    module_name = None\n"
        "    assert module_name is not None, '请填写可导入模块名'\n"
        "    importlib.import_module(module_name)\n"
    )
    return [
        GeneratedTestFile(
            path="tests/test_generated_smoke.py",
            content=content,
            assumptions=["未配置OPENAI_API_KEY，已生成模板测试；请补充可导入模块名与断言。"],
        )
    ]


def _llm_generate(state: WorkflowState) -> list[GeneratedTestFile]:
    snippets = extract_context_by_hunks(state.repo_path, state.diff_hunks)
    snippet_items = list(snippets.items())[:4]

    system = (
        "你是资深Python测试工程师。你将基于代码变更上下文与测试计划，生成可运行的pytest测试文件。\n"
        "要求：\n"
        "1) 只输出一个文件内容（不要markdown），以纯Python代码形式输出。\n"
        "2) 使用pytest风格（test_前缀函数/类）。\n"
        "3) 尽量避免外部依赖：对网络/数据库/文件系统调用优先mock/monkeypatch。\n"
        "4) 断言要有意义：至少验证关键返回值/异常/分支。\n"
        "5) 若无法确定导入路径，给出最保守的import方式，并在代码里用断言提示用户需要调整的模块路径。\n"
    )

    user_lines: list[str] = []
    user_lines.append(f"repo_path: {state.repo_path}")
    user_lines.append(f"changed_files: {state.changed_files}")
    user_lines.append("test_plan:")
    plan = state.prioritized_plan or state.test_plan
    for p in plan[:12]:
        user_lines.append(f"- target={p.target} priority={p.priority} intent={p.intent}")
    if state.retrieved_context:
        user_lines.append("\nretrieved_context:")
        user_lines.append(str(state.retrieved_context)[:2000])
    user_lines.append("\ncode_context_snippets:")
    for rel, txt in snippet_items:
        user_lines.append(f"\n### file: {rel}\n{txt}\n")

    code = chat_text(system, "\n".join(user_lines), temperature=0.2)
    if "def test_" not in code:
        code += "\n\n\ndef test_generated_placeholder():\n    assert True\n"

    return [
        GeneratedTestFile(
            path="tests/test_generated_regression.py",
            content=code.strip() + "\n",
            assumptions=[
                "生成的测试基于diff上下文与轻量依赖分析；如项目导入路径特殊，可能需要调整import。",
            ],
        )
    ]


def generate_tests(state: WorkflowState) -> WorkflowState:
    if llm_available():
        files = _llm_generate(state)
        state.debug["test_gen"] = {"used_llm": True, "model": os.getenv("MUTIAGENT_OPENAI_MODEL", "gpt-4.1-mini")}
    else:
        files = _fallback_tests(state)
        state.debug["test_gen"] = {"used_llm": False}

    state.generated_tests = files
    return state

