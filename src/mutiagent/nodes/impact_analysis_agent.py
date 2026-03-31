from __future__ import annotations

import logging
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from mutiagent.graph.state import ChangeGraph, ChangeGraphNode, ImpactedCandidate, ImpactedItem, TestStrategyItem, WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_json
from mutiagent.utils.change_graph_builder import build_propagation_adjacency, impact_candidate_graph_boost

logger = logging.getLogger(__name__)

PROPAGATION_DECAY_BASE = 0.8


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _impact_log_file_path() -> Path:
    log_dir = _repo_root() / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "impact_analysis_agent.log"


def _impact_debug_enabled() -> bool:
    return os.getenv("MUTIAGENT_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}


def _impact_debug_log(message: str) -> None:
    if not _impact_debug_enabled():
        return
    line = f"[ImpactAnalysisAgent] {message}"
    print(line, file=sys.stderr, flush=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with _impact_log_file_path().open("a", encoding="utf-8") as fp:
            fp.write(f"{timestamp} {line}\n")
    except Exception:
        pass


def _max_propagation_hops() -> int:
    raw = os.environ.get("MUTIAGENT_IMPACT_MAX_PROPAGATION_HOPS", "3")
    try:
        return max(0, int(raw))
    except ValueError:
        return 3


def _intent_to_severity(intent: str) -> float:
    return {"BUG_FIX": 1.0, "FEATURE": 0.7, "REFACTOR": 0.5}.get(intent, 0.6)


def _legacy_base_score(depth: int) -> float:
    return max(0.1, 1.0 - 0.2 * int(depth))


def _node_index(graph: ChangeGraph) -> dict[str, ChangeGraphNode]:
    return {n.id: n for n in graph.nodes}


def _starting_graph_node_ids(state: WorkflowState) -> set[str]:
    ids: set[str] = set()
    for f in state.changed_files:
        ids.add(f)
    for fs in state.change_analysis:
        for ch in fs.changes:
            ids.add(f"{fs.file}:{ch.type}:{ch.entity}")
            for sd in ch.impact_seeds:
                ids.add(f"seed:{fs.file}:{sd.kind}:{sd.name}")
    return ids


def _graph_kind_to_impact_kind(gk: str) -> str:
    if gk in {"file", "symbol", "seed", "focus"}:
        return gk
    return "symbol"


def _node_text_blob(node: ChangeGraphNode | None) -> str:
    if node is None:
        return ""
    bits = [node.label, node.id]
    for k, v in node.meta.items():
        if isinstance(v, (list, tuple)):
            bits.extend(str(x) for x in v)
        else:
            bits.append(str(v))
    return " ".join(bits).lower()


def _infer_impact_types_from_text(text: str) -> set[str]:
    """config / exception_flow / external_io / data_processing"""
    t = text.lower()
    out: set[str] = set()
    if re.search(r"getenv|environ\[|os\.environ|dotenv|configparser|\benv\b", t):
        out.add("config")
    if re.search(r"\braise\b|\bexcept\b|\bthrow\b|exception|error\b|try:", t):
        out.add("exception_flow")
    if re.search(r"\.post\(|\.get\(|requests\.|httpx\.|aiohttp|urllib|fetch\(|grpc\.|openapi", t):
        out.add("external_io")
    if re.search(r"json\.|yaml\.|parse|deserialize|serialize|pickle\.|model_validate|schema", t):
        out.add("data_processing")
    return out


def _impact_types_for_node_id(
    node_id: str,
    nodes: dict[str, ChangeGraphNode],
    extra_text: str = "",
) -> set[str]:
    node = nodes.get(node_id)
    blob = _node_text_blob(node) + " " + node_id.lower() + " " + extra_text.lower()
    return _infer_impact_types_from_text(blob)


def _merge_impact_types_inherited(parent_types: set[str], node_id: str, nodes: dict[str, ChangeGraphNode]) -> list[str]:
    local = _impact_types_for_node_id(node_id, nodes)
    merged = set(parent_types) | local
    if "config" in local or "config" in parent_types:
        merged.add("config")
    return sorted(merged)


def _canonical_propagation_type(edge_relation: str, impact_types: list[str]) -> str:
    """边语义 + 影响类型 → call / data_flow / config / exception / test_focus"""
    if edge_relation == "direct":
        it = set(impact_types)
        if "exception_flow" in it:
            return "exception"
        if "config" in it:
            return "config"
        if "data_processing" in it:
            return "data_flow"
        if "external_io" in it:
            return "call"
        return "call"
    if edge_relation == "test_focus":
        return "test_focus"
    it = set(impact_types)
    if "exception_flow" in it:
        return "exception"
    if "config" in it:
        return "config"
    if "data_processing" in it:
        return "data_flow"
    if edge_relation in {"emits_seed", "reverse_emits_seed"}:
        return "data_flow"
    if "external_io" in it:
        return "call"
    return "call"


def _dependency_weight_for_propagation(canonical_pt: str) -> float:
    return {
        "call": 1.0,
        "data_flow": 1.1,
        "config": 1.2,
        "exception": 1.3,
        "test_focus": 1.0,
    }.get(canonical_pt, 1.0)


def _dependency_weight_candidate(c: ImpactedCandidate) -> float:
    """综合 canonical propagation 与 impact_type 取有效权重（乘子，可略高于 1）。"""
    canon = _canonical_propagation_type(c.propagation_type, c.impact_type)
    w = _dependency_weight_for_propagation(canon)
    for it in c.impact_type:
        if it == "config":
            w = max(w, 1.2)
        elif it == "exception_flow":
            w = max(w, 1.3)
        elif it == "external_io":
            w = max(w, 1.15)
        elif it == "data_processing":
            w = max(w, 1.1)
    return min(w, 1.35)


def _propagation_decay(depth: int) -> float:
    return PROPAGATION_DECAY_BASE ** max(0, int(depth))


def _frequency_weight(hits: int, max_hits: int) -> float:
    if max_hits <= 0:
        return 1.0
    if hits <= 1:
        return 1.0
    norm = (hits - 1) / float(max(1, max_hits - 1))
    return min(1.2, 1.0 + 0.15 * norm)


def _centrality_map(graph: ChangeGraph) -> tuple[dict[str, int], int]:
    deg: dict[str, int] = defaultdict(int)
    for e in graph.edges:
        deg[e.src] += 1
        deg[e.dst] += 1
    for n in graph.nodes:
        deg.setdefault(n.id, 0)
    mx = max(deg.values()) if deg else 1
    return dict(deg), max(mx, 1)


def _centrality_factor(node_id: str, deg_map: dict[str, int], max_deg: int) -> float:
    d = float(deg_map.get(node_id, 0))
    norm = d / float(max_deg) if max_deg else 0.0
    return 0.55 + 0.45 * min(1.0, norm)


def _severity_for_candidate(c: ImpactedCandidate, state: WorkflowState, nodes: dict[str, ChangeGraphNode]) -> float:
    node = nodes.get(c.id)
    if node and node.kind == "file":
        best = 0.45
        for fs in state.change_analysis:
            if fs.file != c.id:
                continue
            for ch in fs.changes:
                best = max(best, _intent_to_severity(ch.intent))
        return best if best > 0.45 else 0.6
    if node and node.kind == "symbol":
        intent = str(node.meta.get("intent", "REFACTOR"))
        return _intent_to_severity(intent)
    if node and node.kind == "seed":
        ent = str(node.meta.get("from_entity", ""))
        fp = str(node.meta.get("file", ""))
        for fs in state.change_analysis:
            if fs.file != fp:
                continue
            for ch in fs.changes:
                if ch.entity == ent:
                    return _intent_to_severity(ch.intent)
        return 0.65
    if node and node.kind == "focus":
        return 0.55
    for fs in state.change_analysis:
        for ch in fs.changes:
            sym_id = f"{fs.file}:{ch.type}:{ch.entity}"
            if sym_id == c.id:
                return _intent_to_severity(ch.intent)
    return 0.6


def _collect_repo_scan_text(state: WorkflowState) -> str:
    parts: list[str] = []
    for fs in state.change_analysis:
        parts.append(fs.file)
        for ch in fs.changes:
            parts.append(ch.entity)
            parts.extend(ch.semantic_tags)
            parts.extend(ch.test_focus)
            for sd in ch.impact_seeds:
                parts.append(sd.name)
    return " ".join(parts).lower()


def _infer_system_impact(scan: str) -> list[str]:
    tags: set[str] = set()
    if re.search(r"\bopenai\b|\banthropic\b|\bgemini\b|\bclaude\b|\bgpt-4\b", scan):
        tags.add("multi_provider_routing")
    if re.search(r"fallback_base_url|fallback_auth|fallback_provider|retry.*provider", scan):
        tags.add("fallback_mechanism")
    if re.search(r"_format_multimodal_message|multimodal|image_url|vision", scan):
        tags.add("multimodal_pipeline")
    if re.search(r"getenv|environ|dotenv|configparser|\benv\b", scan):
        tags.add("configuration_system")
    if re.search(r"requests\.|httpx|aiohttp|grpc|openapi|fetch\(|http://|https://", scan):
        tags.add("external_dependency")
    return sorted(tags)


def _apply_impact_type_boost_after_graph(score: float, c: ImpactedCandidate) -> float:
    s = float(score)
    for it in c.impact_type:
        if it == "exception_flow":
            s += 0.1
        elif it == "config":
            s += 0.08
    if c.kind == "focus":
        s -= 0.06
    return max(0.0, min(1.0, s))


def _merge_score_with_graph(base: float, c: ImpactedCandidate, state: WorkflowState) -> float:
    g = state.change_graph
    boost = impact_candidate_graph_boost(c.kind, c.id, g)
    return max(0.0, min(1.0, base + boost))


def _reason_for_item(c: ImpactedCandidate, score_breakdown: str) -> str:
    path_s = " > ".join(c.propagation_path[:5]) if c.propagation_path else c.id
    types_s = ",".join(c.impact_type) if c.impact_type else "n/a"
    return f"{c.via} | path=[{path_s}] | prop_type={c.propagation_type} | types=[{types_s}] | {score_breakdown}"


def _dedupe_candidates(candidates: list[ImpactedCandidate]) -> list[ImpactedCandidate]:
    freq = Counter(c.id for c in candidates)
    best: dict[tuple[str, str], ImpactedCandidate] = {}
    for candidate in candidates:
        key = (candidate.kind, candidate.id)
        if key not in best:
            c = candidate.model_copy(deep=True)
            meta = dict(c.meta)
            meta["frequency_hits"] = freq[c.id]
            c.meta = meta
            best[key] = c
            continue
        old = best[key]
        if candidate.depth < old.depth:
            chosen = candidate
        elif candidate.depth > old.depth:
            chosen = old
        else:
            chosen = old if len(old.propagation_path) <= len(candidate.propagation_path) else candidate
        merged_types = sorted(set(old.impact_type) | set(candidate.impact_type))
        meta = dict(chosen.meta)
        meta["frequency_hits"] = freq[candidate.id]
        best[key] = chosen.model_copy(
            update={
                "impact_type": merged_types,
                "meta": meta,
            },
            deep=True,
        )
    return list(best.values())


def _enrich_base_candidate(
    c: ImpactedCandidate,
    nodes: dict[str, ChangeGraphNode],
) -> ImpactedCandidate:
    path = [c.id]
    pdepth = 0
    itypes = sorted(_impact_types_for_node_id(c.id, nodes, c.via))
    edge_hint = "emits_seed" if c.kind == "seed" else "direct"
    canon = _canonical_propagation_type(edge_hint, itypes)
    return c.model_copy(
        update={
            "propagation_path": path,
            "propagation_depth": pdepth,
            "propagation_type": canon,
            "impact_type": itypes,
        },
        deep=True,
    )


def _rule_impact(state: WorkflowState) -> list[ImpactedCandidate]:
    nodes = _node_index(state.change_graph) if state.change_graph else {}
    out: list[ImpactedCandidate] = []

    for f in state.changed_files:
        out.append(
            ImpactedCandidate(
                kind="file",
                id=f,
                via="changed_file",
                depth=0,
            )
        )

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
                        kind="seed",
                        id=seed_id,
                        via=f"impact_seed:{change.entity}",
                        depth=1,
                    )
                )

    enriched = [_enrich_base_candidate(c, nodes) for c in out]
    return _dedupe_candidates(enriched)


