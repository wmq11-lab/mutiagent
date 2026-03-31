from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from pprint import pprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mutiagent.graph.state import ChangeGraph, FileChangeSummary, WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import get_model, get_provider
from mutiagent.nodes.code_change_agent import ingest_change
from mutiagent.nodes.impact_analysis_agent import analyze_impact


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run ImpactAnalysisAgent: either load CodeChangeAgent JSON (--input), "
            "or run CodeChangeAgent + ImpactAnalysisAgent from repo + unified diff (--repo --diff)."
        )
    )
    parser.add_argument(
        "--input",
        help=(
            "Path to CodeChangeAgent JSON result (e.g. from run_code_change_agent.py --json). "
            "Not used together with --repo/--diff."
        ),
    )
    parser.add_argument(
        "--repo",
        help="Repository root (use with --diff to run ingest_change then analyze_impact).",
    )
    parser.add_argument(
        "--diff",
        help="Path to unified diff file (use with --repo).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a JSON object instead of a human-friendly summary.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress logs to stderr while ImpactAnalysisAgent runs.",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM ranking and run rule-based impact scoring only.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="When using --repo/--diff: disable per-file CodeChangeAgent cache.",
    )
    parser.add_argument(
        "--save-code-change",
        help="When using --repo/--diff: optional path to write CodeChangeAgent JSON (same shape as run_code_change_agent.py --json).",
    )
    parser.add_argument(
        "--output",
        help="Optional output JSON file path. Parent directory will be created automatically.",
    )
    return parser


def _stderr_log(message: str) -> None:
    print(f"[run_impact_analysis_agent] {message}", file=sys.stderr, flush=True)


