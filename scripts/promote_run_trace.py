#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
EVAL_DIR = ROOT / "packages" / "evals"
for directory in (TOOLS_DIR, EVAL_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from fixture_validation import validate_trace_dict  # noqa: E402
from mcp_helpers import promote_run_trace  # noqa: E402


def _run_eval(trace_path: Path) -> dict[str, Any]:
    from run_eval import run_eval  # noqa: E402

    return run_eval(trace_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Promote a local runner trace to a reviewable fixture candidate "
            "(does not overwrite curated data/traces by default)."
        )
    )
    parser.add_argument(
        "trace_path",
        help="Path to a runner trace JSON, e.g. runs/run_local_guarded_recovery_multi_agent_contract_001.json",
    )
    parser.add_argument(
        "--candidate-dir",
        default="data/trace_candidates",
        help="Directory for promoted candidate trace JSON (default: data/trace_candidates)",
    )
    parser.add_argument(
        "--datasets-path",
        default="data/datasets/generated_candidates.jsonl",
        help="JSONL file for promotion metadata (default: data/datasets/generated_candidates.jsonl)",
    )
    parser.add_argument(
        "--write-fixture",
        action="store_true",
        help="Also write to data/traces/ (requires --fixture-name; refuses overwrite)",
    )
    parser.add_argument(
        "--fixture-name",
        default=None,
        help="Destination filename under data/traces/ when --write-fixture is set",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print result JSON",
    )
    args = parser.parse_args()

    if args.write_fixture and not args.fixture_name:
        parser.error("--fixture-name is required when --write-fixture is set")

    result = promote_run_trace(
        ROOT,
        args.trace_path,
        _run_eval,
        candidate_dir=args.candidate_dir,
        datasets_path=args.datasets_path,
        write_fixture=args.write_fixture,
        fixture_name=args.fixture_name,
        validate_trace_impl=validate_trace_dict,
    )

    indent = 2 if args.pretty else None
    print(json.dumps(result, indent=indent))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
