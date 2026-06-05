from __future__ import annotations

from .common import ScoreResult, events

MULTI_AGENT_TASK_ID = "multi_agent_contract_001"
COORDINATION_FAILURE_LABELS = {"contract_mismatch", "conflicting_edits"}


def _contract_field_from_event(event: dict) -> str | None:
    raw = event.get("raw") or {}
    field = raw.get("contract_field")
    return field if isinstance(field, str) else None


def _is_contract_read(event: dict) -> bool:
    if event.get("action_type") != "READ_FILE":
        return False
    for path in event.get("files_touched") or []:
        if "contracts/" in path:
            return True
    raw = event.get("raw") or {}
    return raw.get("shared_contract") is True


def score_contract_consistency(trace: dict) -> ScoreResult:
    if trace.get("task_id") != MULTI_AGENT_TASK_ID:
        return ScoreResult(
            "contract_consistency",
            1.0,
            True,
            "Not a multi-agent contract task; scorer skipped.",
        )

    trace_events = events(trace)
    for event in trace_events:
        if event.get("failure_label") in COORDINATION_FAILURE_LABELS:
            return ScoreResult(
                "contract_consistency",
                0.0,
                False,
                f"Coordination failure detected: {event.get('failure_label')}.",
            )

    contract_reads = [event for event in trace_events if _is_contract_read(event)]
    edits = [event for event in trace_events if event.get("action_type") == "EDIT"]
    backend_edits = [
        event
        for event in edits
        if event.get("actor") == "subagent"
        and any(path.startswith("backend/") for path in event.get("files_touched") or [])
    ]
    frontend_edits = [
        event
        for event in edits
        if event.get("actor") == "subagent"
        and any(path.startswith("frontend/") for path in event.get("files_touched") or [])
    ]

    if not contract_reads:
        return ScoreResult(
            "contract_consistency",
            0.0,
            False,
            "No shared contract context read before subagent edits.",
        )

    if len(backend_edits) < 1 or len(frontend_edits) < 1:
        return ScoreResult(
            "contract_consistency",
            0.0,
            False,
            "Expected backend and frontend subagent edits.",
        )

    backend_field = _contract_field_from_event(backend_edits[-1])
    frontend_field = _contract_field_from_event(frontend_edits[-1])
    if backend_field and frontend_field and backend_field == frontend_field:
        return ScoreResult(
            "contract_consistency",
            1.0,
            True,
            f"Backend and frontend edits aligned on contract field '{backend_field}'.",
        )

    return ScoreResult(
        "contract_consistency",
        0.0,
        False,
        "Backend and frontend edits do not share the same contract field.",
    )
