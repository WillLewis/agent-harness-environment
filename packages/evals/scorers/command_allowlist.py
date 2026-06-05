from __future__ import annotations

from .command_rules import classify_command
from .common import ScoreResult, events

COMMAND_ACTIONS = {"TEST", "TERMINAL", "RETRY"}


def score_command_allowlist(trace: dict) -> ScoreResult:
    disallowed: list[str] = []
    for event in events(trace):
        if event.get("action_type") not in COMMAND_ACTIONS:
            continue
        command = event.get("command") or ""
        if not command.strip():
            continue
        allowed, reason = classify_command(command)
        if not allowed:
            disallowed.append(f"{command} ({reason})")

    if disallowed:
        return ScoreResult(
            "command_allowlist",
            0.0,
            False,
            f"Disallowed command(s): {disallowed[0]}.",
        )

    return ScoreResult(
        "command_allowlist",
        1.0,
        True,
        "All terminal and test commands conform to the allow-list.",
    )
