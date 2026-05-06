from __future__ import annotations

from pathlib import Path

from mutiagent.graph.state import WorkflowState
from mutiagent.nodes.execution_agent import _sync_repo_tests_artifacts_for_exec


def test_sync_tests_assets_and_changed_under_tests(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "tests" / "assets").mkdir(parents=True)
    (repo / "tests" / "assets" / "print_modules.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "tests" / "support.py").write_text("y = 2\n", encoding="utf-8")

    exec_root = tmp_path / "exec"
    exec_root.mkdir()
    state = WorkflowState(
        repo_path=str(repo),
        diff="",
        changed_files=["tests/support.py", "docs/readme.md"],
    )
    _sync_repo_tests_artifacts_for_exec(repo, exec_root, state)

    assert (exec_root / "tests" / "assets" / "print_modules.py").read_text(encoding="utf-8") == "x = 1\n"
    assert (exec_root / "tests" / "support.py").read_text(encoding="utf-8") == "y = 2\n"
