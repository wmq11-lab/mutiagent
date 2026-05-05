from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

from mutiagent.graph.state import WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_json

_TYPE_TO_PATTERN: dict[str, tuple[str, str, float]] = {
    "api": ("api_contract_or_integration_regression", "high", 0.64),
    "config": ("configuration_drift_or_fallback_regression", "high", 0.68),
    "exception": ("exception_path_or_error_handling_regression", "high", 0.66),
    "data_processing": ("data_transformation_or_boundary_regression", "medium", 0.58),
}
_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "type",
    "risk",
    "score",
    "reason",
    "semantic",
    "unit",
    "pattern",
}
_MEMORY_TOP_K = 5
_MAX_EXAMPLES = 10
_MAX_EMBEDDING_DIMS = 64


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _memory_path() -> Path:
    p = _repo_root() / "log" / "bug_pattern_memory.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _env_enabled() -> bool:
    raw = (os.getenv("MUTIAGENT_ENABLE_BUG_PATTERN", "1") or "").strip().lower()
    return raw not in {"0", "false", "off", "no"}


def _is_enabled(state: WorkflowState) -> bool:
    if state.bug_pattern_enabled is not None:
        return bool(state.bug_pattern_enabled)
    return _env_enabled()


def _clamp_confidence(v: Any, default: float = 0.5) -> float:
    try:
        n = float(v)
    except Exception:
        n = default
    return max(0.0, min(1.0, round(n, 4)))


def _normalize_risk_level(v: Any) -> str:
    x = str(v or "").strip().lower()
    if x in {"low", "medium", "high"}:
        return x
    return "medium"


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for m in _TOKEN_RE.finditer(text or ""):
        t = m.group(0).lower()
        if t in _STOPWORDS:
            continue
        tokens.append(t)
    return tokens


def _make_embedding(text: str) -> dict[str, float]:
    counter: dict[str, int] = {}
    for t in _tokenize(text):
        counter[t] = counter.get(t, 0) + 1
    if not counter:
        return {}
    items = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:_MAX_EMBEDDING_DIMS]
    norm = math.sqrt(sum(v * v for _, v in items)) or 1.0
    return {k: round(v / norm, 6) for k, v in items}


def _cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    common = set(a.keys()) & set(b.keys())
    dot = sum(a[k] * b[k] for k in common)
    na = math.sqrt(sum(v * v for v in a.values())) or 1.0
    nb = math.sqrt(sum(v * v for v in b.values())) or 1.0
    return max(0.0, min(1.0, dot / (na * nb)))


def _build_query_signature(state: WorkflowState) -> str:
    parts: list[str] = []
    for u in state.semantic_units_catalog or []:
        parts.append(
            f"semantic_unit_id={u.semantic_unit_id};type={u.type};priority={u.test_priority};"
            f"integration={u.integration_risk};depth={u.propagation_depth}"
        )
    for r in state.top_risks or []:
        parts.append(f"top_risk={r.semantic_unit_id};reason={r.reason}")
    for g in state.impact_graph or []:
        for s in g.symbols:
            parts.append(f"impacted_symbol={s.symbol_id};name={s.name};entity_type={s.entity_type}")
    return "\n".join(parts)[:6000]


class BugPatternMemory:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._entries: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            self._entries = []
            return
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                self._entries = [x for x in raw if isinstance(x, dict)]
                return
        except Exception:
            pass
        self._entries = []

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def query(self, query_embedding: dict[str, float], *, k: int = _MEMORY_TOP_K) -> list[dict[str, Any]]:
        scored: list[tuple[float, dict[str, Any]]] = []
        for e in self._entries:
            emb = e.get("embedding")
            if not isinstance(emb, dict):
                continue
            sim = _cosine_similarity(query_embedding, {str(kk): float(vv) for kk, vv in emb.items()})
            if sim <= 0:
                continue
            row = dict(e)
            row["similarity"] = round(sim, 4)
            scored.append((sim, row))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:k]]

    def upsert_patterns(self, patterns: list[dict[str, Any]], *, query_signature: str) -> dict[str, int]:
        created = 0
        updated = 0
        for p in patterns:
            name = str(p.get("pattern", "")).strip()
            if not name:
                continue
            conf = _clamp_confidence(p.get("confidence"), default=0.5)
            reason = str(p.get("reason", "")).strip()
            linked = [str(x) for x in (p.get("linked_risks") or []) if str(x).strip()]
            example = {
                "semantic_signature": query_signature[:1000],
                "reason": reason[:500],
                "confidence": conf,
                "linked_risks": linked[:10],
            }
            existing = None
            for e in self._entries:
                if str(e.get("name", "")).strip().lower() == name.lower():
                    existing = e
                    break
            if existing is None:
                pid = hashlib.sha1(name.lower().encode("utf-8")).hexdigest()[:12]
                self._entries.append(
                    {
                        "pattern_id": pid,
                        "name": name,
                        "semantic_signature": query_signature[:2000],
                        "embedding": _make_embedding(query_signature + "\n" + name + "\n" + reason),
                        "examples": [example],
                        "frequency": 1,
                        "confidence": conf,
                    }
                )
                created += 1
                continue

            existing["frequency"] = int(existing.get("frequency", 0) or 0) + 1
            old_conf = _clamp_confidence(existing.get("confidence"), default=conf)
            existing["confidence"] = round((old_conf + conf) / 2.0, 4)
            examples = existing.get("examples")
            if not isinstance(examples, list):
                examples = []
            examples.append(example)
            existing["examples"] = examples[-_MAX_EXAMPLES:]
            existing["semantic_signature"] = query_signature[:2000]
            existing["embedding"] = _make_embedding(
                query_signature + "\n" + str(existing.get("name", "")) + "\n" + str(existing.get("confidence", ""))
            )
            updated += 1
        self._save()
        return {"created": created, "updated": updated}


