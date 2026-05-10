from __future__ import annotations

import os

from mutiagent.utils.coverage_pytest_env import pytest_env_with_isolated_coverage


def test_isolated_coverage_sets_coverage_file_and_clears_stale(tmp_path) -> None:
    stale = tmp_path / ".coverage"
    stale.write_text("x", encoding="utf-8")
    extra = tmp_path / ".coverage.host.123"
    extra.write_text("y", encoding="utf-8")

    base = {"HOME": os.environ.get("HOME", "")}
    env = pytest_env_with_isolated_coverage(base, data_dir=tmp_path)

    assert env["COVERAGE_FILE"] == str((tmp_path / ".coverage").resolve())
    assert not stale.is_file()
    assert not extra.is_file()
