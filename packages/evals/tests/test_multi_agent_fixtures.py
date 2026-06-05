from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from fixture_validation import validate_trace_dict
from run_eval import run_eval
from scorers.contract_consistency import score_contract_consistency
from scorers.tests_passed import score_tests_passed

TOOLS_DIR = Path(__file__).resolve().parents[3] / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from mcp_helpers import create_failure_cluster  # noqa: E402


def test_multi_agent_baseline_fixture_validates():
    path = Path("data/traces/baseline_multi_agent_contract.json")
    trace = json.loads(path.read_text(encoding="utf-8"))
    assert validate_trace_dict(trace, str(path)) == []


def test_multi_agent_guarded_fixture_validates():
    path = Path("data/traces/guarded_recovery_multi_agent_contract.json")
    trace = json.loads(path.read_text(encoding="utf-8"))
    assert validate_trace_dict(trace, str(path)) == []


def test_multi_agent_baseline_scorer_expectations():
    trace = json.loads(Path("data/traces/baseline_multi_agent_contract.json").read_text(encoding="utf-8"))

    assert trace["verdict"] == "rejected"
    assert any(event.get("failure_label") == "contract_mismatch" for event in trace["events"])

    contract = score_contract_consistency(trace)
    tests = score_tests_passed(trace)

    assert contract.passed is False
    assert tests.passed is False


def test_multi_agent_guarded_scorer_expectations():
    trace = json.loads(Path("data/traces/guarded_recovery_multi_agent_contract.json").read_text(encoding="utf-8"))

    assert trace["verdict"] == "accepted"

    contract = score_contract_consistency(trace)
    tests = score_tests_passed(trace)

    assert contract.passed is True
    assert tests.passed is True


def test_multi_agent_traces_are_scoreable_by_run_eval():
    baseline = run_eval(Path("data/traces/baseline_multi_agent_contract.json"))
    guarded = run_eval(Path("data/traces/guarded_recovery_multi_agent_contract.json"))

    assert baseline["verdict"] == "rejected"
    assert guarded["verdict"] == "accepted"
    assert baseline["task_id"] == guarded["task_id"] == "multi_agent_contract_001"
    assert any(score["name"] == "contract_consistency" for score in baseline["scores"])
    assert any(score["name"] == "contract_consistency" for score in guarded["scores"])


def test_multi_agent_dataset_and_task_ids_align():
    tasks = json.loads(Path("data/tasks.json").read_text(encoding="utf-8"))
    dataset_rows = [
        json.loads(line)
        for line in Path("packages/evals/datasets/coding_tasks.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    task = next(item for item in tasks if item["id"] == "multi_agent_contract_001")
    dataset = next(row for row in dataset_rows if row["task_id"] == "multi_agent_contract_001")

    assert task["successCommand"] == dataset["success_command"] == "pnpm test"
    assert task["repo"] == dataset["repo_snapshot"] == "toy_repo_issue_tracker_v1"
    assert "contract_mismatch" in dataset["failure_modes_to_watch"]


def test_failure_cluster_lookup_for_contract_mismatch():
    root = Path(__file__).resolve().parents[3]
    result = create_failure_cluster(root, "contract_mismatch")

    assert result["ok"] is True
    assert result["cluster"]["id"] == "contract_mismatch"
    assert "multi_agent_contract_001" in result["cluster"]["affectedTasks"]


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[3]
