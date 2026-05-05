"""与「是否在目标仓库内创建 venv 并装依赖」相关的统一判定，供 ProjectProbe / Execution 共用。"""

from __future__ import annotations

import os
from typing import Any


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def effective_auto_venv(state: Any) -> bool:
    """
    是否启用「仓库内 .mutiagent/mutiagent_pytest_venv + pip 装依赖」。

    关闭：环境变量 MUTIAGENT_DISABLE_AUTO_VENV=1 或 MUTIAGENT_NO_AUTO_VENV=1（与后者等价）。
    打开：state.auto_venv 为 True，或 MUTIAGENT_AUTO_VENV=1（显式开，便于脚本）。
    """
    if _env_truthy("MUTIAGENT_DISABLE_AUTO_VENV") or _env_truthy("MUTIAGENT_NO_AUTO_VENV"):
        return False
    if bool(getattr(state, "auto_venv", False)):
        return True
    if _env_truthy("MUTIAGENT_AUTO_VENV"):
        return True
    return False
