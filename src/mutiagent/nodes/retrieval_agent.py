from __future__ import annotations

import logging
import os
import re
import time
from pathlib import Path
from typing import Any

from mutiagent.graph.state import WorkflowState

_log = logging.getLogger("mutiagent.workflow")

_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
_TEXT_EXTS = {".py", ".pyi", ".txt", ".md", ".rst", ".toml", ".yaml", ".yml", ".ini"}
_MAX_FILE_BYTES = 200_000
_MAX_SNIPPET_LINES = 6
_MAX_RETRIEVED_ITEMS = 8
_MAX_TEST_FILES_SCAN = 600
_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "this",
    "that",
    "true",
    "false",
    "none",
    "high",
    "medium",
    "low",
    "test",
    "tests",
    "case",
    "intent",
    "target",
    "changed",
    "file",
    "files",
    "reason",
    "function",
    "class",
    "method",
}


def _env_enabled() -> bool:
    raw = (os.getenv("MUTIAGENT_ENABLE_RETRIEVAL", "1") or "").strip().lower()
    return raw not in {"0", "false", "off", "no"}


def _is_enabled(state: WorkflowState) -> bool:
    if state.retrieval_enabled is not None:
        return bool(state.retrieval_enabled)
    return _env_enabled()


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for m in _TOKEN_RE.finditer(text or ""):
        token = m.group(0).lower()
        if token in _STOPWORDS:
            continue
        tokens.append(token)
    return tokens


def _query_terms(state: WorkflowState) -> list[str]:
    raw_terms: list[str] = []
    for rel in state.changed_files or []:
        raw_terms.extend(_tokenize(rel.replace("\\", "/")))
        raw_terms.extend(_tokenize(Path(rel).stem))

    for item in state.impacted_ranked or []:
        raw_terms.extend(_tokenize(item.id))
        raw_terms.extend(_tokenize(item.reason))

    for p in state.prioritized_plan or state.test_plan or []:
        raw_terms.extend(_tokenize(p.target))
        raw_terms.extend(_tokenize(p.intent))

    seen: set[str] = set()
    unique: list[str] = []
    for t in raw_terms:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique[:40]


def _candidate_paths(repo_root: Path, changed_files: list[str]) -> list[Path]:
    out: list[Path] = []
    seen: set[Path] = set()

    def add(p: Path) -> None:
        rp = p.resolve()
        if rp in seen or not p.exists() or not p.is_file():
            return
        seen.add(rp)
        out.append(p)

    for rel in changed_files or []:
        p = (repo_root / rel).resolve()
        if p.exists() and p.is_file():
            add(p)
            stem = p.stem
            parent = p.parent
            # changed file sibling tests: test_foo.py / foo_test.py
            for cand in (parent / f"test_{stem}.py", parent / f"{stem}_test.py"):
                if cand.exists():
                    add(cand)
            # root tests heuristic
            for cand in (
                repo_root / "tests" / f"test_{stem}.py",
                repo_root / "tests" / f"{stem}_test.py",
            ):
                if cand.exists():
                    add(cand)

    tests_dir = repo_root / "tests"
    if tests_dir.exists() and tests_dir.is_dir():
        count = 0
        for pattern in ("test_*.py", "*_test.py"):
            for path in tests_dir.rglob(pattern):
                add(path)
                count += 1
                if count >= _MAX_TEST_FILES_SCAN:
                    return out
    return out


def _read_text(path: Path) -> str:
    if path.suffix.lower() not in _TEXT_EXTS:
        return ""
    try:
        if path.stat().st_size > _MAX_FILE_BYTES:
            return ""
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return ""
    except Exception:
        return ""


def _score_text(text: str, terms: list[str]) -> tuple[float, list[str]]:
    if not text or not terms:
        return 0.0, []
    low = text.lower()
    matched = [t for t in terms if t in low]
    if not matched:
        return 0.0, []
    unique = list(dict.fromkeys(matched))
    density = len(unique) / max(1, len(terms))
    length_penalty = min(1.0, len(text) / 10_000)
    score = density * 0.8 + length_penalty * 0.2
    return round(score, 4), unique[:10]


