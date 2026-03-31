from __future__ import annotations

from mutiagent.graph.state import ChangeRecord, FileChangeSummary, ImpactSeed, WorkflowState
from mutiagent.nodes import impact_analysis_agent as impact_analysis_mod
from mutiagent.nodes.impact_analysis_agent import _rule_impact, analyze_impact
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


def test_rule_impact_seed_ids_match_graph() -> None:
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
                impact_seeds=[ImpactSeed(kind="variable", name="x", source="ast")],
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
    cands = _rule_impact(state)
    seed_c = [c for c in cands if c.id.startswith("seed:")]
    assert any(c.id == "seed:a.py:variable:x" for c in seed_c)
    assert any(c.kind == "seed" for c in seed_c)


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


def test_analyze_impact_propagation_reaches_focus(monkeypatch) -> None:
    monkeypatch.setattr(impact_analysis_mod, "llm_available", lambda: False)
    fs = FileChangeSummary(
        file="src/App.jsx",
        changes=[
            ChangeRecord(
                entity="Navbar",
                type="function",
                change_type="MODIFY",
                semantic_tags=["logic_branch_changed"],
                test_focus=["branch_coverage"],
                intent="BUG_FIX",
                impact_seeds=[
                    ImpactSeed(kind="function", name="close", source="diff"),
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
    kinds = {c.kind for c in out.impacted}
    assert "focus" in kinds
    assert any(c.id.startswith("focus:") for c in out.impacted)
    assert out.debug["impact"]["propagated_candidate_count"] >= 1
    top = out.impacted_ranked[0]
    assert hasattr(top, "test_strategy") and isinstance(top.test_strategy, list)
