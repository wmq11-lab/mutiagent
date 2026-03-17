from __future__ import annotations

from mutiagent.graph.state import WorkflowState
from mutiagent.utils.diff import parse_unified_diff


def ingest_change(state: WorkflowState) -> WorkflowState:
    parsed = parse_unified_diff(state.diff)
    state.changed_files = parsed["changed_files"]
    state.diff_hunks = parsed["hunks_by_file"]
    state.debug["diff_stats"] = parsed["stats"]
    return state

