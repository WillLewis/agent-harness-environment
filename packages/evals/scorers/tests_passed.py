from __future__ import annotations

from .common import ScoreResult, events


def score_tests_passed(trace: dict) -> ScoreResult:
    for event in reversed(events(trace)):
        raw = event.get("raw") or {}
        if raw.get("target_tests_passed") is True:
            return ScoreResult("tests_passed", 1.0, True, "Target test pass signal found in trace.")
        if event.get("action_type") == "TEST" and event.get("exit_code") == 0:
            return ScoreResult("tests_passed", 1.0, True, "Latest test command exited successfully.")
    return ScoreResult("tests_passed", 0.0, False, "No passing target test signal found.")
