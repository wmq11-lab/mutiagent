from __future__ import annotations

from mutiagent.graph.state import (
    ChangeRecord,
    ExecutableTestStrategy,
    FileChangeSummary,
    ImpactGraphFile,
    ImpactGraphSymbol,
    ImpactSeed,
    ImpactTestPlanEntry,
    SemanticUnit,
    StructuredTestCase,
    WorkflowState,
)
from mutiagent.nodes.impact_analysis_agent import analyze_impact
from mutiagent.nodes.test_planning_agent import (
    build_coverage_matrix,
    build_execution_plan,
    build_mock_strategy,
    build_test_layers,
    ensure_p0_coverage,
    generate_test_cases,
    plan_tests,
    _merge_dup_template_cases,
)
from mutiagent.utils.change_graph_builder import build_change_graph


def test_build_execution_plan_and_mock_strategy() -> None:
    ep = build_execution_plan()
    assert ep.ci_blocking == ["P0"]
    assert "http" in build_mock_strategy()


def test_build_test_layers_from_impact_plan() -> None:
    uid = "api:call_x"
    unit = SemanticUnit(
        semantic_unit_id=uid,
        type="api",
        source="test.py:func",
        risk_score=0.5,
        priority_score=0.8,
        test_priority="P0",
        test_strategy=[
            ExecutableTestStrategy(scenario="超时", input="timeout=1", mock="http timeout", assert_="重试")
        ],
    )
    entry = ImpactTestPlanEntry(
        target="func",
        symbol_id="test.py:function:func",
        priority="P0",
        test_types=["integration", "mock"],
    )
    layers = build_test_layers([entry], {uid: unit}, {"test.py:function:func": [uid]})
    assert layers["integration"]
    assert entry.symbol_id in layers["integration"] or entry.symbol_id in layers.get("contract", [])


def test_p0_semantic_unit_gets_coverage() -> None:
    uid = "config:env_key"
    u = SemanticUnit(
        semantic_unit_id=uid,
        type="config",
        source="app.py:get_settings",
        risk_score=0.9,
        priority_score=0.85,
        test_priority="P0",
        test_strategy=[],
    )
    state = WorkflowState(
        repo_path="/tmp",
        diff="",
        impact_graph=[
            ImpactGraphFile(
                file="app.py",
                symbols=[
                    ImpactGraphSymbol(
                        name="get_settings",
                        symbol_id="app.py:function:get_settings",
                        semantic_unit_ids=[uid],
                    )
                ],
            )
        ],
        semantic_units_catalog=[u],
        impact_test_plan=[
            ImpactTestPlanEntry(
                target="get_settings",
                symbol_id="app.py:function:get_settings",
                priority="P0",
                test_types=["env"],
            )
        ],
    )
    uid_map = {uid: u}
    sym_map = {"app.py:function:get_settings": [uid]}
    plan_by = {"app.py:function:get_settings": state.impact_test_plan[0]}
    cases = generate_test_cases(state, uid_map, sym_map, plan_by)
    scope = {uid}
    cases2 = ensure_p0_coverage(cases, uid_map, scope)
    matrix = build_coverage_matrix(scope, cases2)
    row = next(r for r in matrix if r.semantic_unit == uid)
    assert row.covered_by


def test_plan_tests_end_to_end_after_impact() -> None:
    fs = FileChangeSummary(
        file="src/x.py",
        changes=[
            ChangeRecord(
                entity="f",
                type="function",
                change_type="MODIFY",
                semantic_tags=["dependency_call_changed"],
                test_focus=["integration"],
                intent="BUG_FIX",
                impact_seeds=[ImpactSeed(kind="function", name="g", source="diff")],
            )
        ],
    )
    g = build_change_graph([fs])
    state = WorkflowState(
        repo_path="/tmp",
        diff="",
        changed_files=["src/x.py"],
        change_analysis=[fs],
        change_graph=g,
    )
    out = analyze_impact(state)
    out.bug_patterns = []
    planned = plan_tests(out)
    assert planned.structured_test_plan.test_cases
    assert planned.structured_test_plan.coverage_matrix is not None
    assert planned.structured_test_plan.execution_plan.ci_blocking == ["P0"]
    assert planned.test_plan
    assert all(hasattr(p, "intent") for p in planned.test_plan)


def test_merge_dup_template_cases_combines_semantic_unit_ids() -> None:
    base_kw = dict(
        target="Typer",
        symbol_id="typer/main.py:class:Typer",
        layer="unit",
        priority="P1",
        input={"preconditions": "same"},
        mock={"type": "none", "behavior": "隔离"},
        assertions=["合法通过"],
        scenario="identical template",
    )
    a = StructuredTestCase(test_case_id="TC_X_001", semantic_unit_ids=["data_processing:a"], **base_kw)
    b = StructuredTestCase(test_case_id="TC_X_002", semantic_unit_ids=["data_processing:b"], **base_kw)
    out = _merge_dup_template_cases([a, b])
    assert len(out) == 1
    assert set(out[0].semantic_unit_ids) == {"data_processing:a", "data_processing:b"}
    assert out[0].test_case_id == "TC_X_001"
