from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from mutiagent.graph.state import FileChangeSummary

CACHE_FORMAT_VERSION = 1
# 与 code_change_agent 中启发式 / impact_seeds / LLM 门控等逻辑联动；逻辑变更时请递增
ANALYSIS_RULES_VERSION = 3


def cache_enabled() -> bool:
    v = os.environ.get("MUTIAGENT_CODE_CHANGE_CACHE", "1").strip().lower()
    return v not in {"0", "false", "no", "off"}


def _cache_root_for_repo(repo_path: str) -> Path:
    override = os.environ.get("MUTIAGENT_CACHE_DIR", "").strip()
    if override:
        base = Path(override).expanduser().resolve()
        rid = hashlib.sha256(str(Path(repo_path).resolve()).encode("utf-8")).hexdigest()[:24]
        return base / f"repo_{rid}"
    return Path(repo_path).resolve() / ".mutiagent"


def _cache_file_path(repo_path: str) -> Path:
    root = _cache_root_for_repo(repo_path)
    root.mkdir(parents=True, exist_ok=True)
    return root / "code_change_agent.json"


def _llm_triplet() -> str:
    if os.environ.get("MUTIAGENT_DISABLE_LLM", "").strip().lower() in {"1", "true", "yes", "on"}:
        return "llm:disabled"
    from mutiagent.llm import openai_client as oc

    if not oc.available():
        return "llm:unavailable"
    return f"llm:{oc.get_provider()}:{oc.get_model()}"


def file_analysis_fingerprint(rel_path: str, file_diff: str, source_sha256_hex: str) -> str:
    h = hashlib.sha256()
    h.update(str(CACHE_FORMAT_VERSION).encode("utf-8"))
    h.update(b"\n")
    h.update(str(ANALYSIS_RULES_VERSION).encode("utf-8"))
    h.update(b"\n")
    h.update(rel_path.encode("utf-8"))
    h.update(b"\n")
    h.update(file_diff.encode("utf-8"))
    h.update(b"\n")
    h.update(source_sha256_hex.encode("ascii"))
    h.update(b"\n")
    h.update(_llm_triplet().encode("utf-8"))
    return h.hexdigest()


def _read_store(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"format": CACHE_FORMAT_VERSION, "entries": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"format": CACHE_FORMAT_VERSION, "entries": {}}
    if not isinstance(data, dict) or not isinstance(data.get("entries"), dict):
        return {"format": CACHE_FORMAT_VERSION, "entries": {}}
    return data


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    fd, tmp = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=".code_change_cache_",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fp:
            fp.write(raw)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def load_file_summary(repo_path: str, fingerprint: str) -> FileChangeSummary | None:
    if not cache_enabled():
        return None
    path = _cache_file_path(repo_path)
    store = _read_store(path)
    entries: dict[str, Any] = store["entries"]
    row = entries.get(fingerprint)
    if not isinstance(row, dict):
        return None
    blob = row.get("summary")
    if not isinstance(blob, dict):
        return None
    try:
        return FileChangeSummary.model_validate(blob)
    except Exception:
        return None


def save_file_summary(repo_path: str, fingerprint: str, summary: FileChangeSummary) -> None:
    if not cache_enabled():
        return
    path = _cache_file_path(repo_path)
    store = _read_store(path)
    entries: dict[str, Any] = store["entries"]
    entries[fingerprint] = {"summary": summary.model_dump()}
    max_entries = 2000
    try:
        max_entries = max(100, int(os.environ.get("MUTIAGENT_CODE_CHANGE_CACHE_MAX", "2000")))
    except ValueError:
        pass
    if len(entries) > max_entries:
        for k in sorted(entries.keys())[: len(entries) - max_entries]:
            del entries[k]
    store["format"] = CACHE_FORMAT_VERSION
    store["entries"] = entries
    _atomic_write_json(path, store)
