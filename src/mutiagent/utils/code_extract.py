from __future__ import annotations

from pathlib import Path
from typing import Any


def read_file_snippet(path: str, *, max_lines: int = 200) -> str:
    p = Path(path)
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except Exception:
        return ""
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[:max_lines] + ["# ... truncated ..."])


def extract_context_by_hunks(
    repo_path: str, hunks_by_file: dict[str, Any], *, per_file_max_lines: int = 220
) -> dict[str, str]:
    """
    根据 diff hunk 行范围，从目标仓库抽取上下文片段（MVP：抽取文件头+若干相关行附近窗口）。
    """
    root = Path(repo_path)
    out: dict[str, str] = {}
    for rel, hunks in (hunks_by_file or {}).items():
        fp = root / rel
        if not fp.exists():
            continue
        try:
            lines = fp.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue

        windows: list[tuple[int, int]] = []
        for h in hunks:
            start = max(1, int(h.get("target_start", 1)) - 25)
            end = min(
                len(lines),
                int(h.get("target_start", 1)) + int(h.get("target_length", 1)) + 25,
            )
            windows.append((start, end))

        merged: list[tuple[int, int]] = []
        for a, b in sorted(windows):
            if not merged or a > merged[-1][1] + 1:
                merged.append((a, b))
            else:
                merged[-1] = (merged[-1][0], max(merged[-1][1], b))

        snippet_lines: list[str] = []
        head = lines[: min(60, len(lines))]
        snippet_lines.append("# --- file head ---")
        snippet_lines.extend(head)
        snippet_lines.append("# --- hunk contexts ---")

        for a, b in merged:
            snippet_lines.append(f"# --- lines {a}-{b} ---")
            snippet_lines.extend(lines[a - 1 : b])

        if len(snippet_lines) > per_file_max_lines:
            snippet_lines = snippet_lines[:per_file_max_lines] + ["# ... truncated ..."]

        out[rel] = "\n".join(snippet_lines)
    return out
