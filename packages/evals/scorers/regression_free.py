from __future__ import annotations

from .common import ScoreResult, events


def score_regression_free(trace: dict) -> ScoreResult:
    for event in reversed(events(trace)):
        raw = event.get("raw") or {}
        if raw.get("regression_free") is True:
            return ScoreResult("regression_free", 1.0, True, "Regression-free signal found in trace.")
        command = event.get("command") or ""
        if event.get("action_type") == "TEST" and event.get("exit_code") == 0 and "&&" in command:
            return ScoreResult("regression_free", 1.0, True, "Combined target and regression test command passed.")
    return ScoreResult("regression_free", 0.0, False, "No regression-free signal found.")
