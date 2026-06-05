from __future__ import annotations

import json
from pathlib import Path

import pytest

from adapters.weave_adapter import (
    agent_trace_event_to_weave_span,
    build_export_batch,
    export_to_weave,
    get_weave_config,
    run_dry_run,
    scorer_output_to_weave_feedback,
    suite_output_to_weave_eval_batch,
    trace_to_weave_trace,
)


def test_agent_trace_event_to_weave_span_shape():
    event = {
        "run_id": "run_test",
        "task_id": "task_1",
        "step_id": 2,
        "timestamp": "2026-06-04T14:00:05.000Z",
        "actor": "executor",
        "action_type": "READ_FILE",
        "input_summary": "Read file",
        "output_summary": "Read ok",
        "harness_policy": "baseline",
        "files_touched": ["src/foo.ts"],
    }
    span = agent_trace_event_to_weave_span(event)

    assert span["kind"] == "weave_span"
    assert span["id"] == "run_test:2"
    assert span["name"] == "executor.READ_FILE"
    assert span["attributes"]["files_touched"] == ["src/foo.ts"]


def test_trace_to_weave_trace_includes_spans():
    trace = json.loads(Path("data/traces/baseline_date_parser.json").read_text(encoding="utf-8"))
    weave_trace = trace_to_weave_trace(trace)

    assert weave_trace["kind"] == "weave_trace"
    assert weave_trace["id"] == trace["run_id"]
    assert len(weave_trace["spans"]) == len(trace["events"])
    assert weave_trace["spans"][0]["kind"] == "weave_span"
    assert "loop_detected" in weave_trace["attributes"]["failure_labels"]


def test_scorer_output_to_weave_feedback_shape():
    eval_result = {
        "scores": [
            {"name": "tests_passed", "score": 0.0, "passed": False, "reason": "fail"},
        ]
    }
    feedback = scorer_output_to_weave_feedback(eval_result)

    assert feedback[0]["kind"] == "weave_feedback"
    assert feedback[0]["feedback_type"] == "score"
    assert feedback[0]["value"] == 0.0
    assert feedback[0]["attributes"]["passed"] is False


def test_suite_output_to_weave_eval_batch_shape():
    summary = {
        "suite_version": "1",
        "trace_count": 1,
        "validation_ok": True,
        "gates_ok": True,
        "traces": [
            {
                "trace_stem": "baseline_date_parser",
                "run_id": "run_baseline_date_parser_001",
                "task_id": "bugfix_date_parser_001",
                "policy": "baseline",
                "verdict": "rejected",
                "failure_labels": ["loop_detected"],
                "aggregate_run_quality": 0.089,
                "scorer_summary": {
                    "tests_passed": {"passed": False, "score": 0.0},
                },
                "gate_ok": True,
            }
        ],
    }
    batch = suite_output_to_weave_eval_batch(summary)

    assert batch["kind"] == "ahe_weave_eval_batch"
    assert batch["evaluations"][0]["feedback"][0]["name"] == "tests_passed"


def test_get_weave_config_not_configured_by_default(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("WANDB_API_KEY", raising=False)
    config = get_weave_config()

    assert config["configured"] is False
    assert config["api_key_present"] is False


def test_export_to_weave_dry_run_ok():
    batch = {"traces": [{"spans": [1, 2], "feedback": [1]}]}
    result = export_to_weave(batch, dry_run=True)

    assert result["ok"] is True
    assert result["mode"] == "dry_run"
    assert result["summary"]["span_count"] == 2
    assert result["summary"]["feedback_count"] == 1


def test_export_to_weave_not_configured_without_credentials(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.delenv("WANDB_API_KEY", raising=False)
    result = export_to_weave({"traces": []}, dry_run=False)

    assert result["ok"] is False
    assert result["code"] == "not_configured"
    assert result["mode"] == "not_configured"


def test_build_export_batch_covers_current_fixtures(project_root: Path):
    batch = build_export_batch(project_root)

    assert len(batch["traces"]) >= 7
    assert batch["eval_batch"]["trace_count"] >= 7
    assert all(trace["spans"] for trace in batch["traces"])
    assert all("feedback" in trace for trace in batch["traces"])


def test_run_dry_run_summarizes_traces_and_scores(project_root: Path):
    result = run_dry_run(project_root)

    assert result["ok"] is True
    assert result["summary"]["trace_count"] >= 7
    assert result["summary"]["span_count"] > 0
    assert result["summary"]["feedback_count"] > 0
    assert result["summary"]["suite_evaluation_count"] >= 7


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[3]
