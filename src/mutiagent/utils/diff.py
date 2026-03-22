from __future__ import annotations

from collections import defaultdict
from typing import Any

from unidiff import PatchSet

from mutiagent.utils.paths import should_ignore_file


def parse_unified_diff(diff_text: str) -> dict[str, Any]:
    """
    返回：
    - changed_files: [path...]
    - hunks_by_file: {path: [{"source_start":..,"source_len":..,"target_start":..,"target_len":..,"added":..,"removed":..}]}
    """
    patch = PatchSet(diff_text.splitlines(True))

    changed_files: list[str] = []
    hunks_by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    added_lines = 0
    removed_lines = 0

    for f in patch:
        path = f.path
        if path is None:
            continue
        if should_ignore_file(path):
            continue
        changed_files.append(path)
        for h in f:
            hunk_added = sum(1 for l in h if l.is_added)
            hunk_removed = sum(1 for l in h if l.is_removed)
            added_lines += hunk_added
            removed_lines += hunk_removed
            hunks_by_file[path].append(
                {
                    "source_start": h.source_start,
                    "source_length": h.source_length,
                    "target_start": h.target_start,
                    "target_length": h.target_length,
                    "added": hunk_added,
                    "removed": hunk_removed,
                }
            )

    return {
        "changed_files": changed_files,
        "hunks_by_file": dict(hunks_by_file),
        "stats": {"files": len(changed_files), "added": added_lines, "removed": removed_lines},
    }
