from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

RUNNER_DIR = Path(__file__).resolve().parents[3] / "services" / "runner"
EVAL_DIR = Path(__file__).resolve().parents[2] / "evals"
for directory in (RUNNER_DIR, EVAL_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from policy_features import extract_features  # noqa: E402
from reward import calculate_reward_from_eval, normalize_reward  # noqa: E402
from router_state import choose_policy, default_state, feature_key, update_state  # noqa: E402
from train_router import train_router  # noqa: E402
from run_eval import run_eval  # noqa: E402


def test_reward_mapping_prefers_accepted_guarded_trace() -> None:
    guarded_path = Path("data/traces/guarded_recovery_adversarial_env.json")
    baseline_path = Path("data/traces/baseline_adversarial_env.json")
    guarded_trace = json.loads(guarded_path.read_text(encoding="utf-8"))
    baseline_trace = json.loads(baseline_path.read_text(encoding="utf-8"))

    guarded_reward = calculate_reward_from_eval(run_eval(guarded_path), guarded_trace)
    baseline_reward = calculate_reward_from_eval(run_eval(baseline_path), baseline_trace)

    assert guarded_reward > baseline_reward
    assert normalize_reward(guarded_reward) > normalize_reward(baseline_reward)


def test_reward_penalizes_unsafe_and_extra_tools() -> None:
    clean_eval = {
        "scores": [
            {"name": "tests_passed", "passed": True},
            {"name": "recovery_score", "passed": True},
            {"name": "regression_free", "passed": True},
            {"name": "unsafe_tool_use", "passed": True, "score": 0.0},
            {"name": "hallucinated_file", "passed": True, "score": 0.0},
        ]
    }
    unsafe_eval = {
        "scores": [
            {"name": "tests_passed", "passed": True},
            {"name": "recovery_score", "passed": True},
            {"name": "regression_free", "passed": True},
            {"name": "unsafe_tool_use", "passed": False, "score": 1.0},
            {"name": "hallucinated_file", "passed": True, "score": 0.0},
        ]
    }
    clean_trace = {"events": [{"action_type": "TEST"}]}
    noisy_trace = {
        "events": [
            {"action_type": "READ_FILE"},
            {"action_type": "READ_FILE"},
            {"action_type": "TEST"},
            {"action_type": "BLOCKED_ACTION"},
        ]
    }

    clean_reward = calculate_reward_from_eval(clean_eval, clean_trace)
    unsafe_reward = calculate_reward_from_eval(unsafe_eval, clean_trace)
    noisy_reward = calculate_reward_from_eval(clean_eval, noisy_trace)

    assert unsafe_reward < clean_reward
    assert noisy_reward < clean_reward


def test_update_state_tracks_arm_statistics() -> None:
    state = default_state()
    features = {
        "task_type": "bugfix",
        "repo_area": "backend",
        "initial_uncertainty": "medium",
        "expected_files_count": "one",
        "risk_level": "medium",
        "known_failure_pattern": "ignored_test_output",
    }

    update_state(state, features, "guarded_recovery", 0.8)
    update_state(state, features, "guarded_recovery", 0.6)

    arm = state["buckets"][feature_key(features)]["arms"]["guarded_recovery"]
    assert arm["count"] == 2
    assert arm["total_reward"] == 1.4
    assert arm["mean_reward"] == 0.7
    assert arm["last_reward"] == 0.6


def test_ucb_selection_uses_tie_break_and_converges_to_high_reward_arm() -> None:
    features = {
        "task_type": "bugfix",
        "repo_area": "backend",
        "initial_uncertainty": "medium",
        "expected_files_count": "one",
        "risk_level": "medium",
        "known_failure_pattern": "ignored_test_output",
    }
    state = default_state()

    selected, _score = choose_policy(state, features)
    assert selected == "guarded_recovery"

    for _ in range(8):
        update_state(state, features, "baseline", 0.2)
        update_state(state, features, "guarded_recovery", 0.9)

    selected, _score = choose_policy(state, features)
    assert selected == "guarded_recovery"


def test_feature_keys_are_stable_for_current_tasks() -> None:
    tasks = json.loads(Path("data/tasks.json").read_text(encoding="utf-8"))
    keys = [feature_key(extract_features(task)) for task in tasks]

    assert len(keys) == len(set(keys))
    assert all("task_type=" in key for key in keys)


def test_train_router_creates_local_history_and_state(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[3]
    root = tmp_path
    _seed_project(root, project_root)

    summary = train_router(root)

    assert summary["ok"] is True
    assert summary["trained_runs"] == 15
    assert (root / "runs" / "router" / "history.jsonl").exists()
    state_path = root / "runs" / "router" / "state.json"
    assert state_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert len(state["buckets"]) == 3


def _seed_project(root: Path, project_root: Path) -> None:
    for toy_name in ("date_utils", "docs_site", "issue_tracker"):
        toy_src = project_root / "toy_repos" / toy_name
        toy_dest = root / "toy_repos" / toy_name
        toy_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(toy_src, toy_dest)

    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "tasks.json").write_text(
        (project_root / "data" / "tasks.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
