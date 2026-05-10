"""解析 coverage.py 的 JSON 报告（与 collect_experiment_metrics 口径一致）。"""

from __future__ import annotations

import json
import os
from typing import Any


def _total_num_branches(data: dict[str, Any]) -> int:
    totals = data.get("totals")
    if isinstance(totals, dict) and totals:
        return int(totals.get("num_branches") or 0)
    n = 0
    fm = data.get("files")
    if isinstance(fm, dict):
        for fd in fm.values():
            if isinstance(fd, dict):
                s = fd.get("summary")
                if isinstance(s, dict):
                    n += int(s.get("num_branches", 0) or 0)
    return n


def _branch_tracking_disabled(data: dict[str, Any]) -> bool:
    meta = data.get("meta")
    return isinstance(meta, dict) and meta.get("branch_coverage") is False


def _finalize_branch_coverage(data: dict[str, Any], out: dict[str, Any]) -> dict[str, Any]:
    """未开启分支跟踪且报告中无任何分支计数时，避免将 branch_coverage 误标为 0%。包含 meta 且 branch_coverage 为 false、全文件 num_branches 之和为 0 时改为 ``None``。"""
    if _branch_tracking_disabled(data) and _total_num_branches(data) == 0:
        out["branch_coverage"] = None
    return out


def _aggregate_from_files(data: dict[str, Any]) -> dict[str, Any] | None:
    file_map = data.get("files")
    if not isinstance(file_map, dict) or not file_map:
        return None
    cl = nstmt = 0
    cbr = nbr = 0
    for _fp, fd in file_map.items():
        if not isinstance(fd, dict):
            continue
        summ = fd.get("summary")
        if not isinstance(summ, dict):
            continue
        cl += int(summ.get("covered_lines", 0) or 0)
        nstmt += int(summ.get("num_statements", 0) or 0)
        cbr += int(summ.get("covered_branches", 0) or 0)
        nbr += int(summ.get("num_branches", 0) or 0)
    if nstmt == 0 and nbr == 0:
        return None
    stm = nstmt or 1
    if nbr > 0:
        br_cov = float(cbr) / float(nbr) * 100.0
    else:
        br_cov = 0.0
    return {
        "line_coverage": float(cl) / float(stm) * 100.0,
        "branch_coverage": br_cov,
        "covered_lines": cl,
        "total_statements": nstmt,
        "total_lines": nstmt,
    }


def parse_coverage_json(path: str) -> dict[str, Any]:
    """解析 coverage 工具产出的 JSON（支持 totals / summary / 仅 files 三种常见结构）。"""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    totals = data.get("totals")
    if isinstance(totals, dict) and totals:
        nstmt_raw = int(totals.get("num_statements") or 0)
        stm = nstmt_raw or 1
        nbr_raw = int(totals.get("num_branches") or 0)
        if nbr_raw > 0:
            br = nbr_raw
            branch_cov = float(totals.get("covered_branches", 0)) / float(br) * 100.0
        else:
            branch_cov = 0.0
        nstmt = int(totals.get("num_statements", 0))
        out = {
            "line_coverage": float(totals.get("covered_lines", 0)) / stm * 100.0,
            "branch_coverage": branch_cov,
            "covered_lines": int(totals.get("covered_lines", 0)),
            "total_statements": nstmt,
            "total_lines": nstmt,
        }
        return _finalize_branch_coverage(data, out)
    from_files = _aggregate_from_files(data)
    if from_files is not None:
        return _finalize_branch_coverage(data, from_files)
    summ = data.get("summary", {})
    if isinstance(summ, dict) and summ:
        cov_pct = 0.0
        n_files = 0
        for _fp, s in summ.items():
            if isinstance(s, dict) and "percent_covered" in s:
                cov_pct += float(s["percent_covered"])
                n_files += 1
        if n_files:
            out = {
                "line_coverage": cov_pct / n_files,
                "branch_coverage": 0.0,
                "covered_lines": 0,
                "total_statements": 0,
                "total_lines": 0,
            }
            return _finalize_branch_coverage(data, out)
    return {}
