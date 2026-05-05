from __future__ import annotations

import json
import time
from pathlib import Path

from mutiagent.evaluation.experiment_run_log import infer_experiment_module
from mutiagent.evaluation.experiment_run_log import merge_workflow_total_time_into_experiment_record
from mutiagent.evaluation.experiment_run_log import _write_experiment_record_under_workflow_steps
from mutiagent.graph.state import WorkflowState


def test_experiment_record_written_under_workflow_steps_dir(tmp_path: Path) -> None:
    step_dir = tmp_path / "log" / "workflow_steps" / "20990101_120000"
    step_dir.mkdir(parents=True)
    state = WorkflowState(
        repo_path="/tmp/repo",
        diff="",
        debug={
            "workflow_steps_dir": str(step_dir),
            "workflow_steps_stamp": "20990101_120000",
        },
    )
    _write_experiment_record_under_workflow_steps(
        state,
        {"module": "pkg.mod", "test_count": 3, "run_id": "rid-1"},
    )
    out = step_dir / "experiment_record.json"
    assert out.is_file()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["module"] == "pkg.mod"
    assert data["run_id"] == "rid-1"
    assert data["workflow_steps_stamp"] == "20990101_120000"
    assert data["workflow_steps_dir"] == str(step_dir.resolve())


def test_merge_creates_experiment_record_with_workflow_seconds_when_missing(tmp_path: Path) -> None:
    """未先写出 Execution 快照时，工作流结束合并仍生成 experiment_record 并写入 workflow_total_seconds。"""
    step_dir = tmp_path / "log" / "workflow_steps" / "20990101_120000"
    step_dir.mkdir(parents=True)
    rid = "test-run-merge-uuid"
    state = WorkflowState(
        repo_path="/tmp/repo",
        diff="diff --git ...",
        debug={
            "workflow_steps_dir": str(step_dir),
            "workflow_steps_stamp": "20990101_120000",
            "workflow_run_id": rid,
            "workflow_started_at": "2099-01-01T00:00:00+00:00",
            "_workflow_perf_start": time.perf_counter() - 3.05,
        },
    )
    merge_workflow_total_time_into_experiment_record(state)
    out = step_dir / "experiment_record.json"
    assert out.is_file()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["run_id"] == rid
    assert data["workflow_steps_stamp"] == "20990101_120000"
    assert data["workflow_started_at"] == "2099-01-01T00:00:00+00:00"
    assert "workflow_finished_at" in data
    assert isinstance(data.get("workflow_total_seconds"), (int, float))
    assert data["workflow_total_seconds"] >= 3.0


def test_infer_module_prefers_existing_changed_py_over_import_candidates(tmp_path: Path) -> None:
    (tmp_path / "typer").mkdir(parents=True)
    (tmp_path / "typer" / "core.py").write_text("x = 1\n", encoding="utf-8")
    state = WorkflowState(
        repo_path=str(tmp_path),
        diff="",
        changed_files=["typer/core.py"],
        project_profile={"import_candidates": ["typer.utils:unused"]},
    )
    assert infer_experiment_module(state, tmp_path) == "typer.core"


def test_infer_module_falls_back_to_import_candidates_when_changed_missing(tmp_path: Path) -> None:
    state = WorkflowState(
        repo_path=str(tmp_path),
        diff="",
        changed_files=["typer/nope.py"],
        project_profile={"import_candidates": ["typer.utils:main"]},
    )
    assert infer_experiment_module(state, tmp_path) == "typer.utils"


def test_infer_module_debug_override_wins(tmp_path: Path) -> None:
    (tmp_path / "typer").mkdir(parents=True)
    (tmp_path / "typer" / "core.py").write_text("pass\n", encoding="utf-8")
    state = WorkflowState(
        repo_path=str(tmp_path),
        diff="",
        changed_files=["typer/core.py"],
        project_profile={"import_candidates": ["pkg.other:x"]},
        debug={"experiment_cov_module": "explicit.pkg"},
    )
    assert infer_experiment_module(state, tmp_path) == "explicit.pkg"
