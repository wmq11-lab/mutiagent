"""
每次 ExecutionAgent 跑完 pytest 后：
- 向本仓库 ``log/experiment_runs.json`` 追加一条记录（与 Pynguin 风格 JSON 数组项字段对齐）。
- 若工作流在 ``state.debug`` 中带有 ``workflow_steps_dir``（由 ``workflow._execute_workflow`` 注入），
  则在对应目录写入 ``experiment_record.json``（本次 run 快照，与同目录 ``01_*.json``… 步骤归档一致），
  并写入 ``changed_function_coverage.json``：coverage JSON × ``change_analysis`` 中对变更文件的 function/method，
  统计至少有语句被执行的变更函数占比；摘要写入 ``experiment_record.json`` 的 ``changed_function_coverage_ratio`` /
  ``changed_function_coverage_percent``。
- 首次写入 ``experiment_record.json`` 时附带 ``workflow_total_seconds`` / ``workflow_finished_at`` = null；工作流结束时由
  ``merge_workflow_total_time_into_experiment_record`` 合并为真实端到端耗时与时间戳（并保证：即使未跑 pytest 或未生成该文件，
  结束时也会创建或更新同目录 ``experiment_record.json`` 并写入 ``workflow_total_seconds``）。
- 工作流结束时（``graph/workflow._execute_workflow`` 全部步骤完成后）调用 ``merge_workflow_total_time_into_experiment_record``，
  向同目录 ``experiment_record.json`` 合并 ``workflow_total_seconds``、``workflow_finished_at``（并在可能时同步
  ``log/experiment_runs.json`` 中同源 ``run_id`` 的记录）。

环境变量（可选）:
  MUTIAGENT_EXPERIMENT_RUN_LOG   默认 1；0/false 关闭 ``log/experiment_runs.json`` 追加；
                                 但若本次 run 带 ``workflow_steps_dir``（常规工作流），仍会写入对应目录下的
                                 ``experiment_record.json`` 与 ``changed_function_coverage.json``
  MUTIAGENT_EXPERIMENT_COV        默认 1；0 关闭额外 coverage json 子进程
"""

from __future__ import annotations

import ast
import json
import logging
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mutiagent.evaluation.changed_function_coverage import build_changed_function_coverage_report
from mutiagent.evaluation.coverage_json import parse_coverage_json
from mutiagent.evaluation.extended_experiment_metrics import compute_extended_experiment_metrics
from mutiagent.evaluation.pytest_parsing import parse_pytest_output
from mutiagent.graph.state import WorkflowState

_log = logging.getLogger("mutiagent.workflow")

_APP_REPO_ROOT = Path(__file__).resolve().parents[3]

LOG_RELATIVE = Path("log") / "experiment_runs.json"
COVERAGE_STAGING = Path("log") / "last_workflow_coverage.json"
CHANGED_FUNCTION_COVERAGE_JSON_NAME = "changed_function_coverage.json"


def _truthy(name: str, *, default: bool = True) -> bool:
    v = os.environ.get(name, "").strip().lower()
    if not v:
        return default
    if v in {"0", "false", "no", "off"}:
        return False
    if v in {"1", "true", "yes", "on"}:
        return True
    return default


def _path_to_dotted_module(repo: Path, rel: str) -> str:
    p = (repo / rel).resolve()
    no_ext = p.relative_to(repo.resolve()).with_suffix("")
    return str(no_ext).replace("\\", "/").replace("/", ".")


def infer_experiment_module(state: WorkflowState, dataset_repo: Path) -> str | None:
    """
    供实验子进程 ``--cov=<module>`` 与 ``experiment_record.module`` 使用。

    优先与实际变更文件对齐，避免 ``project_profile.import_candidates``（常为入口/侧写）
    盖住 ``typer/core.py`` 这类本轮真正改动的模块，导致覆盖率分母与变更错位。
    """
    raw = state.debug.get("experiment_cov_module")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    for rel in state.changed_files or []:
        if isinstance(rel, str) and rel.endswith(".py"):
            p = dataset_repo / rel
            if p.is_file():
                return _path_to_dotted_module(dataset_repo, rel)
    prof = state.project_profile if isinstance(state.project_profile, dict) else {}
    for c in prof.get("import_candidates") or []:
        if isinstance(c, str) and ":" in c:
            return c.split(":", 1)[0].strip()
    return None


def _count_test_functions_source(src: str) -> int:
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return 0
    n = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            n += 1
    return n


def _syntax_ok_source(src: str) -> bool:
    try:
        ast.parse(src)
        return True
    except SyntaxError:
        return False


