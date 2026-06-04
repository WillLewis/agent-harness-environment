#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def choose_policy(decision: dict) -> tuple[str, float]:
    rewards = decision["expectedRewards"]
    policy, reward = max(rewards.items(), key=lambda item: item[1])
    return policy, reward


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/router_decisions.json")
    data = json.loads(path.read_text())
    for task_id, decision in data.items():
        policy, reward = choose_policy(decision)
        print(json.dumps({"task_id": task_id, "selected_policy": policy, "expected_reward": reward, "why": decision.get("why")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
