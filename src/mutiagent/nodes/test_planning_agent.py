from __future__ import annotations

from mutiagent.graph.state import TestPlanItem, WorkflowState


def plan_tests(state: WorkflowState) -> WorkflowState:
    # 作为“汇聚点”可能被多条边触发；保证幂等，避免重复规划
    if state.test_plan:
        state.debug["test_planning_agent"] = {"skipped": True, "reason": "already_planned"}
        return state

    plan: list[TestPlanItem] = []
    patterns = state.bug_patterns or []
    for item in state.impacted_ranked:
        if item.score < 0.35:
            continue
        if item.kind == "file":
            pattern_hint = ""
            if patterns:
                pattern_hint = f"（bug_patterns: {', '.join([str(p.get('pattern')) for p in patterns[:2]])}）"
            plan.append(
                TestPlanItem(
                    target=item.id,
                    intent="为该文件中的关键变更与受影响逻辑生成回归/单元测试（边界、异常、关键分支）" + pattern_hint,
                    priority="high" if item.score >= 0.7 else "medium",
                )
            )
        else:
            pattern_hint = ""
            if patterns:
                pattern_hint = f"（bug_patterns: {', '.join([str(p.get('pattern')) for p in patterns[:2]])}）"
            plan.append(
                TestPlanItem(
                    target=item.id,
                    intent="为该符号相关路径生成回归/单元测试（覆盖核心分支与常见失败模式）" + pattern_hint,
                    priority="high" if item.score >= 0.7 else "medium",
                )
            )
    if not plan:
        plan.append(
            TestPlanItem(
                target="project",
                intent="变更影响不明确：生成最小冒烟回归（import可用性、核心API调用、异常分支）",
                priority="medium",
            )
        )
    state.test_plan = plan[:20]
    state.debug["test_planning_agent"] = {"skipped": False, "count": len(state.test_plan)}
    return state