def _build_pytest_env_for_dataset(dataset_repo: Path) -> dict[str, str]:
    """与 execution_agent._run_pytest 一致的 PYTHONPATH 策略（精简版）。"""
    env = os.environ.copy()
    pp = [str(dataset_repo)]
    lib = dataset_repo / "lib"
    if lib.is_dir():
        pp.insert(0, str(lib.resolve()))
    inherit = env.get("PYTHONPATH", "").strip()
    if inherit and (os.environ.get("MUTIAGENT_PYTEST_APPEND_PYTHONPATH", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    } or not (lib / "ansible").is_dir()):
        pp.append(inherit)
    env["PYTHONPATH"] = os.pathsep.join(pp)
    return env


def _ensure_pytest_cov(python_exe: str, dataset_repo: Path) -> bool:
    """数据集 venv 历史上只装了 pytest；无 pytest-cov 时 --cov 会失败且不会写出 json。"""
    chk = subprocess.run(
        [python_exe, "-c", "import pytest_cov"],
        cwd=str(dataset_repo),
        capture_output=True,
        text=True,
    )
    if chk.returncode == 0:
        return True
    _log.info("experiment_run_log: 数据集 venv 缺少 pytest-cov，正在 pip install …")
    ins = subprocess.run(
        [python_exe, "-m", "pip", "install", "pytest-cov>=5"],
        cwd=str(dataset_repo),
        capture_output=True,
        text=True,
        timeout=600,
    )
    if ins.returncode != 0:
        _log.warning(
            "experiment_run_log: pip install pytest-cov 失败: %s",
            (ins.stderr or ins.stdout or "")[:800],
        )
        return False
    return True


def _run_coverage_json(
    dataset_repo: Path,
    test_root: Path,
    python_exe: str,
    cov_module: str,
    out_json: Path,
) -> bool:
    if not _ensure_pytest_cov(python_exe, dataset_repo):
        return False
    out_json.parent.mkdir(parents=True, exist_ok=True)
    env = _build_pytest_env_for_dataset(dataset_repo)
    cmd: list[str] = [
        python_exe,
        "-m",
        "pytest",
        str(test_root),
        "-q",
        f"--cov={cov_module}",
        "--cov-branch",
        f"--cov-report=json:{out_json.resolve()}",
    ]
    p = subprocess.run(
        cmd,
        cwd=str(dataset_repo),
        env=env,
        capture_output=True,
        text=True,
    )
    # 与主 run 相同：有失败时 pytest 退出码为 1，但 coverage 仍会写出 json，不应因此丢弃报告。
    if not out_json.is_file():
        _log.warning(
            "experiment_run_log: 未生成 coverage json (exit=%s)。若缺插件，请 pip install pytest-cov。stderr: %s",
            p.returncode,
            (p.stderr or p.stdout or "")[:1200],
        )
        return False
    if p.returncode not in (0, 1, 2, 3, 4, 5):
        # 异常中断（如内部错误、被信号杀死）时文件可能残缺，仍尝试解析
        _log.warning(
            "experiment_run_log: coverage pytest 非典型退出码 %s，仍将尝试解析 %s",
            p.returncode,
            out_json,
        )
    return True


def _zero_coverage() -> dict[str, Any]:
    return {
        "line_coverage": 0.0,
        "branch_coverage": 0.0,
        "covered_lines": 0,
        "total_lines": 0,
    }


def build_experiment_run_record(
    state: WorkflowState,
    dataset_repo: Path,
    *,
    combined_pytest_text: str,
    coverage_data: dict[str, Any] | None,
) -> dict[str, Any]:
    mod = infer_experiment_module(state, dataset_repo) or "unknown"
    exec_p = parse_pytest_output(combined_pytest_text)
    t_count = 0
    syn = True
    for gt in state.generated_tests or []:
        t_count += _count_test_functions_source(gt.content)
        if not _syntax_ok_source(gt.content):
            syn = False
    t_exists = bool(state.generated_tests)

    cov = coverage_data or _zero_coverage()
    return {
        "module": mod,
        "test_file_exists": t_exists,
        "syntax_correct": syn,
        "test_count": t_count,
        "total_tests": int(exec_p.get("total_tests", 0)),
        "passed": int(exec_p.get("passed", 0)),
        "failed": int(exec_p.get("failed", 0)),
        "errors": int(exec_p.get("errors", 0)),
        "skipped": int(exec_p.get("skipped", 0)),
        "deselected": int(exec_p.get("deselected", 0)),
        "xfailed": int(exec_p.get("xfailed", 0)),
        "xpassed": int(exec_p.get("xpassed", 0)),
        "pass_rate": float(exec_p.get("pass_rate", 0.0)),
        "execution_success": bool(exec_p.get("execution_success", False)),
        "line_coverage": float(cov.get("line_coverage", 0.0)),
        "branch_coverage": float(cov.get("branch_coverage", 0.0)),
        "covered_lines": int(cov.get("covered_lines", 0)),
        "total_lines": int(cov.get("total_lines", cov.get("total_statements", 0))),
    }


