"""collect_experiment_metrics / mutiagent.evaluation 中解析逻辑的单元测试。"""

from __future__ import annotations

import json
from pathlib import Path

from mutiagent.evaluation.coverage_json import parse_coverage_json
from mutiagent.evaluation.pytest_parsing import parse_pytest_output


def test_parse_pytest_output_full_summary() -> None:
    text = (
        "foo\n"
        "=== 2 passed, 1 failed, 1 error, 1 skipped, 1 deselected, 1 xfailed, 1 xpassed in 1s ===\n"
    )
    d = parse_pytest_output(text)
    assert d["passed"] == 2
    assert d["failed"] == 1
    assert d["errors"] == 1
    assert d["skipped"] == 1
    assert d["deselected"] == 1
    assert d["xfailed"] == 1
    assert d["xpassed"] == 1
    assert d["total_tests"] == 8
    assert d["execution_success"] is False
    assert d["pass_rate"] == 25.0


def test_parse_pytest_output_failed_only_loose() -> None:
    d = parse_pytest_output("some noise\n=========== 27 failed in 4.04s ============\n")
    assert d["failed"] == 27
    assert d["passed"] == 0
    assert d["total_tests"] == 27
    assert d["execution_success"] is False


def test_parse_pytest_output_all_passed() -> None:
    d = parse_pytest_output("8 passed in 0.1s")
    assert d["passed"] == 8
    assert d["total_tests"] == 8
    assert d["execution_success"] is True


def test_build_experiment_run_record_junit_fallback(tmp_path: Path) -> None:
    from mutiagent.evaluation.experiment_run_log import build_experiment_run_record
    from mutiagent.graph.state import WorkflowState

    state = WorkflowState(repo_path=str(tmp_path), diff="", run_eval=True)
    rec = build_experiment_run_record(
        state,
        tmp_path,
        combined_pytest_text="(no pytest summary keywords)",
        coverage_data=None,
        junit_summary={"tests": "31", "failures": "20", "errors": "1", "skipped": "2"},
    )
    assert rec["total_tests"] == 31
    assert rec["failed"] == 20
    assert rec["errors"] == 1
    assert rec["skipped"] == 2
    assert rec["passed"] == 8
    assert rec["execution_success"] is False


def test_build_experiment_run_record_keeps_parse_when_nonzero(tmp_path: Path) -> None:
    from mutiagent.evaluation.experiment_run_log import build_experiment_run_record
    from mutiagent.graph.state import WorkflowState

    state = WorkflowState(repo_path=str(tmp_path), diff="", run_eval=True)
    text = "=== 2 passed, 1 failed in 0.1s ===\n"
    rec = build_experiment_run_record(
        state,
        tmp_path,
        combined_pytest_text=text,
        coverage_data=None,
        junit_summary={"tests": "99", "failures": "99", "errors": "0", "skipped": "0"},
    )
    assert rec["total_tests"] == 3
    assert rec["passed"] == 2
    assert rec["failed"] == 1


def test_parse_coverage_json_aggregates_from_files(tmp_path: Path) -> None:
    p = tmp_path / "only_files.json"
    p.write_text(
        json.dumps(
            {
                "files": {
                    "a.py": {
                        "summary": {
                            "covered_lines": 3,
                            "num_statements": 10,
                            "covered_branches": 1,
                            "num_branches": 4,
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    c = parse_coverage_json(str(p))
    assert c["covered_lines"] == 3
    assert c["total_lines"] == 10
    assert abs(c["line_coverage"] - 30.0) < 0.01


def test_parse_coverage_json_total_lines(tmp_path: Path) -> None:
    p = tmp_path / "c.json"
    p.write_text(
        json.dumps(
            {
                "totals": {
                    "covered_lines": 3,
                    "num_statements": 10,
                    "covered_branches": 1,
                    "num_branches": 4,
                }
            }
        ),
        encoding="utf-8",
    )
    c = parse_coverage_json(str(p))
    assert c["total_statements"] == 10
    assert c["total_lines"] == 10
    assert c["covered_lines"] == 3
