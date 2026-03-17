from __future__ import annotations

from collections import deque
from pathlib import Path

import networkx as nx

from mutiagent.graph.state import ImpactedCandidate, ImpactedItem, WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_json


def _build_module_graph(state: WorkflowState) -> nx.DiGraph:
    g = nx.DiGraph()
    for u, v in state.module_graph.get("edges", []):
        g.add_edge(u, v)
    for n in state.module_graph.get("nodes", []):
        g.add_node(n)
    return g


def _file_to_module_candidates(state: WorkflowState, changed_file: str) -> list[str]:
    mod_to_file = state.module_graph.get("mod_to_file", {}) or {}
    hit: list[str] = []
    for mod, fp in mod_to_file.items():
        try:
            if Path(fp).as_posix().endswith(changed_file):
                hit.append(mod)
        except Exception:
            continue
    if not hit and changed_file.endswith(".py"):
        guess = changed_file[:-3].replace("/", ".")
        if guess.endswith(".__init__"):
            guess = guess[: -len(".__init__")]
        hit.append(guess)
    return hit


def _rule_impact(state: WorkflowState) -> list[ImpactedCandidate]:
    g = _build_module_graph(state)
    rg = g.reverse(copy=False)

    seeds: list[str] = []
    for f in state.changed_files:
        seeds.extend(_file_to_module_candidates(state, f))

    seen = set(seeds)
    q = deque([(s, 0) for s in seeds])
    out: list[ImpactedCandidate] = []

    for f in state.changed_files:
        out.append(ImpactedCandidate(kind="file", id=f, via="changed_file", depth=0))

    while q:
        node, depth = q.popleft()
        out.append(ImpactedCandidate(kind="symbol", id=f"module:{node}", via="reverse_import", depth=depth))
        if depth >= 2:
            continue
        for pred in rg.neighbors(node):
            if pred in seen:
                continue
            seen.add(pred)
            q.append((pred, depth + 1))

    best: dict[tuple[str, str], ImpactedCandidate] = {}
    for c in out:
        k = (c.kind, c.id)
        if k not in best or c.depth < best[k].depth:
            best[k] = c
    return list(best.values())


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

