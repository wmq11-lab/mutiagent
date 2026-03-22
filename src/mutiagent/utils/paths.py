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
