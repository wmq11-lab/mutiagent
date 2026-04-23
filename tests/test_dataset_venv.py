from __future__ import annotations

from pathlib import Path

from mutiagent.utils.dataset_venv import fingerprint
from mutiagent.utils.dataset_venv import _read_bugsinpy_python_version
from mutiagent.utils.dataset_venv import _resolve_venv_seed_python
from mutiagent.utils.dataset_venv import _try_install_python_with_conda
from mutiagent.utils.dataset_venv import _try_install_python_with_pyenv
from mutiagent.utils.dataset_venv import ensure_dataset_venv


def test_fingerprint_changes_when_requirements_change(tmp_path: Path) -> None:
    req = tmp_path / "requirements.txt"
    req.write_text("a==1\n", encoding="utf-8")
    fp1 = fingerprint(tmp_path)
    req.write_text("a==2\n", encoding="utf-8")
    fp2 = fingerprint(tmp_path)
    assert fp1 != fp2


def test_read_bugsinpy_python_version(tmp_path: Path) -> None:
    info = tmp_path / "bugsinpy_bug.info"
    info.write_text('python_version="3.6.9"\n', encoding="utf-8")
    assert _read_bugsinpy_python_version(tmp_path) == "3.6.9"


def test_resolve_venv_seed_python_from_bugsinpy(
    tmp_path: Path, monkeypatch
) -> None:
    info = tmp_path / "bugsinpy_bug.info"
    info.write_text('python_version="3.6.9"\n', encoding="utf-8")

    def fake_which(name: str) -> str | None:
        return "/opt/homebrew/bin/python3.6" if name == "python3.6" else None

    monkeypatch.setattr("mutiagent.utils.dataset_venv.shutil.which", fake_which)
    py, err = _resolve_venv_seed_python(tmp_path)
    assert err is None
    assert py == "/opt/homebrew/bin/python3.6"


def test_try_install_python_with_pyenv_missing(monkeypatch) -> None:
    monkeypatch.setattr("mutiagent.utils.dataset_venv.shutil.which", lambda _: None)
    ok, msg = _try_install_python_with_pyenv("3.6.9")
    assert ok is False
    assert msg is not None


def test_resolve_venv_seed_python_auto_install_success(
    tmp_path: Path, monkeypatch
) -> None:
    info = tmp_path / "bugsinpy_bug.info"
    info.write_text('python_version="3.6.9"\n', encoding="utf-8")
    monkeypatch.setenv("MUTIAGENT_VENV_AUTO_INSTALL_PYTHON", "1")

    monkeypatch.setattr("mutiagent.utils.dataset_venv.shutil.which", lambda _: None)
    monkeypatch.setattr(
        "mutiagent.utils.dataset_venv._try_install_python_with_conda",
        lambda version: (True, "/opt/anaconda3/envs/mutiagent-py369/bin/python", None),
    )
    py, err = _resolve_venv_seed_python(tmp_path, auto_install_python=True)
    assert err is None
    assert py == "/opt/anaconda3/envs/mutiagent-py369/bin/python"


def test_try_install_python_with_conda_missing(monkeypatch) -> None:
    monkeypatch.setattr(
        "mutiagent.utils.dataset_venv.shutil.which",
        lambda name: None if name == "conda" else None,
    )
    ok, py, msg = _try_install_python_with_conda("3.6.9")
    assert ok is False
    assert py is None
    assert msg is not None


def test_try_install_python_with_conda_fallback_minor_wildcard(monkeypatch) -> None:
    monkeypatch.setattr(
        "mutiagent.utils.dataset_venv.shutil.which",
        lambda name: "/opt/anaconda3/bin/conda" if name == "conda" else None,
    )
    calls: list[list[str]] = []

    class _Fail:
        returncode = 1
        stdout = ""
        stderr = "not found"

    class _Ok:
        returncode = 0
        stdout = "/opt/anaconda3/envs/mutiagent-py383/bin/python\n"
        stderr = ""

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if "create" in cmd and "python=3.8.3" in cmd:
            return _Fail()
        if "create" in cmd and "python=3.8.*" in cmd:
            return _Ok()
        if "run" in cmd:
            return _Ok()
        return _Fail()

    monkeypatch.setattr("mutiagent.utils.dataset_venv._run", fake_run)
    ok, py, msg = _try_install_python_with_conda("3.8.3")
    assert ok is True
    assert py == "/opt/anaconda3/envs/mutiagent-py383/bin/python"
    assert msg is None
    assert any("python=3.8.3" in " ".join(c) for c in calls)
    assert any("python=3.8.*" in " ".join(c) for c in calls)


def test_resolve_venv_seed_python_fallback_to_conda(
    tmp_path: Path, monkeypatch
) -> None:
    info = tmp_path / "bugsinpy_bug.info"
    info.write_text('python_version="3.6.9"\n', encoding="utf-8")

    def fake_pyenv(version: str):
        return False, "pyenv failed"

    def fake_conda(version: str):
        return True, "/opt/anaconda3/envs/mutiagent-py369/bin/python", None

    monkeypatch.setattr("mutiagent.utils.dataset_venv._try_install_python_with_pyenv", fake_pyenv)
    monkeypatch.setattr("mutiagent.utils.dataset_venv._try_install_python_with_conda", fake_conda)
    monkeypatch.setattr("mutiagent.utils.dataset_venv.shutil.which", lambda _: None)
    py, err = _resolve_venv_seed_python(tmp_path, auto_install_python=True)
    assert err is None
    assert py == "/opt/anaconda3/envs/mutiagent-py369/bin/python"


def test_ensure_dataset_venv_filters_self_git_editable(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "pandas"
    repo.mkdir()
    (repo / "bugsinpy_requirements.txt").write_text(
        "numpy==1.0.0\n-e git+https://github.com/pandas-dev/pandas@abc#egg=pandas\n",
        encoding="utf-8",
    )

    class _CP:
        def __init__(self, returncode=0, stdout="", stderr=""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    runs: list[list[str]] = []

    def fake_run(cmd, *, cwd, timeout):
        runs.append(cmd)
        if cmd[1:3] == ["-m", "venv"]:
            vpy = repo / ".mutiagent" / "mutiagent_pytest_venv" / "bin" / "python"
            vpy.parent.mkdir(parents=True, exist_ok=True)
            vpy.write_text("#!/usr/bin/env python\n", encoding="utf-8")
            return _CP()
        if cmd[1:3] == ["-m", "pip"] and "install" in cmd and "-r" in cmd:
            req_path = Path(cmd[cmd.index("-r") + 1])
            txt = req_path.read_text(encoding="utf-8")
            assert "#egg=pandas" not in txt
            return _CP()
        return _CP()

    monkeypatch.setattr("mutiagent.utils.dataset_venv._resolve_venv_seed_python", lambda *a, **k: ("/usr/bin/python3", None))
    monkeypatch.setattr("mutiagent.utils.dataset_venv._run", fake_run)
    py, msg = ensure_dataset_venv(repo)
    assert py is not None
    assert "created venv" in msg
