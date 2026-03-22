from __future__ import annotations

from mutiagent.graph.state import ImpactedCandidate, ImpactedItem, WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_json
from mutiagent.utils.change_graph_builder import impact_candidate_graph_boost


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
            sym_id = f"{file_summary.file}:{change.type}:{change.entity}"
            out.append(
                ImpactedCandidate(
                    kind="symbol",
                    id=sym_id,
                    via="changed_entity",
                    depth=0,
                )
            )
            for seed in change.impact_seeds:
                seed_id = f"seed:{file_summary.file}:{seed.kind}:{seed.name}"
                out.append(
                    ImpactedCandidate(
                        kind="symbol",
                        id=seed_id,
                        via=f"impact_seed:{change.entity}",
                        depth=1,
                    )
                )

    return _dedupe_candidates(out)


def _merge_score_with_graph(base: float, c: ImpactedCandidate, state: WorkflowState) -> float:
    g = state.change_graph
    boost = impact_candidate_graph_boost(c.kind, c.id, g)
    return max(0.0, min(1.0, base + boost))


def _llm_rank(state: WorkflowState, candidates: list[ImpactedCandidate]) -> list[ImpactedItem]:
    system = (
        "你是资深软件测试/静态分析专家。给定代码变更与规则推导出的影响候选集合，"
        "请输出一个JSON对象，字段为 impacted（数组）。每个元素包含：kind(file|symbol), id, score(0-1), reason。"
        "要求：只基于输入信息推断，不要凭空添加不存在的文件/符号；score越高表示越可能需要回归测试关注。"
        "可参考 change_graph 中的边（contains_change、emits_seed、test_focus）理解从变更到 seed、测试关注点的传播。"
    )
    graph_blob: dict | None = None
    if state.change_graph is not None:
        graph_blob = state.change_graph.model_dump()
    payload = {
        "repo_path": state.repo_path,
        "changed_files": state.changed_files,
        "diff_stats": state.debug.get("diff_stats", {}),
        "change_analysis": [item.model_dump() for item in state.change_analysis],
        "change_graph": graph_blob,
        "candidates": [c.model_dump() for c in candidates],
    }
    resp = chat_json(system, f"输入如下（JSON）：\n{payload}\n\n请输出JSON：{{\"impacted\": [...]}}")
    impacted = resp.get("impacted", [])
    out: list[ImpactedItem] = []
    for it in impacted:
        try:
            item = ImpactedItem(**it)
            cand = _find_candidate(item.id, candidates)
            sc = float(item.score)
            if cand is not None:
                sc = _merge_score_with_graph(sc, cand, state)
            out.append(ImpactedItem(kind=item.kind, id=item.id, score=sc, reason=item.reason))
        except Exception:
            continue
    if out:
        return out
    return [
        ImpactedItem(
            kind=c.kind,
            id=c.id,
            score=_merge_score_with_graph(max(0.1, 1.0 - 0.2 * c.depth), c, state),
            reason=c.via,
        )
        for c in candidates
    ]


def _find_candidate(cid: str, candidates: list[ImpactedCandidate]) -> ImpactedCandidate | None:
    for c in candidates:
        if c.id == cid:
            return c
    return None


def analyze_impact(state: WorkflowState) -> WorkflowState:
    candidates = _rule_impact(state)
    state.impacted = candidates

    if llm_available():
        ranked = _llm_rank(state, candidates)
    else:
        ranked = [
            ImpactedItem(
                kind=c.kind,
                id=c.id,
                score=_merge_score_with_graph(max(0.1, 1.0 - 0.2 * c.depth), c, state),
                reason=c.via,
            )
            for c in candidates
        ]

    ranked_sorted = sorted(ranked, key=lambda x: x.score, reverse=True)[:15]
    state.impacted_ranked = ranked_sorted
    state.debug["impact"] = {
        "candidate_count": len(candidates),
        "ranked_count": len(ranked_sorted),
        "used_llm": llm_available(),
        "change_graph_used": state.change_graph is not None,
    }
    return state
