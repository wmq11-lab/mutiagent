from __future__ import annotations

import os
import re

from mutiagent.graph.state import WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_text
from mutiagent.utils.llm_output import strip_markdown_code_fence
from mutiagent.utils.syntax_guard import exec_syntax_error


def _truthy_env(name: str, default: str = "1") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _semantic_repair_known_patterns(code: str) -> tuple[str, list[str]]:
    updated = code
    applied: list[str] = []
    new_code = re.sub(
        r"if not FASTAPI_AVAILABLE:\s*\n\s*pytest\.fail\([^\n]*\)",
        "fastapi = pytest.importorskip('fastapi')",
        updated,
        flags=re.IGNORECASE,
    )
    if new_code != updated:
        applied.append("replace_global_fastapi_fail_guard")
        updated = new_code
    private_import = re.search(
        r"^\s*from\s+fastapi\.routing\s+import\s+(_[A-Za-z0-9_]+)\s*$",
        updated,
        flags=re.MULTILINE,
    )
    if private_import:
        updated = re.sub(
            r"^\s*from\s+fastapi\.routing\s+import\s+(_[A-Za-z0-9_]+)\s*$",
            "import fastapi.routing as _mutiagent_fastapi_routing",
            updated,
            flags=re.MULTILINE,
        )
        sym = private_import.group(1)
        if f"{sym} = getattr(_mutiagent_fastapi_routing" not in updated:
            inject = (
                f"\n{sym} = getattr(_mutiagent_fastapi_routing, '{sym}', None)\n"
                f"if {sym} is None:\n"
                f"    pytest.skip('fastapi.routing.{sym} 不存在，跳过私有符号相关测试')\n"
            )
            if "else:\n    IMPORT_ERROR = None\n" in updated:
                updated = updated.replace("else:\n    IMPORT_ERROR = None\n", "else:\n    IMPORT_ERROR = None\n" + inject)
            else:
                updated = inject + updated
        applied.append("replace_private_fastapi_import")
    return updated, applied


def _llm_fix_syntax(code: str, err: str, state: WorkflowState, test_path: str) -> tuple[str | None, bool]:
    """Returns (fixed_content_if_ok, repaired_ok)."""
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
        f"test_path: {test_path}\n"
        f"repo_path: {state.repo_path}\n"
        f"changed_files: {state.changed_files}\n\n"
        f"syntax_error: {err}\n\n"
        "current_test_file:\n"
        f"{code}\n"
    )
    fixed = strip_markdown_code_fence(chat_text(system, user, temperature=0.2))
    if not fixed or "def test_" not in fixed:
        return None, False
    newc = fixed.strip() + "\n"
    label = test_path if test_path else "<generated_test>"
    if exec_syntax_error(newc, filename=label) is None:
        return newc, True
    return None, False


def test_repair_agent(state: WorkflowState) -> WorkflowState:
    """
    图中 TestRepairAgent 在执行前做一次“可运行性修复”。
    MVP：对每个生成文件做语法检查；失败且有 LLM 则逐项修复。
    """
    semantic_enabled = _truthy_env("MUTIAGENT_TEST_REPAIR_SEMANTIC", "1")
    dbg: dict[str, object] = {
        "skipped": False,
        "semantic_enabled": semantic_enabled,
        "attempted": False,
        "fixed": False,
        "files_processed": 0,
        "per_file": [],
        "semantic_applied": [],
        "syntax_error": None,
    }

    if not state.generated_tests:
        dbg["skipped"] = True
        dbg["reason"] = "no_generated_tests"
        state.debug["test_repair_agent"] = dbg
        return state

    llm_ok = llm_available()
    merged_semantic: list[str] = []
    per_file: list[dict[str, object]] = []
    any_attempted = False
    any_fixed = False

    for idx, tf in enumerate(state.generated_tests):
        code = tf.content
        file_patterns: list[str] = []
        if semantic_enabled:
            repaired, file_patterns = _semantic_repair_known_patterns(code)
            if repaired != code:
                state.generated_tests[idx].content = repaired
                code = repaired
        merged_semantic.extend(file_patterns)

        label = tf.path if tf.path.strip() else f"<generated_test_{idx}>"
        err = exec_syntax_error(code, filename=label)

        row: dict[str, object] = {
            "path": tf.path,
            "semantic_applied": list(file_patterns),
            "syntax_error": err,
            "llm_attempted": False,
            "fixed": False,
        }
        if err is not None:
            if llm_ok:
                fixed_content, repair_ok = _llm_fix_syntax(code, err, state, tf.path or label)
                row["llm_attempted"] = True
                any_attempted = True
                if repair_ok and fixed_content is not None:
                    state.generated_tests[idx].content = fixed_content
                    row["fixed"] = True
                    row["syntax_error"] = exec_syntax_error(fixed_content, filename=label)
                    any_fixed = True
        per_file.append(row)

    dbg["files_processed"] = len(state.generated_tests)
    dbg["per_file"] = per_file
    dbg["semantic_applied"] = list(dict.fromkeys(merged_semantic))
    dbg["attempted"] = any_attempted
    dbg["fixed"] = any_fixed

    unresolved_err: str | None = None
    for row in per_file:
        syn = row.get("syntax_error")
        if syn is not None:
            unresolved_err = syn if isinstance(syn, str) else str(syn)
            break
    dbg["syntax_error"] = unresolved_err
    dbg["syntax_ok"] = unresolved_err is None

    state.debug["test_repair_agent"] = dbg
    return state

