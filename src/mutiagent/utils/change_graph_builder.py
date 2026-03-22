from __future__ import annotations

from mutiagent.graph.state import ChangeGraph, ChangeGraphEdge, ChangeGraphNode, FileChangeSummary


def file_node_id(path: str) -> str:
    return path


def symbol_node_id(file_path: str, entity_type: str, entity: str) -> str:
    return f"{file_path}:{entity_type}:{entity}"


def seed_node_id(file_path: str, seed_kind: str, name: str) -> str:
    return f"seed:{file_path}:{seed_kind}:{name}"


def focus_node_id(focus: str) -> str:
    return f"focus:{focus}"


def build_change_graph(change_analysis: list[FileChangeSummary]) -> ChangeGraph:
    """
    从 change_analysis 构建有向变更图：
    file --contains_change--> symbol --emits_seed--> seed
    symbol --test_focus--> focus:*（测试导向关注点，供影响扩散与优先级加权）
    """
    nodes: dict[str, ChangeGraphNode] = {}
    edges: list[ChangeGraphEdge] = []

    def add_node(n: ChangeGraphNode) -> None:
        nodes.setdefault(n.id, n)

    for fs in change_analysis:
        fid = file_node_id(fs.file)
        add_node(
            ChangeGraphNode(
                id=fid,
                kind="file",
                label=fs.file,
                meta={"change_count": len(fs.changes)},
            )
        )
        for ch in fs.changes:
            sid = symbol_node_id(fs.file, ch.type, ch.entity)
            add_node(
                ChangeGraphNode(
                    id=sid,
                    kind="symbol",
                    label=ch.entity,
                    meta={
                        "file": fs.file,
                        "entity_type": ch.type,
                        "change_type": ch.change_type,
                        "intent": ch.intent,
                        "semantic_tags": ch.semantic_tags,
                        "test_focus": ch.test_focus,
                    },
                )
            )
            edges.append(
                ChangeGraphEdge(src=fid, dst=sid, relation="contains_change", weight=1.0)
            )
            for sd in ch.impact_seeds:
                hid = seed_node_id(fs.file, sd.kind, sd.name)
                add_node(
                    ChangeGraphNode(
                        id=hid,
                        kind="seed",
                        label=f"{sd.kind}:{sd.name}",
                        meta={
                            "file": fs.file,
                            "seed_kind": sd.kind,
                            "name": sd.name,
                            "source": sd.source,
                            "from_entity": ch.entity,
                        },
                    )
                )
                edges.append(
                    ChangeGraphEdge(src=sid, dst=hid, relation="emits_seed", weight=0.85)
                )
            for tf in ch.test_focus:
                foc = focus_node_id(tf)
                add_node(
                    ChangeGraphNode(
                        id=foc,
                        kind="focus",
                        label=tf,
                        meta={"focus": tf},
                    )
                )
                edges.append(
                    ChangeGraphEdge(src=sid, dst=foc, relation="test_focus", weight=0.65)
                )

    return ChangeGraph(nodes=list(nodes.values()), edges=edges)


def graph_adjacency(graph: ChangeGraph) -> dict[str, list[tuple[str, str, float]]]:
    """src -> [(dst, relation, weight), ...]"""
    adj: dict[str, list[tuple[str, str, float]]] = {}
    for e in graph.edges:
        adj.setdefault(e.src, []).append((e.dst, e.relation, e.weight))
    return adj


def graph_reverse_adjacency(graph: ChangeGraph) -> dict[str, list[tuple[str, str, float]]]:
    """dst -> [(src, relation, weight), ...]"""
    radj: dict[str, list[tuple[str, str, float]]] = {}
    for e in graph.edges:
        radj.setdefault(e.dst, []).append((e.src, e.relation, e.weight))
    return radj


def symbol_test_focus_weight(symbol_id: str, graph: ChangeGraph) -> float:
    """由符号出发的 test_focus 边数量与权重聚合，用于粗粒度优先级 boost。"""
    adj = graph_adjacency(graph)
    total = 0.0
    for dst, rel, w in adj.get(symbol_id, []):
        if rel == "test_focus":
            total += w
    return total


def file_aggregate_focus_weight(file_path: str, graph: ChangeGraph) -> float:
    """某文件下所有变更符号的 test_focus 权重之和（上限由调用方截断）。"""
    total = 0.0
    for n in graph.nodes:
        if n.kind == "symbol" and n.meta.get("file") == file_path:
            total += symbol_test_focus_weight(n.id, graph)
    return total


def seed_graph_boost(seed_id: str, graph: ChangeGraph) -> float:
    """seed 经由 emits_seed 连回符号，继承其 test_focus 强度。"""
    radj = graph_reverse_adjacency(graph)
    boost = 0.0
    for src, rel, _w in radj.get(seed_id, []):
        if rel == "emits_seed":
            boost += symbol_test_focus_weight(src, graph) * 0.45
    return boost


def impact_candidate_graph_boost(kind: str, candidate_id: str, graph: ChangeGraph | None) -> float:
    """将图信息转为 0~1 左右的加分项，供规则排序 / 与 LLM 分数融合。"""
    if graph is None or not candidate_id:
        return 0.0
    if kind == "file":
        raw = file_aggregate_focus_weight(candidate_id, graph)
        return min(0.22, 0.06 * raw)
    if candidate_id.startswith("seed:"):
        raw = seed_graph_boost(candidate_id, graph)
        return min(0.2, 0.06 * raw)
    raw = symbol_test_focus_weight(candidate_id, graph)
    return min(0.25, 0.07 * raw)
