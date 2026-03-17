from __future__ import annotations

from mutiagent.graph.state import TestPlanItem, WorkflowState


def plan_tests(state: WorkflowState) -> WorkflowState:
    plan: list[TestPlanItem] = []
    for item in state.impacted_ranked:
        if item.score < 0.35:
            continue
        if item.kind == "file":
            plan.append(
                TestPlanItem(
                    target=item.id,
                    intent="为该文件中的关键变更与受影响逻辑生成回归/单元测试（边界、异常、关键分支）",
                    priority="high" if item.score >= 0.7 else "medium",
                )
            )
        else:
            plan.append(
                TestPlanItem(
                    target=item.id,
                    intent="为该符号相关路径生成回归/单元测试（覆盖核心分支与常见失败模式）",
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
    return state

