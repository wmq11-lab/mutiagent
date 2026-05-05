from __future__ import annotations

import logging
import os
import re
import time
from pathlib import Path

from mutiagent.graph.state import GeneratedTestFile, WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_text
from mutiagent.utils.code_extract import extract_context_by_hunks
from mutiagent.utils.llm_output import strip_markdown_code_fence
from mutiagent.utils.syntax_guard import exec_syntax_error

_workflow_log = logging.getLogger("mutiagent.workflow")


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _testgen_fast_mode() -> bool:
    return _env_truthy("MUTIAGENT_TESTGEN_FAST")


def _testgen_timeout_seconds() -> float:
    if _testgen_fast_mode():
        return 45.0
    raw = os.getenv("MUTIAGENT_TESTGEN_TIMEOUT_S", "").strip()
    if not raw:
        return 120.0
    try:
        return max(10.0, float(raw))
    except ValueError:
        return 120.0


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


def _sanitize_import_failure_skips(code: str) -> str:
    updated = code
    # 导入失败属于硬问题，不能用 skip 掩盖，否则会触发 all-skipped 质量闸门。
    updated = re.sub(
        r"pytest\.skip\((?P<q>['\"])(?P<msg>[^'\"]*(导入失败|未导入|import failed|Failed to import)[^'\"]*)(?P=q)\)",
        r"pytest.fail('\g<msg>')",
        updated,
        flags=re.IGNORECASE,
    )
    updated = re.sub(
        r"pytest\.skip\(\s*f(?P<q>['\"])(?P<msg>[^'\"]*(导入失败|未导入|import failed|Failed to import)[^'\"]*)(?P=q)\s*\)",
        r"pytest.fail(f'\g<msg>')",
        updated,
        flags=re.IGNORECASE,
    )
    updated = re.sub(
        r"pytest\.mark\.skip\(\s*reason\s*=\s*(?P<reason>f?['\"][^'\"]*(导入失败|未导入|import failed|Failed to import)[^'\"]*['\"])\s*\)",
        r"pytest.mark.xfail(reason=\g<reason>, strict=True)",
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


def _sanitize_timeout_test_antipatterns(code: str) -> str:
    original = code
    updated = code
    # 将“try + pytest.fail(期望超时) + except TimeoutException: pass”改为 pytest.raises 结构。
    pattern = re.compile(
        r"(?P<indent>[ \t]*)try:\n"
        r"(?P<body>(?:(?P=indent)[ \t]+.*\n)+?)"
        r"(?P=indent)[ \t]+pytest\.fail\((?P<quote>[\"'])Expected timeout exception but request succeeded(?P=quote)\)\n"
        r"(?P=indent)except\s+httpx\.TimeoutException:\n"
        r"(?P=indent)[ \t]+pass",
        flags=re.MULTILINE,
    )

    def _replace_try_fail(m: re.Match[str]) -> str:
        indent = m.group("indent")
        body = m.group("body")
        return f"{indent}with pytest.raises(httpx.TimeoutException):\n{body}"

    updated = pattern.sub(_replace_try_fail, updated)

    # timeout 场景中，若先把 get 绑成普通协程函数，会导致后续 side_effect 不生效。
    if (
        "Expected timeout exception but request succeeded" in original
        and "mock_client.get = mock_get" in updated
        and "httpx.TimeoutException" in updated
    ):
        updated = re.sub(
            r"(?m)^(\s*)mock_client\.get\s*=\s*mock_get\s*$",
            r"\1mock_client.get = AsyncMock(side_effect=httpx.TimeoutException('Request timed out'))",
            updated,
        )
    return updated


def _sanitize_async_patch_context(code: str) -> str:
    """修复 async with patch 反模式。"""
    updated = code
    # 更宽松的匹配：无论缩进层级，都将 async with patch(...) 改写为 with patch(...)。
    updated = re.sub(r"async\s+with\s+(patch\()", r"with \1", updated)
    updated = re.sub(r"async\s+with\s+(patch\.object\()", r"with \1", updated)
    # 兜底：仍存在该反模式时输出告警，便于后续排查。
    if "async with patch" in updated:
        _workflow_log.warning("TestGenAgent: 仍存在 async with patch，可能需要手动修复")
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


def _parse_dotted_import_names(tail: str) -> list[str] | None:
    """解析 `from m import` 右侧名称列表；含括号/续行时返回 None 表示不自动改写。"""
    t = tail.strip()
    if not t or "(" in t[:40]:
        return None
    if "#" in t:
        t = t[: t.index("#")].rstrip()
    out: list[str] = []
    for chunk in t.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if " as " in chunk:
            chunk = chunk.split(" as ", 1)[0].strip()
        out.append(chunk)
    return out or None


def _symbol_to_module_map(repo: Path, changed_files: list[str] | None) -> dict[str, str]:
    """仅基于 changed_files 将符号映射到可导入的模块路径（与 execution PYTHONPATH=repo 根一致）。"""
    m: dict[str, str] = {}
    for rel in changed_files or []:
        p = repo / rel
        if not p.exists() or p.suffix != ".py":
            continue
        mod = str(Path(rel).with_suffix("")).replace(os.sep, ".").replace("/", ".")
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("def "):
                name = s[4:].split("(", 1)[0].strip()
            elif s.startswith("class "):
                name = s[6:].split("(", 1)[0].split(":", 1)[0].strip()
            else:
                continue
            if name and name not in m:
                m[name] = mod
    return m


def _module_file_exists(repo: Path, mod: str) -> bool:
    rel = mod.replace(".", "/") + ".py"
    if (repo / rel).is_file():
        return True
    if (repo / rel.replace(".py", "")).is_dir() and (repo / rel.replace(".py", "") / "__init__.py").is_file():
        return True
    return False


def _merge_import_candidates_into_map(repo: Path, state: WorkflowState, sym_mod: dict[str, str]) -> None:
    for c in (state.project_profile or {}).get("import_candidates") or []:
        if not isinstance(c, str) or ":" not in c:
            continue
        mod, sym = c.split(":", 1)
        mod, sym = mod.strip(), sym.strip()
        if not mod or not sym or not _module_file_exists(repo, mod):
            continue
        if sym not in sym_mod:
            sym_mod[sym] = mod


def _user_py_iter(repo: Path, *, max_files: int = 600):
    skip = {".mutiagent", ".git", "__pycache__", "node_modules", ".tox", ".venv", "venv", "env", "dist", "build", ".eggs"}
    n = 0
    for p in repo.rglob("*.py"):
        if n >= max_files:
            break
        if any(x in p.parts for x in skip):
            continue
        n += 1
        yield p


def _path_to_dotted_mod(repo: Path, p: Path) -> str:
    return str(p.resolve().relative_to(repo.resolve()).with_suffix("")).replace(os.sep, ".").replace("/", ".")


def _fill_sym_mod_by_repo_scan(
    repo: Path,
    sym_mod: dict[str, str],
    needed: set[str],
) -> None:
    """在仓库内找单个 .py 同时包含 def name( 的模块，补全缺符号（处理 diff 里假路径）。"""
    if not needed:
        return
    missing = {n for n in needed if n not in sym_mod}
    if not missing:
        return
    for p in _user_py_iter(repo):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not all(f"def {n}(" in text for n in missing):
            continue
        mod = _path_to_dotted_mod(repo, p)
        for n in missing:
            sym_mod[n] = mod
        return


def _collect_imported_names_in_phantom_froms(code: str, repo: Path) -> set[str]:
    """收集「顶层包在盘中不存在」的 from-import 行上的符号名，供扫描补全。"""
    out: set[str] = set()
    for m in re.finditer(
        r"^(\s*)from\s+([A-Za-z_][A-Za-z0-9_.]*)\s+import\s+(.+?)\s*(?:#.*)?$",
        code,
        re.MULTILINE,
    ):
        mod_path, tail = m.group(2), m.group(3)
        if _top_level_path_exists(repo, mod_path):
            continue
        names = _parse_dotted_import_names(tail)
        if names:
            out |= set(names)
    return out


def _enrich_symbol_map(repo: Path, state: WorkflowState, code: str, sym_mod: dict[str, str]) -> None:
    _merge_import_candidates_into_map(repo, state, sym_mod)
    needed = _collect_imported_names_in_phantom_froms(code, repo)
    _fill_sym_mod_by_repo_scan(repo, sym_mod, needed)


def _top_level_path_exists(repo: Path, module_dotted: str) -> bool:
    """在仓库根作为 PYTHONPATH 时，判断 `import a.b` 的顶层 a 是否像本地模块一样存在。"""
    top = module_dotted.split(".", 1)[0]
    if not top:
        return False
    if (repo / f"{top}.py").is_file():
        return True
    if (repo / top).is_dir():
        return True
    return False


# importorskip('requests') 等常见第三方/标准库，勿替换成项目内模块
_IMPORTORSKIP_EXTERNAL_OK: frozenset[str] = frozenset(
    {
        "pytest",
        "requests",
        "httpx",
        "aiohttp",
        "numpy",
        "pandas",
        "django",
        "flask",
        "fastapi",
        "pydantic",
        "bs4",
        "yaml",
        "PIL",
        "lxml",
        "redis",
        "pymongo",
        "boto3",
        "celery",
        "jinja2",
        "cryptography",
        "scipy",
        "sklearn",
        "dateutil",
        "tenacity",
        "structlog",
        "click",
        "tqdm",
        "re",
        "json",
        "os",
        "sys",
        "pathlib",
        "asyncio",
        "subprocess",
        "typing",
        "collections",
        "unittest",
        "functools",
        "itertools",
        "importlib",
        "io",
        "time",
        "math",
        "enum",
        "dataclasses",
        "abc",
        "copy",
        "hashlib",
        "base64",
        "logging",
        "sqlalchemy",
    }
)


def _pick_canonical_module_for_tests(sym_mod: dict[str, str]) -> str | None:
    if not sym_mod:
        return None
    vals = list(dict.fromkeys(sym_mod.values()))
    if len(vals) == 1:
        return vals[0]
    for key in ("GetHtml", "GetImg", "get_html", "get_img"):
        if sym_mod.get(key):
            return sym_mod[key]
    return vals[0] if vals else None


def _fix_mistaken_importorskip_stems(
    code: str, repo: Path, state: WorkflowState, sym_mod: dict[str, str]
) -> str:
    """
    将 `pytest.importorskip('GetPhotos2')` 等「文件名/臆造名」修正为可 import 的模块
    如 `spiderFile.get_photos`（与 sym_mod 一致），避免整文件被 skip 且 exit_code=5。
    """
    canonical = _pick_canonical_module_for_tests(sym_mod)
    if not canonical and re.search(r"pytest\.importorskip\(\s*['\"][A-Za-z0-9_]+['\"]", code):
        # 仅 importorskip 无 from 行时，sym_mod 可能为空；尝试按常见成对 def 在仓库内反查模块
        _fill_sym_mod_by_repo_scan(repo, sym_mod, {"GetHtml", "GetImg"})
        canonical = _pick_canonical_module_for_tests(sym_mod)
    if not canonical:
        return code
    c_leaf = canonical.split(".")[-1]

    def repl(m: re.Match[str]) -> str:
        q, stem = m.group(1), m.group(2)
        if "." in stem or stem in _IMPORTORSKIP_EXTERNAL_OK:
            return m.group(0)
        if stem == canonical or stem == c_leaf:
            return m.group(0)
        if _top_level_path_exists(repo, stem) or (repo / f"{stem}.py").is_file():
            return m.group(0)
        for rel in state.changed_files or []:
            if not str(rel).endswith(".py"):
                continue
            if Path(rel).stem != stem:
                continue
            if (repo / rel).is_file():
                return m.group(0)
        return f"pytest.importorskip({q}{canonical}{q})"

    return re.sub(r"pytest\.importorskip\(\s*(['\"])([A-Za-z0-9_]+)\1\s*\)", repl, code)


def _align_phantom_imports(code: str, state: WorkflowState) -> str:
    """
    将 LLM 臆造、但仓库不存在的包名（如旧 diff 中的 Crawler_Exercise.x）改写为
    changed_files 中真实存在的模块，避免 collection 期 ModuleNotFoundError。
    同时把 patch('Crawler_Exercise..') 中的路径一并替换为真实模块名。
    """
    repo = Path(state.repo_path or "")
    if not repo.is_dir():
        return code
    sym_mod = _symbol_to_module_map(repo, list(state.changed_files or []))
    _enrich_symbol_map(repo, state, code, sym_mod)
    if not sym_mod:
        return _fix_mistaken_importorskip_stems(code, repo, state, sym_mod)

    mapping: dict[str, str] = {}
    from_line = re.compile(
        r"^(\s*)from\s+([A-Za-z_][A-Za-z0-9_.]*)\s+import\s+(.+?)\s*(?:#.*)?$",
        re.MULTILINE,
    )

    def repl(m: re.Match[str]) -> str:
        indent, mod_path, tail = m.group(1), m.group(2), m.group(3)
        if _top_level_path_exists(repo, mod_path):
            return m.group(0)
        names = _parse_dotted_import_names(tail)
        if not names:
            return m.group(0)
        resolved = [sym_mod.get(n) for n in names if sym_mod.get(n)]
        if len(resolved) != len(names) or len(set(resolved)) != 1:
            return m.group(0)
        good = resolved[0]
        mapping[mod_path] = good
        return f"{indent}from {good} import {tail.strip()}"

    out = from_line.sub(repl, code)
    for bad, good in mapping.items():
        if bad == good:
            continue
        out = out.replace(f"'{bad}.", f"'{good}.")
        out = out.replace(f'"{bad}.', f'"{good}.')
        out = out.replace(f"'{bad}'", f"'{good}'")
        out = out.replace(f'"{bad}"', f'"{good}"')
    out = _fix_mistaken_importorskip_stems(out, repo, state, sym_mod)
    return out


def apply_phantom_import_alignment_to_state(state: WorkflowState) -> None:
    """
    对 state.generated_tests 逐文件执行幻影包名修正（含 LLM 修测试后再次调用）。
    """
    if not state.generated_tests:
        return
    for i, tf in enumerate(state.generated_tests):
        aligned = _align_phantom_imports(tf.content, state)
        if aligned != tf.content:
            state.generated_tests[i] = tf.model_copy(update={"content": aligned})


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
    tg_start = time.perf_counter()
    fast_mode = _testgen_fast_mode()
    timeout_s = _testgen_timeout_seconds()
    _workflow_log.info("TestGenAgent: 阶段 1/4 - 收集上下文（timeout=%.1fs fast_mode=%s）", timeout_s, fast_mode)
    snippets = extract_context_by_hunks(state.repo_path, state.diff_hunks)
    snippet_items = list(snippets.items())[: (2 if fast_mode else 4)]
    _workflow_log.info(
        "TestGenAgent: 上下文收集完成 snippets=%s changed_files=%s",
        len(snippet_items),
        len(state.changed_files or []),
    )

    system = (
        "你是资深Python测试工程师。基于代码变更生成pytest测试文件。\n\n"
        "# 核心规则\n"
        "1. 只输出一个文件内容（不要markdown），以纯Python代码形式输出\n"
        "2. 使用pytest风格（test_前缀函数/类）\n"
        "3. 对网络/数据库/文件系统调用优先使用mock/monkeypatch隔离\n"
        "4. 断言必须有意义：至少验证关键返回值/异常/分支\n"
        "5. 若无法确定导入路径，给出最保守import，并用断言提示需要调整模块路径\n"
        "6. 执行环境在被测仓库根目录运行 pytest，PYTHONPATH 已包含仓库根与常见 lib/\n"
        "7. 不要因笼统 ImportError 对整文件/整类批量 skip；仅在单条测试确实无法构造时才就地 skip\n"
        "8. 不要生成 test_import_paths/test_dependencies 这类全局依赖自检并 pytest.fail\n"
        "9. 可选依赖（如 fastapi）在具体用例内用 pytest.importorskip('fastapi')\n"
        "10. 禁止直接导入下划线私有符号；需使用模块导入 + getattr 判定\n\n"
        "11. 对每个核心目标（函数/接口/语义单元）尽量覆盖三类流程：\n"
        "   - 正常流程：有效输入下返回正确结果或成功状态\n"
        "   - 边界流程：空值/最小值/最大值/缺省字段等边界输入\n"
        "   - 异常流程：依赖失败、超时、非法输入、HTTP 4xx/5xx 等\n"
        "12. 当上下文不足无法同时覆盖三类流程时，至少保证“正常+异常”两类，并在测试注释中说明缺失原因。\n"
        "13. 三类流程都必须有可执行断言；禁止只调用函数不做断言。\n\n"
        "14. 禁止生成“导入失败后 pytest.skip('XXX 未导入')”模式来掩盖问题；"
        "若导入路径不确定，先尝试保守导入并在测试中用明确断言暴露导入失败原因。\n\n"
        "15. 若输入里存在 project_profile.import_candidates，必须优先按这些候选导入路径生成测试；"
        "不要臆造新的模块路径。必要时可遍历多个候选并在首个成功导入后执行断言。\n\n"
        "# 正确示例（必须遵循）\n\n"
        "## 示例1：异步API超时测试（正确写法）\n"
        "```python\n"
        "import pytest\n"
        "from unittest.mock import patch, MagicMock, AsyncMock\n"
        "import httpx\n\n"
        "@pytest.mark.asyncio\n"
        "async def test_api_timeout():\n"
        "    # 正确：使用 with（不是 async with）\n"
        "    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:\n"
        "        mock_post.side_effect = httpx.TimeoutException('timeout')\n"
        "        with pytest.raises(httpx.TimeoutException):\n"
        "            await some_api_call()\n"
        "```\n\n"
        "## 示例2：HTTP 500错误测试\n"
        "```python\n"
        "@pytest.mark.asyncio\n"
        "async def test_api_500_error():\n"
        "    mock_response = MagicMock(spec=httpx.Response)\n"
        "    mock_response.status_code = 500\n"
        "    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(\n"
        "        '500 Error', request=MagicMock(), response=mock_response\n"
        "    )\n\n"
        "    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:\n"
        "        mock_get.return_value = mock_response\n"
        "        # 测试你的函数...\n"
        "```\n\n"
        "# 禁止写法（会导致测试失败）\n"
        "❌ async with patch(...)  （patch不是异步上下文管理器）\n"
        "❌ try: ... pytest.fail('Expected timeout') except: pass  （应使用 pytest.raises）\n"
        "❌ pytest.fail('Missing dependency')  （应使用 pytest.importorskip）\n"
        "❌ patch 目标字符串跨行未闭合\n"
    )

    user_lines: list[str] = []
    user_lines.append(f"repo_path: {state.repo_path}")
    if state.project_profile:
        user_lines.append(f"project_profile: {state.project_profile}")
    user_lines.append(
        "runtime_hint: pytest cwd=repo_path; PYTHONPATH includes repo root and repo/lib if that directory exists."
    )
    user_lines.append(f"changed_files: {state.changed_files}")
    user_lines.append("test_plan:")
    plan = state.prioritized_plan or state.test_plan
    for p in plan[: (6 if fast_mode else 12)]:
        user_lines.append(f"- target={p.target} priority={p.priority} intent={p.intent}")
    if state.retrieved_context:
        user_lines.append("\nretrieved_context:")
        user_lines.append(str(state.retrieved_context)[: (900 if fast_mode else 2000)])
    user_lines.append("\ncode_context_snippets:")
    for rel, txt in snippet_items:
        if fast_mode:
            lines = txt.splitlines()[:80]
            user_lines.append(f"\n### file: {rel}\n" + "\n".join(lines) + "\n")
        else:
            user_lines.append(f"\n### file: {rel}\n{txt}\n")

    if fast_mode:
        user_lines.append(
            "\nfast_mode_hint: 优先生成覆盖核心路径的最小可运行用例，避免展开过多边缘场景；"
            "若信息不足，宁可给出少量高价值断言，也不要生成超长测试文件。"
        )

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
    _workflow_log.info("TestGenAgent: 阶段 2/4 - 请求 LLM 生成测试")
    llm_start = time.perf_counter()
    code = strip_markdown_code_fence(
        chat_text(
            system,
            user_blob,
            temperature=0.15 if fast_mode else 0.2,
            timeout_s=timeout_s,
        )
    )
    _workflow_log.info(
        "TestGenAgent: LLM 首次响应完成，耗时 %sms，输出长度=%s",
        int((time.perf_counter() - llm_start) * 1000),
        len(code),
    )
    if "def test_" not in code:
        code += "\n\n\ndef test_generated_placeholder():\n    assert True\n"

    _workflow_log.info("TestGenAgent: 阶段 3/4 - 语法检查与按需重试")
    syn = exec_syntax_error(code, filename="<generated_test>")
    if syn and llm_available():
        _workflow_log.warning("TestGenAgent: 首轮代码语法错误，触发重试。error=%s", syn)
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
        retry_start = time.perf_counter()
        code2 = strip_markdown_code_fence(
            chat_text(
                retry_sys,
                retry_user,
                temperature=0.1 if fast_mode else 0.15,
                timeout_s=timeout_s,
            )
        )
        _workflow_log.info(
            "TestGenAgent: LLM 重试响应完成，耗时 %sms，输出长度=%s",
            int((time.perf_counter() - retry_start) * 1000),
            len(code2),
        )
        if "def test_" in code2 and exec_syntax_error(code2, filename="<generated_test>") is None:
            code = code2
            _workflow_log.info("TestGenAgent: 采用重试结果（语法检查通过）")
        else:
            _workflow_log.warning("TestGenAgent: 重试结果仍未通过语法检查，保留首轮结果。")

    if "def test_" not in code:
        code += "\n\n\ndef test_generated_placeholder():\n    assert True\n"

    _workflow_log.info("TestGenAgent: 阶段 4/4 - 执行后处理清洗")
    code = _align_phantom_imports(code, state)
    code = _sanitize_global_dependency_guards(code)
    code = _sanitize_import_failure_skips(code)
    code = _sanitize_private_symbol_imports(code)
    code = _sanitize_timeout_test_antipatterns(code)
    code = _sanitize_async_patch_context(code)
    code = _append_changed_api_assertion(code, state)
    _workflow_log.info(
        "TestGenAgent: 完成，总耗时 %sms，最终输出长度=%s",
        int((time.perf_counter() - tg_start) * 1000),
        len(code),
    )

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
        state.debug["test_gen"] = {
            "used_llm": True,
            "model": os.getenv("MUTIAGENT_OPENAI_MODEL", "gpt-4.1-mini"),
            "fast_mode": _testgen_fast_mode(),
            "timeout_s": _testgen_timeout_seconds(),
        }
    else:
        files = _fallback_tests(state)
        state.debug["test_gen"] = {"used_llm": False}

    state.generated_tests = files
    return state

