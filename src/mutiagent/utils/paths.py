from __future__ import annotations

IGNORE_DIRS: frozenset[str] = frozenset(
    {
        "dist",
        "build",
        "node_modules",
        ".git",
        "coverage",
    }
)

IGNORE_DIRS_LOWER: frozenset[str] = frozenset(p.lower() for p in IGNORE_DIRS)

IGNORE_EXT: frozenset[str] = frozenset(
    {
        ".map",
        ".min.js",
        ".lock",
    }
)

IGNORE_EXT_LOWER: frozenset[str] = frozenset(e.lower() for e in IGNORE_EXT)


def should_ignore_file(file_path: str) -> bool:
    """按路径段与后缀过滤构建产物、依赖与锁文件等噪声路径。"""
    if not file_path:
        return False
    normalized = file_path.replace("\\", "/").strip("/")
    parts = normalized.split("/")
    if any(p.lower() in IGNORE_DIRS_LOWER for p in parts):
        return True
    lower = normalized.lower()
    for ext in IGNORE_EXT_LOWER:
        if lower.endswith(ext):
            return True
    return False


def is_under_project_tests_tree(rel: str) -> bool:
    """
    是否位于仓库常规 ``tests/`` 树（测试代码与辅助物），不作为「为生产代码生成测试」的目标路径。
    仅判断规范化相对路径是否以 ``tests/`` 开头。
    """
    n = (rel or "").replace("\\", "/").strip().lstrip("/")
    return n.startswith("tests/")


def production_changed_files(changed_files: list[str]) -> list[str]:
    """变更文件中排除 ``tests/`` 子树后的路径（生产/库代码测试目标）。"""
    return [f for f in changed_files if f and not is_under_project_tests_tree(f)]
