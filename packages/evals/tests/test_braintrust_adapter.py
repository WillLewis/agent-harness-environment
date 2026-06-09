from __future__ import annotations

import json
from pathlib import Path

import pytest

from adapters import braintrust_adapter
from adapters.braintrust_adapter import (
    build_export_batch,
    coding_task_row_to_braintrust_dataset_row,
    export_to_braintrust,
    get_braintrust_config,
    perform_live_export,
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
    # default source=real: one reliability dataset + cockpit trace experiment
    batch = build_export_batch(project_root)

    assert len(batch["datasets"]) == 1
    reliability_rows = batch["datasets"][0]["rows"]
    examples = batch["experiments"][0]["examples"]

    assert len(reliability_rows) > 0  # cells from reliability_*_001.json files
    assert len(examples) == 6  # cockpit traces
    assert batch["suite_batch"]["trace_count"] is None  # no suite for real source
    assert all("scores" in example for example in examples)


def test_run_dry_run_summarizes_all_tasks_traces_scores(project_root: Path):
    # default source=real: reliability rows + cockpit trace examples
    result = run_dry_run(project_root)

    assert result["ok"] is True
    assert result["summary"]["dataset_row_count"] > 0  # reliability cells
    assert result["summary"]["example_count"] == 6  # cockpit traces
    assert result["summary"]["suite_trace_count"] is None  # no suite for real source


def test_export_dry_run_never_calls_live_export(monkeypatch: pytest.MonkeyPatch):
    live_called = False

    def fail_live(*_a: object, **_k: object) -> dict:
        nonlocal live_called
        live_called = True
        raise AssertionError("perform_live_export must not run during dry-run")

    def fail_import() -> object:
        raise AssertionError("braintrust module must not be imported during dry-run")

    monkeypatch.setattr(braintrust_adapter, "perform_live_export", fail_live)
    monkeypatch.setattr(braintrust_adapter, "_import_braintrust_module", fail_import)

    result = export_to_braintrust({"datasets": [], "experiments": []}, dry_run=True)

    assert result["ok"] is True
    assert result["code"] == "dry_run"
    assert live_called is False


def test_export_live_refuses_missing_package_and_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("BRAINTRUST_API_KEY", raising=False)
    monkeypatch.setattr(braintrust_adapter, "_braintrust_package_installed", lambda: False)

    result = export_to_braintrust({"datasets": []}, dry_run=False)

    assert result["ok"] is False
    assert result["code"] == "not_configured"
    assert "braintrust package" in result["message"]
    assert "BRAINTRUST_API_KEY" in result["message"]


def test_perform_live_export_calls_fake_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("BRAINTRUST_API_KEY", "test-key")
    monkeypatch.setattr(braintrust_adapter, "_braintrust_package_installed", lambda: True)

    class FakeDataset:
        def __init__(self) -> None:
            self.inserts: list[dict] = []

        def insert(self, **kwargs: object) -> None:
            self.inserts.append(dict(kwargs))

        def flush(self) -> None:
            pass

    class FakeExperiment:
        def __init__(self) -> None:
            self.logs: list[dict] = []

        def log(self, **kwargs: object) -> None:
            self.logs.append(dict(kwargs))

        def flush(self) -> None:
            pass

    fake_datasets: list[FakeDataset] = []
    fake_experiments: list[FakeExperiment] = []

    class FakeBraintrust:
        @staticmethod
        def init_dataset(*, project: str, name: str) -> FakeDataset:
            assert project == "test-project"
            assert name == "ahe_tasks"
            ds = FakeDataset()
            fake_datasets.append(ds)
            return ds

        @staticmethod
        def init(*, project: str, experiment: str, is_public: bool = False) -> FakeExperiment:
            assert project == "test-project"
            assert experiment in {"ahe_static_trace_fixtures", "ahe_static_suite"}
            # Public hosted demo: experiments must be uploaded publicly readable.
            assert is_public is True
            exp = FakeExperiment()
            fake_experiments.append(exp)
            return exp

    batch = {
        "project": "test-project",
        "datasets": [
            {
                "name": "ahe_tasks",
                "rows": [
                    {
                        "id": "task_1",
                        "input": {"task_id": "task_1"},
                        "expected": {"success_command": "npm test"},
                        "metadata": {"source": "test"},
                    }
                ],
            }
        ],
        "experiments": [
            {
                "name": "ahe_static_trace_fixtures",
                "examples": [
                    {
                        "id": "run_1",
                        "input": {"task_id": "task_1"},
                        "expected": {"verdict": "accepted"},
                        "scores": [{"name": "tests_passed", "score": 1.0}],
                        "metadata": {"source": "test"},
                    }
                ],
            }
        ],
        "suite_batch": {
            "experiments": [
                {
                    "name": "ahe_static_suite",
                    "examples": [
                        {
                            "id": "suite_1",
                            "input": {"task_id": "task_1"},
                            "expected": {"verdict": "rejected"},
                            "scores": [{"name": "tests_passed", "score": 0.0}],
                        }
                    ],
                }
            ],
            "trace_count": 1,
        },
    }

    result = perform_live_export(batch, braintrust_module=FakeBraintrust)

    assert result["ok"] is True
    assert result["code"] == "live_export_ok"
    assert len(fake_datasets) == 1
    assert fake_datasets[0].inserts[0]["input"] == {"task_id": "task_1"}
    assert fake_datasets[0].inserts[0]["metadata"]["ahe_row_id"] == "task_1"
    assert len(fake_experiments) == 2
    assert fake_experiments[0].logs[0]["scores"] == {"tests_passed": 1.0}
    assert fake_experiments[1].logs[0]["scores"] == {"tests_passed": 0.0}
    assert result["summary"]["datasets"][0]["row_count"] == 1
    assert result["summary"]["experiments"][1]["name"] == "ahe_static_suite"


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[3]
