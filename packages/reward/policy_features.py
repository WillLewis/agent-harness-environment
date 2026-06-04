from __future__ import annotations

from typing import Literal, TypedDict


class TaskFeatures(TypedDict):
    task_type: Literal["bugfix", "feature", "refactor", "adversarial", "multi_agent"]
    repo_area: Literal["frontend", "backend", "infra", "tests", "docs"]
    initial_uncertainty: Literal["low", "medium", "high"]
    expected_files_count: Literal["one", "few", "many"]
    risk_level: Literal["low", "medium", "high"]
    known_failure_pattern: str


def extract_features(task: dict) -> TaskFeatures:
    tags = set(task.get("tags", []))
    task_type = task.get("type", "bugfix")
    return {
        "task_type": task_type,
        "repo_area": "frontend" if "frontend" in tags else "backend",
        "initial_uncertainty": "medium",
        "expected_files_count": "one" if "single-file" in tags else "few",
        "risk_level": "high" if task_type == "adversarial" else "medium",
        "known_failure_pattern": (task.get("failureModes") or ["none"])[0],
    }
