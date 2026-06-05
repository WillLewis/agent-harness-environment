from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from mcp_helpers import normalize_trace_for_candidate, promote_run_trace, read_dataset_candidates

EVAL_DIR = Path(__file__).resolve().parents[2] / "packages" / "evals"
import sys

if str(EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_DIR))

from fixture_validation import validate_trace_dict  # noqa: E402


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _seed_promotion_project(root: Path, project_root: Path) -> Path:
    trace_src = project_root / "data" / "traces" / "guarded_recovery_multi_agent_contract.json"
    runs_dir = root / "runs"
    runs_dir.mkdir(parents=True)
    trace_path = runs_dir / "run_local_guarded_recovery_multi_agent_contract_001.json"
    trace = json.loads(trace_src.read_text(encoding="utf-8"))
    trace["run_id"] = "run_local_guarded_recovery_multi_agent_contract_001"
    trace["sandbox_path"] = "runs/sandboxes/run_local_guarded_recovery_multi_agent_contract_001"
    trace["events"][0]["raw"] = {
        "terminal_output": "x" * 800,
        "note": str(project_root / "runs" / "sandboxes" / "demo"),
    }
    trace_path.write_text(json.dumps(trace), encoding="utf-8")

    data_dir = root / "data"
    data_dir.mkdir(parents=True)
    shutil.copy(project_root / "data" / "failure_clusters.json", data_dir / "failure_clusters.json")

    curated = root / "data" / "traces"
    curated.mkdir(parents=True)
    for path in (project_root / "data" / "traces").glob("*.json"):
        shutil.copy(path, curated / path.name)

    return trace_path


def test_promote_run_trace_writes_candidate_and_metadata(project_root: Path, tmp_path: Path):
    root = tmp_path
    trace_path = _seed_promotion_project(root, project_root)

    def fake_eval(_path: Path) -> dict:
        return {
            "verdict": "accepted",
            "policy": "guarded_recovery",
            "aggregate_run_quality": 0.818,
            "scores": [{"name": "contract_consistency", "score": 1.0, "passed": True, "reason": "ok"}],
        }

    result = promote_run_trace(
        root,
        str(trace_path.relative_to(root)),
        fake_eval,
        validate_trace_impl=validate_trace_dict,
    )

    assert result["ok"] is True
    assert result["metadata_written"] is True
    assert result["already_exists"] is False
    candidate_path = root / result["candidate_trace_path"]
    assert candidate_path.exists()

    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    assert candidate["run_id"] == "run_local_guarded_recovery_multi_agent_contract_001"
    assert "sandbox_path" not in candidate
    assert validate_trace_dict(candidate, str(candidate_path)) == []

    metadata_rows = read_dataset_candidates(root / "data" / "datasets" / "generated_candidates.jsonl")
    assert len(metadata_rows) == 1
    row = metadata_rows[0]
    assert row["source_run_id"] == "run_local_guarded_recovery_multi_agent_contract_001"
    assert row["task_id"] == "multi_agent_contract_001"
    assert row["aggregate_run_quality"] == 0.818
    assert "failure_labels" in row
    assert row["candidate_trace_path"] == result["candidate_trace_path"]


def test_promote_run_trace_is_idempotent_by_source_run_id(project_root: Path, tmp_path: Path):
    root = tmp_path
    trace_path = _seed_promotion_project(root, project_root)

    def fake_eval(_path: Path) -> dict:
        return {
            "verdict": "accepted",
            "policy": "guarded_recovery",
            "aggregate_run_quality": 0.818,
            "scores": [],
        }

    first = promote_run_trace(root, str(trace_path.relative_to(root)), fake_eval)
    second = promote_run_trace(root, str(trace_path.relative_to(root)), fake_eval)

    assert first["metadata_written"] is True
    assert second["already_exists"] is True
    assert second["metadata_written"] is False
    assert second["candidate_refreshed"] is True

    rows = read_dataset_candidates(root / "data" / "datasets" / "generated_candidates.jsonl")
    assert len(rows) == 1


def test_promote_run_trace_does_not_overwrite_curated_fixtures_by_default(
    project_root: Path, tmp_path: Path
):
    root = tmp_path
    trace_path = _seed_promotion_project(root, project_root)
    curated_path = root / "data" / "traces" / "guarded_recovery_multi_agent_contract.json"
    before = curated_path.read_text(encoding="utf-8")

    result = promote_run_trace(
        root,
        str(trace_path.relative_to(root)),
        lambda _p: {"verdict": "accepted", "aggregate_run_quality": 0.5, "scores": []},
    )

    assert result["ok"] is True
    assert result["fixture_written"] is False
    assert curated_path.read_text(encoding="utf-8") == before


def test_promote_run_trace_write_fixture_requires_explicit_name(project_root: Path, tmp_path: Path):
    root = tmp_path
    trace_path = _seed_promotion_project(root, project_root)

    result = promote_run_trace(
        root,
        str(trace_path.relative_to(root)),
        lambda _p: {"verdict": "accepted", "aggregate_run_quality": 0.5, "scores": []},
        write_fixture=True,
        fixture_name=None,
    )

    assert result["ok"] is False
    assert result["code"] == "fixture_name_required"


def test_normalize_trace_for_candidate_strips_transient_fields(project_root: Path, tmp_path: Path):
    trace = {
        "run_id": "run_local_test",
        "sandbox_path": "runs/sandboxes/run_local_test",
        "events": [
            {
                "step_id": 1,
                "timestamp": "2026-01-01T00:00:00+00:00",
                "raw": {"terminal_output": "line\n" * 200},
            }
        ],
    }
    normalized = normalize_trace_for_candidate(trace, project_root)
    assert "sandbox_path" not in normalized
    assert normalized["events"][0]["timestamp"].endswith("Z")
    assert "truncated" in normalized["events"][0]["raw"]["terminal_output"]
