from __future__ import annotations

import json
import tempfile
from pathlib import Path

from mutiagent.graph.state import EvalSummary, WorkflowState
from mutiagent.nodes.evaluation_agent import _coverage_from_report_dir, _extract_coverage, evaluation_agent


def test_extract_coverage_parses_term_total() -> None:
    out = (
        ".......                                                                [100%]\n"
        "Name                      Stmts   Miss  Cover\n"
        "---------------------------------------------\n"
        "pkg/mod.py                  10      1    90%\n"
        "---------------------------------------------\n"
        "TOTAL                       10      1    90%\n"
    )
    assert _extract_coverage(out) == 0.90


def test_coverage_from_report_dir_json() -> None:
    totals = {
        "covered_lines": 9,
        "num_statements": 10,
        "covered_branches": 0,
        "num_branches": 0,
    }
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "coverage.json"
        p.write_text(json.dumps({"totals": totals}), encoding="utf-8")
        assert abs(float(_coverage_from_report_dir(td) or 0.0) - 0.90) < 1e-9


def test_evaluation_fills_coverage_from_json_when_stdout_missing_total() -> None:
    with tempfile.TemporaryDirectory() as td:
        rd = Path(td)
        (rd / "coverage.json").write_text(
            json.dumps(
                {
                    "totals": {
                        "covered_lines": 5,
                        "num_statements": 10,
                        "covered_branches": 0,
                        "num_branches": 1,
                    }
                }
            ),
            encoding="utf-8",
        )
        state = WorkflowState(repo_path="/tmp/r", diff="", run_eval=True)
        state.execution = {
            "ran": True,
            "exit_code": 0,
            "stdout": "no total line here\n",
            "stderr": "",
            "report_dir": str(rd),
            "junit_summary": {"tests": "0", "failures": "0", "errors": "0", "skipped": "0", "time": "0"},
            "junit_cases": [],
        }
        evaluation_agent(state)
        assert state.evaluation is not None
        assert isinstance(state.evaluation, EvalSummary)
        assert state.evaluation.coverage == 0.5
        assert state.evaluation.metric_flags.get("pr_f1_redundancy_meaningful") is False
        assert state.evaluation.metric_flags.get("test_reduction_meaningful") is False
        assert state.evaluation.metric_flags.get("time_reduction_meaningful") is False
