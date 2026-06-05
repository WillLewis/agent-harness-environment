#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
RUNNER_DIR = Path(__file__).resolve().parent
TOOLS_DIR = ROOT / "tools"
EVAL_DIR = ROOT / "packages" / "evals"
for directory in (RUNNER_DIR, TOOLS_DIR, EVAL_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from fixture_validation import validate_trace_dict  # noqa: E402
from mcp_helpers import promote_run_trace  # noqa: E402
from run_eval import run_eval  # noqa: E402
from task_runner import list_batch_combinations, run_task, write_trace  # noqa: E402

BATCH_VERSION = "1"


def scorer_signals(eval_result: dict[str, Any]) -> dict[str, list[str]]:
    scores = eval_result.get("scores", [])
    return {
        "passed": [score["name"] for score in scores if score.get("passed")],
        "failed": [score["name"] for score in scores if not score.get("passed")],
    }


def run_batch_item(
    project_root: Path,
    task_id: str,
    policy: str,
    *,
    promote_candidates: bool,
    run_eval_impl: Callable[[Path], dict[str, Any]],
    promote_impl: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    trace = run_task(project_root, policy, task_id)
    trace_path = write_trace(project_root, trace)
    relative_trace_path = str(trace_path.relative_to(project_root))
    eval_result = run_eval_impl(trace_path)

    row: dict[str, Any] = {
        "ok": True,
        "run_id": trace["run_id"],
        "task_id": task_id,
        "policy": policy,
        "verdict": trace["verdict"],
        "trace_path": relative_trace_path,
        "aggregate_run_quality": eval_result.get("aggregate_run_quality"),
        "scorer_signals": scorer_signals(eval_result),
    }

    if promote_candidates:
        promote = promote_impl or promote_run_trace
        promotion = promote(
            project_root,
            relative_trace_path,
            run_eval_impl,
            validate_trace_impl=validate_trace_dict,
        )
        row["promotion_ok"] = promotion.get("ok", False)
        if promotion.get("ok"):
            row["candidate_trace_path"] = promotion.get("candidate_trace_path")
            row["promotion"] = {
                "already_exists": promotion.get("already_exists", False),
                "metadata_written": promotion.get("metadata_written", False),
                "candidate_refreshed": promotion.get("candidate_refreshed", False),
            }
        else:
            row["promotion_error"] = promotion.get("message", "promotion failed")

    return row


def run_batch(
    project_root: Path,
    *,
    promote_candidates: bool = False,
    run_eval_impl: Callable[[Path], dict[str, Any]] | None = None,
    promote_impl: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    eval_impl = run_eval_impl or run_eval
    runs: list[dict[str, Any]] = []
    errors = 0

    for task_id, policy in list_batch_combinations():
        try:
            runs.append(
                run_batch_item(
                    project_root,
                    task_id,
                    policy,
                    promote_candidates=promote_candidates,
                    run_eval_impl=eval_impl,
                    promote_impl=promote_impl,
                )
            )
        except Exception as exc:  # noqa: BLE001 — collect per-run failures in batch summary
            errors += 1
            runs.append(
                {
                    "ok": False,
                    "task_id": task_id,
                    "policy": policy,
                    "error": str(exc),
                }
            )

    accepted = sum(1 for row in runs if row.get("verdict") == "accepted")
    rejected = sum(1 for row in runs if row.get("verdict") == "rejected")

    return {
        "ok": errors == 0,
        "batch_version": BATCH_VERSION,
        "promote_candidates": promote_candidates,
        "run_count": len(runs),
        "accepted_count": accepted,
        "rejected_count": rejected,
        "error_count": errors,
        "runs": runs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run all supported local runner task/policy pairs and score traces."
    )
    parser.add_argument(
        "--promote-candidates",
        action="store_true",
        help="Promote each generated trace to data/trace_candidates/ (idempotent).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    args = parser.parse_args()

    summary = run_batch(ROOT, promote_candidates=args.promote_candidates)
    indent = 2 if args.pretty else None
    print(json.dumps(summary, indent=indent, separators=None if args.pretty else (",", ":")))
    return 0 if summary.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