def _impact_summary(state: WorkflowState) -> dict[str, Any]:
    units = state.semantic_units_catalog or []
    top_risks = state.top_risks or []
    impacted_symbols: list[str] = []
    for g in state.impact_graph or []:
        for s in g.symbols:
            if s.symbol_id:
                impacted_symbols.append(s.symbol_id)
    return {
        "semantic_units_count": len(units),
        "top_risks_count": len(top_risks),
        "impacted_symbols_count": len(impacted_symbols),
        "has_change_graph": state.change_graph is not None,
    }


def _collect_linked_risks(state: WorkflowState, semantic_unit_id: str) -> list[str]:
    links: list[str] = []
    key = (semantic_unit_id or "").strip().lower()
    if not key:
        return links
    for r in state.top_risks or []:
        rid = (r.semantic_unit_id or "").strip().lower()
        if rid == key or rid.startswith(f"{key}:") or key.startswith(f"{rid}:"):
            links.append(r.semantic_unit_id)
    return list(dict.fromkeys(links))


def _build_rule_candidates(state: WorkflowState) -> list[dict[str, Any]]:
    patterns: dict[str, dict[str, Any]] = {}
    impacted_symbols: list[str] = []
    for g in state.impact_graph or []:
        for s in g.symbols:
            if s.symbol_id:
                impacted_symbols.append(s.symbol_id)

    # semantic_units -> bug pattern 主映射
    for u in state.semantic_units_catalog or []:
        mapped = _TYPE_TO_PATTERN.get(u.type)
        if not mapped:
            continue
        p_name, risk_level, base_conf = mapped
        linked = _collect_linked_risks(state, u.semantic_unit_id)
        # top_risks 作为强化信号
        conf = base_conf + (0.12 if linked else 0.0)
        if u.integration_risk:
            conf += 0.05
            if risk_level == "medium":
                risk_level = "high"
        reason = (
            f"语义单元 {u.semantic_unit_id}（type={u.type}）在影响图中被标记；"
            f"priority={u.test_priority}，propagation_depth={u.propagation_depth}。"
        )
        if linked:
            reason += f" 命中 top_risks 强信号：{', '.join(linked[:3])}。"
        if impacted_symbols:
            reason += f" 相关受影响符号数={len(impacted_symbols)}。"

        cur = patterns.get(p_name)
        if cur is None or _clamp_confidence(conf) > _clamp_confidence(cur.get("confidence")):
            patterns[p_name] = {
                "pattern": p_name,
                "confidence": _clamp_confidence(conf),
                "risk_level": risk_level,
                "reason": reason,
                "linked_risks": linked,
            }
        elif linked:
            cur_links = list(dict.fromkeys((cur.get("linked_risks") or []) + linked))
            cur["linked_risks"] = cur_links

    # 仅使用 impact 结构，允许 open-set 的先验候选（非 diff 统计）
    if state.change_graph and (state.top_risks or []):
        patterns.setdefault(
            "cross_symbol_propagation_regression",
            {
                "pattern": "cross_symbol_propagation_regression",
                "confidence": 0.57,
                "risk_level": "medium",
                "reason": "change_graph 与 top_risks 同时存在，提示跨符号传播风险。",
                "linked_risks": [r.semantic_unit_id for r in (state.top_risks or [])[:4]],
            },
        )

    return list(patterns.values())


