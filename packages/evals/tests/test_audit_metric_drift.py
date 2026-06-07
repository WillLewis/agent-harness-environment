from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from audit_metric_drift import (  # noqa: E402
    SOURCE_RUNNER,
    SOURCE_SYNTHETIC,
    SOURCE_TRACE,
    build_audit,
    format_table,
)


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def test_build_audit_classifies_metric_sources(project_root: Path):
    report = build_audit(project_root, include_runner=False)

    assert report["audit_version"] == "1"
    assert report["sources"]["hosted_policy_comparison"]["classification"] == SOURCE_SYNTHETIC
    assert report["sources"]["static_trace_suite"]["classification"] == SOURCE_TRACE
    assert report["sources"]["runner_batch"]["status"] == "skipped"
    assert report["sources"]["static_trace_suite"]["trace_count"] == 14


def test_build_audit_flags_drift_warnings(project_root: Path):
    report = build_audit(project_root, include_runner=False)
    codes = {warning["code"] for warning in report["warnings"]}

    assert "hosted_policy_without_trace_fixtures" in codes
    assert "trace_policy_absent_from_hosted_table" in codes
    assert "metric_basis_mismatch" in codes
    assert "scorer_metrics_absent_from_hosted_table" in codes
    assert "same_policy_divergent_headline_metric" in codes

    hosted_only = report["policy_coverage"]["hosted_only"]
    # test_first and context_first now have promoted replay traces, so they are no
    # longer hosted-only; rl_lite_router stays a hosted/router-only policy.
    assert "test_first" not in hosted_only
    assert "context_first" not in hosted_only
    assert "rl_lite_router" in hosted_only
    assert "test_first" in report["policy_coverage"]["overlapping"]
    assert "context_first" in report["policy_coverage"]["overlapping"]
    assert "baseline_with_steering" in report["policy_coverage"]["trace_only"]


def test_build_audit_includes_runner_when_present(project_root: Path, tmp_path: Path):
    root = tmp_path
    _seed_audit_project(root, project_root)

    runner_src = project_root / "data" / "traces" / "guarded_recovery_date_parser.json"
    runs_dir = root / "runs"
    runs_dir.mkdir(parents=True)
    trace = json.loads(runner_src.read_text(encoding="utf-8"))
    trace["run_id"] = "run_local_guarded_recovery_date_parser_001"
    (runs_dir / "run_local_guarded_recovery_date_parser_001.json").write_text(
        json.dumps(trace), encoding="utf-8"
    )

    report = build_audit(root, include_runner=True)

    assert report["sources"]["runner_batch"]["status"] == "loaded"
    assert report["sources"]["runner_batch"]["classification"] == SOURCE_RUNNER
    assert report["sources"]["runner_batch"]["run_count"] == 1
    assert report["runner_summary"]


def test_format_table_renders_warnings(project_root: Path):
    report = build_audit(project_root, include_runner=False)
    table = format_table(report)

    assert "Metric drift audit" in table
    assert "metric_basis_mismatch" in table
    assert "hosted_policy_without_trace_fixtures" in table


def _seed_audit_project(root: Path, project_root: Path) -> None:
    shutil.copytree(project_root / "data", root / "data")


def test_build_audit_idempotent_warning_shape(project_root: Path):
    first = build_audit(project_root, include_runner=False)
    second = build_audit(project_root, include_runner=False)

    assert first["warning_count"] == second["warning_count"]
    assert first["policy_coverage"] == second["policy_coverage"]