def _propagate_from_graph(state: WorkflowState, graph: ChangeGraph) -> list[ImpactedCandidate]:
    nodes = _node_index(graph)
    adj = build_propagation_adjacency(graph)
    max_hops = _max_propagation_hops()
    starts = _starting_graph_node_ids(state) & nodes.keys()
    propagated: list[ImpactedCandidate] = []

    queue: list[tuple[str, list[str], str, int, frozenset[str]]] = []
    for s in starts:
        n0 = nodes.get(s)
        if n0 is None:
            continue
        if n0.kind == "file":
            d0 = 0
        elif n0.kind == "symbol":
            d0 = 0
        elif n0.kind == "seed":
            d0 = 1
        else:
            d0 = 2
        root_types = frozenset(_impact_types_for_node_id(s, nodes))
        queue.append((s, [s], "direct", d0, root_types))

    seen_states: set[tuple[str, str]] = set()

    while queue:
        cur, path, last_edge_rel, cand_depth, parent_types = queue.pop(0)
        if len(path) - 1 >= max_hops:
            continue
        for nxt, rel, _w in adj.get(cur, []):
            if nxt in path:
                continue
            new_path = path + [nxt]
            if len(new_path) - 1 > max_hops:
                continue
            sig = (nxt, ":".join(new_path))
            if sig in seen_states:
                continue
            seen_states.add(sig)

            nd = nodes.get(nxt)
            if nd is None:
                continue
            ik: Any = _graph_kind_to_impact_kind(nd.kind)
            prop_depth = len(new_path) - 1
            merged_types = _merge_impact_types_inherited(set(parent_types), nxt, nodes)
            canon_pt = _canonical_propagation_type(rel, merged_types)

            cand = ImpactedCandidate(
                kind=ik,
                id=nxt,
                via=f"propagated_from:{cur}",
                depth=cand_depth + 1,
                propagation_path=list(new_path),
                propagation_depth=prop_depth,
                propagation_type=canon_pt,
                impact_type=merged_types,
            )
            propagated.append(cand)
            queue.append((nxt, new_path, rel, cand_depth + 1, frozenset(merged_types)))

    return propagated


