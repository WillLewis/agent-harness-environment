from __future__ import annotations

import json
from pathlib import Path

import pytest

from adapters.braintrust_adapter import (
    build_export_batch,
    coding_task_row_to_braintrust_dataset_row,
    export_to_braintrust,
    get_braintrust_config,
    run_dry_run,
    scorer_output_to_braintrust_scores,
    suite_output_to_export_batch,
    task_to_braintrust_dataset_row,
    trace_to_braintrust_example,
)


def test_task_to_braintrust_dataset_row_shape():
    task = {
        "id": "bugfix_date_parser_001",
        "title": "Bugfix",
        "type": "bugfix",
        "repo": "toy_repo_date_utils_v1",
        "issue": "Parser fails",
        "successCommand": "npm test -- dateParser",
        "tags": ["bugfix"],
        "failureModes": ["loop_detected"],
    }
    row = task_to_braintrust_dataset_row(task)

    assert row["id"] == "bugfix_date_parser_001"
    assert row["input"]["repo_snapshot"] == "toy_repo_date_utils_v1"
    assert row["expected"]["success_command"] == "npm test -- dateParser"
    assert row["metadata"]["failure_modes_to_watch"] == ["loop_detected"]


def test_coding_task_row_to_braintrust_dataset_row_shape():
    row = coding_task_row_to_braintrust_dataset_row(
        {
            "task_id": "adversarial_env_001",
            "repo_snapshot": "toy_repo_docs_site_v1",
            "issue": "Fix docs",
            "expected_behavior": "Tests pass",
            "success_command": "npm test",
            "gold_files": ["docs/build.md"],
            "failure_modes_to_watch": ["unsafe_tool_attempt"],
        }
    )

    assert row["id"] == "adversarial_env_001"
    assert row["expected"]["gold_files"] == ["docs/build.md"]


def test_trace_to_braintrust_example_omits_events():
    trace = json.loads(Path("data/traces/baseline_date_parser.json").read_text(encoding="utf-8"))
    example = trace_to_braintrust_example(trace)

    assert example["id"] == trace["run_id"]
    assert "events" not in example
    assert example["metadata"]["event_count"] == len(trace["events"])
    assert "loop_detected" in example["metadata"]["failure_labels"]


def test_scorer_output_to_braintrust_scores_shape():
    eval_result = {
        "scores": [
            {"name": "tests_passed", "score": 1.0, "passed": True, "reason": "ok"},
        ]
    }
    scores = scorer_output_to_braintrust_scores(eval_result)

    assert scores[0]["name"] == "tests_passed"
    assert scores[0]["metadata"]["passed"] is True
    assert scores[0]["metadata"]["reason"] == "ok"


def test_suite_output_to_export_batch_shape():
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
    batch = suite_output_to_export_batch(summary)

    assert batch["kind"] == "ahe_suite_export_batch"
    assert batch["experiments"][0]["examples"][0]["scores"][0]["name"] == "tests_passed"


def test_get_braintrust_config_not_configured_by_default(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("BRAINTRUST_API_KEY", raising=False)
    config = get_braintrust_config()

    assert config["configured"] is False
    assert config["api_key_present"] is False


def test_export_to_braintrust_dry_run_ok():
    batch = {"datasets": [{"rows": [1, 2]}], "experiments": [{"examples": [1]}]}
    result = export_to_braintrust(batch, dry_run=True)

    assert result["ok"] is True
    assert result["mode"] == "dry_run"
    assert result["code"] == "dry_run"
    assert result["summary"]["dataset_row_count"] == 2


def test_export_to_braintrust_not_configured_without_credentials(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.delenv("BRAINTRUST_API_KEY", raising=False)
    result = export_to_braintrust({"datasets": []}, dry_run=False)

    assert result["ok"] is False
    assert result["code"] == "not_configured"
    assert result["mode"] == "not_configured"


def test_build_export_batch_covers_current_fixtures(project_root: Path):
    batch = build_export_batch(project_root)

    task_rows = batch["datasets"][0]["rows"]
    coding_rows = batch["datasets"][1]["rows"]
    examples = batch["experiments"][0]["examples"]

    assert len(task_rows) == 3
    assert len(coding_rows) == 3
    assert len(examples) >= 7
    assert batch["suite_batch"]["trace_count"] >= 7
    assert all("scores" in example for example in examples)


def test_run_dry_run_summarizes_all_tasks_traces_scores(project_root: Path):
    result = run_dry_run(project_root)

    assert result["ok"] is True
    assert result["summary"]["dataset_row_count"] == 6
    assert result["summary"]["example_count"] >= 7
    assert result["summary"]["suite_trace_count"] >= 7


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[3]
