#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVENT_FIELDS = {
    "run_id",
    "task_id",
    "step_id",
    "timestamp",
    "actor",
    "action_type",
    "input_summary",
    "output_summary",
    "harness_policy",
}


def validate_trace(path: Path) -> list[str]:
    errors: list[str] = []
    trace = json.loads(path.read_text())
    events = trace.get("events", [])
    if not events:
        errors.append(f"{path}: no events")
    for index, event in enumerate(events, start=1):
        missing = REQUIRED_EVENT_FIELDS - set(event)
        if missing:
            errors.append(f"{path}: event {index} missing {sorted(missing)}")
        if event.get("step_id") != index:
            errors.append(f"{path}: event {index} has step_id {event.get('step_id')}")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in sorted((ROOT / "data" / "traces").glob("*.json")):
        errors.extend(validate_trace(path))
    if errors:
        print("Fixture validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Fixture validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
