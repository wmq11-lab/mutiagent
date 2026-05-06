from __future__ import annotations

from pathlib import Path

from mutiagent.graph.state import GeneratedTestFile, WorkflowState
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


def test_sync_tests_package_context_init_conftest_utils(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("# pkg\n", encoding="utf-8")
    (repo / "tests" / "conftest.py").write_text("import pytest\n", encoding="utf-8")
    (repo / "tests" / "utils.py").write_text("FLAG = 1\n", encoding="utf-8")
    (repo / "tests" / "test_others.py").write_text(
        "from .utils import FLAG\n\ndef test_x():\n    assert FLAG == 1\n",
        encoding="utf-8",
    )

    exec_root = tmp_path / "exec"
    exec_root.mkdir()
    state = WorkflowState(
        repo_path=str(repo),
        diff="",
        changed_files=["tests/test_others.py"],
    )
    _sync_repo_tests_artifacts_for_exec(repo, exec_root, state)

    assert (exec_root / "tests" / "__init__.py").read_text(encoding="utf-8") == "# pkg\n"
    assert (exec_root / "tests" / "conftest.py").read_text(encoding="utf-8") == "import pytest\n"
    assert (exec_root / "tests" / "utils.py").read_text(encoding="utf-8") == "FLAG = 1\n"


def test_sync_tests_package_context_nested_utils_package(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "tests" / "sub").mkdir(parents=True)
    (repo / "tests" / "__init__.py").touch()
    (repo / "tests" / "sub" / "__init__.py").touch()
    (repo / "tests" / "sub" / "utils").mkdir(parents=True)
    (repo / "tests" / "sub" / "utils" / "__init__.py").write_text("x = 42\n", encoding="utf-8")
    (repo / "tests" / "sub" / "test_a.py").write_text(
        "from .utils import x\n\ndef test_a():\n    assert x == 42\n",
        encoding="utf-8",
    )

    exec_root = tmp_path / "exec"
    exec_root.mkdir()
    state = WorkflowState(repo_path=str(repo), diff="", changed_files=["tests/sub/test_a.py"])
    _sync_repo_tests_artifacts_for_exec(repo, exec_root, state)

    assert (exec_root / "tests" / "sub" / "utils" / "__init__.py").read_text(encoding="utf-8") == "x = 42\n"


def test_sync_tests_package_context_from_generated_tests_only(tmp_path: Path) -> None:
    """generated_tests 中有 tests/*.py 但 changed_files 无 tests 时也应补齐包文件。"""
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "utils.py").write_text("U = 1\n", encoding="utf-8")

    exec_root = tmp_path / "exec"
    exec_root.mkdir()
    state = WorkflowState(
        repo_path=str(repo),
        diff="",
        changed_files=["src/app.py"],
        generated_tests=[
            GeneratedTestFile(
                path="tests/test_new.py",
                content="from .utils import U\n\ndef test_n():\n    assert U == 1\n",
            )
        ],
    )
    _sync_repo_tests_artifacts_for_exec(repo, exec_root, state)

    assert (exec_root / "tests" / "__init__.py").is_file()
    assert (exec_root / "tests" / "utils.py").read_text(encoding="utf-8") == "U = 1\n"
