#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from task_runner import DEFAULT_TASK_ID, run_task, write_trace

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python services/runner/run_task.py <policy> [task_id]", file=sys.stderr)
        print("Supported policies: guarded_recovery, baseline", file=sys.stderr)
        print(f"Default task_id: {DEFAULT_TASK_ID}", file=sys.stderr)
        print("Example: python services/runner/run_task.py baseline adversarial_env_001", file=sys.stderr)
        return 2

    policy = sys.argv[1]
    task_id = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TASK_ID
    try:
        trace = run_task(ROOT, policy, task_id)
        path = write_trace(ROOT, trace)
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
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
