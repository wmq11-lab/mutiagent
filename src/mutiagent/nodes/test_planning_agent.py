from __future__ import annotations

import json
import re
from collections import defaultdict
from typing import Any, Callable

from mutiagent.graph.state import (
    DEFAULT_TEST_PLAN_MOCK_STRATEGY,
    CoverageMatrixEntry,
    ExecutableTestStrategy,
    ImpactTestPlanEntry,
    SemanticUnit,
    StructuredTestCase,
    StructuredTestPlanRoot,
    StructuredTestPlanSummary,
    TestLayerKind,
    TestPlanItem,
    TestPriorityTier,
    WorkflowState,
)
from mutiagent.graph.state import ExecutionPlanTiers


def _catalog_map(state: WorkflowState) -> dict[str, SemanticUnit]:
    return {u.semantic_unit_id: u for u in state.semantic_units_catalog}


def _symbol_to_unit_ids(state: WorkflowState) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for gf in state.impact_graph or []:
        for sym in gf.symbols:
            out[sym.symbol_id] = list(sym.semantic_unit_ids)
    return out


def _plan_index(impact_test_plan: list[ImpactTestPlanEntry]) -> dict[str, ImpactTestPlanEntry]:
    """symbol_id 优先；其次 target 短名（用于无 symbol_id 的退化）。"""
    by: dict[str, ImpactTestPlanEntry] = {}
    for e in impact_test_plan:
        if e.symbol_id:
            by[e.symbol_id] = e
        by.setdefault(f"name:{e.target}", e)
    return by


def _slug_token(s: str, max_len: int = 28) -> str:
    t = re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").upper()
    if not t:
        t = "SU"
    return t[:max_len]


def _infer_mock_type(text: str) -> str:
    sl = text.lower()
    if any(k in sl for k in ("http", "https", "requests", "httpx", "aiohttp", "respx", "urllib")):
        return "http"
    if any(k in sl for k in ("getenv", "environ", "env", "monkeypatch", "settings")):
        return "env"
    if any(k in sl for k in ("time", "sleep", "datetime", "freezegun")):
        return "time"
    if any(k in sl for k in ("raise", "exception", "error", "pytest.raises", "patch(")):
        return "exception"
    return "none"


