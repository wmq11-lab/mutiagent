from pathlib import Path

from mutiagent.utils.diff_worktree_check import check_diff_worktree_consistency


def test_empty_diff_ok(tmp_path: Path) -> None:
    r = check_diff_worktree_consistency(tmp_path, "")
    assert "跳过" in r.get("recommendation_zh", "") or r.get("ok") is True


def test_modified_missing_flagged(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    diff = """diff --git a/missing.py b/missing.py
index 123..456 100644
--- a/missing.py
+++ b/missing.py
@@ -1,2 +1,3 @@
 def f():
+    return 1
     pass
"""
    r = check_diff_worktree_consistency(tmp_path, diff)
    assert r["ok"] is False
    assert "missing.py" in r["modified_paths_missing_in_worktree"]


def test_modified_present_ok(tmp_path: Path) -> None:
    p = tmp_path / "ok.py"
    p.write_text("def f():\n    pass\n", encoding="utf-8")
    diff = """diff --git a/ok.py b/ok.py
--- a/ok.py
+++ b/ok.py
@@ -1,1 +1,2 @@
 def f():
+    pass
"""
    r = check_diff_worktree_consistency(tmp_path, diff)
    assert r["ok"] is True
    assert r["modified_paths_missing_in_worktree"] == []


def test_added_file_not_counted_as_mismatch(tmp_path: Path) -> None:
    diff = """diff --git a/brand_new.py b/brand_new.py
new file mode 100644
--- /dev/null
+++ b/brand_new.py
@@ -0,0 +1,1 @@
+x=1
"""
    r = check_diff_worktree_consistency(tmp_path, diff)
    assert r["ok"] is True
    assert "brand_new.py" in r["added_paths_not_yet_in_worktree"]