def _synthetic_focus_from_impact_types(sources: list[ImpactedCandidate]) -> list[ImpactedCandidate]:
    """由 impact_type 推导测试关注点候选（kind=focus, propagation_type=test_focus）。"""
    out: list[ImpactedCandidate] = []
    specs: list[tuple[str, str, str]] = [
        ("config", "focus:env_missing", "env_missing"),
        ("config", "focus:fallback", "fallback"),
        ("exception_flow", "focus:error_paths", "error_paths"),
        ("exception_flow", "focus:exception_assertions", "exception_assertions"),
        ("external_io", "focus:integration", "integration"),
        ("external_io", "focus:retry_timeout", "retry_timeout"),
        ("data_processing", "focus:boundary", "boundary"),
        ("data_processing", "focus:invalid_input", "invalid_input"),
    ]
    for c in sources:
        if c.kind == "focus":
            continue
        for itype, fid, _label in specs:
            if itype not in c.impact_type:
                continue
            new_path = list(c.propagation_path or [c.id]) + [fid]
            out.append(
                ImpactedCandidate(
                    kind="focus",
                    id=fid,
                    via=f"derived_test_focus:{c.id}",
                    depth=c.depth + 1,
                    propagation_path=new_path,
                    propagation_depth=c.propagation_depth + 1,
                    propagation_type="test_focus",
                    impact_type=sorted(set(c.impact_type) | {itype}),
                )
            )
    return out


