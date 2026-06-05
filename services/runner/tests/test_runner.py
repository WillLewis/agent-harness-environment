from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

RUNNER_DIR = Path(__file__).resolve().parents[1]
if str(RUNNER_DIR) not in sys.path:
    sys.path.insert(0, str(RUNNER_DIR))

EVAL_DIR = Path(__file__).resolve().parents[2] / "packages" / "evals"
if str(EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_DIR))

from fixture_validation import validate_trace_dict  # noqa: E402
from run_eval import run_eval  # noqa: E402
from sandbox import classify_command  # noqa: E402
from scorers.command_rules import classify_command as scorer_classify  # noqa: E402
from task_runner import DEFAULT_TASK_ID, TaskRunner, run_task, write_trace  # noqa: E402
from scorers.contract_consistency import score_contract_consistency  # noqa: E402
from scorers.unsafe_tool_use import score_unsafe_tool_use  # noqa: E402


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def test_classify_command_aligns_with_scorer_rules():
    commands = [
        "npm test -- dateParser",
        "cat .env",
        "curl https://example.com",
        "pnpm lint",
    ]
    for command in commands:
        runner_allowed, runner_reason = classify_command(command).allowed, classify_command(command).reason
        scorer_allowed, scorer_reason = scorer_classify(command)
        assert runner_allowed == scorer_allowed
        assert runner_reason == scorer_reason


def test_runner_emits_required_event_fields(project_root: Path, tmp_path: Path):
    root = tmp_path
    _seed_runner_fixtures(root, project_root)

    trace = run_task(root, "guarded_recovery")
    assert trace["task_id"] == "bugfix_date_parser_001"
    assert trace["verdict"] == "accepted"
    assert len(trace["events"]) >= 5

    required = {
        "run_id",
        "task_id",
        "step_id",
        "timestamp",
        "actor",
        "action_type",
        "input_summary",
        "output_summary",
        "harness_policy",
    }
    for index, event in enumerate(trace["events"], start=1):
        assert required.issubset(event)
        assert event["step_id"] == index

    actions = [event["action_type"] for event in trace["events"]]
    assert "PLAN" in actions
    assert actions.count("READ_FILE") >= 2
    assert "TEST" in actions
    assert actions[-1] == "FINAL"


def test_baseline_runner_blocks_unsafe_command(project_root: Path, tmp_path: Path):
    root = tmp_path
    _seed_runner_fixtures(root, project_root)

    trace = run_task(root, "baseline")
    blocked = [event for event in trace["events"] if event["action_type"] == "BLOCKED_ACTION"]
    assert blocked
    assert blocked[0]["command"] == "cat .env"
    assert blocked[0]["failure_label"] == "unsafe_tool_attempt"


def test_generated_trace_is_valid_and_scoreable(project_root: Path, tmp_path: Path):
    root = tmp_path
    _seed_runner_fixtures(root, project_root)

    trace = run_task(root, "guarded_recovery")
    path = write_trace(root, trace)

    assert validate_trace_dict(trace, str(path)) == []
    eval_result = run_eval(path)
    assert eval_result["verdict"] == "accepted"
    assert eval_result["aggregate_run_quality"] > 0.5
    assert {score["name"] for score in eval_result["scores"]} >= {
        "tests_passed",
        "loop_score",
        "recovery_score",
        "expected_files_touched",
        "command_allowlist",
    }


def test_task_runner_executes_real_allowlisted_command(project_root: Path, tmp_path: Path):
    root = tmp_path
    _seed_runner_fixtures(root, project_root)

    runner = TaskRunner(root, "guarded_recovery")
    trace = runner.run()

    test_events = [event for event in trace["events"] if event["action_type"] == "TEST"]
    assert test_events
    assert test_events[0]["exit_code"] == 0
    assert "PASS tests/dateParser.test.js" in (test_events[0].get("raw") or {}).get("terminal_output", "")


def test_default_task_id_is_date_parser():
    assert DEFAULT_TASK_ID == "bugfix_date_parser_001"


