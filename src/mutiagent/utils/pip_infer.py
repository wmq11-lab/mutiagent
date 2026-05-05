"""
根据变更的 .py 文件中的 import 语句，在缺少 requirements.txt 时推断常见第三方 PyPI 包名，
写入 `.mutiagent/mutiagent_inferred_pip.txt` 供 dataset_venv 安装。
仅接受白名单映射，避免对任意模块名跑 pip 带来安全风险。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# 顶层 import / from 的模块名 -> pip 包名（可多个，取第一个为 canonical）
_MODULE_TO_PIP: dict[str, str] = {
    "requests": "requests",
    "urllib3": "urllib3",
    "httpx": "httpx",
    "aiohttp": "aiohttp",
    "bs4": "beautifulsoup4",
    "lxml": "lxml",
    "yaml": "pyyaml",
    "PIL": "Pillow",
    "Image": "Pillow",
    "numpy": "numpy",
    "pandas": "pandas",
    "django": "Django",
    "flask": "flask",
    "fastapi": "fastapi",
    "pydantic": "pydantic",
    "sqlalchemy": "sqlalchemy",
    "redis": "redis",
    "pymongo": "pymongo",
    "boto3": "boto3",
    "botocore": "botocore",
    "celery": "celery",
    "jinja2": "jinja2",
    "markdown": "markdown",
    "cryptography": "cryptography",
    "OpenSSL": "pyopenssl",
    "scipy": "scipy",
    "sklearn": "scikit-learn",
    "dateutil": "python-dateutil",
    "tenacity": "tenacity",
    "structlog": "structlog",
    "click": "click",
    "tqdm": "tqdm",
}


def _stdlib_top_levels() -> set[str]:
    try:
        names: set[str] = set(getattr(sys, "stdlib_module_names", ()))  # type: ignore[arg-type]
    except Exception:
        names = set()
    if not names:
        names = {
            "os",
            "sys",
            "re",
            "io",
            "json",
            "math",
            "time",
            "typing",
            "pathlib",
            "collections",
            "itertools",
            "functools",
            "operator",
            "enum",
            "abc",
            "copy",
            "hashlib",
            "base64",
            "html",
            "http",
            "email",
            "importlib",
            "logging",
            "unittest",
            "asyncio",
            "subprocess",
            "shutil",
            "tempfile",
            "argparse",
            "datetime",
        }
    return names


def _add_top_from_import_line(line: str, acc: set[str]) -> None:
    m = re.match(r"^\s*import\s+(.+?)\s*(?:#.*)?$", line)
    if not m:
        return
    before_as = m.group(1)
    for piece in before_as.split(","):
        p = piece.strip()
        if not p:
            continue
        p = p.split(" as ")[0].strip()
        top = p.split(".", 1)[0].strip()
        if top:
            acc.add(top)


def _add_top_from_from_line(line: str, acc: set[str]) -> None:
    m = re.match(r"^\s*from\s+(\.+)?([\w.]+)\s+import", line)
    if not m or m.group(1):
        return
    name = m.group(2) or ""
    if not name or name.startswith("."):
        return
    top = name.split(".", 1)[0].strip()
    if top:
        acc.add(top)


def _collect_toplevels_from_text(text: str) -> set[str]:
    out: set[str] = set()
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("import "):
            _add_top_from_import_line(line, out)
        elif s.startswith("from "):
            _add_top_from_from_line(line, out)
    return out


def infer_pip_packages_for_changed_files(repo: Path, changed_files: list[str] | None) -> list[str]:
    stdlib = _stdlib_top_levels()
    toplevel: set[str] = set()
    for rel in changed_files or []:
        p = repo / rel
        if not p.is_file() or not str(rel).endswith(".py"):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        toplevel |= _collect_toplevels_from_text(text)
    pips: set[str] = set()
    for top in toplevel:
        if not top or top in stdlib:
            continue
        pip = _MODULE_TO_PIP.get(top)
        if pip:
            pips.add(pip)
    return sorted(pips)


def infer_enabled() -> bool:
    import os

    v = os.environ.get("MUTIAGENT_INFER_PIP", "1").strip().lower()
    return v not in {"0", "false", "no", "off"}


def write_inferred_pip_requirements(repo: Path, changed_files: list[str] | None) -> list[str]:
    """
    将推断的 pip 包名写入 `repo/.mutiagent/mutiagent_inferred_pip.txt`（一行一个，排序）。
    无推断结果时若文件已存在则删除。返回将写入/已写入过的包名列表（有序）。
    """
    if not infer_enabled():
        out_path = (repo / ".mutiagent" / "mutiagent_inferred_pip.txt").resolve()
        try:
            if out_path.is_file():
                out_path.unlink()
        except OSError:
            pass
        return []

    rel_file = Path(".mutiagent") / "mutiagent_inferred_pip.txt"
    out_path = (repo / rel_file).resolve()
    if not (repo / "requirements.txt").is_file() and not (repo / "bugsinpy_requirements.txt").is_file():
        pkgs = infer_pip_packages_for_changed_files(repo, changed_files)
    else:
        pkgs = []
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not pkgs:
        try:
            if out_path.is_file():
                out_path.unlink()
        except OSError:
            pass
        return []
    out_path.write_text("\n".join(pkgs) + "\n", encoding="utf-8")
    return pkgs