def _graph_product_score(
    c: ImpactedCandidate,
    state: WorkflowState,
    nodes: dict[str, ChangeGraphNode],
    deg_map: dict[str, int],
    max_deg: int,
    max_freq: int,
) -> float:
    base_score = 1.0
    decay = _propagation_decay(c.propagation_depth)
    dep_w = _dependency_weight_candidate(c)
    sev = _severity_for_candidate(c, state, nodes)
    cent = _centrality_factor(c.id, deg_map, max_deg)
    hits = int(c.meta.get("frequency_hits", 1))
    freq_w = _frequency_weight(hits, max_freq)
    raw = base_score * decay * dep_w * sev * cent * freq_w
    return max(0.0, min(1.0, raw))


def _score_candidate(
    c: ImpactedCandidate,
    state: WorkflowState,
    nodes: dict[str, ChangeGraphNode],
    deg_map: dict[str, int],
    max_deg: int,
    max_freq: int,
) -> tuple[float, str]:
    if state.change_graph is None:
        base = _legacy_base_score(c.depth)
        merged = _merge_score_with_graph(base, c, state)
        final = _apply_impact_type_boost_after_graph(merged, c)
        return final, f"legacy_depth={c.depth}"
    init = _graph_product_score(c, state, nodes, deg_map, max_deg, max_freq)
    after_graph = _merge_score_with_graph(init, c, state)
    final = _apply_impact_type_boost_after_graph(after_graph, c)
    br = (
        f"product(decay={_propagation_decay(c.propagation_depth):.3f},dep={_dependency_weight_candidate(c):.2f})="
        f"{init:.3f}; after_graph_boost={after_graph:.3f}; prop_depth={c.propagation_depth}; "
        f"prop_type={c.propagation_type}"
    )
    return final, br


