"""由 coverage.py JSON × change_analysis 归纳「变更函数」语句是否被覆盖（用于实验落盘）。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mutiagent.utils.paths import production_changed_files


def _changed_function_rows(state: Any) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    changed = set(production_changed_files(state.changed_files or []))
    for fc in state.change_analysis or []:
        fn = getattr(fc, "file", "") or ""
        if fn not in changed:
            continue
        for ch in getattr(fc, "changes", []) or []:
            typ = str(getattr(ch, "type", "") or "")
            if typ not in {"function", "method"}:
                continue
            ent = str(getattr(ch, "entity", "") or "").strip()
            if not ent:
                continue
            rows.append(
                {
                    "file": fn.replace("\\", "/"),
                    "entity": ent,
                    "change_type": str(getattr(ch, "change_type", "") or ""),
                }
            )
    return rows


def _dedupe_changed_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, str]] = []
    for r in rows:
        key = (r["file"], r["entity"])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def _normalize_rel_path(p: str) -> str:
    return p.strip().replace("\\", "/")


def _last_name_segment(qualified: str) -> str:
    """取 ``a.b.c`` / ``a::b::c`` 的最后一段，用于 coverage 键与 entity 的宽松对齐。"""
    q = qualified.strip().replace("::", ".")
    if not q:
        return q
    return q.split(".")[-1]


def _file_cov_block(files_map: dict[str, Any], rel: str) -> dict[str, Any] | None:
    rel_n = _normalize_rel_path(rel)
    if rel_n in files_map and isinstance(files_map[rel_n], dict):
        return files_map[rel_n]
    for k, v in files_map.items():
        if not isinstance(k, str) or not isinstance(v, dict):
            continue
        if _normalize_rel_path(k) == rel_n:
            return v
    return None


def _summary_dict(v: Any) -> dict[str, Any] | None:
    if isinstance(v, dict):
        summ = v.get("summary")
        return summ if isinstance(summ, dict) else None
    return None


def _lookup_function_summary(funcs_map: dict[str, Any], entity: str) -> dict[str, Any] | None:
    """coverage JSON 内 functions 键可能是 simple name、Qualified.name、或与 change_analysis 短名不一致。"""
    if not isinstance(funcs_map, dict) or not entity.strip():
        return None
    ent = entity.strip()
    ent_dots = ent.replace("::", ".")

    for key in (ent, ent_dots):
        s = _summary_dict(funcs_map.get(key))
        if s:
            return s

    qualified_suffix: list[dict[str, Any]] = []
    for k, v in funcs_map.items():
        if k == "" or not isinstance(k, str) or not isinstance(v, dict):
            continue
        kd = k.replace("::", ".")
        s = _summary_dict(v)
        if s is None:
            continue
        if k == ent or kd == ent_dots:
            return s
        if kd.endswith("." + ent_dots) or k.endswith("::" + ent):
            qualified_suffix.append(s)
            continue
        if ent_dots and (kd.endswith("." + ent) or k.endswith("::" + ent)):
            qualified_suffix.append(s)

    if qualified_suffix:
        return max(qualified_suffix, key=lambda sm: int(sm.get("covered_lines", 0) or 0))

    ent_last = _last_name_segment(ent_dots)
    if not ent_last:
        return None

    ent_variants = {ent_last}
    if ent_last.startswith("_") and len(ent_last) > 1:
        ent_variants.add(ent_last[1:])

    loose: list[dict[str, Any]] = []
    for k, v in funcs_map.items():
        if k == "" or not isinstance(k, str) or not isinstance(v, dict):
            continue
        s = _summary_dict(v)
        if s is None:
            continue
        k_last = _last_name_segment(k.replace("::", "."))
        if k_last in ent_variants:
            loose.append(s)
            continue
        if k_last.startswith("_") and len(k_last) > 1 and ent_last == k_last[1:]:
            loose.append(s)

    if not loose:
        return None
    if len(loose) == 1:
        return loose[0]
    return max(loose, key=lambda sm: int(sm.get("covered_lines", 0) or 0))


def build_changed_function_coverage_report(
    state: Any,
    coverage_json_path: str | Path | None,
) -> dict[str, Any]:
    """
    Returns a dict suitable for JSON dump (UTF-8, indent=2).

    changed_function_coverage_ratio:
        至少有 1 行语句被执行的变更函数数 / 变更函数数（若无变更函数则为 null）。
    """
    raw: dict[str, Any] = {}
    src: str | None = None
    if coverage_json_path is not None:
        path = Path(coverage_json_path)
        if path.is_file():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                src = str(path.resolve())
            except (OSError, json.JSONDecodeError):
                raw = {}

    base: dict[str, Any] = {
        "schema_version": 1,
        "algorithm_zh": (
            "对 change_analysis 中变更文件下的 function/method 实体，在 coverage json 的 "
            "files[path].functions 中匹配：精确键、:: 与 . 统一、qualified 后缀（多键同后缀时取 covered_lines 较大者）、"
            "**最后一段同名**（及可选的单侧下划线差异；多候选时同样取 covered_lines 较大者）。"
            "summary.covered_lines>0 视为该变更函数已被测试执行到。"
        ),
        "coverage_json_source": src,
    }

    rows = _dedupe_changed_rows(_changed_function_rows(state))
    if not rows:
        base.update(
            {
                "changed_function_coverage_ratio": None,
                "changed_function_coverage_percent": None,
                "changed_function_count": 0,
                "changed_functions_any_line_covered_count": 0,
                "entities": [],
                "note_zh": "无变更文件上的 function/method 实体可统计。",
            }
        )
        return base

    files_map = raw.get("files")
    if not isinstance(files_map, dict):
        files_map = {}

    entities_out: list[dict[str, Any]] = []
    any_hit = 0
    for row in rows:
        rel = row["file"]
        ent = row["entity"]
        block = _file_cov_block(files_map, rel)
        funcs = block.get("functions") if isinstance(block, dict) else None
        funcs = funcs if isinstance(funcs, dict) else {}
        summ = _lookup_function_summary(funcs, ent)
        covered = int(summ.get("covered_lines", 0) or 0) if summ else 0
        nstmt = int(summ.get("num_statements", 0) or 0) if summ else 0
        pct = float(summ.get("percent_statements_covered", 0.0) or 0.0) if summ else None
        hit = covered > 0
        if hit:
            any_hit += 1
        entities_out.append(
            {
                "file": rel,
                "entity": ent,
                "change_type": row["change_type"],
                "covered_lines": covered,
                "num_statements": nstmt,
                "statement_coverage_percent": pct,
                "any_line_covered": hit,
            }
        )

    n = len(entities_out)
    ratio = float(any_hit) / float(n) if n else None
    base.update(
        {
            "changed_function_count": n,
            "changed_functions_any_line_covered_count": any_hit,
            "changed_function_coverage_ratio": ratio,
            "changed_function_coverage_percent": (ratio * 100.0) if ratio is not None else None,
            "entities": entities_out,
        }
    )
    if not src:
        base.setdefault(
            "note_zh",
            "未读到 coverage.json（未生成或未落盘）；实体行数为 0 或无法对齐文件时覆盖率为占位。",
        )
    return base
