from __future__ import annotations

from mutiagent.graph.state import ImpactedCandidate, ImpactedItem, WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_json


def _dedupe_candidates(candidates: list[ImpactedCandidate]) -> list[ImpactedCandidate]:
    best: dict[tuple[str, str], ImpactedCandidate] = {}
    for candidate in candidates:
        key = (candidate.kind, candidate.id)
        if key not in best or candidate.depth < best[key].depth:
            best[key] = candidate
    return list(best.values())


def _rule_impact(state: WorkflowState) -> list[ImpactedCandidate]:
    out: list[ImpactedCandidate] = []

    for f in state.changed_files:
        out.append(ImpactedCandidate(kind="file", id=f, via="changed_file", depth=0))

    for file_summary in state.change_analysis:
        for change in file_summary.changes:
            out.append(
                ImpactedCandidate(
                    kind="symbol",
                    id=f"{file_summary.file}:{change.type}:{change.entity}",
                    via="changed_entity",
                    depth=0,
                )
            )
            for seed in change.impact_seeds:
                out.append(
                    ImpactedCandidate(
                        kind="symbol",
                        id=f"{seed.kind}:{seed.name}",
                        via=f"impact_seed:{change.entity}",
                        depth=1,
                    )
                )

    return _dedupe_candidates(out)


def _llm_rank(state: WorkflowState, candidates: list[ImpactedCandidate]) -> list[ImpactedItem]:
    system = (
        "你是资深软件测试/静态分析专家。给定代码变更与规则推导出的影响候选集合，"
        "请输出一个JSON对象，字段为 impacted（数组）。每个元素包含：kind(file|symbol), id, score(0-1), reason。"
        "要求：只基于输入信息推断，不要凭空添加不存在的文件/符号；score越高表示越可能需要回归测试关注。"
    )
    payload = {
        "repo_path": state.repo_path,
        "changed_files": state.changed_files,
        "diff_stats": state.debug.get("diff_stats", {}),
        "change_analysis": [item.model_dump() for item in state.change_analysis],
        "candidates": [c.model_dump() for c in candidates],
    }
    resp = chat_json(system, f"输入如下（JSON）：\n{payload}\n\n请输出JSON：{{\"impacted\": [...]}}")
    impacted = resp.get("impacted", [])
    out: list[ImpactedItem] = []
    for it in impacted:
        try:
            out.append(ImpactedItem(**it))
        except Exception:
            continue
    return out or [
        ImpactedItem(kind=c.kind, id=c.id, score=max(0.1, 1.0 - 0.2 * c.depth), reason=c.via) for c in candidates
    ]


def analyze_impact(state: WorkflowState) -> WorkflowState:
    candidates = _rule_impact(state)
    state.impacted = candidates

    if llm_available():
        ranked = _llm_rank(state, candidates)
    else:
        ranked = [
            ImpactedItem(kind=c.kind, id=c.id, score=max(0.1, 1.0 - 0.2 * c.depth), reason=c.via) for c in candidates
        ]

    ranked_sorted = sorted(ranked, key=lambda x: x.score, reverse=True)[:15]
    state.impacted_ranked = ranked_sorted
    state.debug["impact"] = {
        "candidate_count": len(candidates),
        "ranked_count": len(ranked_sorted),
        "used_llm": llm_available(),
    }
    return state

