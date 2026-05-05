"""解析 coverage.py 的 JSON 报告（与 collect_experiment_metrics 口径一致）。"""

from __future__ import annotations

import json
import os
from typing import Any


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
    br = nbr or 1
    return {
        "line_coverage": float(cl) / float(stm) * 100.0,
        "branch_coverage": float(cbr) / float(br) * 100.0,
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
        stm = int(totals.get("num_statements") or 0) or 1
        br = int(totals.get("num_branches") or 0) or 1
        nstmt = int(totals.get("num_statements", 0))
        return {
            "line_coverage": float(totals.get("covered_lines", 0)) / stm * 100.0,
            "branch_coverage": float(totals.get("covered_branches", 0)) / br * 100.0,
            "covered_lines": int(totals.get("covered_lines", 0)),
            "total_statements": nstmt,
            "total_lines": nstmt,
        }
    from_files = _aggregate_from_files(data)
    if from_files is not None:
        return from_files
    summ = data.get("summary", {})
    if isinstance(summ, dict) and summ:
        cov_pct = 0.0
        n_files = 0
        for _fp, s in summ.items():
            if isinstance(s, dict) and "percent_covered" in s:
                cov_pct += float(s["percent_covered"])
                n_files += 1
        if n_files:
            return {
                "line_coverage": cov_pct / n_files,
                "branch_coverage": 0.0,
                "covered_lines": 0,
                "total_statements": 0,
                "total_lines": 0,
            }
    return {}
