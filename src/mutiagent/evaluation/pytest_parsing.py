"""从 pytest 终端输出中解析与 Pynguin 实验口径一致的各状态计数。"""

from __future__ import annotations

import re
from typing import Any


def parse_pytest_output(output: str) -> dict[str, Any]:
    """解析 pytest 标准输出/错误合并文本。"""
    summary_pattern = re.compile(
        r"(\d+)\s+"
        r"(passed|failed|error|errors|skipped|deselected|xfailed|xpassed)"
    )
    matches = summary_pattern.findall(output)

    results = {
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "deselected": 0,
        "xfailed": 0,
        "xpassed": 0,
    }

    for count, status in matches:
        n = int(count)
        if status == "passed":
            results["passed"] = n
        elif status == "failed":
            results["failed"] = n
        elif status in ("error", "errors"):
            results["errors"] = n
        elif status == "skipped":
            results["skipped"] = n
        elif status == "deselected":
            results["deselected"] = n
        elif status == "xfailed":
            results["xfailed"] = n
        elif status == "xpassed":
            results["xpassed"] = n

    total = sum(
        results[k]
        for k in (
            "passed",
            "failed",
            "errors",
            "skipped",
            "deselected",
            "xfailed",
            "xpassed",
        )
    )
    pass_rate = (results["passed"] / max(total, 1)) * 100

    return {
        "total_tests": total,
        "passed": results["passed"],
        "failed": results["failed"],
        "errors": results["errors"],
        "skipped": results["skipped"],
        "deselected": results["deselected"],
        "xfailed": results["xfailed"],
        "xpassed": results["xpassed"],
        "pass_rate": round(pass_rate, 2),
        "execution_success": results["failed"] == 0 and results["errors"] == 0,
    }
