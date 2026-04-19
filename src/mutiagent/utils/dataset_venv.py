"""为每个被测仓库自动创建独立 venv 并安装依赖（可选，由 auto_venv / 环境变量开启）。"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

_FP_REL = ".install_fingerprint"
_VENV_SEG = Path(".mutiagent") / "mutiagent_pytest_venv"

# 参与指纹的文件：变更后触发重装
_FINGERPRINT_FILES = (
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
)


def _venv_python(venv_root: Path) -> Path:
    if sys.platform == "win32":
        return venv_root / "Scripts" / "python.exe"
    return venv_root / "bin" / "python"


def fingerprint(repo: Path) -> str:
    h = hashlib.sha256()
    for rel in _FINGERPRINT_FILES:
        p = repo / rel
        if p.is_file():
            h.update(rel.encode())
            h.update(b"\0")
            h.update(p.read_bytes())
            h.update(b"\n")
    return h.hexdigest()


def _run(
    cmd: list[str],
    *,
    cwd: Path,
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _install_timeout() -> int:
    raw = os.environ.get("MUTIAGENT_VENV_INSTALL_TIMEOUT", "900").strip()
    try:
        return max(60, int(raw))
    except ValueError:
        return 900


def ensure_dataset_venv(repo: Path) -> tuple[str | None, str]:
    """
    在 repo/.mutiagent/mutiagent_pytest_venv 创建或复用 venv，并按指纹安装依赖。

    Returns:
        (python_path, message): 成功时 message 为 reuse / created；失败时 python_path 为 None。
    """
    if not repo.is_dir():
        return None, f"repo_path 不是目录: {repo}"

    timeout = _install_timeout()
    venv_root = (repo / _VENV_SEG).resolve()
    venv_root.parent.mkdir(parents=True, exist_ok=True)

    fp = fingerprint(repo)
    fp_file = venv_root / _FP_REL
    py = _venv_python(venv_root)

    if py.is_file() and fp_file.is_file():
        try:
            if fp_file.read_text(encoding="utf-8", errors="replace").strip() == fp:
                return str(py), "reuse venv (fingerprint match)"
        except OSError:
            pass

    if venv_root.exists():
        shutil.rmtree(venv_root)

    r = _run([sys.executable, "-m", "venv", str(venv_root)], cwd=repo, timeout=180)
    if r.returncode != 0:
        return None, f"python -m venv 失败 (cwd={repo}):\n{(r.stderr or r.stdout or '').strip()}"

    pip = [str(py), "-m", "pip"]
    r = _run(pip + ["install", "--upgrade", "pip"], cwd=repo, timeout=min(300, timeout))
    if r.returncode != 0:
        return None, f"pip install --upgrade pip 失败:\n{(r.stderr or r.stdout or '').strip()}"

    r = _run(pip + ["install", "pytest"], cwd=repo, timeout=min(300, timeout))
    if r.returncode != 0:
        return None, f"pip install pytest 失败:\n{(r.stderr or r.stdout or '').strip()}"

    req = repo / "requirements.txt"
    if req.is_file():
        r = _run(pip + ["install", "-r", str(req)], cwd=repo, timeout=timeout)
        if r.returncode != 0:
            return None, f"pip install -r requirements.txt 失败:\n{(r.stderr or r.stdout or '').strip()}"

    if (repo / "pyproject.toml").is_file() or (repo / "setup.py").is_file():
        r = _run(pip + ["install", "-e", "."], cwd=repo, timeout=timeout)
        if r.returncode != 0:
            return None, f"pip install -e . 失败:\n{(r.stderr or r.stdout or '').strip()}"

    try:
        fp_file.write_text(fp + "\n", encoding="utf-8")
    except OSError as e:
        return None, f"写入 venv 指纹失败: {e}"

    return str(py), "created venv and installed dependencies"
