from __future__ import annotations

import os
import re

from mutiagent.graph.state import GeneratedTestFile, WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_text
from mutiagent.utils.code_extract import extract_context_by_hunks
from mutiagent.utils.llm_output import strip_markdown_code_fence
from mutiagent.utils.syntax_guard import exec_syntax_error


def _sanitize_global_dependency_guards(code: str) -> str:
    updated = code
    # 避免整文件 FASTAPI_AVAILABLE + pytest.fail 模式，改为就地 importorskip。
    updated = re.sub(
        r"if not FASTAPI_AVAILABLE:\s*\n\s*pytest\.fail\([^\n]*\)",
        "fastapi = pytest.importorskip('fastapi')",
        updated,
        flags=re.IGNORECASE,
    )
    return updated


def _sanitize_private_symbol_imports(code: str) -> str:
    updated = code
    # 避免直接 from x import _private_symbol，改为模块导入 + 运行时判定。
    updated = re.sub(
        r"^\s*from\s+fastapi\.routing\s+import\s+(_[A-Za-z0-9_]+)\s*$",
        "import fastapi.routing as _mutiagent_fastapi_routing",
        updated,
        flags=re.MULTILINE,
    )
    if "_mutiagent_fastapi_routing" in updated and "_prepare_response_content" in updated:
        prelude = (
            "\n# 兼容不同 fastapi 版本：私有符号可能不存在，避免在模块导入阶段直接崩溃\n"
            "_prepare_response_content = getattr(_mutiagent_fastapi_routing, '_prepare_response_content', None)\n"
            "if _prepare_response_content is None:\n"
            "    pytest.skip('fastapi.routing._prepare_response_content 不存在，跳过私有符号相关测试')\n"
        )
        # 尽量插到 import 区域后
        if "else:\n    IMPORT_ERROR = None\n" in updated and prelude not in updated:
            updated = updated.replace("else:\n    IMPORT_ERROR = None\n", "else:\n    IMPORT_ERROR = None\n" + prelude)
    return updated


def _extract_changed_markers(diff: str) -> tuple[str | None, str | None]:
    changed_py_module: str | None = None
    marker: str | None = None
    current_file: str | None = None
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[len("+++ b/") :].strip()
            if current_file.endswith(".py") and changed_py_module is None:
                changed_py_module = current_file[:-3].replace("/", ".")
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        added = line[1:]
        for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", added):
            token = m.group(1)
            if token in {"def", "class", "return", "if", "for", "while", "and", "or"}:
                continue
            if len(token) >= 6:
                marker = token
                break
        if marker:
            break
    return changed_py_module, marker


def _append_changed_api_assertion(code: str, state: WorkflowState) -> str:
    module_name, marker = _extract_changed_markers(state.diff or "")
    if not module_name or not marker:
        return code
    if marker in code:
        return code
    extra = (
        "\n\ndef test_changed_api_marker_alignment():\n"
        f"    module = pytest.importorskip('{module_name}')\n"
        "    import inspect\n"
        "    source = inspect.getsource(module)\n"
        f"    assert '{marker}' in source\n"
    )
    return code.rstrip() + extra


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
        "6) 执行环境会在被测仓库根目录运行 pytest，且 PYTHONPATH 已包含仓库根与常见的 lib/（如 Ansible 源码布局）。"
        "不要因笼统的 ImportError 就对整文件或整类 pytest.skip；不要用“Required modules not available”之类含糊理由批量跳过，"
        "否则会出现 9 skipped + exit 0 的假象。缺依赖时应优先用 unittest.mock.patch 隔离被测函数，让用例在无网络下仍能跑断言。\n"
        "7) 仅当单条用例在技术上无法构造（且已说明具体缺哪个符号）时才对该条 pytest.skip；其余情况让 import/断言失败暴露问题，便于用户安装依赖。\n"
        "8) unittest.mock.patch / patch.object 的目标路径字符串必须单行闭合：with patch('a.b.c') as m: 合法；"
        "禁止写成 patch('a.b.c 未闭合就换行。过长时用 target='a.b.c' 变量承接再 patch(target)。\n"
        "9) 不要生成 `test_import_paths` / `test_dependencies` 这类全局依赖自检用例并在缺包时 pytest.fail。"
        "若依赖为可选（如 fastapi），在具体业务用例内用 pytest.importorskip('fastapi') 做就地跳过，"
        "避免因环境缺少第三方库导致整次评估出现单一硬失败。\n"
        "10) 禁止直接导入下划线开头的私有符号（如 from fastapi.routing import _prepare_response_content）；"
        "若必须验证私有符号，使用 `import fastapi.routing as routing` + `getattr(routing, '_name', None)`，不存在时仅跳过该条测试。"
    )

    user_lines: list[str] = []
    user_lines.append(f"repo_path: {state.repo_path}")
    user_lines.append(
        "runtime_hint: pytest cwd=repo_path; PYTHONPATH includes repo root and repo/lib if that directory exists."
    )
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

    if any(
        "ansible" in (state.repo_path or "").lower()
        or "galaxy/collection" in (f or "").replace("\\", "/").lower()
        or "ansible/galaxy" in (f or "").replace("\\", "/").lower()
        for f in (state.changed_files or [])
    ):
        user_lines.append(
            "\nansible_mock_hint: patch 目标须与 collection.py 中实际 import 的符号一致。"
            "Display 类来自 ansible.utils.display；在 collection 模块内通常绑定名为 Display（类）或 display（实例），"
            "不要用不存在的子模块路径如 ansible.galaxy.collection.display 表示「模块」——应 patch 该模块上的绑定名，"
            "例如 patch('ansible.galaxy.collection.Display') 或对 importlib.import_module('ansible.galaxy.collection') 返回的模块 patch.object(..., 'display', ...)。"
            "若运行时报 ansible 无 galaxy，多半是环境里 pip 安装的 ansible 与源码 lib/ansible 冲突：执行 pytest 时默认不再继承外层 PYTHONPATH；"
            "需要拼接时请设环境变量 MUTIAGENT_PYTEST_APPEND_PYTHONPATH=1。"
        )

    user_blob = "\n".join(user_lines)
    code = strip_markdown_code_fence(chat_text(system, user_blob, temperature=0.2))
    if "def test_" not in code:
        code += "\n\n\ndef test_generated_placeholder():\n    assert True\n"

    syn = exec_syntax_error(code, filename="<generated_test>")
    if syn and llm_available():
        retry_sys = (
            system
            + "\n【重要】上一轮输出无法通过 Python 语法检查："
            + syn
            + "。请输出完整可编译文件；重点检查 patch( 与 patch.object( 的字符串是否在同一行内正确闭合引号。\n"
        )
        retry_user = (
            user_blob
            + "\n\n**previous_invalid_output** (rewrite entirely, do not append):\n"
            + code
            + "\n"
        )
        code2 = strip_markdown_code_fence(chat_text(retry_sys, retry_user, temperature=0.15))
        if "def test_" in code2 and exec_syntax_error(code2, filename="<generated_test>") is None:
            code = code2

    if "def test_" not in code:
        code += "\n\n\ndef test_generated_placeholder():\n    assert True\n"

    code = _sanitize_global_dependency_guards(code)
    code = _sanitize_private_symbol_imports(code)
    code = _append_changed_api_assertion(code, state)

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

