from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from adapters import weave_adapter
from adapters.weave_adapter import (
    agent_trace_event_to_weave_span,
    build_export_batch,
    export_to_weave,
    get_weave_config,
    perform_live_export,
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


def test_export_dry_run_never_calls_live_export(monkeypatch: pytest.MonkeyPatch):
    def fail_live(*_a: object, **_k: object) -> dict:
        raise AssertionError("perform_live_export must not run during dry-run")

    def fail_import() -> object:
        raise AssertionError("weave module must not be imported during dry-run")

    monkeypatch.setattr(weave_adapter, "perform_live_export", fail_live)
    monkeypatch.setattr(weave_adapter, "_import_weave_module", fail_import)

    result = export_to_weave({"traces": []}, dry_run=True)

    assert result["ok"] is True
    assert result["code"] == "dry_run"


def test_export_live_refuses_missing_weave_package_and_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("WANDB_API_KEY", raising=False)
    monkeypatch.setattr(
        weave_adapter,
        "_weave_packages_installed",
        lambda: {"weave": False, "wandb": False, "any": False},
    )

    result = export_to_weave({"traces": []}, dry_run=False)

    assert result["ok"] is False
    assert result["code"] == "not_configured"
    assert "weave package" in result["message"]
    assert "WANDB_API_KEY" in result["message"]


def test_perform_live_export_calls_fake_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("WANDB_API_KEY", "test-key")
    monkeypatch.setattr(
        weave_adapter,
        "_weave_packages_installed",
        lambda: {"weave": True, "wandb": True, "any": True},
    )

    class FakeFeedback:
        def __init__(self) -> None:
            self.items: list[tuple[str, dict]] = []

        def add(self, feedback_type: str, payload: dict) -> None:
            self.items.append((feedback_type, payload))

    class FakeCall:
        def __init__(self) -> None:
            self.feedback = FakeFeedback()

    class FakeClient:
        def __init__(self) -> None:
            self.inited_with: str | None = None
            self.calls_created: list[tuple[FakeCall, dict[str, Any]]] = []
            self.calls_finished: list[dict[str, Any]] = []

        def create_call(self, **kwargs: Any) -> FakeCall:
            call = FakeCall()
            self.calls_created.append((call, kwargs))
            return call

        def finish_call(self, call: FakeCall, output: Any = None, **_kwargs: Any) -> None:
            self.calls_finished.append({"call": call, "output": output})

        def flush(self) -> None:
            pass

    fake_client = FakeClient()

    class FakeWeave:
        @staticmethod
        def init(project_name: str) -> FakeClient:
            fake_client.inited_with = project_name
            return fake_client

    batch = {
        "project": "agent-harness-environment",
        "entity": "test-entity",
        "traces": [
            {
                "id": "run_1",
                "op_name": "ahe.run/baseline",
                "attributes": {
                    "task_id": "task_1",
                    "policy": "baseline",
                    "verdict": "rejected",
                },
                "spans": [
                    {
                        "id": "run_1:0",
                        "name": "executor.READ_FILE",
                        "attributes": {"step_id": 0},
                    }
                ],
                "feedback": [
                    {
                        "name": "tests_passed",
                        "value": 0.0,
                        "attributes": {"passed": False},
                    }
                ],
            }
        ],
        "eval_batch": {
            "trace_count": 1,
            "evaluations": [
                {
                    "id": "run_1",
                    "attributes": {"task_id": "task_1", "verdict": "rejected"},
                    "feedback": [{"name": "tests_passed", "value": 0.0, "attributes": {}}],
                }
            ],
        },
    }

    result = perform_live_export(batch, weave_module=FakeWeave)

    assert result["ok"] is True
    assert result["code"] == "live_export_ok"
    assert fake_client.inited_with == "test-entity/agent-harness-environment"
    assert len(fake_client.calls_created) == 3  # root trace + span + suite eval
    root_call, root_kwargs = fake_client.calls_created[0]
    span_call, span_kwargs = fake_client.calls_created[1]
    assert root_kwargs["op"] == "ahe.run/baseline"
    assert span_kwargs["parent"] is root_call
    assert len(fake_client.calls_finished) == 2
    assert fake_client.calls_finished[0]["output"]["verdict"] == "rejected"
    assert fake_client.calls_finished[0]["call"].feedback.items[0][0] == "tests_passed"
    assert result["summary"]["traces"][0]["span_count"] == 1


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[3]
