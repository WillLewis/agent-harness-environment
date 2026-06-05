from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcp_helpers import (
    compare_policies,
    create_failure_cluster,
    get_trace,
    list_eval_runs,
    promote_trace_to_dataset,
    summarize_trace,
)


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_list_eval_runs_returns_ok_envelope(project_root: Path):
    result = list_eval_runs(project_root)
    assert result["ok"] is True
    assert result["count"] >= 3
    assert all("run_id" in run for run in result["runs"])


def test_get_trace_compact_summary_shape(project_root: Path):
    result = get_trace(project_root, "run_baseline_date_parser_001", verbose=False)
    assert result["ok"] is True
    summary = result["summary"]
    assert summary["run_id"] == "run_baseline_date_parser_001"
    assert summary["policy"] == "baseline"
    assert summary["verdict"] == "rejected"
    assert summary["event_count"] >= 1
    assert "loop_detected" in summary["failure_labels"]
    assert summary["events"][0]["action_type"] == "PLAN"
    assert "raw" not in summary["events"][0]


def test_get_trace_compact_payload_stays_small(project_root: Path):
    result = get_trace(project_root, "run_baseline_date_parser_001", verbose=False)
    payload = json.dumps(result)
    assert len(payload.encode("utf-8")) < 4096


def test_get_trace_verbose_returns_full_trace(project_root: Path):
    compact = get_trace(project_root, "run_guarded_date_parser_001", verbose=False)
    verbose = get_trace(project_root, "run_guarded_date_parser_001", verbose=True)

    assert compact["ok"] is True
    assert verbose["ok"] is True
    assert verbose["verbose"] is True
    assert "events" in verbose["trace"]
    assert "raw" in verbose["trace"]["events"][0]


def test_get_trace_missing_run_returns_structured_error(project_root: Path):
    result = get_trace(project_root, "missing_run_id", verbose=False)
    assert result["ok"] is False
    assert result["code"] == "trace_not_found"
    assert "available_run_ids" in result
    assert "missing_run_id" not in result["available_run_ids"]


def test_compare_policies_success(project_root: Path):
    result = compare_policies(project_root, "baseline", "guarded_recovery")
    assert result["ok"] is True
    assert result["comparison"]["policy_a"]["policy"] == "baseline"
    assert result["comparison"]["policy_b"]["policy"] == "guarded_recovery"


def test_compare_policies_missing_policy_error(project_root: Path):
    result = compare_policies(project_root, "baseline", "missing_policy")
    assert result["ok"] is False
    assert result["code"] == "policy_not_found"
    assert "missing_policy" in result["missing_policies"]
    assert "baseline" in result["available_policies"]


def test_create_failure_cluster_lookup(project_root: Path):
    by_id = create_failure_cluster(project_root, "repeated_terminal_command")
    by_label = create_failure_cluster(project_root, "Looping")

    assert by_id["ok"] is True
    assert by_label["ok"] is True
    assert by_id["cluster"]["id"] == "repeated_terminal_command"


def test_create_failure_cluster_missing_error(project_root: Path):
    result = create_failure_cluster(project_root, "does_not_exist")
    assert result["ok"] is False
    assert result["code"] == "cluster_not_found"
    assert "available_clusters" in result


def test_promote_trace_to_dataset_writes_and_deduplicates(project_root: Path, tmp_path: Path, monkeypatch):
    root = tmp_path
    trace_src = project_root / "data" / "traces" / "baseline_date_parser.json"
    traces_dir = root / "data" / "traces"
    traces_dir.mkdir(parents=True)
    (traces_dir / "baseline_date_parser.json").write_text(trace_src.read_text(encoding="utf-8"), encoding="utf-8")

    clusters_src = project_root / "data" / "failure_clusters.json"
    clusters_dir = root / "data"
    clusters_dir.mkdir(parents=True, exist_ok=True)
    (clusters_dir / "failure_clusters.json").write_text(clusters_src.read_text(encoding="utf-8"), encoding="utf-8")

    def fake_eval(_trace_path: Path) -> dict:
        return {
            "verdict": "rejected",
            "policy": "baseline",
            "aggregate_run_quality": 0.089,
            "scores": [{"name": "loop_score", "score": 0.91, "passed": False, "reason": "loop"}],
        }

    first = promote_trace_to_dataset(root, "run_baseline_date_parser_001", fake_eval)
    second = promote_trace_to_dataset(root, "run_baseline_date_parser_001", fake_eval)

    assert first["ok"] is True
    assert first["written"] is True
    assert first["already_exists"] is False
    assert first["candidate_trace_path"].startswith("data/trace_candidates/")
    assert (root / first["candidate_trace_path"]).exists()
    assert first["candidate"]["source_run_id"] == "run_baseline_date_parser_001"
    assert first["candidate"]["failure_mode"] == "loop_detected"
    assert first["candidate"]["expected_policy_behavior"] == "inspect failing assertion before retry"
    assert "eval_summary" in first["candidate"]

    assert second["ok"] is True
    assert second["written"] is False
    assert second["already_exists"] is True

    output = root / "data" / "datasets" / "generated_candidates.jsonl"
    lines = [line for line in output.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1


def test_summarize_trace_includes_scorer_ready_metadata(project_root: Path):
    trace_path = project_root / "data" / "traces" / "guarded_recovery_date_parser.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    summary = summarize_trace(trace, str(trace_path.relative_to(project_root)))

    assert summary["success_command"] == "npm test -- dateParser"
    assert summary["known_files"]
    assert summary["failure_labels"] == [] or isinstance(summary["failure_labels"], list)
