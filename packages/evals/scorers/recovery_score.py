from __future__ import annotations

from .common import ScoreResult, events

EVIDENCE_ACTIONS = {"READ_FILE", "SEARCH", "ASK_USER"}


def score_recovery(trace: dict) -> ScoreResult:
    trace_events = events(trace)
    failed_steps = [event.get("step_id", 0) for event in trace_events if event.get("action_type") == "TEST" and event.get("exit_code") not in {None, 0}]
    if not failed_steps:
        return ScoreResult("recovery_score", 1.0, True, "No failed test command required recovery.")

    recovered = 0
    for step in failed_steps:
        later = [event for event in trace_events if event.get("step_id", 0) > step]
        saw_evidence = any(event.get("action_type") in EVIDENCE_ACTIONS for event in later)
        later_pass = any(event.get("action_type") == "TEST" and event.get("exit_code") == 0 for event in later)
        if saw_evidence and later_pass:
            recovered += 1

    score = recovered / len(failed_steps)
    return ScoreResult("recovery_score", round(score, 2), score >= 0.75, f"Recovered from {recovered}/{len(failed_steps)} failed test step(s) with new evidence.")
