from __future__ import annotations

from mutiagent.utils.diff import parse_unified_diff
from mutiagent.utils.paths import should_ignore_file


def test_should_ignore_file_by_dir_segment() -> None:
    assert should_ignore_file("dist/assets/index.js")
    assert should_ignore_file("src/foo/node_modules/pkg/x.js")
    assert should_ignore_file(".git/hooks/pre-commit")
    assert should_ignore_file("coverage/lcov.info")
    assert not should_ignore_file("src/distribution/config.py")
    assert not should_ignore_file("src/app.tsx")


def test_should_ignore_file_by_suffix() -> None:
    assert should_ignore_file("static/app.min.js")
    assert should_ignore_file("bundle.js.map")
    assert should_ignore_file("pnpm-lock.yaml") is False  # 后缀为 .yaml，非 .lock
    assert should_ignore_file("yarn.lock")


def test_parse_unified_diff_drops_ignored_paths() -> None:
    diff = (
        "--- a/dist/bundle.js\n"
        "+++ b/dist/bundle.js\n"
        "@@ -1 +1 @@\n"
        "-x\n"
        "+y\n"
        "--- a/src/app.py\n"
        "+++ b/src/app.py\n"
        "@@ -1 +1 @@\n"
        "-a\n"
        "+b\n"
    )
    out = parse_unified_diff(diff)
    assert out["changed_files"] == ["src/app.py"]
    assert "dist/bundle.js" not in out["hunks_by_file"]
    assert out["stats"]["files"] == 1
    assert out["stats"]["added"] == 1
    assert out["stats"]["removed"] == 1
