from __future__ import annotations

from mutiagent.nodes.impact_analysis_agent import _build_semantic_strategies


def test_data_processing_strategies_differ_by_seed_variable() -> None:
    a = _build_semantic_strategies("data_processing", "__init__", "typer/main.py", "seed:variable:TyperInfo")
    b = _build_semantic_strategies("data_processing", "__init__", "typer/main.py", "seed:variable:MarkupMode")
    assert len(a) >= 1 and len(b) >= 1
    assert a[0].scenario != b[0].scenario
    assert "TyperInfo" in a[0].scenario
    assert "MarkupMode" in b[0].scenario


def test_data_processing_includes_aspect_in_assertions() -> None:
    s = _build_semantic_strategies("data_processing", "callback", "pkg/mod.py", "seed:variable:foo")[0]
    assert "foo" in s.assert_.lower() or "foo" in s.scenario
