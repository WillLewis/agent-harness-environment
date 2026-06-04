from __future__ import annotations

from .common import ScoreResult, events


def score_loop(trace: dict) -> ScoreResult:
    commands: list[str] = []
    for event in events(trace):
        if event.get("action_type") in {"TEST", "TERMINAL", "RETRY"} and event.get("exit_code") not in {None, 0}:
            commands.append(event.get("command") or "")

    max_repeat = 0
    current = 0
    last = None
    for command in commands:
        if command and command == last:
            current += 1
        else:
            current = 1
            last = command
        max_repeat = max(max_repeat, current)

    label_loop = any(event.get("failure_label") == "loop_detected" for event in events(trace))
    if label_loop or max_repeat >= 2:
        return ScoreResult("loop_score", 0.91 if label_loop else 0.7, False, "Repeated failing command detected without intervening evidence.")
    return ScoreResult("loop_score", 0.02, True, "No repeated failing command loop detected.")
