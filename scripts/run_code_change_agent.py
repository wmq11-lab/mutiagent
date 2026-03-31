from __future__ import annotations

import argparse
import json
import os
import sys
import time
from contextlib import redirect_stderr
from pathlib import Path
from pprint import pprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import get_model, get_provider
from mutiagent.graph.state import WorkflowState
from mutiagent.nodes.code_change_agent import ingest_change


class TeeStderr:
    def __init__(self, *streams: object) -> None:
        self._streams = streams

    def write(self, data: str) -> int:
        for stream in self._streams:
            stream.write(data)
        return len(data)

    def flush(self) -> None:
        for stream in self._streams:
            stream.flush()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run CodeChangeAgent with your own diff input.")
    parser.add_argument("--repo", required=True, help="Target repository root path.")
    parser.add_argument("--diff", required=True, help="Path to a unified diff file.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a JSON object instead of a human-friendly summary.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress logs to stderr while CodeChangeAgent runs.",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM refinement and run rule-based analysis only.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable per-file analysis cache (see MUTIAGENT_CODE_CHANGE_CACHE / MUTIAGENT_CACHE_DIR).",
    )
    parser.add_argument(
        "--log-file",
        help="Write verbose stderr logs to the given file path.",
    )
    parser.add_argument(
        "--output",
        help="Optional output JSON file path. Parent directory will be created automatically.",
    )
    return parser


def _stderr_log(message: str) -> None:
    print(f"[run_code_change_agent] {message}", file=sys.stderr, flush=True)


def _run(args: argparse.Namespace) -> None:
    if args.verbose:
        os.environ["MUTIAGENT_DEBUG"] = "1"
    if args.no_llm:
        os.environ["MUTIAGENT_DISABLE_LLM"] = "1"
    if args.no_cache:
        os.environ["MUTIAGENT_CODE_CHANGE_CACHE"] = "0"

    repo_path = str(Path(args.repo).expanduser().resolve())
    diff_path = Path(args.diff).expanduser().resolve()
    if not diff_path.exists():
        raise SystemExit(f"Diff file not found: {diff_path}")
    started_at = time.perf_counter()
    if args.verbose:
        _stderr_log(f"repo={repo_path}")
        _stderr_log(f"diff={diff_path}")
        _stderr_log(
            "llm="
            f"{'enabled' if llm_available() else 'disabled'} "
            f"provider={get_provider()} model={get_model()}"
        )
        if args.no_llm:
            _stderr_log("llm disabled by --no-llm")
        _stderr_log("reading diff file")
    diff_text = diff_path.read_text(encoding="utf-8")
    if args.verbose:
        _stderr_log(f"diff bytes={len(diff_text.encode('utf-8'))} chars={len(diff_text)}")
        _stderr_log("running CodeChangeAgent")

    state = WorkflowState(repo_path=repo_path, diff=diff_text, run_eval=False)
    out = ingest_change(state)
    if args.verbose:
        _stderr_log(
            "run complete: "
            f"changed_files={len(out.changed_files)} "
            f"changes={sum(len(item.changes) for item in out.change_analysis)} "
            f"elapsed={time.perf_counter() - started_at:.2f}s"
        )

    payload = {
        "repo_path": repo_path,
        "diff_path": str(diff_path),
        "changed_files": out.changed_files,
        "diff_hunks": out.diff_hunks,
        "change_analysis": [item.model_dump() for item in out.change_analysis],
        "change_graph": out.change_graph.model_dump() if out.change_graph else None,
        "debug": out.debug,
    }

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.verbose:
            _stderr_log(f"result saved to {output_path}")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print("=== changed_files ===")
    pprint(payload["changed_files"])
    print("\n=== diff_hunks ===")
    pprint(payload["diff_hunks"])
    print("\n=== change_analysis ===")
    pprint(payload["change_analysis"])
    print("\n=== change_graph ===")
    pprint(payload["change_graph"])
    print("\n=== debug ===")
    pprint(payload["debug"])


def main() -> None:
    args = build_parser().parse_args()
    if args.log_file:
        log_path = Path(args.log_file).expanduser().resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w", encoding="utf-8") as log_fp:
            tee = TeeStderr(sys.stderr, log_fp)
            with redirect_stderr(tee):
                _stderr_log(f"log file={log_path}")
                _run(args)
        return

    _run(args)


if __name__ == "__main__":
    main()
