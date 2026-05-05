"""从 unified diff × coverage.py JSON 计算「变更 + 号行」被执行的比例（Recall 语义）。"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _norm_rel(p: str) -> str:
    return (p or "").strip().replace("\\", "/")


def _iter_git_chunks(diff_text: str) -> list[tuple[str, str]]:
    """返回 (normalized b_path, chunk_text) 列表。"""
    if not (diff_text or "").strip():
        return []
    parts = re.split(r"(?=^diff --git )", diff_text, flags=re.MULTILINE)
    out: list[tuple[str, str]] = []
    for part in parts:
        if not part.strip():
            continue
        first = part.splitlines()[0] if part else ""
        m = re.match(r"^diff --git a/(.+?) b/(.+?)\s*$", first)
        if not m:
            continue
        b_path = _norm_rel(m.group(2))
        out.append((b_path, part))
    return out


def _plus_line_numbers_from_chunk(chunk: str) -> list[int]:
    """单文件 diff 片段内，new 一侧 `+` 行（非 +++）在目标文件上的行号。"""
    plus_line_nums: list[int] = []
    hunk = re.compile(r"@@\s*-\d+(?:,\d+)?\s*\+(\d+)(?:,(\d+))?\s*@@")
    for m in hunk.finditer(chunk):
        new_start = int(m.group(1))
        line_start = m.end() + 1 if m.end() < len(chunk) and chunk[m.end() : m.end() + 1] == "\n" else m.end()
        if m.end() < len(chunk) and chunk[m.end() : m.end() + 1] != "\n":
            line_start = m.end()
        nxt = hunk.search(chunk, line_start)
        block = chunk[line_start : nxt.start() if nxt else len(chunk)]
        cur = new_start
        for line in block.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                plus_line_nums.append(cur)
                cur += 1
            elif not line.startswith("-"):
                cur += 1
    return plus_line_nums


def _lookup_fd(files_map: dict[str, Any], rel: str) -> dict[str, Any] | None:
    rel_n = _norm_rel(rel)
    if rel_n in files_map and isinstance(files_map[rel_n], dict):
        return files_map[rel_n]
    for k, v in files_map.items():
        if not isinstance(k, str) or not isinstance(v, dict):
            continue
        if _norm_rel(k) == rel_n:
            return v
        kn = _norm_rel(k)
        if kn.endswith("/" + rel_n.split("/")[-1]) or kn.endswith(rel_n.split("/")[-1]):
            return v
    return None


def _executed_lines(fd: dict[str, Any]) -> set[int]:
    ex: set[int] = set()
    for el in fd.get("executed_lines") or fd.get("covered_lines") or []:
        if isinstance(el, int):
            ex.add(el)
    if not ex and isinstance(fd.get("line_data"), list):
        for i, row in enumerate(fd["line_data"], 1):
            if isinstance(row, dict) and row.get("hits", 0) > 0:
                ex.add(i)
    return ex


def change_line_coverage_from_diff_and_cov_paths(
    diff_text: str,
    cov_path: str | Path,
    *,
    preferred_rels: list[str] | None = None,
) -> dict[str, Any]:
    """
    在 unified diff 中聚合 ``preferred_rels`` 所指文件（或未指定则处理所有 chunk）的变更 + 行与 coverage.json 对齐。

    返回::
        recall_frac: 0~1（covered_plus / change_plus），无变更 + 行则为 None
        change_plus_lines, covered_plus_lines
    """
    p = Path(cov_path)
    if not p.is_file():
        return {"recall_frac": None, "change_plus_lines": 0, "covered_plus_lines": 0, "note": "coverage.json 不存在"}
    try:
        cov = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"recall_frac": None, "change_plus_lines": 0, "covered_plus_lines": 0, "note": "coverage.json 无法解析"}

    file_map = cov.get("files")
    if not isinstance(file_map, dict) or not file_map:
        return {"recall_frac": None, "change_plus_lines": 0, "covered_plus_lines": 0, "note": "coverage 无 files"}

    targets = [_norm_rel(x) for x in (preferred_rels or []) if str(x).strip()]
    chunks = _iter_git_chunks(diff_text)
    if not chunks:
        return {"recall_frac": None, "change_plus_lines": 0, "covered_plus_lines": 0, "note": "diff 无 diff --git 块"}

    def use_chunk(b_path: str) -> bool:
        if not targets:
            return True
        if b_path in targets:
            return True
        last = b_path.split("/")[-1]
        return any(t.split("/")[-1] == last for t in targets)

    total_plus = 0
    total_hit = 0
    used_files: list[str] = []
    for b_path, chunk in chunks:
        if not use_chunk(b_path):
            continue
        nums = _plus_line_numbers_from_chunk(chunk)
        if not nums:
            continue
        fd = _lookup_fd(file_map, b_path)
        if fd is None and targets:
            for t in targets:
                fd = _lookup_fd(file_map, t)
                if fd is not None:
                    break
        if fd is None:
            continue
        exe = _executed_lines(fd)
        hit = sum(1 for ln in nums if ln in exe)
        total_plus += len(nums)
        total_hit += hit
        used_files.append(b_path)

    if total_plus <= 0:
        return {
            "recall_frac": None,
            "change_plus_lines": 0,
            "covered_plus_lines": 0,
            "note": "未解析到变更 + 号行或未匹配 coverage 文件键",
        }

    frac = float(total_hit) / float(total_plus)
    return {
        "recall_frac": round(frac, 6),
        "change_plus_lines": total_plus,
        "covered_plus_lines": total_hit,
        "covered_files": used_files,
    }