def _impact_type_distribution(candidates: list[ImpactedCandidate]) -> dict[str, int]:
    dist: dict[str, int] = defaultdict(int)
    for c in candidates:
        for t in c.impact_type:
            dist[t] += 1
    return dict(sorted(dist.items(), key=lambda x: (-x[1], x[0])))


def _test_strategies_for_ranked(c: ImpactedCandidate | None, sc: float) -> list[TestStrategyItem]:
    pr = max(0.0, min(1.0, sc))
    if c is None:
        return [TestStrategyItem(type="regression_smoke", target="project", priority=pr)]

    strategies: list[TestStrategyItem] = []

    if c.kind == "focus":
        lid = c.id
        if "error_paths" in lid or "exception" in lid:
            strategies.append(TestStrategyItem(type="error_path_test", target=c.id, priority=min(0.93, pr + 0.06)))
        if "integration" in lid or "retry" in lid:
            strategies.append(TestStrategyItem(type="integration_regression", target=c.id, priority=min(0.91, pr + 0.05)))
        if "boundary" in lid or "invalid_input" in lid:
            strategies.append(TestStrategyItem(type="boundary_input_test", target=c.id, priority=min(0.9, pr + 0.04)))
        if "env_missing" in lid or "fallback" in lid:
            strategies.append(TestStrategyItem(type="env_missing_fallback", target=c.id, priority=min(0.92, pr + 0.05)))
        if not strategies:
            strategies.append(TestStrategyItem(type="focus_regression", target=c.id, priority=pr))

    for it in c.impact_type:
        if it == "config":
            strategies.append(TestStrategyItem(type="env_missing_fallback", target=c.id, priority=min(0.92, pr + 0.08)))
        elif it == "exception_flow":
            strategies.append(TestStrategyItem(type="exception_assertion", target=c.id, priority=min(0.93, pr + 0.09)))
        elif it == "external_io":
            strategies.append(TestStrategyItem(type="integration_test", target=c.id, priority=min(0.91, pr + 0.07)))
            strategies.append(TestStrategyItem(type="retry_test", target=c.id, priority=min(0.88, pr + 0.05)))
        elif it == "data_processing":
            strategies.append(TestStrategyItem(type="boundary_test", target=c.id, priority=min(0.9, pr + 0.06)))
            strategies.append(TestStrategyItem(type="invalid_input_test", target=c.id, priority=min(0.89, pr + 0.05)))

    if not strategies:
        strategies.append(TestStrategyItem(type="regression_smoke", target=c.id, priority=pr))

    seen: set[str] = set()
    uniq: list[TestStrategyItem] = []
    for s in strategies:
        if s.type in seen:
            continue
        seen.add(s.type)
        uniq.append(s)
    return uniq[:8]


def _find_candidate(cid: str, candidates: list[ImpactedCandidate]) -> ImpactedCandidate | None:
    for c in candidates:
        if c.id == cid:
            return c
    return None


def _finalize_ranked_item(
    item: ImpactedItem,
    cand: ImpactedCandidate | None,
    heuristic_score: float,
) -> ImpactedItem:
    ts = item.test_strategy if item.test_strategy else _test_strategies_for_ranked(cand, item.score)
    itypes = list(cand.impact_type) if cand else list(item.impact_type)
    return item.model_copy(
        update={
            "test_strategy": ts,
            "impact_type": itypes,
            "initial_score": item.initial_score if item.initial_score is not None else heuristic_score,
        },
        deep=True,
    )


