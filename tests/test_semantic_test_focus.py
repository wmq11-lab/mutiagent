from __future__ import annotations

from mutiagent.utils.semantic_test_focus import SEMANTIC_TAG_TO_TEST_FOCUS, semantic_tags_to_test_focus


def test_test_focus_merges_and_dedupes() -> None:
    tags = ["logic_branch_changed", "dependency_call_changed", "logic_branch_changed"]
    got = semantic_tags_to_test_focus(tags)
    assert got == sorted(set().union(*(SEMANTIC_TAG_TO_TEST_FOCUS[t] for t in ["logic_branch_changed", "dependency_call_changed"])))
    assert "conditional_render" in got
    assert "integration" in got


def test_unknown_tag_ignored() -> None:
    assert semantic_tags_to_test_focus(["not_a_real_tag", "logic_branch_changed"]) == sorted(
        SEMANTIC_TAG_TO_TEST_FOCUS["logic_branch_changed"]
    )
