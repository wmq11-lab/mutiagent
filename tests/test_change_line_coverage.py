from __future__ import annotations

import json
from pathlib import Path

from mutiagent.evaluation.change_line_coverage import change_line_coverage_from_diff_and_cov_paths


def test_recall_frac_all_git_chunks_match_executed_lines(tmp_path: Path) -> None:
    cov = tmp_path / "cov.json"
    cov.write_text(
        json.dumps(
            {
                "files": {
                    "pkg/mod.py": {"executed_lines": [10, 11]},
                }
            }
        ),
        encoding="utf-8",
    )
    diff = (
        "diff --git a/pkg/mod.py b/pkg/mod.py\n"
        "--- a/pkg/mod.py\n+++ b/pkg/mod.py\n"
        "@@ -8,6 +8,7 @@ def f():\n"
        "     pass\n"
        "+added line one\n"
        "+added line two\n"
        "     return\n"
    )
    r = change_line_coverage_from_diff_and_cov_paths(diff, cov)
    assert r["change_plus_lines"] == 2
    assert r["covered_plus_lines"] == 2
    assert r["recall_frac"] == 1.0


def test_skips_tests_dir_py_for_denominator(tmp_path: Path) -> None:
    cov = tmp_path / "cov.json"
    cov.write_text(
        json.dumps(
            {
                "files": {
                    "pkg/mod.py": {"executed_lines": [10]},
                    "tests/t.py": {"executed_lines": [2]},
                }
            }
        ),
        encoding="utf-8",
    )
    diff = (
        "diff --git a/pkg/mod.py b/pkg/mod.py\n"
        "--- a/pkg/mod.py\n+++ b/pkg/mod.py\n"
        "@@ -8,4 +8,5 @@ def f():\n"
        "     pass\n"
        "+in prod\n"
        "     return\n"
        "diff --git a/tests/t.py b/tests/t.py\n"
        "--- a/tests/t.py\n+++ b/tests/t.py\n"
        "@@ -1,2 +1,3 @@\n"
        " x\n"
        "+only test file\n"
    )
    r = change_line_coverage_from_diff_and_cov_paths(diff, cov)
    assert r["change_plus_lines"] == 1
    assert r["covered_plus_lines"] == 1
    assert r["recall_frac"] == 1.0


def test_non_py_chunks_skipped_in_change_coverage(tmp_path: Path) -> None:
    cov = tmp_path / "cov.json"
    cov.write_text(
        json.dumps(
            {
                "files": {
                    "pkg/mod.py": {"executed_lines": [2]},
                    "README.md": {"executed_lines": [1]},
                }
            }
        ),
        encoding="utf-8",
    )
    diff = (
        "diff --git a/pkg/mod.py b/pkg/mod.py\n"
        "--- a/pkg/mod.py\n+++ b/pkg/mod.py\n"
        "@@ -1,2 +1,3 @@\n"
        " a\n"
        "+b\n"
        "diff --git a/README.md b/README.md\n"
        "--- a/README.md\n+++ b/README.md\n"
        "@@ -1 +1 @@\n"
        "-x\n"
        "+y\n"
    )
    r = change_line_coverage_from_diff_and_cov_paths(diff, cov)
    assert r["change_plus_lines"] == 1
    assert r["covered_plus_lines"] == 1


def test_executed_misses_plus_lines(tmp_path: Path) -> None:
    cov = tmp_path / "cov.json"
    cov.write_text(
        json.dumps({"files": {"a.py": {"executed_lines": [99]}}}),
        encoding="utf-8",
    )
    diff = (
        "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1 +1 @@\n-x\n+y\n"
    )
    r = change_line_coverage_from_diff_and_cov_paths(diff, cov)
    assert r["change_plus_lines"] == 1
    assert r["covered_plus_lines"] == 0
    assert r["recall_frac"] == 0.0


def test_compute_all_metrics_pass_rate_and_change_line_recall() -> None:
    from mutiagent.evaluation.metrics import compute_all_metrics

    m = compute_all_metrics(
        selected_tests=["a"],
        all_tests=["a", "b"],
        failing_tests=[],
        execution_time=10.0,
        full_time=20.0,
        precision_pass_rate=0.8,
        recall_change_line=0.5,
    )
    assert m["precision"] == 0.8
    assert m["recall"] == 0.5
    expect_f1 = 2.0 * 0.8 * 0.5 / (0.8 + 0.5)
    assert abs(m["f1"] - expect_f1) < 1e-5
