"""changed_function_coverage 报告构建。"""

from __future__ import annotations

import json
from pathlib import Path

from mutiagent.evaluation.changed_function_coverage import build_changed_function_coverage_report
from mutiagent.graph.state import ChangeRecord, FileChangeSummary, WorkflowState


def test_changed_function_coverage_hits_matching_functions(tmp_path: Path) -> None:
    cov = {
        "files": {
            "pkg/mod.py": {
                "functions": {
                    "foo": {"summary": {"covered_lines": 0, "num_statements": 3, "percent_statements_covered": 0.0}},
                    "bar": {"summary": {"covered_lines": 2, "num_statements": 2, "percent_statements_covered": 100.0}},
                }
            }
        }
    }
    p = tmp_path / "cov.json"
    p.write_text(json.dumps(cov), encoding="utf-8")

    st = WorkflowState(repo_path="/tmp/r", diff="", run_eval=True)
    st.changed_files = ["pkg/mod.py"]
    st.change_analysis = [
        FileChangeSummary(
            file="pkg/mod.py",
            summary="",
            risk="low",
            intent="FEATURE",
            tags=[],
            entities=[],
            changes=[
                ChangeRecord(entity="foo", type="function", change_type="MODIFY"),
                ChangeRecord(entity="bar", type="function", change_type="ADD"),
            ],
        )
    ]
    rep = build_changed_function_coverage_report(st, p)
    assert rep["changed_function_count"] == 2
    assert rep["changed_functions_any_line_covered_count"] == 1
    assert abs(float(rep["changed_function_coverage_ratio"] or 0) - 0.5) < 1e-9
    assert abs(float(rep["changed_function_coverage_percent"] or 0) - 50.0) < 1e-9
