from __future__ import annotations

from mutiagent.graph.state import ChangeRecord, FileChangeSummary, ImpactSeed, WorkflowState
from mutiagent.nodes.impact_analysis_agent import analyze_impact, build_impact_graph
from mutiagent.utils.change_graph_builder import (
    build_change_graph,
    impact_candidate_graph_boost,
    seed_node_id,
    symbol_node_id,
)


def test_build_change_graph_edges_and_focus() -> None:
    fs = FileChangeSummary(
        file="src/App.jsx",
        changes=[
            ChangeRecord(
                entity="Navbar",
                type="function",
                change_type="MODIFY",
                semantic_tags=["logic_branch_changed"],
                test_focus=["conditional_render", "branch_coverage"],
                intent="BUG_FIX",
                impact_seeds=[
                    ImpactSeed(kind="function", name="close", source="diff"),
                ],
            )
        ],
    )
    g = build_change_graph([fs])
    ids = {n.id for n in g.nodes}
    assert "src/App.jsx" in ids
    sym = symbol_node_id("src/App.jsx", "function", "Navbar")
    assert sym in ids
    assert seed_node_id("src/App.jsx", "function", "close") in ids
    assert "focus:conditional_render" in ids
    rels = {(e.src, e.dst, e.relation) for e in g.edges}
    assert ("src/App.jsx", sym, "contains_change") in rels


def test_build_impact_graph_includes_non_pruned_seed() -> None:
    """非剪枝 seed 应进入对应符号的 semantic_unit.source。"""
    fs = FileChangeSummary(
        file="a.py",
        changes=[
            ChangeRecord(
                entity="f",
                type="function",
                change_type="MODIFY",
                semantic_tags=[],
                test_focus=[],
                intent="REFACTOR",
                impact_seeds=[ImpactSeed(kind="variable", name="user_id", source="ast")],
            )
        ],
    )
    state = WorkflowState(
        repo_path="/tmp",
        diff="",
        changed_files=["a.py"],
        change_analysis=[fs],
        change_graph=build_change_graph([fs]),
    )
    graph, catalog = build_impact_graph(state)
    assert graph and catalog
    assert any("seed:variable:user_id" in u.source for u in catalog)
    assert any(sym.semantic_unit_ids for g in graph for sym in g.symbols)


def test_impact_candidate_graph_boost_nonzero_for_focus() -> None:
    fs = FileChangeSummary(
        file="b.py",
        changes=[
            ChangeRecord(
                entity="g",
                type="function",
                change_type="MODIFY",
                semantic_tags=["dependency_call_changed"],
                test_focus=["integration"],
                intent="REFACTOR",
                impact_seeds=[],
            )
        ],
    )
    g = build_change_graph([fs])
    sid = symbol_node_id("b.py", "function", "g")
    assert impact_candidate_graph_boost("symbol", sid, g) > 0


def test_analyze_impact_builds_layered_impact_graph() -> None:
    fs = FileChangeSummary(
        file="src/App.jsx",
        changes=[
            ChangeRecord(
                entity="Navbar",
                type="function",
                change_type="MODIFY",
                semantic_tags=["logic_branch_changed", "dependency_call_changed"],
                test_focus=["branch_coverage"],
                intent="BUG_FIX",
                impact_seeds=[
                    ImpactSeed(kind="function", name="fetchUser", source="diff"),
                ],
            )
        ],
    )
    g = build_change_graph([fs])
    state = WorkflowState(
        repo_path="/tmp",
        diff="",
        changed_files=["src/App.jsx"],
        change_analysis=[fs],
        change_graph=g,
    )
    out = analyze_impact(state)
    assert out.impacted == []
    assert out.impacted_ranked == []
    assert out.impact_graph
    assert out.impact_graph[0].file == "src/App.jsx"
    sym = out.impact_graph[0].symbols[0]
    assert sym.name == "Navbar"
    assert sym.semantic_unit_ids
    cmap = {u.semantic_unit_id: u for u in out.semantic_units_catalog}
    u0 = cmap[sym.semantic_unit_ids[0]]
    assert u0.test_focus
    assert all(tf.derived_from for tf in u0.test_focus)
    assert u0.test_strategy
    assert u0.test_strategy[0].scenario
    assert u0.priority_score >= 0.0
    assert out.debug["impact"]["mode"] == "impact_graph_v4"
    assert out.debug["impact"].get("priority_score_top_5")
    assert out.impact_test_plan


def test_build_impact_graph_prunes_builtin_seed() -> None:
    fs = FileChangeSummary(
        file="x.py",
        changes=[
            ChangeRecord(
                entity="f",
                type="function",
                change_type="MODIFY",
                semantic_tags=[],
                intent="REFACTOR",
                impact_seeds=[ImpactSeed(kind="function", name="strip", source="diff")],
            )
        ],
    )
    state = WorkflowState(repo_path="/tmp", diff="", change_analysis=[fs])
    graph, catalog = build_impact_graph(state)
    assert graph == [] and catalog == [] or all("strip" not in u.source for u in catalog)