def _snippet(text: str, matched_terms: list[str]) -> str:
    lines = text.splitlines()
    if not lines:
        return ""
    low_lines = [ln.lower() for ln in lines]
    hit_idx = -1
    for i, line in enumerate(low_lines):
        if any(t in line for t in matched_terms):
            hit_idx = i
            break
    if hit_idx < 0:
        return "\n".join(lines[:_MAX_SNIPPET_LINES])
    start = max(0, hit_idx - 2)
    end = min(len(lines), hit_idx + 1 + (_MAX_SNIPPET_LINES - 3))
    return "\n".join(lines[start:end])


def _build_items(repo_root: Path, candidates: list[Path], terms: list[str]) -> list[dict[str, Any]]:
    ranked: list[tuple[float, dict[str, Any]]] = []
    for p in candidates:
        text = _read_text(p)
        score, matched = _score_text(text, terms)
        if score <= 0:
            continue
        rel = str(p.resolve().relative_to(repo_root.resolve()))
        ranked.append(
            (
                score,
                {
                    "path": rel,
                    "score": score,
                    "matched_terms": matched,
                    "preview": _snippet(text, matched)[:1200],
                },
            )
        )
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [it for _, it in ranked[:_MAX_RETRIEVED_ITEMS]]


def retrieval_agent(state: WorkflowState) -> WorkflowState:
    start = time.perf_counter()
    impacted_cnt = len(state.impacted_ranked or [])
    plan_cnt = len(state.prioritized_plan or state.test_plan or [])
    changed_cnt = len(state.changed_files or [])
    enabled = _is_enabled(state)
    _log.info(
        "RetrievalAgent: 开始上下文检索 repo=%s, enabled=%s, changed_files=%s, impacted=%s, planned_cases=%s",
        state.repo_path,
        enabled,
        changed_cnt,
        impacted_cnt,
        plan_cnt,
    )
    if not enabled:
        state.retrieved_context = {
            "enabled": False,
            "backend": "disabled",
            "items": [],
            "reason": "disabled_by_switch",
        }
        state.debug["retrieval_agent"] = {
            "enabled": False,
            "phase": "disabled",
            "input": {
                "changed_files": changed_cnt,
                "impacted": impacted_cnt,
                "planned_cases": plan_cnt,
            },
            "switch": {
                "state_override": state.retrieval_enabled,
                "env_MUTIAGENT_ENABLE_RETRIEVAL": os.getenv("MUTIAGENT_ENABLE_RETRIEVAL"),
            },
        }
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        _log.info("RetrievalAgent: 开关关闭，跳过检索，耗时 %sms", elapsed_ms)
        return state

    _log.info("RetrievalAgent: 阶段 1/3 - 生成检索关键词")
    terms = _query_terms(state)
    _log.info("RetrievalAgent: 关键词数=%s", len(terms))

    _log.info("RetrievalAgent: 阶段 2/3 - 扫描候选文件并执行词法检索")
    repo_root = Path(state.repo_path or "")
    candidates = _candidate_paths(repo_root, state.changed_files or []) if repo_root.exists() else []
    items = _build_items(repo_root, candidates, terms) if repo_root.exists() else []

    _log.info("RetrievalAgent: 阶段 3/3 - 回填检索上下文（items=%s）", len(items))
    state.retrieved_context = {
        "enabled": True,
        "backend": "lexical",
        "terms": terms[:20],
        "items": items,
        "stats": {
            "candidate_files": len(candidates),
            "retrieved_items": len(items),
        },
    }
    state.debug["retrieval_agent"] = {
        "enabled": True,
        "phase": "lexical_retrieval",
        "input": {
            "changed_files": changed_cnt,
            "impacted": impacted_cnt,
            "planned_cases": plan_cnt,
        },
        "candidate_files": len(candidates),
        "retrieved_items": len(items),
    }
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    _log.info("RetrievalAgent: 完成，耗时 %sms（backend=lexical, items=%s）", elapsed_ms, len(items))
    return state

