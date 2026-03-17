from __future__ import annotations

from collections import deque
from typing import Any

import networkx as nx

from mutiagent.graph.state import WorkflowState


def _build_nx_graph(nodes: list[str], edges: list[tuple[str, str]]) -> nx.DiGraph:
    g = nx.DiGraph()
    for n in nodes:
        g.add_node(n)
    for u, v in edges:
        g.add_edge(u, v)
    return g


def _seed_modules_from_changed_files(state: WorkflowState) -> list[str]:
    seeds: list[str] = []
    mod_to_file: dict[str, str] = state.module_graph.get("mod_to_file", {}) or {}
    for rel in state.changed_files:
        # 优先用扫描得到的映射
        for mod, fp in mod_to_file.items():
            if fp.replace("\\", "/").endswith("/" + rel) or fp.replace("\\", "/").endswith(rel):
                seeds.append(mod)
        # 兜底：按路径推断 module
        if rel.endswith(".py"):
            guess = rel[:-3].replace("/", ".")
            if guess.endswith(".__init__"):
                guess = guess[: -len(".__init__")]
            seeds.append(guess)
    # 去重保持顺序
    seen = set()
    out = []
    for s in seeds:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def code_change_graph_agent(state: WorkflowState) -> WorkflowState:
    """
    Code Change Graph (CCG)：
    - 节点：changed_file / module / function(symbol)
    - 边：change_affects（文件->模块）、import_dep（模块依赖）、call_dep（函数调用，轻量）

    MVP：以“变更文件/模块”为种子，从 module_dep_graph 与 call_graph 做 k-hop 邻域扩展生成子图。
    """
    module_nodes: list[str] = state.module_graph.get("nodes", []) or []
    module_edges: list[tuple[str, str]] = state.module_graph.get("edges", []) or []
    call_nodes: list[str] = state.call_graph.get("nodes", []) or []
    call_edges: list[tuple[str, str]] = state.call_graph.get("edges", []) or []

    mod_g = _build_nx_graph(module_nodes, module_edges)
    call_g = _build_nx_graph(call_nodes, call_edges)

    seed_modules = _seed_modules_from_changed_files(state)
    k = 2  # 邻域扩展深度（MVP）

    # 模块子图：从 seed_modules 向前（依赖）与向后（被依赖）各扩展 k hop
    mod_sub: set[str] = set(seed_modules)
    for direction in ("out", "in"):
        q = deque([(m, 0) for m in seed_modules])
        while q:
            m, d = q.popleft()
            if d >= k:
                continue
            nbrs = mod_g.successors(m) if direction == "out" else mod_g.predecessors(m)
            for n in nbrs:
                if n not in mod_sub:
                    mod_sub.add(n)
                    q.append((n, d + 1))

    # 函数子图：只取属于这些模块的函数节点（caller/callee 名形如 "mod:func"）
    def in_mod_sub(fn: str) -> bool:
        if ":" not in fn:
            return False
        mod, _ = fn.split(":", 1)
        return mod in mod_sub

    call_sub_nodes = {n for n in call_g.nodes if in_mod_sub(n)}
    call_sub_edges = [(u, v) for (u, v) in call_g.edges if u in call_sub_nodes and v in call_sub_nodes]

    # 组装 CCG（用统一节点ID编码类型，方便前端/可视化）
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for f in state.changed_files:
        nodes.append({"id": f"file:{f}", "type": "file", "label": f})

    for m in sorted(mod_sub):
        nodes.append({"id": f"module:{m}", "type": "module", "label": m})

    for fn in sorted(call_sub_nodes):
        nodes.append({"id": f"func:{fn}", "type": "function", "label": fn})

    # file -> module（change_affects）
    for f in state.changed_files:
        # 用 seed_modules 的推断结果连接（避免乱连所有模块）
        for m in seed_modules:
            edges.append({"source": f"file:{f}", "target": f"module:{m}", "type": "change_affects"})

    # module dependency edges
    for u, v in module_edges:
        if u in mod_sub and v in mod_sub:
            edges.append({"source": f"module:{u}", "target": f"module:{v}", "type": "import_dep"})

    # call edges
    for u, v in call_sub_edges:
        edges.append({"source": f"func:{u}", "target": f"func:{v}", "type": "call_dep"})

    state.ccg = {
        "seeds": {"changed_files": list(state.changed_files), "modules": seed_modules},
        "params": {"k_hop": k},
        "nodes": nodes,
        "edges": edges,
    }
    state.debug["ccg"] = {"node_count": len(nodes), "edge_count": len(edges), "k_hop": k}
    return state

