"""为每个被测仓库自动创建独立 venv 并安装依赖（可选，由 auto_venv / 环境变量开启）。"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from mutiagent.utils.pip_infer import infer_enabled

_FP_REL = ".install_fingerprint"
_VENV_SEG = Path(".mutiagent") / "mutiagent_pytest_venv"

# 参与指纹的文件：变更后触发重装
_FINGERPRINT_FILES = (
    "requirements.txt",
    "bugsinpy_requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "bugsinpy_bug.info",
    ".mutiagent/mutiagent_inferred_pip.txt",
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


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _read_bugsinpy_python_version(repo: Path) -> str | None:
    info = repo / "bugsinpy_bug.info"
    if not info.is_file():
        return None
    try:
        text = info.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.search(r'^\s*python_version\s*=\s*"([^"]+)"\s*$', text, flags=re.MULTILINE)
    if not m:
        return None
    v = m.group(1).strip()
    return v or None


def _resolve_venv_seed_python(
    repo: Path, *, auto_install_python: bool = False
) -> tuple[str | None, str | None]:
    """
    选择用于创建 venv 的解释器：
    - 若存在 bugsinpy_bug.info 的 python_version，优先匹配该版本；
    - 否则回退到当前进程解释器。
    """
    required = _read_bugsinpy_python_version(repo)
    if not required:
        return sys.executable, None

    parts = required.split(".")
    major_minor = ".".join(parts[:2]) if len(parts) >= 2 else required
    candidates = [f"python{required}", f"python{major_minor}", required, major_minor]

    # 显式加入 pyenv shim 常见命名，便于 PATH 可见时命中。
    if major_minor and not major_minor.startswith("python"):
        candidates.append(f"python{major_minor}m")

    for name in candidates:
        ex = shutil.which(name)
        if ex:
            return ex, None

    if auto_install_python or _env_truthy("MUTIAGENT_VENV_AUTO_INSTALL_PYTHON"):
        errs: list[str] = []
        ok, conda_python, msg = _try_install_python_with_conda(required)
        if ok and conda_python:
            return conda_python, None
        if msg:
            errs.append(msg)

        if errs:
            return None, "；\n".join(errs)

    # 最后允许用户显式覆盖；保持与 execution_agent 一致的优先级风格。
    forced = os.environ.get("MUTIAGENT_VENV_PYTHON", "").strip()
    if forced:
        return forced, None

    return (
        None,
        f"未找到项目要求的 Python {required} 解释器。请安装后重试，"
        f"或设置 MUTIAGENT_VENV_PYTHON 指向可用解释器。",
    )


def _try_install_python_with_pyenv(version: str) -> tuple[bool, str | None]:
    # 保留该函数以兼容旧测试/引用；当前自动安装路径已切换为 conda 优先且不再调用 pyenv。
    pyenv = shutil.which("pyenv")
    if not pyenv:
        return (
            False,
            "未找到 pyenv，无法自动安装 Python。请先安装 pyenv，或关闭 "
            "MUTIAGENT_VENV_AUTO_INSTALL_PYTHON 并手动准备解释器。",
        )
    timeout = max(600, _install_timeout())
    r = _run([pyenv, "install", "-s", version], cwd=Path.cwd(), timeout=timeout)
    if r.returncode != 0:
        return (
            False,
            f"pyenv install -s {version} 失败:\n{(r.stderr or r.stdout or '').strip()}",
        )
    return True, None


def _try_install_python_with_conda(version: str) -> tuple[bool, str | None, str | None]:
    conda = shutil.which("conda")
    if not conda:
        return (
            False,
            None,
            "未找到 conda，无法自动创建 conda 环境安装 Python。",
        )

    env_name = f"mutiagent-py{version.replace('.', '')}"
    timeout = max(600, _install_timeout())
    parts = version.split(".")
    specs = [version]
    if len(parts) >= 2:
        specs.append(f"{parts[0]}.{parts[1]}.*")
    errs: list[str] = []
    ok = False
    for spec in specs:
        try:
            r = _run(
                [conda, "create", "-n", env_name, "-c", "conda-forge", f"python={spec}", "-y"],
                cwd=Path.cwd(),
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as e:
            errs.append(f"conda create python={spec} 超时: {e}")
            continue
        if r.returncode == 0:
            ok = True
            break
        errs.append(
            f"conda create -n {env_name} -c conda-forge python={spec} -y 失败:\n"
            f"{(r.stderr or r.stdout or '').strip()}"
        )
    if not ok:
        return False, None, "；\n".join(errs)

    r = _run(
        [conda, "run", "-n", env_name, "python", "-c", "import sys; print(sys.executable)"],
        cwd=Path.cwd(),
        timeout=120,
    )
    if r.returncode != 0:
        return (
            False,
            None,
            f"conda 环境 {env_name} 已创建，但解析解释器路径失败:\n{(r.stderr or r.stdout or '').strip()}",
        )
    py = (r.stdout or "").strip().splitlines()
    if not py:
        return False, None, f"conda 环境 {env_name} 已创建，但未获取到 python 可执行路径。"
    return True, py[-1].strip(), None


def ensure_dataset_venv(
    repo: Path, *, auto_install_python: bool = False
) -> tuple[str | None, str]:
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
    seed_python, seed_err = _resolve_venv_seed_python(repo, auto_install_python=auto_install_python)
    if not seed_python:
        return None, seed_err or "无法确定创建 venv 的 Python 解释器"

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

    r = _run([seed_python, "-m", "venv", str(venv_root)], cwd=repo, timeout=180)
    if r.returncode != 0:
        return None, (
            f"{seed_python} -m venv 失败 (cwd={repo}):\n"
            f"{(r.stderr or r.stdout or '').strip()}"
        )

    pip = [str(py), "-m", "pip"]
    r = _run(pip + ["install", "--upgrade", "pip"], cwd=repo, timeout=min(300, timeout))
    if r.returncode != 0:
        return None, f"pip install --upgrade pip 失败:\n{(r.stderr or r.stdout or '').strip()}"

    r = _run(
        pip + ["install", "pytest", "pytest-cov>=5"],
        cwd=repo,
        timeout=min(300, timeout),
    )
    if r.returncode != 0:
        return None, f"pip install pytest/pytest-cov 失败:\n{(r.stderr or r.stdout or '').strip()}"

    for req_name in ("requirements.txt", "bugsinpy_requirements.txt"):
        req = repo / req_name
        if not req.is_file():
            continue
        # BugsInPy 某些数据集（如 pandas）会在 requirements 里包含
        # “-e git+...#egg=<project>”自引用，导致重复 clone 远程仓库并失败。
        # 这里按仓库名做最小过滤，保留其余依赖不变。
        req_text = req.read_text(encoding="utf-8", errors="replace")
        project_name = repo.name.lower()
        kept: list[str] = []
        for raw in req_text.splitlines():
            line = raw.strip()
            if line.startswith("-e git+") and f"#egg={project_name}" in line.lower():
                continue
            kept.append(raw)
        target_req = req
        temp_req: Path | None = None
        if len(kept) != len(req_text.splitlines()):
            temp_req = repo / ".mutiagent" / f".filtered_{req_name}"
            temp_req.parent.mkdir(parents=True, exist_ok=True)
            temp_req.write_text("\n".join(kept) + "\n", encoding="utf-8")
            target_req = temp_req
        r = _run(pip + ["install", "-r", str(target_req)], cwd=repo, timeout=timeout)
        if temp_req is not None:
            try:
                temp_req.unlink()
            except OSError:
                pass
        if r.returncode != 0:
            return None, (
                f"pip install -r {req_name} 失败:\n"
                f"{(r.stderr or r.stdout or '').strip()}"
            )

    inf = repo / ".mutiagent" / "mutiagent_inferred_pip.txt"
    if inf.is_file() and infer_enabled():
        r = _run(pip + ["install", "-r", str(inf)], cwd=repo, timeout=timeout)
        if r.returncode != 0:
            return None, (
                f"pip install 推断依赖 -r {inf.name} 失败:\n"
                f"{(r.stderr or r.stdout or '').strip()}"
            )

    if (repo / "pyproject.toml").is_file() or (repo / "setup.py").is_file():
        r = _run(pip + ["install", "-e", "."], cwd=repo, timeout=timeout)
        if r.returncode != 0:
            return None, f"pip install -e . 失败:\n{(r.stderr or r.stdout or '').strip()}"

    try:
        fp_file.write_text(fp + "\n", encoding="utf-8")
    except OSError as e:
        return None, f"写入 venv 指纹失败: {e}"

    return str(py), "created venv and installed dependencies"
