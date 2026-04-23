from __future__ import annotations

import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

_log = logging.getLogger("mutiagent.db")


def _truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def db_enabled() -> bool:
    """Return whether sqlite persistence is enabled (enabled by default)."""
    raw = os.environ.get("MUTIAGENT_DB_ENABLED", "").strip()
    if not raw:
        return True
    return _truthy(raw)


def resolve_db_path(repo_root: Path) -> Path:
    """Resolve database path from env or default location."""
    raw = os.environ.get("MUTIAGENT_DB_PATH", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return (repo_root / "log" / "mutiagent.sqlite3").resolve()


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS workflow_runs (
            run_id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            status TEXT NOT NULL,
            repo_path TEXT NOT NULL,
            run_eval INTEGER NOT NULL,
            auto_venv INTEGER NOT NULL,
            auto_install_python INTEGER NOT NULL,
            diff_text TEXT NOT NULL,
            error_message TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS workflow_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            step_index INTEGER NOT NULL,
            node TEXT NOT NULL,
            label TEXT NOT NULL,
            created_at TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            file_path TEXT,
            FOREIGN KEY(run_id) REFERENCES workflow_runs(run_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            exit_code INTEGER,
            attempted_fix INTEGER NOT NULL DEFAULT 0,
            first_run_exit_code INTEGER,
            report_dir TEXT,
            payload_json TEXT NOT NULL,
            FOREIGN KEY(run_id) REFERENCES workflow_runs(run_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS generated_test_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            file_path TEXT NOT NULL,
            content TEXT NOT NULL,
            assumptions_json TEXT NOT NULL,
            status TEXT NOT NULL,
            exit_code INTEGER,
            FOREIGN KEY(run_id) REFERENCES workflow_runs(run_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS generated_test_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            suite TEXT NOT NULL,
            classname TEXT NOT NULL,
            case_name TEXT NOT NULL,
            case_time TEXT NOT NULL,
            status TEXT NOT NULL,
            detail TEXT NOT NULL,
            exit_code INTEGER,
            FOREIGN KEY(run_id) REFERENCES workflow_runs(run_id)
        )
        """
    )
    conn.commit()


def _connect(repo_root: Path) -> sqlite3.Connection:
    db_path = resolve_db_path(repo_root)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    _ensure_schema(conn)
    return conn


def start_workflow_run(
    *,
    repo_root: Path,
    repo_path: str,
    diff: str,
    run_eval: bool,
    auto_venv: bool,
    auto_install_python: bool,
) -> str | None:
    if not db_enabled():
        return None
    run_id = str(uuid.uuid4())
    now = datetime.now().isoformat(timespec="seconds")
    try:
        with _connect(repo_root) as conn:
            conn.execute(
                """
                INSERT INTO workflow_runs(
                    run_id, started_at, status, repo_path, run_eval, auto_venv, auto_install_python, diff_text
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    now,
                    "running",
                    repo_path,
                    int(run_eval),
                    int(auto_venv),
                    int(auto_install_python),
                    diff,
                ),
            )
            conn.commit()
        return run_id
    except Exception as exc:  # noqa: BLE001
        _log.warning("初始化 SQLite workflow run 失败: %s", exc)
        return None


def write_workflow_step(
    *,
    repo_root: Path,
    run_id: str | None,
    step_index: int,
    node: str,
    label: str,
    payload: Any,
    file_path: str | None,
) -> None:
    if not run_id:
        return
    now = datetime.now().isoformat(timespec="seconds")
    try:
        with _connect(repo_root) as conn:
            conn.execute(
                """
                INSERT INTO workflow_steps(
                    run_id, step_index, node, label, created_at, payload_json, file_path
                )
                VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    step_index,
                    node,
                    label,
                    now,
                    json.dumps(payload, ensure_ascii=False),
                    file_path,
                ),
            )
            conn.commit()
    except Exception as exc:  # noqa: BLE001
        _log.warning("写入 SQLite workflow step 失败(run_id=%s, step=%s): %s", run_id, step_index, exc)


def finish_workflow_run(
    *,
    repo_root: Path,
    run_id: str | None,
    status: str,
    error_message: str | None = None,
) -> None:
    if not run_id:
        return
    now = datetime.now().isoformat(timespec="seconds")
    try:
        with _connect(repo_root) as conn:
            conn.execute(
                """
                UPDATE workflow_runs
                SET finished_at = ?, status = ?, error_message = ?
                WHERE run_id = ?
                """,
                (now, status, error_message, run_id),
            )
            conn.commit()
    except Exception as exc:  # noqa: BLE001
        _log.warning("更新 SQLite workflow run 状态失败(run_id=%s): %s", run_id, exc)


def write_execution_payload(
    *,
    repo_root: Path,
    run_id: str | None,
    payload: dict[str, Any],
) -> None:
    if not run_id:
        return
    now = datetime.now().isoformat(timespec="seconds")
    try:
        with _connect(repo_root) as conn:
            conn.execute(
                """
                INSERT INTO executions(
                    run_id, created_at, exit_code, attempted_fix, first_run_exit_code, report_dir, payload_json
                )
                VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    now,
                    payload.get("exit_code"),
                    int(bool(payload.get("attempted_fix"))),
                    payload.get("first_run_exit_code"),
                    payload.get("report_dir"),
                    json.dumps(payload, ensure_ascii=False),
                ),
            )
            conn.commit()
    except Exception as exc:  # noqa: BLE001
        _log.warning("写入 SQLite execution 失败(run_id=%s): %s", run_id, exc)


def write_generated_tests(
    *,
    repo_root: Path,
    run_id: str | None,
    generated_tests: list[dict[str, Any]],
    status: str,
    exit_code: int | None,
) -> None:
    """Persist generated test files and status for one workflow run."""
    if not run_id or not generated_tests:
        return
    now = datetime.now().isoformat(timespec="seconds")
    rows: list[tuple[Any, ...]] = []
    for item in generated_tests:
        rows.append(
            (
                run_id,
                now,
                str(item.get("path", "")),
                str(item.get("content", "")),
                json.dumps(item.get("assumptions", []), ensure_ascii=False),
                status,
                exit_code,
            )
        )
    try:
        with _connect(repo_root) as conn:
            conn.executemany(
                """
                INSERT INTO generated_test_files(
                    run_id, created_at, file_path, content, assumptions_json, status, exit_code
                )
                VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            conn.commit()
    except Exception as exc:  # noqa: BLE001
        _log.warning("写入 SQLite generated tests 失败(run_id=%s): %s", run_id, exc)


def write_generated_test_cases(
    *,
    repo_root: Path,
    run_id: str | None,
    junit_cases: list[dict[str, Any]],
    exit_code: int | None,
) -> None:
    """Persist junit testcase rows for one workflow run."""
    if not run_id or not junit_cases:
        return
    now = datetime.now().isoformat(timespec="seconds")
    rows: list[tuple[Any, ...]] = []
    for item in junit_cases:
        rows.append(
            (
                run_id,
                now,
                str(item.get("suite", "")),
                str(item.get("classname", "")),
                str(item.get("name", "")),
                str(item.get("time", "")),
                str(item.get("status", "")),
                str(item.get("detail", "")),
                exit_code,
            )
        )
    try:
        with _connect(repo_root) as conn:
            conn.executemany(
                """
                INSERT INTO generated_test_cases(
                    run_id, created_at, suite, classname, case_name, case_time, status, detail, exit_code
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            conn.commit()
    except Exception as exc:  # noqa: BLE001
        _log.warning("写入 SQLite generated test cases 失败(run_id=%s): %s", run_id, exc)
