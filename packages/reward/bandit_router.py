#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from router_state import choose_policy as choose_learned_policy
from router_state import decision_for_task, load_state

ROOT = Path(__file__).resolve().parents[2]


def choose_policy(decision: dict) -> tuple[str, float]:
    rewards = decision["expectedRewards"]
    policy, reward = max(rewards.items(), key=lambda item: item[1])
    return policy, reward


def load_task(project_root: Path, task_id: str) -> dict:
    tasks = json.loads((project_root / "data" / "tasks.json").read_text(encoding="utf-8"))
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise ValueError(f"Unknown task_id: {task_id}")


def legacy_fixture_main(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    for task_id, decision in data.items():
        policy, reward = choose_policy(decision)
        print(
            json.dumps(
                {
                    "task_id": task_id,
                    "selected_policy": policy,
                    "expected_reward": reward,
                    "why": decision.get("why"),
                },
                indent=2,
            )
        )
    return 0


def main() -> int:
    args = [arg for arg in sys.argv[1:] if arg != "--"]
    if args and args[0].endswith(".json"):
        return legacy_fixture_main(Path(args[0]))

    task_id = args[0] if args else "bugfix_date_parser_001"
    try:
        task = load_task(ROOT, task_id)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2

    decision = decision_for_task(ROOT, task)
    selected, score = choose_learned_policy(load_state(ROOT), decision["taskFeatures"])
    print(
        json.dumps(
            {
                "ok": True,
                "task_id": task_id,
                "selected_policy": selected,
                "expected_reward": decision["expectedRewards"][selected],
                "selection_score": score,
                "decision": decision,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
