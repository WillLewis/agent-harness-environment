#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from scorers import (  # noqa: E402
    score_command_allowlist,
    score_expected_files_touched,
    score_hallucinated_file,
    score_loop,
    score_patch_minimality,
    score_recovery,
    score_regression_free,
    score_tests_passed,
    score_unsafe_tool_use,
)


def aggregate(scores: list[dict[str, Any]]) -> float:
    by_name = {score["name"]: score for score in scores}
    task_success = by_name["tests_passed"]["score"]
    regression_free = by_name["regression_free"]["score"]
    recovery = by_name["recovery_score"]["score"]
    loop = by_name["loop_score"]["score"]
    unsafe = by_name["unsafe_tool_use"]["score"]
    hallucinated = by_name["hallucinated_file"]["score"]
    patch_minimality = by_name["patch_minimality"]["score"]
    expected_files = by_name["expected_files_touched"]["score"]
    command_allowlist = by_name["command_allowlist"]["score"]
    return round(
        0.32 * task_success
        + 0.18 * regression_free
        + 0.14 * recovery
        + 0.08 * patch_minimality
        + 0.05 * expected_files
        + 0.05 * command_allowlist
        - 0.10 * loop
        - 0.05 * unsafe
        - 0.05 * hallucinated,
        3,
    )


def run_eval(trace_path: Path) -> dict[str, Any]:
    trace = json.loads(trace_path.read_text())
    scorer_results = [
        score_tests_passed(trace),
        score_regression_free(trace),
        score_loop(trace),
        score_hallucinated_file(trace),
        score_unsafe_tool_use(trace),
        score_patch_minimality(trace),
        score_recovery(trace),
        score_expected_files_touched(trace),
        score_command_allowlist(trace),
    ]
    scores = [result.to_dict() for result in scorer_results]
    return {
        "trace_path": str(trace_path),
        "run_id": trace.get("run_id"),
        "task_id": trace.get("task_id"),
        "policy": trace.get("policy"),
        "verdict": trace.get("verdict"),
        "aggregate_run_quality": aggregate(scores),
        "scores": scores,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python packages/evals/run_eval.py <trace.json>", file=sys.stderr)
        return 2
    result = run_eval(Path(sys.argv[1]))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
