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


def test_cross_module_counts_calls_pkg_a_and_pkg_b(tmp_path: Path) -> None:
    """仅 ``import pkg``，用 ``pkg.a.f()`` / ``pkg.b.g()`` 也应计入跨模块。"""
    ds = tmp_path / "ds"
    (ds / "pkg").mkdir(parents=True)
    (ds / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (ds / "pkg" / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    (ds / "pkg" / "b.py").write_text("def g():\n    return 2\n", encoding="utf-8")
    src = "import pkg\n\ndef test_calls_two_submodules():\n    pkg.a.f()\n    pkg.b.g()\n"
    st = WorkflowState(
        repo_path=str(ds),
        diff="",
        generated_tests=[GeneratedTestFile(path="t_test.py", content=src)],
        changed_files=["pkg/a.py", "pkg/b.py"],
    )
    r = compute_cross_module_test_cases(st, ds, ["pkg/a.py", "pkg/b.py"])
    assert r["cross_module_test_case_count"] == 1


def test_cross_module_from_import_name_call(tmp_path: Path) -> None:
    ds = tmp_path / "ds"
    (ds / "m").mkdir(parents=True)
    (ds / "m" / "__init__.py").write_text("", encoding="utf-8")
    (ds / "m" / "u.py").write_text("X=1\n", encoding="utf-8")
    (ds / "m" / "v.py").write_text("Y=2\n", encoding="utf-8")
    src = "from m import u, v\n\ndef test_both():\n    assert u.X == 1\n    assert v.Y == 2\n"
    st = WorkflowState(
        repo_path=str(ds),
        diff="",
        generated_tests=[GeneratedTestFile(path="t_test.py", content=src)],
        changed_files=["m/u.py", "m/v.py"],
    )
    r = compute_cross_module_test_cases(st, ds, ["m/u.py", "m/v.py"])
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
        junit_cases=None,
        python_exe="python",
        mutiagent_repo_root=tmp_path / "mal",
        generated_test_function_count=1,
    )
    assert blk["bug_detection_rate_pct"] is None
    assert "N/A" in (blk.get("bug_detection_rate_note") or "")


def test_bug_detection_from_junit_when_failures_present(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("FAILING_TESTS", raising=False)
    st = WorkflowState(repo_path=str(tmp_path), diff="", changed_files=[])
    (tmp_path / "mal").mkdir()
    junit_cases = [
        {"classname": "tests.test_x", "name": "test_a", "status": "failed"},
        {"classname": "tests.test_x", "name": "test_b", "status": "passed"},
    ]
    blk = compute_extended_experiment_metrics(
        st,
        tmp_path,
        cov_json_primary=None,
        cov_json_fallback=None,
        combined_pytest_output="1 passed in 0.05s\n",
        selected_tests=["tests.test_x::test_a"],
        junit_summary={},
        junit_cases=junit_cases,
        python_exe="python",
        mutiagent_repo_root=tmp_path / "mal",
        generated_test_function_count=1,
    )
    assert blk["bug_detection_rate_pct"] == 100.0
    assert "junit" in (blk.get("bug_detection_rate_note") or "").lower()


def test_added_function_coverage_from_change_analysis_add(
    tmp_path: Path,
) -> None:
    from mutiagent.graph.state import ChangeRecord, FileChangeSummary

    ds = tmp_path / "ds"
    (ds / "pkg").mkdir(parents=True)
    (ds / "pkg" / "mod.py").write_text("def new_fn():\n    return 1\n", encoding="utf-8")
    cov_path = tmp_path / "cov.json"
    cov_path.write_text(
        json.dumps({"files": {"pkg/mod.py": {"executed_lines": [1, 2]}}}),
        encoding="utf-8",
    )
    st = WorkflowState(
        repo_path=str(ds),
        diff="+# only comment\n",
        changed_files=["pkg/mod.py"],
        change_analysis=[
            FileChangeSummary(
                file="pkg/mod.py",
                summary="",
                risk="low",
                intent="FEATURE",
                tags=[],
                entities=[],
                changes=[
                    ChangeRecord(entity="new_fn", type="function", change_type="ADD"),
                ],
            )
        ],
    )
    r = compute_added_function_coverage_pct(st, ds, cov_path)
    assert r["added_function_total"] == 1
    assert r["added_function_covered"] == 1


def test_cross_module_loose_substring_ty_style(tmp_path: Path) -> None:
    """AST 未命中两条边时，宽松模式靠源码子串 ``typer.cli`` / ``typer.core`` 兜底。"""
    ds = tmp_path / "ds"
    (ds / "typer").mkdir(parents=True)
    (ds / "typer" / "cli.py").write_text("X=1\n", encoding="utf-8")
    (ds / "typer" / "core.py").write_text("Y=2\n", encoding="utf-8")
    src = (
        "def test_both():\n"
        '    _ = "see typer.cli and typer.core"\n'
    )
    st = WorkflowState(
        repo_path=str(ds),
        diff="",
        generated_tests=[GeneratedTestFile(path="t.py", content=src)],
        changed_files=["typer/cli.py", "typer/core.py"],
    )
    r = compute_cross_module_test_cases(st, ds, ["typer/cli.py", "typer/core.py"])
    assert r["cross_module_test_case_count"] >= 1
