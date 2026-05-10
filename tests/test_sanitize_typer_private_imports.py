"""sanitize_typer_private_imports：Typer 私有符号改为 import + getattr，避免收集期 ImportError。"""

from mutiagent.nodes.test_gen_agent import sanitize_typer_private_imports


def test_splits_private_names_from_typer_core_mixed() -> None:
    src = "from typer.core import _write_opts, TyperCommand\n"
    out = sanitize_typer_private_imports(src)
    assert "TyperCommand" in out
    assert "from typer.core import TyperCommand" in out
    assert "getattr" in out
    assert "_write_opts" in out
    assert "_mutiagent_typer_typer_core" in out


def test_only_privates_become_import_getattr() -> None:
    src = "from typer.core import _main_shell_completion\nx = 1\n"
    out = sanitize_typer_private_imports(src)
    assert "from typer.core import" not in out
    assert "import typer.core as _mutiagent_typer_typer_core" in out
    assert "_main_shell_completion=getattr" in out.replace(" ", "")
    assert "x = 1" in out


def test_removes_star_import_from_typer() -> None:
    src = "from typer.main import *\n"
    out = sanitize_typer_private_imports(src)
    assert "import *" not in out
    assert "typer.main" not in out


def test_keeps_non_typer_imports() -> None:
    src = "from click import Command\nimport pytest\n"
    out = sanitize_typer_private_imports(src)
    assert "from click import Command" in out
    assert "import pytest" in out


def test_private_import_with_alias_uses_getattr() -> None:
    """`from typer.core import _foo as bar`：改为对 bar 的 getattr 赋值。"""
    src = "from typer.core import _secret as public_name\n"
    out = sanitize_typer_private_imports(src)
    assert "from typer.core import" not in out
    assert "public_name" in out
    assert "getattr" in out
    assert "'_secret'" in out or '"_secret"' in out


def test_strips_callback_from_typer_main_import() -> None:
    """``callback`` 非 typer.main 模块级导出，剥离后保留 Typer 等合法名称。"""
    src = "from typer.main import Typer, callback\nx = 1\n"
    out = sanitize_typer_private_imports(src)
    assert "callback" not in out
    assert "from typer.main import Typer" in out
    assert "x = 1" in out


def test_removes_typer_main_callback_only_import() -> None:
    src = "from typer.main import callback\n"
    out = sanitize_typer_private_imports(src)
    assert "typer.main" not in out
    assert "callback" not in out

