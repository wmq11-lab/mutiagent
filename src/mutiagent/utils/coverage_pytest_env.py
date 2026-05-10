"""为 pytest-cov 隔离 coverage 数据文件，避免与仓库内陈旧 .coverage 合并报错。"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping


def pytest_env_with_isolated_coverage(
    base_env: Mapping[str, str],
    *,
    data_dir: Path,
) -> dict[str, str]:
    """
    将 ``COVERAGE_FILE`` 指到 ``data_dir`` 下，并删除该目录内既有 ``.coverage*``，
    防止 coverage 在 ``combine()`` 时把本次 ``--cov-branch`` 数据与仓库 cwd 里
    旧版「仅语句」并行片段混在一起，触发
    ``DataError: Can't combine statement coverage data with branch data``。
    """
    d = data_dir.resolve()
    d.mkdir(parents=True, exist_ok=True)
    for p in d.iterdir():
        name = p.name
        if name == ".coverage" or name.startswith(".coverage."):
            try:
                p.unlink()
            except OSError:
                pass
    out = dict(base_env)
    out["COVERAGE_FILE"] = str(d / ".coverage")
    # 避免子进程继承到外层已设的歧义路径
    for k in ("COVERAGE_PROCESS_START",):
        out.pop(k, None)
    return out
