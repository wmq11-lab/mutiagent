from __future__ import annotations

import json
from pathlib import Path

from mutiagent.evaluation.extended_experiment_metrics import (
    compute_added_function_coverage_pct,
    compute_cross_module_test_cases,
    compute_extended_experiment_metrics,
)
from mutiagent.graph.state import GeneratedTestFile, WorkflowState


def test_added_function_coverage_hits_body_line(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CHANGED_FUNCS", "pkg/mod.py:foo")
    ds = tmp_path / "ds"
    (ds / "pkg").mkdir(parents=True)
    (ds / "pkg" / "mod.py").write_text("def foo():\n    return 42\n", encoding="utf-8")
    cov_path = tmp_path / "cov.json"
    cov_path.write_text(
        json.dumps({"files": {"pkg/mod.py": {"executed_lines": [1, 2]}}}),
        encoding="utf-8",
    )
    st = WorkflowState(repo_path=str(ds), diff="")
    r = compute_added_function_coverage_pct(st, ds, cov_path)
    assert r["added_function_total"] == 1
    assert r["added_function_covered"] == 1
    assert r["added_function_coverage_pct"] == 100.0


def test_cross_module_imports_two_changed_files(tmp_path: Path) -> None:
    ds = tmp_path / "ds"
    (ds / "a").mkdir(parents=True)
    (ds / "a" / "__init__.py").write_text("", encoding="utf-8")
    (ds / "a" / "x.py").write_text("XA=1\n", encoding="utf-8")
    (ds / "a" / "y.py").write_text("YA=1\n", encoding="utf-8")
    src = "import a.x\nimport a.y\ndef test_cross():\n    assert a.x.XA == 1\n"
    st = WorkflowState(
        repo_path=str(ds),
        diff="",
        generated_tests=[GeneratedTestFile(path="t_test.py", content=src)],
        changed_files=["a/x.py", "a/y.py"],
    )
    r = compute_cross_module_test_cases(st, ds, ["a/x.py", "a/y.py"])
    assert r["cross_module_test_case_count"] == 1


def test_extended_bug_detection_na_without_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("FAILING_TESTS", raising=False)
    st = WorkflowState(repo_path=str(tmp_path), diff="", changed_files=[])
    (tmp_path / "mal").mkdir()
    blk = compute_extended_experiment_metrics(
        st,
        tmp_path,
        cov_json_primary=None,
        cov_json_fallback=None,
        combined_pytest_output="1 passed in 0.05s\n",
        selected_tests=["tests.t::test_x"],
        junit_summary={},
        python_exe="python",
        mutiagent_repo_root=tmp_path / "mal",
        generated_test_function_count=1,
    )
    assert blk["bug_detection_rate_pct"] is None
    assert "N/A" in (blk.get("bug_detection_rate_note") or "")
