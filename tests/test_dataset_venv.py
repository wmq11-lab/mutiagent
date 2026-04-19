from __future__ import annotations

from pathlib import Path

from mutiagent.utils.dataset_venv import fingerprint


def test_fingerprint_changes_when_requirements_change(tmp_path: Path) -> None:
    req = tmp_path / "requirements.txt"
    req.write_text("a==1\n", encoding="utf-8")
    fp1 = fingerprint(tmp_path)
    req.write_text("a==2\n", encoding="utf-8")
    fp2 = fingerprint(tmp_path)
    assert fp1 != fp2
