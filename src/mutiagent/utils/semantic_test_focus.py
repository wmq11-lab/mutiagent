from __future__ import annotations

from typing import Iterable

# semantic_tag → 测试设计关注点（可多对多，合并后去重排序）
SEMANTIC_TAG_TO_TEST_FOCUS: dict[str, frozenset[str]] = {
    "logic_branch_changed": frozenset(
        {
            "conditional_render",
            "branch_coverage",
            "state_transition",
        }
    ),
    "dependency_call_changed": frozenset(
        {
            "integration",
            "interaction",
            "dependency_stub",
            "side_effects",
        }
    ),
    "api_signature_changed": frozenset(
        {
            "contract_tests",
            "signature_compat",
            "call_site_updates",
            "mock_boundaries",
        }
    ),
    "exception_handling_changed": frozenset(
        {
            "error_paths",
            "exception_assertions",
            "resilience",
        }
    ),
    "input_validation_added": frozenset(
        {
            "invalid_input",
            "boundary_values",
            "rejection_behavior",
        }
    ),
    "null_check_added": frozenset(
        {
            "null_safety",
            "optional_inputs",
            "edge_cases",
        }
    ),
    "return_value_changed": frozenset(
        {
            "output_contract",
            "regression_assertions",
            "snapshot_or_golden",
        }
    ),
}


def semantic_tags_to_test_focus(tags: Iterable[str]) -> list[str]:
    """由 semantic_tags 聚合测试导向关注点，稳定排序、去重。"""
    acc: set[str] = set()
    for tag in tags:
        if not isinstance(tag, str):
            continue
        acc |= SEMANTIC_TAG_TO_TEST_FOCUS.get(tag, frozenset())
    return sorted(acc)
