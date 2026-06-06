from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from policy_features import extract_features
from reward import calculate_reward_from_eval, normalize_reward, scorer_summary

STATE_VERSION = "1"
ROUTER_POLICY = "rl_lite_router"
DIRECT_POLICY_ARMS = (
    "baseline",
    "test_first",
    "context_first",
    "guarded_recovery",
    "high_reasoning_on_failure",
)
TIE_BREAK_ORDER = (
    "guarded_recovery",
    "context_first",
    "test_first",
    "high_reasoning_on_failure",
    "baseline",
)
DEFAULT_PRIOR_REWARD = 0.5
EXPLORATION_WEIGHT = 0.25


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def router_dir(project_root: Path) -> Path:
    return project_root / "runs" / "router"


def history_path(project_root: Path) -> Path:
    return router_dir(project_root) / "history.jsonl"


def state_path(project_root: Path) -> Path:
    return router_dir(project_root) / "state.json"


def default_state() -> dict[str, Any]:
    return {"version": STATE_VERSION, "updated_at": None, "buckets": {}}


def feature_key(features: dict[str, Any]) -> str:
    fields = [
        "task_type",
        "repo_area",
        "initial_uncertainty",
        "expected_files_count",
        "risk_level",
        "known_failure_pattern",
    ]
    return "|".join(f"{field}={features.get(field, 'unknown')}" for field in fields)


def load_state(project_root: Path) -> dict[str, Any]:
    path = state_path(project_root)
    if not path.exists():
        return default_state()
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(project_root: Path, state: dict[str, Any]) -> None:
    path = state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    state["version"] = STATE_VERSION
    state["updated_at"] = now()
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _empty_arm() -> dict[str, Any]:
    return {"count": 0, "total_reward": 0.0, "mean_reward": DEFAULT_PRIOR_REWARD, "last_reward": None}


def ensure_bucket(state: dict[str, Any], key: str) -> dict[str, Any]:
    buckets = state.setdefault("buckets", {})
    bucket = buckets.setdefault(key, {"arms": {}})
    arms = bucket.setdefault("arms", {})
    for policy in DIRECT_POLICY_ARMS:
        arms.setdefault(policy, _empty_arm())
    return bucket


def update_state(state: dict[str, Any], features: dict[str, Any], policy: str, observed_reward: float) -> dict[str, Any]:
    if policy not in DIRECT_POLICY_ARMS:
        raise ValueError(f"Cannot update router state for non-arm policy: {policy}")

    bucket = ensure_bucket(state, feature_key(features))
    arm = bucket["arms"][policy]
    count = int(arm.get("count", 0)) + 1
    total = round(float(arm.get("total_reward") or 0.0) + observed_reward, 6)
    arm.update(
        {
            "count": count,
            "total_reward": total,
            "mean_reward": round(total / count, 3),
            "last_reward": observed_reward,
        }
    )
    return state


def policy_stats(state: dict[str, Any], features: dict[str, Any]) -> dict[str, dict[str, Any]]:
    bucket = ensure_bucket(state, feature_key(features))
    return {policy: dict(bucket["arms"][policy]) for policy in DIRECT_POLICY_ARMS}


def expected_rewards(state: dict[str, Any], features: dict[str, Any]) -> dict[str, float]:
    stats = policy_stats(state, features)
    return {
        policy: round(float(arm.get("mean_reward", DEFAULT_PRIOR_REWARD)), 3)
        for policy, arm in stats.items()
    }


def selection_scores(state: dict[str, Any], features: dict[str, Any]) -> dict[str, float]:
    stats = policy_stats(state, features)
    total_count = sum(int(arm.get("count", 0)) for arm in stats.values())
    scores: dict[str, float] = {}
    for policy, arm in stats.items():
        count = int(arm.get("count", 0))
        mean = float(arm.get("mean_reward", DEFAULT_PRIOR_REWARD))
        exploration = EXPLORATION_WEIGHT * math.sqrt(math.log(total_count + 1) / (count + 1))
        scores[policy] = round(mean + exploration, 3)
    return scores


def choose_policy(state: dict[str, Any], features: dict[str, Any]) -> tuple[str, float]:
    scores = selection_scores(state, features)
    priorities = {policy: index for index, policy in enumerate(TIE_BREAK_ORDER)}
    selected = max(
        DIRECT_POLICY_ARMS,
        key=lambda policy: (scores[policy], -priorities.get(policy, len(TIE_BREAK_ORDER))),
    )
    return selected, scores[selected]


def decision_for_task(project_root: Path, task: dict[str, Any]) -> dict[str, Any]:
    state = load_state(project_root)
    features = extract_features(task)
    selected, _reward = choose_policy(state, features)
    return {
        "taskFeatures": features,
        "featureKey": feature_key(features),
        "selectedPolicy": selected,
        "why": f"Highest learned contextual-bandit score for {features['task_type']} tasks in bucket {feature_key(features)}.",
        "expectedRewards": expected_rewards(state, features),
        "selectionScores": selection_scores(state, features),
        "policyStats": policy_stats(state, features),
    }


def append_history(project_root: Path, row: dict[str, Any]) -> None:
    path = history_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def read_history(project_root: Path) -> list[dict[str, Any]]:
    path = history_path(project_root)
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def rebuild_state(rows: list[dict[str, Any]]) -> dict[str, Any]:
    state = default_state()
    for row in rows:
        update_state(
            state,
            row["features"],
            row["selected_policy"],
            float(row["observed_reward"]),
        )
    return state


def record_observation(
    project_root: Path,
    *,
    task: dict[str, Any],
    trace: dict[str, Any],
    eval_result: dict[str, Any],
    selected_policy: str,
    decision: dict[str, Any] | None = None,
) -> dict[str, Any]:
    features = extract_features(task)
    before_decision = decision or decision_for_task(project_root, task)
    raw_reward = calculate_reward_from_eval(eval_result, trace)
    observed_reward = normalize_reward(raw_reward)
    row = {
        "created_at": now(),
        "run_id": trace.get("run_id"),
        "task_id": trace.get("task_id"),
        "features": features,
        "feature_key": feature_key(features),
        "selected_policy": selected_policy,
        "expected_rewards": before_decision.get("expectedRewards", {}),
        "observed_reward": observed_reward,
        "raw_reward": raw_reward,
        "scorer_summary": scorer_summary(eval_result),
    }
    append_history(project_root, row)
    state = load_state(project_root)
    update_state(state, features, selected_policy, observed_reward)
    save_state(project_root, state)
    return row


def export_decisions(project_root: Path, tasks: list[dict[str, Any]]) -> dict[str, Any]:
    return {task["id"]: decision_for_task(project_root, task) for task in tasks}
