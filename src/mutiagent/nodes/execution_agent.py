from __future__ import annotations

import html
import json
import logging
import os
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from mutiagent.graph.state import WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_text
from mutiagent.utils.dataset_venv import ensure_dataset_venv
from mutiagent.utils.llm_output import strip_markdown_code_fence
from mutiagent.utils.syntax_guard import exec_syntax_error

_workflow_log = logging.getLogger("mutiagent.workflow")

try:
    _PYTEST_LOG_CAP = int(os.environ.get("MUTIAGENT_PYTEST_LOG_MAX_CHARS", "60000"))
except ValueError:
    _PYTEST_LOG_CAP = 60000


def _log_pytest_output(phase: str, exit_code: int, stdout: str, stderr: str) -> None:
    """将 pytest 文本输出写入 mutiagent.workflow → log/mutiagent.log（单段过长则截断）。"""
    half = max(2000, _PYTEST_LOG_CAP // 2)

    def clip(s: str, limit: int) -> str:
        t = s or ""
        if len(t) <= limit:
            return t if t else "(空)"
        return t[: max(0, limit - 80)] + "\n... [已截断；完整见 report_dir 下 pytest_stdout.txt / pytest_stderr.txt]\n"

    _workflow_log.info(
        "ExecutionAgent: pytest %s · 退出码=%s\n--- stdout ---\n%s\n--- stderr ---\n%s",
        phase,
        exit_code,
        clip(stdout, half),
        clip(stderr, half),
    )


def _test_reports_enabled() -> bool:
    v = os.environ.get("MUTIAGENT_DISABLE_TEST_REPORT", "").strip().lower()
    return v not in {"1", "true", "yes", "on"}


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _resolve_pytest_executable(repo: Path, state: WorkflowState) -> tuple[str | None, str | None]:
    """
    返回 (python 可执行路径, 错误信息)。
    显式 MUTIAGENT_PYTEST_PYTHON 优先；否则 auto_venv / MUTIAGENT_AUTO_VENV 时创建/复用仓库内 venv；否则用 PATH 上的 python。
    """
    ex = os.environ.get("MUTIAGENT_PYTEST_PYTHON", "").strip()
    if ex:
        return ex, None
    if state.auto_venv or _env_truthy("MUTIAGENT_AUTO_VENV"):
        py, msg = ensure_dataset_venv(repo)
        if not py:
            state.debug.setdefault("dataset_venv", {}).update({"status": "error", "message": msg})
            return None, msg or "dataset venv 初始化失败"
        state.debug.setdefault("dataset_venv", {}).update(
            {"python": py, "bootstrap": msg, "status": "ok"}
        )
        return py, None
    return "python", None


def _create_report_dir(repo: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    d = repo / ".mutiagent" / "reports" / stamp
    d.mkdir(parents=True, exist_ok=True)
    return d


def _junit_summary_and_rows(junit_path: Path | None) -> tuple[dict[str, str], list[dict[str, str]]]:
    """Parse pytest junit.xml for HTML table rows."""
    agg = {"tests": "0", "failures": "0", "errors": "0", "skipped": "0", "time": "—", "name": "pytest"}
    rows: list[dict[str, str]] = []
    if junit_path is None or not junit_path.exists():
        return agg, rows
    try:
        tree = ET.parse(junit_path)
        root = tree.getroot()
    except ET.ParseError:
        return agg, rows

    # Single <testsuite> or wrapper <testsuites>
    suites = root.findall("testsuite")
    if not suites and root.tag == "testsuite":
        suites = [root]
    total_t = total_f = total_e = total_s = 0
    time_parts: list[str] = []
    for ts in suites:
        total_t += int(ts.get("tests") or 0)
        total_f += int(ts.get("failures") or 0)
        total_e += int(ts.get("errors") or 0)
        total_s += int(ts.get("skipped") or 0)
        if ts.get("time"):
            time_parts.append(str(ts.get("time")))
        name = ts.get("name") or "pytest"
        for tc in ts.findall("testcase"):
            cname = tc.get("classname") or ""
            tname = tc.get("name") or ""
            ttime = tc.get("time") or ""
            status = "passed"
            detail = ""
            el = tc.find("failure")
            if el is not None:
                status = "failed"
                detail = (el.get("message") or "").strip() + "\n" + (el.text or "").strip()
            el = tc.find("error")
            if el is not None:
                status = "error"
                detail = (el.get("message") or "").strip() + "\n" + (el.text or "").strip()
            el = tc.find("skipped")
            if el is not None:
                status = "skipped"
                detail = (el.get("message") or "").strip() + "\n" + (el.text or "").strip()
            rows.append(
                {
                    "suite": name,
                    "classname": cname,
                    "name": tname,
                    "time": ttime,
                    "status": status,
                    "detail": detail.strip(),
                }
            )
    agg = {
        "tests": str(total_t),
        "failures": str(total_f),
        "errors": str(total_e),
        "skipped": str(total_s),
        "time": " / ".join(time_parts) if time_parts else "—",
        "name": suites[0].get("name", "pytest") if suites else "pytest",
    }
    return agg, rows


def _write_html_report(
    report_dir: Path,
    *,
    junit_path: Path | None,
    stdout: str,
    stderr: str,
    exit_code: int,
    attempted_fix: bool,
    repo_path: str,
    junit_before_repair: bool,
) -> None:
    agg, cases = _junit_summary_and_rows(junit_path)
    ok = exit_code == 0
    status_label = "通过" if ok else "未通过"
    status_class = "ok" if ok else "fail"

    def esc(s: str) -> str:
        return html.escape(s, quote=True)

    case_rows_html = []
    for c in cases:
        st = c["status"]
        st_class = {"passed": "ok", "failed": "fail", "error": "err", "skipped": "skip"}.get(st, "")
        detail = c["detail"]
        detail_id = f"d{len(case_rows_html)}"
        row = (
            f"<tr class='{esc(st_class)}'>"
            f"<td><span class='badge {esc(st_class)}'>{esc(st)}</span></td>"
            f"<td class='mono'>{esc(c['classname'])}</td>"
            f"<td class='mono'>{esc(c['name'])}</td>"
            f"<td>{esc(c['time'])}</td>"
            f"<td>"
        )
        if detail:
            row += (
                f"<details id='{detail_id}'><summary>详情</summary>"
                f"<pre class='detail'>{esc(detail)}</pre></details>"
            )
        else:
            row += "—"
        row += "</td></tr>"
        case_rows_html.append(row)

    table_body = "\n".join(case_rows_html) if case_rows_html else "<tr><td colspan='5'>未解析到用例（可能未生成 junit.xml）</td></tr>"

    extra_links = ""
    if junit_before_repair:
        extra_links = "<p class='muted'>另见同目录 <code>junit_before_repair.xml</code>（修复前）。</p>"

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>mutiagent pytest 报告</title>
  <style>
    :root {{
      --bg: #0f1419;
      --card: #1a2332;
      --text: #e6edf3;
      --muted: #8b949e;
      --border: #30363d;
      --ok: #3fb950;
      --fail: #f85149;
      --err: #d29922;
      --skip: #8b949e;
    }}
    body {{
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "PingFang SC", sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 1.25rem;
      line-height: 1.5;
    }}
    h1 {{ font-size: 1.25rem; margin: 0 0 0.5rem; }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1rem 1.25rem;
      margin-bottom: 1rem;
    }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 0.75rem; }}
    .stat {{ font-size: 0.85rem; color: var(--muted); }}
    .stat b {{ display: block; font-size: 1.35rem; color: var(--text); margin-top: 0.2rem; }}
    .badge {{ display: inline-block; padding: 0.15rem 0.45rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }}
    .badge.ok {{ background: rgba(63, 185, 80, 0.2); color: var(--ok); }}
    .badge.fail {{ background: rgba(248, 81, 73, 0.2); color: var(--fail); }}
    .badge.err {{ background: rgba(210, 153, 34, 0.2); color: var(--err); }}
    .badge.skip {{ background: rgba(139, 148, 158, 0.2); color: var(--skip); }}
    tr.ok td {{ border-left: 3px solid var(--ok); }}
    tr.fail td {{ border-left: 3px solid var(--fail); }}
    tr.err td {{ border-left: 3px solid var(--err); }}
    tr.skip td {{ border-left: 3px solid var(--skip); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
    th, td {{ text-align: left; padding: 0.5rem 0.6rem; border-bottom: 1px solid var(--border); vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 600; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.82rem; word-break: break-all; }}
    pre.log, pre.detail {{
      background: #0d1117;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.75rem;
      overflow: auto;
      max-height: 28rem;
      font-size: 0.8rem;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .muted {{ color: var(--muted); font-size: 0.85rem; margin: 0.5rem 0 0; }}
    details summary {{ cursor: pointer; color: var(--muted); }}
    code {{ background: #21262d; padding: 0.1rem 0.35rem; border-radius: 4px; font-size: 0.85em; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>pytest 执行结果 <span class="badge {status_class}">{esc(status_label)}</span></h1>
    <p class="muted">仓库：<code>{esc(repo_path)}</code> · 退出码 <code>{exit_code}</code>
    · LLM 尝试修复：{'是' if attempted_fix else '否'}</p>
    <div class="grid">
      <div class="stat">用例数<b>{esc(agg['tests'])}</b></div>
      <div class="stat">失败<b>{esc(agg['failures'])}</b></div>
      <div class="stat">错误<b>{esc(agg['errors'])}</b></div>
      <div class="stat">跳过<b>{esc(agg['skipped'])}</b></div>
      <div class="stat">耗时(s)<b>{esc(agg['time'])}</b></div>
    </div>
    {extra_links}
  </div>
  <div class="card">
    <h1 style="font-size:1.1rem">用例明细</h1>
    <table>
      <thead><tr><th>状态</th><th>类</th><th>用例</th><th>耗时</th><th>信息</th></tr></thead>
      <tbody>
        {table_body}
      </tbody>
    </table>
  </div>
  <div class="card">
    <h1 style="font-size:1.1rem">标准输出</h1>
    <pre class="log">{esc(stdout or '(空)')}</pre>
  </div>
  <div class="card">
    <h1 style="font-size:1.1rem">标准错误</h1>
    <pre class="log">{esc(stderr or '(空)')}</pre>
  </div>
  <p class="muted">由 mutiagent 生成 · 同目录含 <code>junit.xml</code>、<code>summary.json</code> 与文本日志</p>
</body>
</html>
"""
    (report_dir / "report.html").write_text(doc, encoding="utf-8")


def _write_eval_report_files(
    report_dir: Path,
    *,
    stdout: str,
    stderr: str,
    exit_code: int,
    attempted_fix: bool,
    repo_path: str,
    junit_before_repair: bool = False,
) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "pytest_stdout.txt").write_text(stdout, encoding="utf-8", errors="replace")
    (report_dir / "pytest_stderr.txt").write_text(stderr, encoding="utf-8", errors="replace")
    junit_path = report_dir / "junit.xml"
    _write_html_report(
        report_dir,
        junit_path=junit_path if junit_path.exists() else None,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        attempted_fix=attempted_fix,
        repo_path=repo_path,
        junit_before_repair=junit_before_repair,
    )
    files: dict[str, str] = {
        "html": "report.html",
        "stdout": "pytest_stdout.txt",
        "stderr": "pytest_stderr.txt",
        "junit": "junit.xml",
    }
    if junit_before_repair:
        files["junit_before_repair"] = "junit_before_repair.xml"
    summary = {
        "exit_code": exit_code,
        "attempted_fix": attempted_fix,
        "repo_path": repo_path,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "files": files,
    }
    (report_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_generated_tests(tmpdir: Path, state: WorkflowState) -> Path:
    for f in state.generated_tests:
        rel = f.path.lstrip("/").replace("\\", "/")
        out_path = tmpdir / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(f.content, encoding="utf-8")
    return tmpdir


def _run_pytest(
    repo: Path,
    test_root: Path,
    *,
    python_exe: str,
    with_cov: bool = False,
    junit_xml: Path | None = None,
) -> tuple[int, str, str]:
    env = os.environ.copy()
    # 许多 Python 项目（如 Ansible）把可导入包放在 lib/ 下，仅设仓库根目录会 ModuleNotFoundError。
    pp = [str(repo)]
    lib = repo / "lib"
    if lib.is_dir():
        pp.insert(0, str(lib.resolve()))
    inherit = env.get("PYTHONPATH", "").strip()
    # 源码树含 lib/ansible 时，继承宿主的 PYTHONPATH 可能带入 site-packages 之外的冲突路径；
    # 默认不再拼接，避免 conda 里另一个 ansible 与 lib/ansible 混用导致 ansible 无 galaxy 子包。
    if inherit and (
        _env_truthy("MUTIAGENT_PYTEST_APPEND_PYTHONPATH") or not (lib / "ansible").is_dir()
    ):
        pp.append(inherit)
    env["PYTHONPATH"] = os.pathsep.join(pp)

    cmd: list[str] = [python_exe, "-m", "pytest", "-q"]
    if with_cov:
        cmd.extend(["--cov", "--cov-report=term-missing"])
    cmd.append(str(test_root))
    if junit_xml is not None:
        cmd.extend([f"--junitxml={junit_xml.resolve()}", "-o", "junit_family=xunit2"])

    p = subprocess.run(cmd, cwd=str(repo), env=env, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def _llm_fix_by_failure(state: WorkflowState, stdout: str, stderr: str) -> None:
    if not state.generated_tests:
        return
    system = (
        "你是资深Python测试工程师。给定pytest失败输出与当前测试文件，请修复测试使其更可能通过。"
        "不要通过整批 pytest.skip 或“Required modules not available”式跳过掩盖失败；优先 mock/patch 或修正 import。"
        "patch( 与 patch.object( 的第一个参数字符串必须单行完整闭合引号与括号，禁止在引号未闭合时换行；过长路径用变量承接。"
        "若错误为 ansible 无 galaxy / patch 解析失败：检查 patch 目标是否与 collection.py 中 import 的符号一致"
        "（Display 常在 ansible.utils.display；在 collection 模块命名空间下多用 patch('ansible.galaxy.collection.Display') 或对已 import 的模块 patch.object）。"
        "只输出修复后的完整Python测试文件内容（不要markdown，不要解释）。"
    )
    user = (
        f"repo_path: {state.repo_path}\n"
        f"changed_files: {state.changed_files}\n\n"
        f"pytest_stdout:\n{stdout}\n\npytest_stderr:\n{stderr}\n\n"
        "current_test_file:\n"
        f"{state.generated_tests[0].content}\n"
    )
    fixed = strip_markdown_code_fence(chat_text(system, user, temperature=0.2))
    if fixed and "def test_" in fixed:
        newc = fixed.strip() + "\n"
        syn_fix = exec_syntax_error(newc, filename="<generated_test>")
        if syn_fix is None:
            state.generated_tests[0].content = newc
        else:
            _workflow_log.warning(
                "ExecutionAgent: LLM 按失败修复后的代码仍有语法错误，已保留修复前版本。%s",
                syn_fix,
            )


def execution_agent(state: WorkflowState) -> WorkflowState:
    if not state.run_eval:
        state.execution = {"ran": False}
        return state

    repo = Path(state.repo_path)
    if not repo.exists():
        state.execution = {
            "ran": True,
            "exit_code": 2,
            "stdout": "",
            "stderr": "repo_path 不存在",
            "report_dir": None,
        }
        return state

    py_exe, py_err = _resolve_pytest_executable(repo, state)
    if py_err:
        state.execution = {
            "ran": True,
            "exit_code": 2,
            "stdout": "",
            "stderr": py_err,
            "report_dir": None,
        }
        return state

    report_dir: Path | None = None
    junit_xml: Path | None = None
    if _test_reports_enabled():
        try:
            report_dir = _create_report_dir(repo)
            junit_xml = report_dir / "junit.xml"
        except OSError:
            report_dir = None
            junit_xml = None

    junit_before_repair = False
    with tempfile.TemporaryDirectory(prefix="mutiagent_exec_") as td:
        tmpdir = Path(td)
        _write_generated_tests(tmpdir, state)
        code, out, err = _run_pytest(
            repo, tmpdir, python_exe=py_exe, with_cov=False, junit_xml=junit_xml
        )
        _log_pytest_output("第1次运行", code, out, err)

        repaired = False
        if code != 0 and llm_available():
            if report_dir is not None and junit_xml is not None and junit_xml.exists():
                shutil.copy2(junit_xml, report_dir / "junit_before_repair.xml")
                junit_before_repair = True
            _llm_fix_by_failure(state, out, err)
            repaired = True
            retry_dir = tmpdir / "retry"
            retry_dir.mkdir(parents=True, exist_ok=True)
            _write_generated_tests(retry_dir, state)
            code, out, err = _run_pytest(
                repo, retry_dir, python_exe=py_exe, with_cov=False, junit_xml=junit_xml
            )
            _log_pytest_output("LLM 修复后重试", code, out, err)

        payload: dict[str, object] = {
            "ran": True,
            "exit_code": code,
            "stdout": out,
            "stderr": err,
            "attempted_fix": repaired,
            "pytest_python": py_exe,
        }
        j_agg: dict[str, str] = {}
        j_rows: list[dict[str, str]] = []
        if junit_xml is not None and junit_xml.exists():
            j_agg, j_rows = _junit_summary_and_rows(junit_xml)
        payload["junit_summary"] = j_agg
        payload["junit_cases"] = j_rows

        if report_dir is not None:
            _write_eval_report_files(
                report_dir,
                stdout=out,
                stderr=err,
                exit_code=code,
                attempted_fix=repaired,
                repo_path=str(repo.resolve()),
                junit_before_repair=junit_before_repair,
            )
            payload["report_dir"] = str(report_dir.resolve())
        else:
            payload["report_dir"] = None

        if code != 0:
            err_one = (err.strip() or "(空)").splitlines()[0] if err else "(空)"
            _workflow_log.warning(
                "ExecutionAgent: pytest 退出码 %s；stderr 首行: %s",
                code,
                err_one[:500],
            )

        state.execution = payload

    return state

