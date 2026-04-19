"""应用级日志：将 mutiagent 包内日志写入项目根目录 log/mutiagent.log。"""
from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

_configured = False


def _default_repo_root() -> Path:
    # src/mutiagent/utils/logging_config.py -> parents[3] = 仓库根
    return Path(__file__).resolve().parents[3]


def configure_app_logging(
    repo_root: Path | None = None,
    *,
    reset_log_file: bool | None = None,
) -> Path:
    """
    为 logger ``mutiagent`` 配置 RotatingFileHandler。

    - 默认每次调用会 **清空** ``log/mutiagent.log`` 并重建 handler（用于 API 进程每次启动）。
    - 若需保留历史，启动前设置环境变量 ``MUTIAGENT_LOG_APPEND=1``。
    """
    global _configured
    root = (repo_root or _default_repo_root()).resolve()
    log_dir = root / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "mutiagent.log"

    if reset_log_file is None:
        reset_log_file = os.environ.get("MUTIAGENT_LOG_APPEND", "").strip().lower() not in {
            "1",
            "true",
            "yes",
            "on",
        }

    base = logging.getLogger("mutiagent")
    if _configured:
        for h in list(base.handlers):
            base.removeHandler(h)
            try:
                h.close()
            except Exception:
                pass
        _configured = False

    if reset_log_file and log_path.exists():
        try:
            log_path.unlink()
        except OSError:
            log_path.write_text("", encoding="utf-8")

    base.setLevel(logging.INFO)
    base.propagate = False

    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    fh = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    base.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(logging.WARNING)
    sh.setFormatter(fmt)
    base.addHandler(sh)

    _configured = True
    base.info("mutiagent 日志已初始化，文件: %s（pytest 输出见同文件 ExecutionAgent 段落）", log_path)
    return log_path
