from __future__ import annotations

import os

from mutiagent.graph.state import TestPlanItem, WorkflowState
from mutiagent.utils.change_graph_builder import impact_candidate_graph_boost


def _truthy_env(name: str, default: bool = True) -> bool:
    v = os.environ.get(name, "").strip().lower()
    if not v:
        return default
    if v in {"0", "false", "no", "off"}:
        return False
    if v in {"1", "true", "yes", "on"}:
        return True
    return default



def test_prioritization_agent(state: WorkflowState) -> WorkflowState:
    """
    按 impacted score 粗排，并用 Change Graph（test_focus 传播）做小幅 tie-break，
    便于与「影响范围」一致地抬高集成/分支等关注点相关用例。
    """
    score_by_target: dict[str, float] = {}

    cmap = {u.semantic_unit_id: u for u in state.semantic_units_catalog}
    if state.impact_graph:
        for igf in state.impact_graph:
            best_file = 0.0
            for sym in igf.symbols:
                su_max = max(
                    (cmap[i].priority_score for i in sym.semantic_unit_ids if i in cmap),
                    default=0.0,
                )
                su_max *= sym.centrality
                best_file = max(best_file, su_max)
                score_by_target[sym.symbol_id] = max(score_by_target.get(sym.symbol_id, 0.0), su_max)
            score_by_target[igf.file] = max(score_by_target.get(igf.file, 0.0), best_file)
    else:
        for it in state.impacted_ranked:
            score_by_target[it.id] = max(score_by_target.get(it.id, 0.0), float(it.score))

    graph = state.change_graph

    def graph_tie_break(target: str) -> float:
        if graph is None:
            return 0.0
        if target in state.changed_files:
            return impact_candidate_graph_boost("file", target, graph) * 0.15
        if target.startswith("seed:"):
            return impact_candidate_graph_boost("seed", target, graph) * 0.15
        if target.startswith("focus:"):
            return impact_candidate_graph_boost("focus", target, graph) * 0.15
        return impact_candidate_graph_boost("symbol", target, graph) * 0.15

    def key(p: TestPlanItem) -> float:
        return score_by_target.get(p.target, 0.5) + graph_tie_break(p.target)

    prioritized = sorted(state.test_plan, key=key, reverse=True)
    out: list[TestPlanItem] = []
    for p in prioritized:
        s = key(p)
        pr = "high" if s >= 0.72 else ("medium" if s >= 0.42 else "low")
        out.append(TestPlanItem(target=p.target, intent=p.intent, priority=pr))  # type: ignore[arg-type]

    ranked_no_low = [p for p in out if p.priority != "low"]
    dropped_low_n = len(out) - len(ranked_no_low)
    drop_on = _truthy_env("MUTIAGENT_PRIORITIZATION_DROP_LOW", default=True)
    if drop_on and ranked_no_low:
        filtered = ranked_no_low
        used_drop_low = True
    else:
        filtered = out
        used_drop_low = False

    state.prioritized_plan = filtered
    state.debug["test_prioritization_agent"] = {
        "count": len(filtered),
        "count_before_drop_low": len(out),
        "dropped_low_count": dropped_low_n if used_drop_low else 0,
        "used_change_graph": graph is not None,
    }
    return state

