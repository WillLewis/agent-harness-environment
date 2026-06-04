#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from sandbox import classify_command
from trace_store import JsonTraceStore

ROOT = Path(__file__).resolve().parents[2]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def event(run_id: str, task_id: str, step: int, actor: str, action: str, input_summary: str, output_summary: str, policy: str, **extra):
    return {
        "run_id": run_id,
        "task_id": task_id,
        "step_id": step,
        "timestamp": now(),
        "actor": actor,
        "action_type": action,
        "input_summary": input_summary,
        "output_summary": output_summary,
        "harness_policy": policy,
        **extra,
    }


def run_stubbed_task(policy: str = "guarded_recovery") -> dict:
    run_id = f"local_stub_{policy}"
    task_id = "bugfix_date_parser_001"
    command = "npm test -- dateParser"
    decision = classify_command(command)
    events = [
        event(run_id, task_id, 1, "planner", "PLAN", "Load task and policy.", "Plan requires reading failing test before edit.", policy),
        event(run_id, task_id, 2, "executor", "READ_FILE", "Read failing test.", "Found timezone offset assertion.", policy, files_touched=["tests/dateParser.test.ts"]),
        event(run_id, task_id, 3, "executor", "READ_FILE", "Read parser source.", "Found broad punctuation stripping.", policy, files_touched=["src/dateParser.ts"]),
    ]
    if not decision.allowed:
        events.append(event(run_id, task_id, 4, "executor", "BLOCKED_ACTION", command, decision.reason, policy, command=command, failure_label="unsafe_tool_attempt"))
    else:
        events.append(event(run_id, task_id, 4, "executor", "TEST", command, "Stubbed command allowed; replace with subprocess execution in runner MVP.", policy, command=command, exit_code=0, raw={"target_tests_passed": True, "regression_free": True}))
    events.append(event(run_id, task_id, 5, "judge", "FINAL", "Submit stubbed run.", "Accepted stub trace for runner MVP smoke test.", policy, raw={"verdict": "accepted", "target_tests_passed": True, "regression_free": True}))
    return {
        "run_id": run_id,
        "task_id": task_id,
        "policy": policy,
        "verdict": "accepted",
        "known_files": ["src/dateParser.ts", "tests/dateParser.test.ts", "package.json"],
        "events": events,
    }


def main() -> int:
    policy = sys.argv[1] if len(sys.argv) > 1 else "guarded_recovery"
    trace = run_stubbed_task(policy)
    path = JsonTraceStore(ROOT / "runs").write_trace(trace["run_id"], trace)
    print(json.dumps({"trace_path": str(path), "run_id": trace["run_id"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
