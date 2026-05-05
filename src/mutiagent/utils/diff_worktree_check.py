"""
检查 unified diff 中的目标路径与本地 repo 工作区是否一致，避免 diff 来自已合入版本、
而工作区未 pull/未打补丁时，下游仍按 diff 路径生成 import 导致错路径。

- 对「修改 / 重命名」类 hunk：期望工作区已存在对应文件；不存在则视为不匹配（建议先同步或应用补丁）。
- 对「纯新增」类：目标文件尚不存在属正常（未 apply）；仅作提示。
- 对「删除」类：若工作区仍存在该文件，说明删除未落地；作弱提示。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from unidiff import PatchSet

from mutiagent.utils.paths import should_ignore_file


def check_diff_worktree_consistency(repo: Path, diff_text: str) -> dict[str, Any]:
    """
    Returns:
      - ok: bool — 无「修改/重命名目标」类路径缺失（可安全认为与「已合入」状态一致）
      - modified_paths_missing_in_worktree: 这些路径在 diff 中为修改/重命名目标，但磁盘上无该文件
      - added_paths_not_yet_in_worktree: diff 为新增文件，工作区尚无（未打补丁时正常）
      - removed_paths_still_in_worktree: diff 为删除，但文件仍在
      - recommendation_zh: 给人看的短句
    """
    out: dict[str, Any] = {
        "ok": True,
        "repo_path": str(repo.resolve()) if repo.exists() else "",
        "files_in_diff": 0,
        "modified_paths_missing_in_worktree": [],
        "added_paths_not_yet_in_worktree": [],
        "removed_paths_still_in_worktree": [],
        "recommendation_zh": "",
    }
    if not repo.is_dir():
        out["ok"] = False
        out["recommendation_zh"] = "repo_path 不是有效目录，无法对照 diff。"
        return out
    if not (diff_text or "").strip():
        out["recommendation_zh"] = "diff 为空，跳过与仓库对照。"
        return out

    repo_r = repo.resolve()
    try:
        patch = PatchSet(diff_text.splitlines(True))
    except Exception as e:  # noqa: BLE001
        out["ok"] = False
        out["recommendation_zh"] = f"无法解析 diff（{e!s}），跳过与仓库路径对照。"
        return out

    mod_miss: list[str] = []
    add_absent: list[str] = []
    rem_still: list[str] = []
    n = 0
    for f in patch:
        path = f.path
        if path is None or should_ignore_file(str(path)):
            continue
        n += 1
        rel = str(path).replace("\\", "/").strip()
        if ".." in rel.split("/"):
            continue
        full = (repo / rel).resolve()
        try:
            full.relative_to(repo_r)
        except ValueError:
            continue
        exists = full.is_file()
        if f.is_modified_file or f.is_rename:
            if not exists:
                mod_miss.append(rel)
        elif f.is_added_file:
            if not exists:
                add_absent.append(rel)
        elif f.is_removed_file and exists:
            rem_still.append(rel)

    out["files_in_diff"] = n
    out["modified_paths_missing_in_worktree"] = mod_miss
    out["added_paths_not_yet_in_worktree"] = add_absent
    out["removed_paths_still_in_worktree"] = rem_still
    out["ok"] = len(mod_miss) == 0

    if mod_miss:
        out["recommendation_zh"] = (
            "以下路径在 diff 中为「修改/重命名」目标，但当前工作区不存在对应文件："
            + ", ".join(mod_miss[:12])
            + (" …" if len(mod_miss) > 12 else "")
            + "。请先在仓库中 git pull/合并/应用与 diff 一致后再分析，或换成与当前工作区一致的 diff。"
        )
    elif add_absent and not rem_still:
        out["recommendation_zh"] = (
            f"有 {len(add_absent)} 个在 diff 中为「新增」的文件，工作区尚不存在"
            "（未打补丁时属正常）。若你期望以「已合入」状态分析，请先应用该 diff。"
        )
    elif rem_still:
        out["recommendation_zh"] = (
            f"有 {len(rem_still)} 个在 diff 中为「删除」的文件，工作区仍存在；"
            "若与预期不符，请同步工作区或检查 diff 来源。"
        )
    else:
        out["recommendation_zh"] = "diff 中的修改/重命名类路径均在工作区存在，与「已合入」状态一致。"

    return out