def _structured_input(text: str) -> dict[str, Any]:
    raw = (text or "").strip()
    if not raw:
        return {}
    parts = re.split(r"[;；\n]+", raw)
    out: dict[str, Any] = {}
    notes: list[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if ":" in p:
            k, v = p.split(":", 1)
            k, v = k.strip(), v.strip()
            if k:
                out[k] = v
            else:
                notes.append(p)
        else:
            notes.append(p)
    if notes:
        out.setdefault("preconditions", notes if len(notes) > 1 else notes[0])
    if not out:
        return {"description": raw}
    return out


def _structured_assertions(text: str) -> list[str]:
    raw = (text or "").strip()
    if not raw:
        return []
    bits = re.split(r"[;；\n]+", raw)
    return [b.strip() for b in bits if b.strip()]


def _mock_payload(strategy_line: str) -> dict[str, Any]:
    s = strategy_line or ""
    return {"type": _infer_mock_type(s), "behavior": s[:500]}


def build_mock_strategy() -> dict[str, str]:
    return dict(DEFAULT_TEST_PLAN_MOCK_STRATEGY)


def build_execution_plan() -> ExecutionPlanTiers:
    return ExecutionPlanTiers(
        ci_blocking=["P0"],
        nightly=["P1"],
        low_priority=["P2"],
    )


def _primary_layer_for_unit(unit: SemanticUnit) -> TestLayerKind:
    """语义单元类型 → 用例主分层（规则映射）。"""
    sid = unit.semantic_unit_id.lower()
    if unit.type == "api":
        if any(k in sid for k in ("schema", "openapi", "swagger", "json_schema", "contract")):
            return "contract"
        return "integration"
    if unit.type == "config":
        return "integration"
    if unit.type == "exception":
        return "unit"
    if unit.type == "data_processing":
        return "unit"
    return "unit"


def _layers_for_symbol_entry(
    entry: ImpactTestPlanEntry,
    units: list[SemanticUnit],
) -> set[TestLayerKind]:
    """合并 impact_test_plan.test_types 与语义单元类型。"""
    layers: set[TestLayerKind] = set()
    tt = set(entry.test_types or [])

    if "unit" in tt or "exception" in tt:
        layers.add("unit")
    if "integration" in tt or "mock" in tt:
        layers.add("integration")
    if "env" in tt:
        layers.add("integration")

    for u in units:
        pl = _primary_layer_for_unit(u)
        layers.add(pl)
        if u.type == "exception" and "exception" in tt:
            layers.add("unit")
        if u.type == "api" and pl == "contract":
            layers.add("contract")

    tier = entry.priority
    if tier == "P0" and any(u.integration_risk for u in units):
        layers.add("e2e")

    if not layers:
        layers.add("unit")
    return layers


def build_test_layers(
    impact_test_plan: list[ImpactTestPlanEntry],
    uid_to_unit: dict[str, SemanticUnit],
    symbol_to_units: dict[str, list[str]],
) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {"unit": [], "integration": [], "contract": [], "e2e": []}
    seen: dict[str, set[str]] = {k: set() for k in buckets}

    for entry in impact_test_plan:
        uids = symbol_to_units.get(entry.symbol_id, []) if entry.symbol_id else []
        units = [uid_to_unit[i] for i in uids if i in uid_to_unit]
        if not units and entry.symbol_id:
            # 无映射时仍可根据 test_types 分层
            units = []
        layer_set = _layers_for_symbol_entry(entry, units)
        target_ref = entry.symbol_id or entry.target
        for layer in layer_set:
            if target_ref not in seen[layer]:
                buckets[layer].append(target_ref)
                seen[layer].add(target_ref)

    return buckets


def augment_test_layers_from_cases(
    layers: dict[str, list[str]],
    cases: list[StructuredTestCase],
) -> dict[str, list[str]]:
    """当 impact_test_plan 为空或分层未命中时，从用例反推目标分层。"""
    if any(layers.get(k) for k in ("unit", "integration", "contract", "e2e")):
        return layers
    seen: dict[str, set[str]] = {k: set() for k in ("unit", "integration", "contract", "e2e")}
    out = {k: list(v) for k, v in layers.items()}
    for c in cases:
        tid = c.symbol_id or c.target
        if not tid:
            continue
        layer = c.layer if c.layer in seen else "unit"
        if tid not in seen[layer]:
            out.setdefault(layer, []).append(tid)
            seen[layer].add(tid)
    return out


def _make_id_allocator(existing: list[StructuredTestCase] | None = None) -> Callable[[str], str]:
    counts: dict[str, int] = defaultdict(int)
    if existing:
        for c in existing:
            m = re.match(r"^TC_([A-Z0-9_]+)_(\d{3})$", c.test_case_id)
            if m:
                pfx = m.group(1)
                counts[pfx] = max(counts[pfx], int(m.group(2)))

    def alloc(semantic_unit_id: str) -> str:
        p = _slug_token(semantic_unit_id)
        counts[p] += 1
        return f"TC_{p}_{counts[p]:03d}"

    return alloc


def _tier_rank(t: TestPriorityTier) -> int:
    return {"P0": 0, "P1": 1, "P2": 2}.get(t, 3)


def _priority_for_symbol(
    symbol_id: str,
    plan_by: dict[str, ImpactTestPlanEntry],
    units: list[SemanticUnit],
) -> TestPriorityTier:
    e = plan_by.get(symbol_id) or plan_by.get(f"name:{symbol_id}")
    if e:
        return e.priority
    if not units:
        return "P2"
    return min((u.test_priority for u in units), key=_tier_rank)


def _synthetic_strategies(unit: SemanticUnit) -> list[ExecutableTestStrategy]:
    if unit.test_strategy:
        return list(unit.test_strategy)
    lines: list[str] = []
    for tf in unit.test_focus[:2]:
        lines.append(f"{tf.type}（{tf.derived_from[:120]}）")
    scen = "；".join(lines) if lines else f"覆盖语义单元 {unit.semantic_unit_id}"
    return [
        ExecutableTestStrategy(
            scenario=scen,
            input="",
            mock="",
            assert_="行为符合变更后预期；关键分支与异常路径需覆盖",
        )
    ]


def generate_test_cases(
    state: WorkflowState,
    uid_to_unit: dict[str, SemanticUnit],
    symbol_to_units: dict[str, list[str]],
    plan_by: dict[str, ImpactTestPlanEntry],
) -> list[StructuredTestCase]:
    alloc = _make_id_allocator()
    cases: list[StructuredTestCase] = []

    if state.impact_graph:
        for gf in state.impact_graph:
            for sym in gf.symbols:
                uids = list(sym.semantic_unit_ids)
                units = [uid_to_unit[i] for i in uids if i in uid_to_unit]
                entry = plan_by.get(sym.symbol_id) or plan_by.get(f"name:{sym.name}")
                priority = _priority_for_symbol(sym.symbol_id, plan_by, units)
                display_target = entry.target if entry else sym.name

                for uid in uids:
                    u = uid_to_unit.get(uid)
                    if not u:
                        continue
                    if u.priority_score < 0.22 and u.test_priority != "P0":
                        continue
                    layer = _primary_layer_for_unit(u)
                    for ex in _synthetic_strategies(u):
                        cases.append(
                            StructuredTestCase(
                                test_case_id=alloc(u.semantic_unit_id),
                                target=display_target,
                                symbol_id=sym.symbol_id,
                                layer=layer,
                                priority=priority,
                                input=_structured_input(ex.input),
                                mock=_mock_payload(ex.mock),
                                assertions=_structured_assertions(ex.assert_),
                                scenario=ex.scenario,
                                semantic_unit_ids=[uid],
                            )
                        )
        return cases

    # 无 impact_graph：由 ranked impacted 或 catalog 退化生成
    if state.impacted_ranked:
        for it in state.impacted_ranked:
            if it.score < 0.35:
                continue
            layer: TestLayerKind = "integration" if "integration" in (it.impact_type or []) else "unit"
            pri: TestPriorityTier = "P0" if it.score >= 0.85 else ("P1" if it.score >= 0.55 else "P2")
            tid = _slug_token(it.id.replace(":", "_").replace("/", "_"))
            cases.append(
                StructuredTestCase(
                    test_case_id=f"TC_{tid}_{len(cases) + 1:03d}",
                    target=it.id.rsplit(":", 1)[-1] if ":" in it.id else it.id,
                    symbol_id=it.id if it.kind == "symbol" else "",
                    layer=layer,
                    priority=pri,
                    input={"impacted_id": it.id, "reason": it.reason[:500]},
                    mock={"type": "none", "behavior": ""},
                    assertions=["覆盖受影响路径上的关键行为与回归点"],
                    scenario=it.reason[:400] or "受影响项回归",
                    semantic_unit_ids=[],
                )
            )
        return cases

    for u in state.semantic_units_catalog:
        if u.priority_score < 0.22 and u.test_priority != "P0":
            continue
        layer = _primary_layer_for_unit(u)
        priority = u.test_priority
        for ex in _synthetic_strategies(u):
            cases.append(
                StructuredTestCase(
                    test_case_id=alloc(u.semantic_unit_id),
                    target=u.semantic_unit_id,
                    symbol_id="",
                    layer=layer,
                    priority=priority,
                    input=_structured_input(ex.input),
                    mock=_mock_payload(ex.mock),
                    assertions=_structured_assertions(ex.assert_),
                    scenario=ex.scenario,
                    semantic_unit_ids=[u.semantic_unit_id],
                )
            )
    return cases


def _scope_semantic_unit_ids(state: WorkflowState) -> set[str]:
    ids: set[str] = set()
    for gf in state.impact_graph or []:
        for sym in gf.symbols:
            ids.update(sym.semantic_unit_ids)
    if not ids:
        ids = {u.semantic_unit_id for u in state.semantic_units_catalog}
    return ids


def ensure_p0_coverage(
    cases: list[StructuredTestCase],
    uid_to_unit: dict[str, SemanticUnit],
    scope_ids: set[str],
) -> list[StructuredTestCase]:
    """每个 P0 语义单元至少一条用例（在作用域内）。"""
    covered: set[str] = set()
    for c in cases:
        for su in c.semantic_unit_ids:
            covered.add(su)

    p0_units = [
        uid_to_unit[s]
        for s in scope_ids
        if s in uid_to_unit and uid_to_unit[s].test_priority == "P0"
    ]
    alloc = _make_id_allocator(cases)
    out = list(cases)
    for u in p0_units:
        if u.semantic_unit_id in covered:
            continue
        out.append(
            StructuredTestCase(
                test_case_id=alloc(u.semantic_unit_id),
                target=u.semantic_unit_id,
                symbol_id="",
                layer=_primary_layer_for_unit(u),
                priority="P0",
                input={"note": "synthetic_p0_coverage", "semantic_unit_id": u.semantic_unit_id},
                mock={"type": _infer_mock_type(" ".join(u.edge_types or [])), "behavior": ""},
                assertions=["实现针对该 P0 语义单元的最小可执行断言（返回值/异常/副作用）"],
                scenario="P0 语义单元兜底覆盖",
                semantic_unit_ids=[u.semantic_unit_id],
            )
        )
        covered.add(u.semantic_unit_id)
    return out


def _dedupe_cases(cases: list[StructuredTestCase]) -> list[StructuredTestCase]:
    seen: set[tuple[Any, ...]] = set()
    out: list[StructuredTestCase] = []
    for c in cases:
        key = (c.symbol_id, c.layer, c.scenario[:120], tuple(c.semantic_unit_ids))
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


def _cap_cases(cases: list[StructuredTestCase], limit: int = 96) -> list[StructuredTestCase]:
    if len(cases) <= limit:
        return cases
    ranked = sorted(
        cases,
        key=lambda c: (_tier_rank(c.priority), c.layer != "contract", c.test_case_id),
    )
    return ranked[:limit]


def build_coverage_matrix(
    scope_ids: set[str],
    cases: list[StructuredTestCase],
) -> list[CoverageMatrixEntry]:
    su_to: dict[str, list[str]] = defaultdict(list)
    for c in cases:
        for su in c.semantic_unit_ids:
            su_to[su].append(c.test_case_id)
    rows: list[CoverageMatrixEntry] = []
    for su in sorted(scope_ids):
        ids = sorted(set(su_to.get(su, [])))
        rows.append(CoverageMatrixEntry(semantic_unit=su, covered_by=ids))
    return rows


def build_summary(
    structured: StructuredTestPlanRoot,
    scope_ids: set[str],
    uid_to_unit: dict[str, SemanticUnit],
) -> StructuredTestPlanSummary:
    p0_scope = [s for s in scope_ids if s in uid_to_unit and uid_to_unit[s].test_priority == "P0"]
    covered = {m.semantic_unit for m in structured.coverage_matrix if m.covered_by}
    p0_covered = sum(1 for s in p0_scope if s in covered)
    layer_counts = {k: len(v) for k, v in structured.test_layers.items()}
    uniq_targets = len({t for vs in structured.test_layers.values() for t in vs})
    return StructuredTestPlanSummary(
        total_cases=len(structured.test_cases),
        total_targets=uniq_targets,
        p0_semantic_units=len(p0_scope),
        p0_covered=p0_covered,
        test_layer_counts=layer_counts,
    )


def _plan_items_from_cases(cases: list[StructuredTestCase]) -> list[TestPlanItem]:
    """派生扁平条目，供 TestPrioritization / LLM 使用。"""
    pr_map = {"P0": "high", "P1": "medium", "P2": "low"}

    def sort_key(c: StructuredTestCase) -> tuple[int, str]:
        return (_tier_rank(c.priority), c.test_case_id)

    ordered = sorted(cases, key=sort_key)
    out: list[TestPlanItem] = []
    for c in ordered[:20]:
        payload = {
            "test_case_id": c.test_case_id,
            "layer": c.layer,
            "priority": c.priority,
            "scenario": c.scenario,
            "input": c.input,
            "mock": c.mock,
            "assertions": c.assertions,
        }
        tgt = c.symbol_id or c.target
        out.append(
            TestPlanItem(
                target=tgt,
                intent=json.dumps(payload, ensure_ascii=False)[:4000],
                priority=pr_map.get(c.priority, "medium"),  # type: ignore[arg-type]
            )
        )
    return out


def _fallback_structured_root(pattern_hint: str = "") -> StructuredTestPlanRoot:
    smoke = StructuredTestCase(
        test_case_id="TC_PROJECT_001",
        target="project",
        symbol_id="",
        layer="unit",
        priority="P2",
        input={},
        mock={"type": "none", "behavior": ""},
        assertions=["核心模块可导入", "主路径可执行"],
        scenario="变更影响不明确：最小冒烟回归" + pattern_hint,
        semantic_unit_ids=[],
    )
    root = StructuredTestPlanRoot(
        test_layers={"unit": ["project"], "integration": [], "contract": [], "e2e": []},
        test_cases=[smoke],
        coverage_matrix=[],
        execution_plan=build_execution_plan(),
        mock_strategy=build_mock_strategy(),
    )
    root.summary = StructuredTestPlanSummary(
        total_cases=1,
        total_targets=1,
        p0_semantic_units=0,
        p0_covered=0,
        test_layer_counts={k: len(v) for k, v in root.test_layers.items()},
    )
    return root


def plan_tests(state: WorkflowState) -> WorkflowState:
    if state.test_plan:
        state.debug["test_planning_agent"] = {"skipped": True, "reason": "already_planned"}
        return state

    patterns = state.bug_patterns or []
    pattern_hint = ""
    if patterns:
        pattern_hint = "（bug_patterns: " + ", ".join([str(p.get("pattern")) for p in patterns[:2]]) + "）"

    uid_to_unit = _catalog_map(state)
    symbol_to_units = _symbol_to_unit_ids(state)
    plan_by = _plan_index(state.impact_test_plan or [])

    test_layers = (
        build_test_layers(state.impact_test_plan or [], uid_to_unit, symbol_to_units)
        if state.impact_test_plan
        else {"unit": [], "integration": [], "contract": [], "e2e": []}
    )

    cases = generate_test_cases(state, uid_to_unit, symbol_to_units, plan_by)
    cases = _dedupe_cases(cases)
    scope_ids = _scope_semantic_unit_ids(state)
    cases = ensure_p0_coverage(cases, uid_to_unit, scope_ids)
    cases = _cap_cases(cases)
    test_layers = augment_test_layers_from_cases(test_layers, cases)

    if not cases:
        reason_code = "NO_SEMANTIC_UNITS"
        if state.impact_graph:
            reason_code = "NO_GENERATABLE_CASES"
        root = _fallback_structured_root(pattern_hint)
        state.structured_test_plan = root
        state.test_plan = _plan_items_from_cases(root.test_cases)
        state.debug["test_planning_agent"] = {
            "skipped": False,
            "count": len(state.test_plan),
            "fallback": True,
            "reason_code": reason_code,
        }
        return state

    root = StructuredTestPlanRoot(
        test_layers=test_layers,
        test_cases=cases,
        coverage_matrix=[],
        execution_plan=build_execution_plan(),
        mock_strategy=build_mock_strategy(),
    )
    if pattern_hint:
        for tc in root.test_cases:
            tc.scenario = (tc.scenario + pattern_hint)[:2000]

    root.coverage_matrix = build_coverage_matrix(scope_ids, root.test_cases)
    root.summary = build_summary(root, scope_ids, uid_to_unit)

    state.structured_test_plan = root
    state.test_plan = _plan_items_from_cases(root.test_cases)
    state.debug["test_planning_agent"] = {
        "skipped": False,
        "count": len(state.test_plan),
        "structured_cases": len(cases),
        "p0_semantic_units": root.summary.p0_semantic_units,
        "p0_covered": root.summary.p0_covered,
        "fallback": False,
        "reason_code": "OK",
    }
    return state