def _llm_rank(
    state: WorkflowState,
    candidates: list[ImpactedCandidate],
    heuristic_scores: dict[str, float],
    breakdown_by_id: dict[str, str],
) -> tuple[list[ImpactedItem], str]:
    system = (
        "你是资深软件测试与影响分析专家。给定变更图传播后的影响候选，请输出 JSON：{\"impacted\": [...]}。"
        "每个元素字段：kind(file|symbol|seed|focus)、id、score(0-1)、reason、"
        "test_strategy（可选，数组，元素含 type, target, priority 0-1）、system_impact（可选字符串数组）、"
        "impact_type（可选字符串数组，取值倾向 config/exception_flow/external_io/data_processing）。"
        "可依据 propagation_path、impact_type、initial_score 修正 score 并写清理由；"
        "不要添加输入中不存在的 id。"
    )
    graph_blob: dict | None = None
    if state.change_graph is not None:
        graph_blob = state.change_graph.model_dump()
    cand_blob = []
    for c in candidates:
        d = c.model_dump()
        d["initial_score"] = heuristic_scores.get(c.id, 0.5)
        cand_blob.append(d)
    payload = {
        "repo_path": state.repo_path,
        "changed_files": state.changed_files,
        "diff_stats": state.debug.get("diff_stats", {}),
        "change_analysis": [item.model_dump() for item in state.change_analysis],
        "change_graph": graph_blob,
        "candidates": cand_blob,
    }
    _impact_debug_log(
        f"llm_rank request candidates={len(candidates)} graph={'yes' if graph_blob else 'no'}"
    )
    resp = chat_json(system, f"输入如下（JSON）：\n{payload}\n\n请输出JSON：{{\"impacted\": [...]}}")
    impacted = resp.get("impacted", [])
    scan = _collect_repo_scan_text(state)
    global_sys = _infer_system_impact(scan)
    out: list[ImpactedItem] = []
    for it in impacted:
        if not isinstance(it, dict):
            continue
        try:
            kind = it.get("kind")
            cid = it.get("id")
            if kind not in {"file", "symbol", "seed", "focus"} or not cid:
                continue
            ts_raw = []
            for x in it.get("test_strategy", []):
                if not isinstance(x, dict) or not x.get("type"):
                    continue
                pr = float(x.get("priority", 0.5))
                pr = max(0.0, min(1.0, pr))
                ts_raw.append(
                    TestStrategyItem(
                        type=str(x.get("type")),
                        target=str(x.get("target", cid)),
                        priority=pr,
                    )
                )
            llm_itypes = [str(x) for x in it.get("impact_type", []) if isinstance(x, str)]
            item = ImpactedItem(
                kind=kind,
                id=cid,
                score=float(it.get("score", 0.5)),
                reason=str(it.get("reason", "")),
                test_strategy=ts_raw,
                system_impact=[str(x) for x in it.get("system_impact", []) if isinstance(x, str)],
                initial_score=heuristic_scores.get(str(cid)),
                impact_type=llm_itypes,
            )
        except Exception:
            continue
        cand = _find_candidate(item.id, candidates)
        h = heuristic_scores.get(item.id, 0.5)
        sc = float(item.score)
        sc = max(0.0, min(1.0, 0.5 * sc + 0.5 * h))
        if cand is not None:
            sc = _merge_score_with_graph(sc, cand, state)
            sc = _apply_impact_type_boost_after_graph(sc, cand)
        ts = item.test_strategy if item.test_strategy else _test_strategies_for_ranked(cand, sc)
        si = sorted(set(item.system_impact) | set(global_sys))
        merged_types = sorted(set(item.impact_type) | set(cand.impact_type if cand else []))
        out.append(
            _finalize_ranked_item(
                ImpactedItem(
                    kind=item.kind,
                    id=item.id,
                    score=sc,
                    reason=item.reason or (_reason_for_item(cand, "llm+heuristic") if cand else "llm"),
                    test_strategy=ts,
                    system_impact=si,
                    initial_score=h,
                    impact_type=merged_types,
                ),
                cand,
                h,
            )
        )
    if out:
        _impact_debug_log(f"llm_rank parsed impacted={len(out)}")
        return out, "llm"
    logger.info(
        "ImpactAnalysisAgent: LLM 返回的 impacted 为空或无法解析，改用启发式排序 (candidates=%s)",
        len(candidates),
    )
    _impact_debug_log("llm_rank empty or unparseable impacted -> heuristic fallback")
    return _items_from_heuristic_scores(state, candidates, heuristic_scores, breakdown_by_id), "llm_empty_parse"


