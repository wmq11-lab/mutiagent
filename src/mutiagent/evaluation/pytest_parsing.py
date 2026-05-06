"""从 pytest 终端输出中解析与 Pynguin 实验口径一致的各状态计数。"""

from __future__ import annotations

import re
from typing import Any


def parse_pytest_output(output: str) -> dict[str, Any]:
    """解析 pytest 标准输出/错误合并文本。"""
    summary_pattern = re.compile(
        r"(\d+)\s+"
        r"(passed|failed|error|errors|skipped|deselected|xfailed|xpassed)",
        flags=re.IGNORECASE,
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

    def _accumulate(pairs: list[tuple[str, str]]) -> None:
        for count, status in pairs:
            n = int(count)
            s = status.lower()
            if s == "passed":
                results["passed"] = n
            elif s == "failed":
                results["failed"] = n
            elif s in ("error", "errors"):
                results["errors"] = n
            elif s == "skipped":
                results["skipped"] = n
            elif s == "deselected":
                results["deselected"] = n
            elif s == "xfailed":
                results["xfailed"] = n
            elif s == "xpassed":
                results["xpassed"] = n

    _accumulate(matches)

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

    # 仅摘要行里出现「N failed in …」等、但上一段正则未扫到（例如输出被裁剪、格式差异）时，宽松再扫一轮；
    # 取各状态最后一次出现的计数，避免与上一段重复累加。
    if total == 0 and output.strip():
        loose = re.compile(
            r"\b(\d+)\s+(passed|failed|errors?|skipped|deselected|xfailed|xpassed)\b",
            flags=re.IGNORECASE,
        )
        tail = output[-80000:] if len(output) > 80000 else output
        _accumulate(loose.findall(tail))
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
