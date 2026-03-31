from __future__ import annotations

from mutiagent.graph.state import TestPlanItem, WorkflowState


def _catalog_map(state: WorkflowState) -> dict:
    return {u.semantic_unit_id: u for u in state.semantic_units_catalog}


def plan_tests(state: WorkflowState) -> WorkflowState:
    # 作为“汇聚点”可能被多条边触发；保证幂等，避免重复规划
    if state.test_plan:
        state.debug["test_planning_agent"] = {"skipped": True, "reason": "already_planned"}
        return state

    plan: list[TestPlanItem] = []
    patterns = state.bug_patterns or []
    pattern_hint = ""
    if patterns:
        pattern_hint = f"（bug_patterns: {', '.join([str(p.get('pattern')) for p in patterns[:2]])}）"

    # 主路径：V3 通过 semantic_unit_id 解析 catalog（priority_score + 可执行策略）
    if state.impact_graph:
        cmap = _catalog_map(state)
        for igf in state.impact_graph:
            for sym in igf.symbols:
                if not sym.semantic_unit_ids:
                    continue
                units = [cmap[i] for i in sym.semantic_unit_ids if i in cmap]
                if not units:
                    continue
                max_p = max(u.priority_score for u in units)
                if max_p < 0.22:
                    continue
                exec_lines: list[str] = []
                for u in units:
                    for ex in u.test_strategy[:2]:
                        exec_lines.append(
                            f"场景:{ex.scenario[:120]} | 输入:{ex.input[:80]} | mock:{ex.mock[:80]} | 断言:{ex.assert_[:120]}"
                        )
                intent_body = "；".join(exec_lines[:5])[:1800]
                plan.append(
                    TestPlanItem(
                        target=sym.symbol_id,
                        intent=(
                            f"依据 impact_graph[{igf.file}::{sym.name}] 的语义单元 id {sym.semantic_unit_ids} 生成用例；"
                            f"优先覆盖规则关注点 {', '.join(f'{tf.type}({tf.derived_from[:40]}...)' for u in units for tf in u.test_focus[:2])[:400]}。"
                            f"可执行策略：{intent_body}"
                        )
                        + pattern_hint,
                        priority="high" if max_p >= 0.72 else "medium",
                    )
                )
    else:
        for item in state.impacted_ranked:
            if item.score < 0.35:
                continue
            if item.kind == "file":
                plan.append(
                    TestPlanItem(
                        target=item.id,
                        intent="为该文件中的关键变更与受影响逻辑生成回归/单元测试（边界、异常、关键分支）" + pattern_hint,
                        priority="high" if item.score >= 0.7 else "medium",
                    )
                )
            else:
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

