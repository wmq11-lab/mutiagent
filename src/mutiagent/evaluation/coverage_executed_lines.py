"""从 coverage.py JSON 单个 file 节点聚合「已执行行号」集合（含 functions/classes 子树）。"""

from __future__ import annotations

from typing import Any


def executed_lines_from_file_block(fd: dict[str, Any]) -> set[int]:
    """
    合并 file 块顶层与嵌套 ``functions`` / ``classes`` 下的 ``executed_lines`` / ``covered_lines``。
    若仍为空且仅顶层存在 ``line_data``，则按行号回落（与 coverage 整文件粒度一致；子块上的 line_data 不用）。
    """
    acc: set[int] = set()

    def walk(block: dict[str, Any]) -> None:
        for el in block.get("executed_lines") or block.get("covered_lines") or []:
            if isinstance(el, int):
                acc.add(el)
        for nest in ("functions", "classes"):
            sub = block.get(nest)
            if not isinstance(sub, dict):
                continue
            for v in sub.values():
                if isinstance(v, dict):
                    walk(v)

    walk(fd)
    if not acc and isinstance(fd.get("line_data"), list):
        for i, row in enumerate(fd["line_data"], 1):
            if isinstance(row, dict) and row.get("hits", 0) > 0:
                acc.add(i)
    return acc
