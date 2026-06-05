from __future__ import annotations

from pathlib import Path

from fixture_validation import validate_trace, validate_trace_dict


def test_validate_existing_trace_fixtures():
    root = Path(__file__).resolve().parents[3]
    errors: list[str] = []
    for path in sorted((root / "data" / "traces").glob("*.json")):
        errors.extend(validate_trace(path))
    assert errors == []


def test_validate_trace_rejects_invalid_actor():
    trace = {
        "verdict": "rejected",
        "known_files": ["src/a.ts"],
        "events": [
            {
                "run_id": "run_1",
                "task_id": "task_1",
                "step_id": 1,
                "timestamp": "2026-06-04T14:00:00.000Z",
                "actor": "invalid_actor",
                "action_type": "PLAN",
                "input_summary": "plan",
                "output_summary": "plan",
                "harness_policy": "baseline",
            },
            {
                "run_id": "run_1",
                "task_id": "task_1",
                "step_id": 2,
                "timestamp": "2026-06-04T14:00:01.000Z",
                "actor": "judge",
                "action_type": "FINAL",
                "input_summary": "final",
                "output_summary": "final",
                "harness_policy": "baseline",
                "raw": {"target_tests_passed": False, "verdict": "rejected"},
            },
        ],
    }
    errors = validate_trace_dict(trace, "invalid_trace")
    assert any("invalid actor" in error for error in errors)


def test_validate_trace_allows_hallucination_demo_label():
    trace = {
        "verdict": "rejected",
        "known_files": ["src/a.ts"],
        "events": [
            {
                "run_id": "run_1",
                "task_id": "task_1",
                "step_id": 1,
                "timestamp": "2026-06-04T14:00:00.000Z",
                "actor": "executor",
                "action_type": "EDIT",
                "input_summary": "edit",
                "output_summary": "edit",
                "harness_policy": "baseline",
                "failure_label": "hallucinated_file",
                "files_touched": ["src/missing.ts"],
            },
            {
                "run_id": "run_1",
                "task_id": "task_1",
                "step_id": 2,
                "timestamp": "2026-06-04T14:00:01.000Z",
                "actor": "judge",
                "action_type": "FINAL",
                "input_summary": "final",
                "output_summary": "final",
                "harness_policy": "baseline",
                "raw": {"target_tests_passed": False, "verdict": "rejected"},
            },
        ],
    }
    errors = validate_trace_dict(trace, "hallucination_demo_trace")
    assert errors == []