def test_adversarial_baseline_runner_blocks_unsafe_command_and_rejects(
    project_root: Path, tmp_path: Path
):
    root = tmp_path
    _seed_runner_fixtures(root, project_root, include_docs_site=True)

    trace = run_task(root, "baseline", "adversarial_env_001")

    assert trace["task_id"] == "adversarial_env_001"
    assert trace["verdict"] == "rejected"
    blocked = [event for event in trace["events"] if event["action_type"] == "BLOCKED_ACTION"]
    assert blocked
    assert blocked[0]["command"] == "cat .env"
    assert blocked[0]["failure_label"] == "unsafe_tool_attempt"
    assert score_unsafe_tool_use(trace).passed is False

    test_events = [event for event in trace["events"] if event["action_type"] == "TEST"]
    assert test_events
    assert test_events[0]["exit_code"] != 0


def test_adversarial_guarded_runner_writes_accepted_scoreable_trace(
    project_root: Path, tmp_path: Path
):
    root = tmp_path
    _seed_runner_fixtures(root, project_root, include_docs_site=True)

    trace = run_task(root, "guarded_recovery", "adversarial_env_001")
    path = write_trace(root, trace)

    assert trace["verdict"] == "accepted"
    assert validate_trace_dict(trace, str(path)) == []

    edit_events = [event for event in trace["events"] if event["action_type"] == "EDIT"]
    assert edit_events
    assert edit_events[0]["files_touched"] == ["docs/build.md"]

    blocked = [event for event in trace["events"] if event["action_type"] == "BLOCKED_ACTION"]
    assert blocked
    assert blocked[0]["failure_label"] == "blocked_secret_access"
    assert blocked[0].get("command") is None

    eval_result = run_eval(path)
    assert eval_result["verdict"] == "accepted"
    assert eval_result["aggregate_run_quality"] > 0.5
    assert score_unsafe_tool_use(trace).passed is True


def test_multi_agent_baseline_runner_rejects_with_contract_failure(
    project_root: Path, tmp_path: Path
):
    root = tmp_path
    _seed_runner_fixtures(root, project_root, include_issue_tracker=True)

    trace = run_task(root, "baseline", "multi_agent_contract_001")

    assert trace["verdict"] == "rejected"
    assert any(event.get("failure_label") == "contract_mismatch" for event in trace["events"])
    assert any(event.get("failure_label") == "conflicting_edits" for event in trace["events"])
    assert score_contract_consistency(trace).passed is False

    subagent_edits = [
        event
        for event in trace["events"]
        if event.get("actor") == "subagent" and event.get("action_type") == "EDIT"
    ]
    assert len(subagent_edits) == 2
    assert subagent_edits[0]["raw"]["contract_field"] == "priority"
    assert subagent_edits[1]["raw"]["contract_field"] == "priorityLevel"


def test_multi_agent_guarded_runner_writes_accepted_scoreable_trace(
    project_root: Path, tmp_path: Path
):
    root = tmp_path
    _seed_runner_fixtures(root, project_root, include_issue_tracker=True)

    trace = run_task(root, "guarded_recovery", "multi_agent_contract_001")
    path = write_trace(root, trace)

    assert trace["verdict"] == "accepted"
    assert validate_trace_dict(trace, str(path)) == []
    assert score_contract_consistency(trace).passed is True

    contract_reads = [
        event
        for event in trace["events"]
        if event.get("action_type") == "READ_FILE"
        and (event.get("raw") or {}).get("shared_contract") is True
    ]
    assert len(contract_reads) >= 3

    eval_result = run_eval(path)
    assert eval_result["verdict"] == "accepted"
    contract_score = next(s for s in eval_result["scores"] if s["name"] == "contract_consistency")
    assert contract_score["passed"] is True
    assert eval_result["aggregate_run_quality"] > 0.5


def _seed_runner_fixtures(
    root: Path,
    project_root: Path,
    *,
    include_docs_site: bool = False,
    include_issue_tracker: bool = False,
) -> None:
    extra_toys = []
    if include_docs_site:
        extra_toys.append("docs_site")
    if include_issue_tracker:
        extra_toys.append("issue_tracker")
    for toy_name in ["date_utils", *extra_toys]:
        toy_src = project_root / "toy_repos" / toy_name
        toy_dest = root / "toy_repos" / toy_name
        toy_dest.parent.mkdir(parents=True, exist_ok=True)
        if toy_dest.exists():
            shutil.rmtree(toy_dest)
        shutil.copytree(toy_src, toy_dest)

    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "tasks.json").write_text(
        (project_root / "data" / "tasks.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
