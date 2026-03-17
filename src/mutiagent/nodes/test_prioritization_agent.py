from __future__ import annotations

from mutiagent.graph.state import TestPlanItem, WorkflowState


def test_prioritization_agent(state: WorkflowState) -> WorkflowState:
    """
    MVP：按 impacted score 粗排优先级；后续可引入历史失败率/覆盖率增益等信号。
    """
    score_by_target: dict[str, float] = {}
    for it in state.impacted_ranked:
        score_by_target[it.id] = max(score_by_target.get(it.id, 0.0), float(it.score))

    def key(p: TestPlanItem) -> float:
        return score_by_target.get(p.target, 0.5)

    prioritized = sorted(state.test_plan, key=key, reverse=True)
    out: list[TestPlanItem] = []
    for p in prioritized:
        s = key(p)
        pr = "high" if s >= 0.7 else ("medium" if s >= 0.4 else "low")
        out.append(TestPlanItem(target=p.target, intent=p.intent, priority=pr))  # type: ignore[arg-type]

    state.prioritized_plan = out
    state.debug["test_prioritization_agent"] = {"count": len(out)}
    return state

