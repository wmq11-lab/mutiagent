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


def test_parse_pytest_output_all_passed() -> None:
    d = parse_pytest_output("8 passed in 0.1s")
    assert d["passed"] == 8
    assert d["total_tests"] == 8
    assert d["execution_success"] is True


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
