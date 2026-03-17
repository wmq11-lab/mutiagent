from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from mutiagent.graph.state import WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_text


def _write_generated_tests(tmpdir: Path, state: WorkflowState) -> Path:
    for f in state.generated_tests:
        rel = f.path.lstrip("/").replace("\\", "/")
        out_path = tmpdir / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(f.content, encoding="utf-8")
    return tmpdir


def _run_pytest(repo: Path, test_root: Path, *, with_cov: bool = False) -> tuple[int, str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo)

    cmd = ["python", "-m", "pytest", "-q", str(test_root)]
    if with_cov:
        cmd = ["python", "-m", "pytest", "-q", "--cov", "--cov-report=term-missing", str(test_root)]

    p = subprocess.run(cmd, cwd=str(repo), env=env, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def _llm_fix_by_failure(state: WorkflowState, stdout: str, stderr: str) -> None:
    if not state.generated_tests:
        return
    system = (
        "你是资深Python测试工程师。给定pytest失败输出与当前测试文件，请修复测试使其更可能通过。"
        "只输出修复后的完整Python测试文件内容（不要markdown，不要解释）。"
    )
    user = (
        f"repo_path: {state.repo_path}\n"
        f"changed_files: {state.changed_files}\n\n"
        f"pytest_stdout:\n{stdout}\n\npytest_stderr:\n{stderr}\n\n"
        "current_test_file:\n"
        f"{state.generated_tests[0].content}\n"
    )
    fixed = chat_text(system, user, temperature=0.2)
    if fixed and "def test_" in fixed:
        state.generated_tests[0].content = fixed.strip() + "\n"


def execution_agent(state: WorkflowState) -> WorkflowState:
    if not state.run_eval:
        state.execution = {"ran": False}
        return state

    repo = Path(state.repo_path)
    if not repo.exists():
        state.execution = {"ran": True, "exit_code": 2, "stdout": "", "stderr": "repo_path 不存在"}
        return state

    with tempfile.TemporaryDirectory(prefix="mutiagent_exec_") as td:
        tmpdir = Path(td)
        _write_generated_tests(tmpdir, state)
        code, out, err = _run_pytest(repo, tmpdir, with_cov=False)

        repaired = False
        if code != 0 and llm_available():
            _llm_fix_by_failure(state, out, err)
            repaired = True
            retry_dir = tmpdir / "retry"
            retry_dir.mkdir(parents=True, exist_ok=True)
            _write_generated_tests(retry_dir, state)
            code, out, err = _run_pytest(repo, retry_dir, with_cov=False)

        state.execution = {
            "ran": True,
            "exit_code": code,
            "stdout": out,
            "stderr": err,
            "attempted_fix": repaired,
        }

    return state