def _llm_refine_patterns(
    state: WorkflowState,
    candidates: list[dict[str, Any]],
    historical_patterns: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not llm_available():
        return candidates

    units_brief = [
        {
            "semantic_unit_id": u.semantic_unit_id,
            "type": u.type,
            "risk_score": u.risk_score,
            "priority_score": u.priority_score,
            "test_priority": u.test_priority,
            "integration_risk": u.integration_risk,
            "propagation_depth": u.propagation_depth,
        }
        for u in (state.semantic_units_catalog or [])[:40]
    ]
    top_risks_brief = [{"semantic_unit_id": r.semantic_unit_id, "reason": r.reason} for r in (state.top_risks or [])[:20]]
    impacted_symbols = []
    for g in state.impact_graph or []:
        for s in g.symbols:
            impacted_symbols.append({"symbol_id": s.symbol_id, "name": s.name, "entity_type": s.entity_type})

    system = (
        "你是 Impact-aware semantic bug pattern reasoning agent。"
        "请基于语义影响信息归纳 bug patterns。必须输出 JSON 对象，且仅包含键 patterns。"
        "patterns 为数组，每个元素必须含：pattern(str), confidence(0~1), risk_level(low|medium|high), "
        "reason(str), linked_risks(list[str])。"
        "要求："
        "1) 允许 multi-label；2) 允许 open-set 新模式（不必受候选限制）；"
        "3) 不要使用 diff added/removed 统计；4) reason 必须引用 semantic_units/top_risks/impacted symbols 信号；"
        "5) 必须参考 historical_patterns（检索到的历史模式）进行迁移学习。"
    )
    user = str(
        {
            "impact_summary": _impact_summary(state),
            "semantic_units": units_brief,
            "top_risks": top_risks_brief,
            "impacted_symbols": impacted_symbols[:40],
            "historical_patterns": historical_patterns,
            "candidate_patterns": candidates,
        }
    )
    try:
        out = chat_json(system, user, temperature=0.1)
        raw = out.get("patterns", [])
        if not isinstance(raw, list):
            return candidates
        normalized: list[dict[str, Any]] = []
        for p in raw:
            if not isinstance(p, dict):
                continue
            pattern = str(p.get("pattern", "")).strip()
            if not pattern:
                continue
            normalized.append(
                {
                    "pattern": pattern,
                    "confidence": _clamp_confidence(p.get("confidence"), default=0.52),
                    "risk_level": _normalize_risk_level(p.get("risk_level")),
                    "reason": str(p.get("reason", "")).strip() or "LLM 基于 impact 信号归纳。",
                    "linked_risks": [str(x) for x in (p.get("linked_risks") or []) if str(x).strip()],
                }
            )
        return normalized or candidates
    except Exception:
        return candidates


def bug_pattern_agent(state: WorkflowState) -> WorkflowState:
    enabled = _is_enabled(state)
    if not enabled:
        state.bug_patterns = []
        state.debug["bug_pattern_agent"] = {
            "enabled": False,
            "phase": "disabled",
            "impact_summary": _impact_summary(state),
            "switch": {
                "state_override": state.bug_pattern_enabled,
                "env_MUTIAGENT_ENABLE_BUG_PATTERN": os.getenv("MUTIAGENT_ENABLE_BUG_PATTERN"),
            },
        }
        return state

    query_signature = _build_query_signature(state)
    query_embedding = _make_embedding(query_signature)
    memory = BugPatternMemory(_memory_path())
    retrieved_hist = memory.query(query_embedding, k=_MEMORY_TOP_K)

    candidates = _build_rule_candidates(state)
    # 从 memory 检索结果注入候选，增强连续学习迁移能力
    for h in retrieved_hist:
        p_name = str(h.get("name", "")).strip()
        if not p_name:
            continue
        candidates.append(
            {
                "pattern": p_name,
                "confidence": _clamp_confidence(h.get("confidence"), default=0.5),
                "risk_level": "medium",
                "reason": "来自历史 memory 的相似模式迁移。",
                "linked_risks": [],
            }
        )

    if not candidates:
        candidates = [
            {
                "pattern": "novel_semantic_regression_pattern",
                "confidence": 0.35,
                "risk_level": "medium",
                "reason": "impact_analysis 可用信号不足，保留 open-set 新模式入口供后续推理扩展。",
                "linked_risks": [],
            }
        ]

    refined = _llm_refine_patterns(state, candidates, retrieved_hist)

    # 统一格式 + 去重（multi-label）
    by_pattern: dict[str, dict[str, Any]] = {}
    for p in refined:
        key = str(p.get("pattern", "")).strip()
        if not key:
            continue
        cur = {
            "pattern": key,
            "confidence": _clamp_confidence(p.get("confidence"), default=0.5),
            "risk_level": _normalize_risk_level(p.get("risk_level")),
            "reason": str(p.get("reason", "")).strip() or "基于 impact 信号归纳。",
            "linked_risks": list(dict.fromkeys([str(x) for x in (p.get("linked_risks") or []) if str(x).strip()])),
        }
        old = by_pattern.get(key)
        if old is None or cur["confidence"] > old["confidence"]:
            by_pattern[key] = cur
        elif old is not None:
            old["linked_risks"] = list(dict.fromkeys(old["linked_risks"] + cur["linked_risks"]))

    state.bug_patterns = list(by_pattern.values())
    mem_stats = memory.upsert_patterns(state.bug_patterns, query_signature=query_signature)
    state.debug["bug_pattern_agent"] = {
        "pattern_count": len(state.bug_patterns),
        "candidate_count": len(candidates),
        "llm_refined": bool(llm_available()),
        "impact_summary": _impact_summary(state),
        "memory": {
            "path": str(_memory_path()),
            "query_embedding_dims": len(query_embedding),
            "retrieved_top_k": len(retrieved_hist),
            "created": mem_stats["created"],
            "updated": mem_stats["updated"],
        },
    }
    return state

