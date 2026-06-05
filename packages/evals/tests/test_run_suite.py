from __future__ import annotations

import json
from pathlib import Path

import pytest

from run_suite import discover_traces, format_markdown, format_table, run_suite
from suite_gates import check_trace_gate


def test_discover_traces_finds_static_suite():
    traces = discover_traces(Path("data/traces"))
    stems = {path.stem for path in traces}
    assert len(traces) >= 7
    assert "baseline_date_parser" in stems
    assert "guarded_recovery_multi_agent_contract" in stems


def test_suite_json_summary_shape():
    summary = run_suite(Path("data/traces"))

    assert summary["suite_version"] == "1"
    assert summary["trace_count"] == len(summary["traces"])
    assert summary["validation_ok"] is True
    assert summary["gates_ok"] is True
    assert summary["gate_failures"] == []
    assert "by_task_id" in summary
    assert "by_policy" in summary
    assert "by_verdict" in summary
    assert "by_failure_label" in summary

    row = summary["traces"][0]
    assert {"trace_stem", "task_id", "policy", "verdict", "scorer_summary", "gate_ok"} <= set(row)
    assert isinstance(row["scorer_summary"], dict)
    assert "passed" in next(iter(row["scorer_summary"].values()))


def test_suite_groups_failure_labels_for_baselines():
    summary = run_suite(Path("data/traces"))
    by_label = summary["by_failure_label"]
    assert "loop_detected" in by_label
    assert "unsafe_tool_attempt" in by_label
    assert "contract_mismatch" in by_label


def test_format_table_and_markdown_include_trace_rows():
    summary = run_suite(Path("data/traces"))
    table = format_table(summary)
    markdown = format_markdown(summary)

    assert "baseline_date_parser" in table
    assert "guarded_recovery_date_parser" in markdown
    assert "validation=ok" in table


def test_gate_fails_when_expected_failure_label_missing():
    trace = json.loads(Path("data/traces/baseline_adversarial_env.json").read_text(encoding="utf-8"))
    for event in trace["events"]:
        if event.get("failure_label") == "unsafe_tool_attempt":
            event.pop("failure_label", None)

    eval_result = {
        "scores": [
            {"name": "tests_passed", "passed": False, "score": 0.0},
            {"name": "unsafe_tool_use", "passed": False, "score": 1.0},
        ],
        "aggregate_run_quality": 0.1,
    }
    gate = check_trace_gate("baseline_adversarial_env", trace, eval_result)

    assert gate.ok is False
    assert any(failure.rule == "failure_label" for failure in gate.failures)


def test_gate_fails_when_accepted_trace_loses_tests_passed():
    trace = {
        "verdict": "accepted",
        "events": [{"failure_label": None}],
    }
    eval_result = {
        "scores": [
            {"name": "tests_passed", "passed": False, "score": 0.0},
            {"name": "regression_free", "passed": True, "score": 1.0},
        ],
        "aggregate_run_quality": 0.9,
    }
    gate = check_trace_gate("synthetic_accepted", trace, eval_result)

    assert gate.ok is False
    assert any(failure.rule == "accepted_scorer" for failure in gate.failures)


def test_ci_gate_exit_code_via_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    import run_suite as run_suite_module

    bad_trace = {
        "task_id": "bugfix_date_parser_001",
        "run_id": "run_bad",
        "policy": "baseline",
        "verdict": "accepted",
        "known_files": ["src/dateParser.ts"],
        "events": [
            {
                "run_id": "run_bad",
                "task_id": "bugfix_date_parser_001",
                "step_id": 1,
                "timestamp": "2026-06-04T14:00:00.000Z",
                "actor": "planner",
                "action_type": "FINAL",
                "input_summary": "done",
                "output_summary": "done",
                "harness_policy": "baseline",
                "raw": {"target_tests_passed": True, "verdict": "accepted"},
            }
        ],
    }
    trace_path = tmp_path / "bad_gate.json"
    trace_path.write_text(json.dumps(bad_trace), encoding="utf-8")

    monkeypatch.setattr(
        run_suite_module,
        "discover_traces",
        lambda _dir: [trace_path],
    )
    monkeypatch.setattr(
        run_suite_module,
        "validate_trace",
        lambda _path: ["bad_gate.json: synthetic validation error"],
    )

    summary = run_suite_module.run_suite(tmp_path)
    assert summary["validation_ok"] is False
    assert summary["gates_ok"] is False

    monkeypatch.setattr(
        "sys.argv",
        ["run_suite.py", "--ci", "--traces-dir", str(tmp_path)],
    )
    assert run_suite_module.main() == 1


def test_fixture_expectations_cover_all_discovered_traces():
    from suite_gates import FIXTURE_EXPECTATIONS

    for path in discover_traces(Path("data/traces")):
        assert path.stem in FIXTURE_EXPECTATIONS, f"missing gate expectations for {path.stem}"
