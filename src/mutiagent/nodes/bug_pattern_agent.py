from __future__ import annotations

from mutiagent.graph.state import WorkflowState


def bug_pattern_agent(state: WorkflowState) -> WorkflowState:
    """
    MVP：基于diff统计与常见变更类型做轻量bug pattern提示。
    后续可升级：接入历史缺陷模式库/LLM分类器。
    """
    stats = state.debug.get("diff_stats", {}) or {}
    added = int(stats.get("added", 0) or 0)
    removed = int(stats.get("removed", 0) or 0)

    patterns: list[dict[str, object]] = []
    if added > 0 and removed > 0:
        patterns.append({"pattern": "behavior_change", "confidence": 0.55, "reason": "同时有新增与删除行，可能存在行为变更"})
    if removed > added:
        patterns.append({"pattern": "logic_simplification_or_bug", "confidence": 0.45, "reason": "删除行多于新增行，可能删减逻辑/条件"})
    if not patterns:
        patterns.append({"pattern": "unknown", "confidence": 0.2, "reason": "缺少足够信号，保持保守回归策略"})

    state.bug_patterns = patterns
    state.debug["bug_pattern_agent"] = {"pattern_count": len(patterns)}
    return state