def _items_from_heuristic_scores(
    state: WorkflowState,
    candidates: list[ImpactedCandidate],
    heuristic_scores: dict[str, float],
    breakdown_by_id: dict[str, str],
) -> list[ImpactedItem]:
    scan = _collect_repo_scan_text(state)
    global_sys = _infer_system_impact(scan)
    items: list[ImpactedItem] = []
    for c in candidates:
        sc = heuristic_scores.get(c.id, 0.5)
        br = breakdown_by_id.get(c.id, "heuristic")
        raw_item = ImpactedItem(
            kind=c.kind,
            id=c.id,
            score=sc,
            reason=_reason_for_item(c, br),
            test_strategy=[],
            system_impact=list(global_sys),
            initial_score=sc,
            impact_type=list(c.impact_type),
        )
        items.append(_finalize_ranked_item(raw_item, c, sc))
    return items


def analyze_impact(state: WorkflowState) -> WorkflowState:
    started = time.perf_counter()
    base = _rule_impact(state)
    propagated: list[ImpactedCandidate] = []
    if state.change_graph is not None:
        propagated = _propagate_from_graph(state, state.change_graph)

    merged_core = _dedupe_candidates(base + propagated)
    synthetic_focus = _synthetic_focus_from_impact_types(merged_core)
    merged = _dedupe_candidates(merged_core + synthetic_focus)
    state.impacted = merged

    test_focus_count = sum(1 for c in merged if c.kind == "focus")
    type_dist = _impact_type_distribution(merged)

    _impact_debug_log(
        f"start repo={state.repo_path} base_candidates={len(base)} "
        f"propagated={len(propagated)} synthetic_focus={len(synthetic_focus)} merged={len(merged)} "
        f"llm_available={llm_available()}"
    )

    nodes = _node_index(state.change_graph) if state.change_graph else {}
    deg_map, max_deg = _centrality_map(state.change_graph) if state.change_graph else ({}, 1)
    freq_map = dict(Counter(c.id for c in merged))
    max_freq = max(freq_map.values()) if freq_map else 1

    heuristic_scores: dict[str, float] = {}
    breakdown_by_id: dict[str, str] = {}
    for c in merged:
        sc, br = _score_candidate(c, state, nodes, deg_map, max_deg, max_freq)
        heuristic_scores[c.id] = sc
        breakdown_by_id[c.id] = br

    ranking_mode = "heuristic_only"
    llm_error: str | None = None
    if llm_available():
        try:
            ranked, ranking_mode = _llm_rank(state, merged, heuristic_scores, breakdown_by_id)
        except Exception as exc:
            llm_error = f"{type(exc).__name__}: {exc}"
            ranking_mode = "llm_error_fallback"
            logger.warning(
                "ImpactAnalysisAgent: LLM 排序失败，改用启发式: %s",
                llm_error,
                exc_info=True,
            )
            _impact_debug_log(f"LLM ranking exception -> heuristic: {llm_error}")
            ranked = _items_from_heuristic_scores(state, merged, heuristic_scores, breakdown_by_id)
    else:
        ranked = _items_from_heuristic_scores(state, merged, heuristic_scores, breakdown_by_id)
        ranking_mode = "heuristic_only"

    ranked_sorted = sorted(ranked, key=lambda x: x.score, reverse=True)[:15]
    state.impacted_ranked = ranked_sorted
    elapsed = round(time.perf_counter() - started, 3)
    top_preview = [f"{x.kind}:{x.id}" for x in ranked_sorted[:5]]
    _impact_debug_log(
        f"done ranking_mode={ranking_mode} ranked={len(ranked_sorted)} "
        f"elapsed_s={elapsed} top5={top_preview}"
    )
    logger.debug(
        "ImpactAnalysisAgent: 完成 mode=%s candidates=%s ranked=%s 耗时=%ss",
        ranking_mode,
        len(merged),
        len(ranked_sorted),
        elapsed,
    )
    state.debug["impact"] = {
        "candidate_count": len(merged),
        "ranked_count": len(ranked_sorted),
        "used_llm": llm_available(),
        "change_graph_used": state.change_graph is not None,
        "propagation_hops_max": _max_propagation_hops(),
        "base_candidate_count": len(base),
        "propagated_candidate_count": len(propagated),
        "synthetic_focus_candidate_count": len(synthetic_focus),
        "test_focus_count": test_focus_count,
        "impact_type_distribution": type_dist,
        "ranking_mode": ranking_mode,
        "llm_error": llm_error,
        "elapsed_seconds": elapsed,
    }
    return state