def _load_code_change_payload(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Input file not found: {path}")
    text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise SystemExit(f"Invalid JSON input: {path} (top-level must be object)")
        return payload
    except json.JSONDecodeError as exc:
        extracted = _extract_first_json_object(text)
        if extracted is None:
            raise SystemExit(f"Invalid JSON input: {path} ({exc})") from exc
        try:
            payload = json.loads(extracted)
        except json.JSONDecodeError as inner_exc:
            raise SystemExit(f"Invalid JSON object extracted from input: {path} ({inner_exc})") from inner_exc
        if not isinstance(payload, dict):
            raise SystemExit(f"Invalid JSON object extracted from input: {path} (top-level must be object)")
        return payload


def _extract_first_json_object(text: str) -> str | None:
    in_string = False
    escape = False
    depth = 0
    start_idx = -1
    for idx, ch in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch == "{":
            if depth == 0:
                start_idx = idx
            depth += 1
            continue
        if ch == "}":
            if depth == 0:
                continue
            depth -= 1
            if depth == 0 and start_idx >= 0:
                return text[start_idx : idx + 1]
    return None


def _state_from_code_change_payload(payload: dict) -> WorkflowState:
    repo_path = str(payload.get("repo_path", "")).strip()
    if not repo_path:
        raise SystemExit("Invalid input JSON: missing `repo_path`.")

    changed_files = payload.get("changed_files", [])
    change_analysis_raw = payload.get("change_analysis", [])
    change_graph_raw = payload.get("change_graph")
    debug = payload.get("debug", {})

    state = WorkflowState(repo_path=repo_path, diff="", run_eval=False)
    state.changed_files = [str(item) for item in changed_files if isinstance(item, str)]
    state.change_analysis = [FileChangeSummary(**item) for item in change_analysis_raw]
    state.change_graph = ChangeGraph(**change_graph_raw) if isinstance(change_graph_raw, dict) else None
    state.debug = debug if isinstance(debug, dict) else {}
    return state


def _run(args: argparse.Namespace) -> None:
    if args.verbose:
        os.environ["MUTIAGENT_DEBUG"] = "1"
    if args.no_llm:
        os.environ["MUTIAGENT_DISABLE_LLM"] = "1"
    if getattr(args, "no_cache", False):
        os.environ["MUTIAGENT_CODE_CHANGE_CACHE"] = "0"

    from_diff = bool(args.repo or args.diff)
    if from_diff:
        if not args.repo or not args.diff:
            raise SystemExit("使用 diff 流水线时请同时提供 --repo 与 --diff。")
        if args.input:
            raise SystemExit("不要同时使用 --input 与 --repo/--diff。")
    elif not args.input:
        raise SystemExit("请提供 --input JSON，或同时提供 --repo 与 --diff。")

    started_at = time.perf_counter()
    diff_path_resolved: str | None = None

    if args.verbose:
        _stderr_log(
            "llm="
            f"{'enabled' if llm_available() else 'disabled'} "
            f"provider={get_provider()} model={get_model()}"
        )
        if args.no_llm:
            _stderr_log("llm disabled by --no-llm")

    if from_diff:
        repo_path = str(Path(args.repo).expanduser().resolve())
        diff_path = Path(args.diff).expanduser().resolve()
        if not diff_path.exists():
            raise SystemExit(f"Diff file not found: {diff_path}")
        diff_path_resolved = str(diff_path)
        diff_text = diff_path.read_text(encoding="utf-8")
        if args.verbose:
            _stderr_log(f"repo={repo_path}")
            _stderr_log(f"diff={diff_path}")
            _stderr_log(f"diff chars={len(diff_text)}")
            _stderr_log("running CodeChangeAgent (ingest_change)")
        state = WorkflowState(repo_path=repo_path, diff=diff_text, run_eval=False)
        state = ingest_change(state)
        if args.save_code_change:
            cc_path = Path(args.save_code_change).expanduser().resolve()
            cc_path.parent.mkdir(parents=True, exist_ok=True)
            cc_payload = {
                "repo_path": repo_path,
                "diff_path": diff_path_resolved,
                "changed_files": state.changed_files,
                "diff_hunks": state.diff_hunks,
                "change_analysis": [item.model_dump() for item in state.change_analysis],
                "change_graph": state.change_graph.model_dump() if state.change_graph else None,
                "debug": state.debug,
            }
            cc_path.write_text(json.dumps(cc_payload, ensure_ascii=False, indent=2), encoding="utf-8")
            if args.verbose:
                _stderr_log(f"code_change snapshot saved to {cc_path}")
    else:
        input_path = Path(args.input).expanduser().resolve()
        if args.verbose:
            _stderr_log(f"input={input_path}")
            _stderr_log("loading code_change_agent output")
        payload = _load_code_change_payload(input_path)
        state = _state_from_code_change_payload(payload)

    if args.verbose:
        _stderr_log(
            f"before impact: changed_files={len(state.changed_files)} "
            f"change_analysis={len(state.change_analysis)} "
            f"has_graph={state.change_graph is not None}"
        )
        _stderr_log("running ImpactAnalysisAgent")

    out = analyze_impact(state)
    if args.verbose:
        ng = len(out.impact_graph)
        n_cat = len(out.semantic_units_catalog)
        n_plan = len(out.impact_test_plan)
        _stderr_log(
            "run complete: "
            f"impact_graph_files={ng} catalog_units={n_cat} impact_test_plan={n_plan} "
            f"legacy_impacted={len(out.impacted)} legacy_ranked={len(out.impacted_ranked)} "
            f"elapsed={time.perf_counter() - started_at:.2f}s"
        )

    result: dict = {
        "repo_path": out.repo_path,
        "changed_files": out.changed_files,
        "semantic_units_catalog": [
            u.model_dump(mode="json", by_alias=True) for u in out.semantic_units_catalog
        ],
        "impact_graph": [g.model_dump(mode="json", by_alias=True) for g in out.impact_graph],
        "impact_test_plan": [p.model_dump(mode="json") for p in out.impact_test_plan],
        "top_risks": [r.model_dump(mode="json") for r in out.top_risks],
        "impacted": [item.model_dump() for item in out.impacted],
        "impacted_ranked": [item.model_dump() for item in out.impacted_ranked],
        "debug": out.debug,
    }
    if from_diff:
        result["diff_path"] = diff_path_resolved
        result["diff_hunks"] = out.diff_hunks
        result["change_analysis"] = [item.model_dump() for item in out.change_analysis]
        result["change_graph"] = out.change_graph.model_dump() if out.change_graph else None

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.verbose:
            _stderr_log(f"result saved to {output_path}")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if result.get("diff_path"):
        print("=== diff_path ===")
        pprint(result["diff_path"])
    print("=== changed_files ===")
    pprint(result["changed_files"])
    if result.get("change_analysis") is not None:
        print("\n=== change_analysis (summary) ===")
        for fs in result["change_analysis"]:
            fn = fs.get("file", "")
            nch = len(fs.get("changes") or [])
            print(f"  {fn}: {nch} change(s)")
    print("\n=== semantic_units_catalog (count) ===")
    print(f"  {len(result.get('semantic_units_catalog') or [])} unique semantic unit(s)")
    print("\n=== impact_test_plan (summary) ===")
    for row in (result.get("impact_test_plan") or [])[:12]:
        print(
            f"  [{row.get('priority')}] {row.get('target')} "
            f"cases~{row.get('estimated_cases')} types={row.get('test_types')}"
        )
    print("\n=== top_risks (V4) ===")
    for tr in (result.get("top_risks") or [])[:8]:
        print(f"  {tr.get('semantic_unit_id')}: {tr.get('reason')}")
    print("\n=== impact_graph (summary) ===")
    for gf in result.get("impact_graph") or []:
        fn = gf.get("file", "")
        for sym in gf.get("symbols") or []:
            n_u = len(sym.get("semantic_unit_ids") or [])
            print(f"  {fn} :: {sym.get('name')} ({n_u} semantic unit id(s))")
    print("\n=== impacted (legacy flat, may be empty) ===")
    pprint(result["impacted"])
    print("\n=== impacted_ranked (legacy, may be empty) ===")
    pprint(result["impacted_ranked"])
    print("\n=== debug ===")
    pprint(result["debug"])


def main() -> None:
    args = build_parser().parse_args()
    _run(args)


if __name__ == "__main__":
    main()