def _append_json_array_file(path: Path, item: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data: list[Any]
    if path.exists():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            data = raw if isinstance(raw, list) else []
        except (json.JSONDecodeError, OSError):
            data = []
    else:
        data = []
    data.append(item)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_changed_function_coverage_under_workflow_steps(
    state: WorkflowState, report: dict[str, Any]
) -> None:
    """在同一 log/workflow_steps/<stamp>/ 下写入变更函数覆盖率详情。"""
    raw = state.debug.get("workflow_steps_dir") if isinstance(state.debug, dict) else None
    if not raw or not str(raw).strip():
        return
    try:
        dest_dir = Path(str(raw).strip()).resolve()
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / CHANGED_FUNCTION_COVERAGE_JSON_NAME
        dest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _log.info("experiment_run_log: 已写入变更函数覆盖 %s", dest)
    except OSError as e:
        _log.warning("experiment_run_log: 写入 changed_function_coverage 失败（已忽略）: %s", e)


def _write_experiment_record_under_workflow_steps(state: WorkflowState, record: dict[str, Any]) -> None:
    """与本次 run 对应的 log/workflow_steps/<stamp>/ 下写入单条实验快照。"""
    raw = state.debug.get("workflow_steps_dir") if isinstance(state.debug, dict) else None
    if not raw or not str(raw).strip():
        return
    try:
        dest_dir = Path(str(raw).strip()).resolve()
        dest = dest_dir / "experiment_record.json"
        dest_dir.mkdir(parents=True, exist_ok=True)
        payload = dict(record)
        payload["workflow_steps_dir"] = str(dest_dir)
        stamp = state.debug.get("workflow_steps_stamp") if isinstance(state.debug, dict) else None
        if stamp:
            payload["workflow_steps_stamp"] = str(stamp)
        dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _log.info("experiment_run_log: 已写入本次实验记录 %s", dest)
    except OSError as e:
        _log.warning("experiment_run_log: 写入 workflow_steps 下实验记录失败（已忽略）: %s", e)


def _patch_global_experiment_runs_json(run_id: str, patch: dict[str, Any]) -> None:
    """在 log/experiment_runs.json 中按 run_id 合并字段（从最新项向前匹配）。"""
    rid = str(run_id or "").strip()
    if not rid or not patch:
        return
    path = (_APP_REPO_ROOT / LOG_RELATIVE).resolve()
    if not path.is_file():
        return
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        arr = raw if isinstance(raw, list) else []
    except (OSError, json.JSONDecodeError):
        return
    for item in reversed(arr):
        if isinstance(item, dict) and str(item.get("run_id", "")).strip() == rid:
            item.update(patch)
            break
    else:
        return
    try:
        path.write_text(json.dumps(arr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as e:
        _log.warning("experiment_run_log: 更新 experiment_runs.json 耗时字段失败（已忽略）: %s", e)


def merge_workflow_total_time_into_experiment_record(state: WorkflowState) -> None:
    """
    工作流全部步骤结束后调用：写入 workflow_total_seconds（perf_counter 口径）、workflow_finished_at，
    并回写 ``workflow_steps_dir/experiment_record.json``；若存在同源 run_id 的全局 ``experiment_runs.json`` 条目则一并更新。
    若此前未执行 Evaluation / 尚无 ``experiment_record.json``，亦会新建该文件并仅含耗时与可追溯字段，保证端到端时间每次可落盘。
    """
    dbg = state.debug if isinstance(state.debug, dict) else {}
    raw_dir = dbg.get("workflow_steps_dir")
    if not raw_dir or not str(raw_dir).strip():
        return

    patch: dict[str, Any] = {
        "workflow_finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    t0 = dbg.get("_workflow_perf_start")
    if t0 is not None:
        try:
            patch["workflow_total_seconds"] = round(max(0.0, time.perf_counter() - float(t0)), 3)
        except (TypeError, ValueError):
            pass

    wsa = dbg.get("workflow_started_at")
    if isinstance(wsa, str) and wsa.strip():
        patch["workflow_started_at"] = wsa.strip()

    dest = Path(str(raw_dir).strip()).resolve() / "experiment_record.json"
    dest.parent.mkdir(parents=True, exist_ok=True)

    data: dict[str, Any] = {}
    if dest.is_file():
        try:
            loaded = json.loads(dest.read_text(encoding="utf-8"))
            data = loaded if isinstance(loaded, dict) else {}
        except (OSError, json.JSONDecodeError):
            data = {}
    else:
        resolved = Path(str(raw_dir).strip()).resolve()
        data["workflow_steps_dir"] = str(resolved)
        stamp = dbg.get("workflow_steps_stamp")
        if stamp:
            data["workflow_steps_stamp"] = str(stamp)
        rid0 = dbg.get("workflow_run_id")
        if rid0 is not None and str(rid0).strip():
            data["run_id"] = str(rid0).strip()

    data.update(patch)
    try:
        dest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _log.info("experiment_run_log: 已合并工作流总耗时 %s", dest)
    except OSError as e:
        _log.warning("experiment_run_log: 合并 workflow_total_seconds 失败（已忽略）: %s", e)
    rid = dbg.get("workflow_run_id")
    if rid is not None and str(rid).strip():
        slim = {
            k: patch[k]
            for k in ("workflow_total_seconds", "workflow_finished_at", "workflow_started_at")
            if k in patch
        }
        if slim:
            _patch_global_experiment_runs_json(str(rid), slim)


def append_experiment_run_log(
    mutiagent_repo_root: Path,
    state: WorkflowState,
    dataset_repo: Path,
    last_test_dir: Path,
    pytest_stdout: str,
    pytest_stderr: str,
    python_exe: str,
    *,
    pytest_cov_json_path: Path | None = None,
    junit_summary: dict[str, str] | None = None,
    selected_tests: list[str] | None = None,
) -> None:
    if not state.run_eval:
        return
    ws_dir = ""
    if isinstance(state.debug, dict):
        raw = state.debug.get("workflow_steps_dir")
        ws_dir = str(raw).strip() if raw is not None else ""
    global_log = _truthy("MUTIAGENT_EXPERIMENT_RUN_LOG", default=True)
    if not global_log and not ws_dir:
        return
    try:
        combined = (pytest_stdout or "") + "\n" + (pytest_stderr or "")
        coverage_data: dict[str, Any] | None = None
        cov_written: Path | None = None
        if _truthy("MUTIAGENT_EXPERIMENT_COV", default=True) and last_test_dir.is_dir():
            cov_mod = infer_experiment_module(state, dataset_repo)
            if cov_mod:
                out_json = (mutiagent_repo_root / COVERAGE_STAGING).resolve()
                ok = _run_coverage_json(
                    dataset_repo, last_test_dir, python_exe, cov_mod, out_json
                )
                if ok:
                    coverage_data = parse_coverage_json(str(out_json))
                    cov_written = out_json.resolve()
        record = build_experiment_run_record(
            state,
            dataset_repo,
            combined_pytest_text=combined,
            coverage_data=coverage_data,
        )
        rid = state.debug.get("workflow_run_id")
        if rid is not None and str(rid).strip() != "":
            record["run_id"] = str(rid)

        cf_report = build_changed_function_coverage_report(state, cov_written)
        cr = cf_report.get("changed_function_coverage_ratio")
        cp = cf_report.get("changed_function_coverage_percent")
        record["changed_function_coverage_ratio"] = cr
        record["changed_function_coverage_percent"] = cp

        ext = compute_extended_experiment_metrics(
            state,
            dataset_repo.resolve(),
            cov_json_primary=pytest_cov_json_path,
            cov_json_fallback=cov_written,
            combined_pytest_output=combined,
            selected_tests=list(selected_tests) if selected_tests else None,
            junit_summary=dict(junit_summary or {}),
            python_exe=python_exe,
            mutiagent_repo_root=mutiagent_repo_root.resolve(),
            generated_test_function_count=int(record.get("test_count", 0) or 0),
        )
        record.update(ext)

        wsa = state.debug.get("workflow_started_at") if isinstance(state.debug, dict) else None
        if isinstance(wsa, str) and wsa.strip():
            record["workflow_started_at"] = wsa.strip()

        record["workflow_total_seconds"] = None
        record["workflow_finished_at"] = None

        _write_experiment_record_under_workflow_steps(state, record)

        cf_out = dict(cf_report)
        if rid is not None and str(rid).strip() != "":
            cf_out["run_id"] = str(rid)
        stamp = state.debug.get("workflow_steps_stamp") if isinstance(state.debug, dict) else None
        if stamp:
            cf_out["workflow_steps_stamp"] = str(stamp)
        _write_changed_function_coverage_under_workflow_steps(state, cf_out)
        if global_log:
            out_path = mutiagent_repo_root / LOG_RELATIVE
            _append_json_array_file(out_path, record)
            _log.info("ExecutionAgent: 已追加实验记录到 %s (module=%s)", out_path, record.get("module"))
        elif ws_dir:
            _log.info(
                "experiment_run_log: 全局 experiment_runs.json 已关闭，已仅写入 workflow_steps/experiment_record.json (module=%s)",
                record.get("module"),
            )
    except Exception as e:  # noqa: BLE001
        _log.warning("ExecutionAgent: 写入实验记录失败（已忽略）: %s", e)
