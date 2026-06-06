#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RUNNER_DIR = ROOT / "services" / "runner"
EVAL_DIR = ROOT / "packages" / "evals"
for directory in (RUNNER_DIR, EVAL_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from run_eval import run_eval  # noqa: E402
from router_state import DIRECT_POLICY_ARMS, load_state, record_observation, save_state  # noqa: E402
from task_runner import TASK_CONFIGS, load_task, run_task, write_trace  # noqa: E402


def train_router(project_root: Path, *, reset: bool = False) -> dict[str, Any]:
    if reset:
        save_state(project_root, {"version": "1", "updated_at": None, "buckets": {}})

    rows: list[dict[str, Any]] = []
    for task_id in sorted(TASK_CONFIGS):
        task = load_task(project_root, task_id)
        for policy in DIRECT_POLICY_ARMS:
            trace = run_task(project_root, policy, task_id)
            trace_path = write_trace(project_root, trace)
            eval_result = run_eval(trace_path)
            history_row = record_observation(
                project_root,
                task=task,
                trace=trace,
                eval_result=eval_result,
                selected_policy=policy,
            )
            rows.append(
                {
                    "task_id": task_id,
                    "policy": policy,
                    "run_id": trace["run_id"],
                    "verdict": trace["verdict"],
                    "trace_path": str(trace_path.relative_to(project_root)),
                    "observed_reward": history_row["observed_reward"],
                    "raw_reward": history_row["raw_reward"],
                }
            )

    return {
        "ok": True,
        "trained_runs": len(rows),
        "policies": list(DIRECT_POLICY_ARMS),
        "state": load_state(project_root),
        "runs": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Train the local contextual-bandit router.")
    parser.add_argument("--reset", action="store_true", help="Reset derived router state before training.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args([arg for arg in sys.argv[1:] if arg != "--"])

    summary = train_router(ROOT, reset=args.reset)
    print(json.dumps(summary, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
