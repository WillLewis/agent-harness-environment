#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REWARD_DIR = ROOT / "packages" / "reward"
EVAL_DIR = ROOT / "packages" / "evals"
for directory in (REWARD_DIR, EVAL_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from router_state import ROUTER_POLICY, record_observation
from run_eval import run_eval
from task_runner import DEFAULT_TASK_ID, ALL_SUPPORTED_POLICIES, load_task, run_task, write_trace


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python services/runner/run_task.py <policy> [task_id]", file=sys.stderr)
        print(f"Supported policies: {', '.join(ALL_SUPPORTED_POLICIES)}", file=sys.stderr)
        print(f"Default task_id: {DEFAULT_TASK_ID}", file=sys.stderr)
        print("Example: python services/runner/run_task.py baseline adversarial_env_001", file=sys.stderr)
        return 2

    policy = sys.argv[1]
    task_id = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TASK_ID
    try:
        trace = run_task(ROOT, policy, task_id)
        path = write_trace(ROOT, trace)
        router_history = None
        if policy == ROUTER_POLICY:
            eval_result = run_eval(path)
            router_history = record_observation(
                ROOT,
                task=load_task(ROOT, task_id),
                trace=trace,
                eval_result=eval_result,
                selected_policy=trace["routed_policy"],
                decision=trace.get("router_decision"),
            )
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2
    except RuntimeError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "trace_path": str(path.relative_to(ROOT)),
                "run_id": trace["run_id"],
                "verdict": trace["verdict"],
                "sandbox_path": trace.get("sandbox_path"),
                "routed_policy": trace.get("routed_policy"),
                "router_history": router_history,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
