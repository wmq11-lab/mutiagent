from __future__ import annotations

from mutiagent.utils.paths import is_under_project_tests_tree, production_changed_files


def test_is_under_project_tests_tree() -> None:
    assert is_under_project_tests_tree("tests/foo.py")
    assert is_under_project_tests_tree("tests/a/b.py")
    assert not is_under_project_tests_tree("typer/cli.py")
    assert not is_under_project_tests_tree("src/tests/foo.py")


def test_production_changed_files_filters_tests_prefix() -> None:
    raw = ["typer/cli.py", "tests/assets/x.py", "typer/core.py"]
    assert production_changed_files(raw) == ["typer/cli.py", "typer/core.py"]
