#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from run_eval import run_eval  # noqa: E402
from run_suite import run_suite  # noqa: E402

AUDIT_VERSION = "1"

SOURCE_SYNTHETIC = "synthetic_benchmark_fixture"
SOURCE_TRACE = "deterministic_trace_score"
SOURCE_RUNNER = "runner_generated_local_trace"

HOSTED_TO_SCORER: dict[str, str] = {
    "success": "tests_passed",
    "recovery": "recovery_score",
    "loop": "loop_score",
    "hallucinatedFiles": "hallucinated_file",
    "unsafeAttempts": "unsafe_tool_use",
}

HOSTED_ONLY_METRICS = ("humanInterventions", "costTier", "toolCalls")

ALL_SCORERS = (
    "tests_passed",
    "regression_free",
    "loop_score",
    "hallucinated_file",
    "unsafe_tool_use",
    "patch_minimality",
    "recovery_score",
    "expected_files_touched",
    "command_allowlist",
    "contract_consistency",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_hosted_policy_rows(project_root: Path) -> list[dict[str, Any]]:
    path = project_root / "data" / "evals" / "policy_comparison.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_static_suite_summary(project_root: Path) -> dict[str, Any]:
    traces_dir = project_root / "data" / "traces"
    return run_suite(traces_dir)


def discover_runner_traces(project_root: Path) -> list[Path]:
    runs_dir = project_root / "runs"
    if not runs_dir.exists():
        return []
    return sorted(path for path in runs_dir.glob("run_local_*.json") if path.is_file())


def _policy_trace_rollup(trace_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in trace_rows:
        grouped[str(row.get("policy") or "unknown")].append(row)

    rollup: dict[str, dict[str, Any]] = {}
    for policy, rows in grouped.items():
        scorer_means: dict[str, float] = {}
        for scorer_name in ALL_SCORERS:
            values = [
                row.get("scorer_summary", {}).get(scorer_name, {}).get("score", 0.0) for row in rows
            ]
            if values:
                scorer_means[scorer_name] = round(sum(values) / len(values), 4)

        aggregates = [row.get("aggregate_run_quality", 0.0) for row in rows]
        rollup[policy] = {
            "trace_count": len(rows),
            "run_ids": [row.get("run_id") for row in rows],
            "mean_aggregate_run_quality": round(sum(aggregates) / len(aggregates), 4) if aggregates else None,
            "scorer_means": scorer_means,
            "tests_passed_pass_rate": round(
                sum(
                    1
                    for row in rows
                    if row.get("scorer_summary", {}).get("tests_passed", {}).get("passed")
                )
                / len(rows),
                4,
            ),
            "metric_source": SOURCE_TRACE,
        }
    return rollup


def _runner_rollup(project_root: Path, runner_paths: list[Path]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in runner_paths:
        eval_result = run_eval(path)
        key = f"{eval_result.get('task_id')}::{eval_result.get('policy')}"
        grouped[key].append(
            {
                "run_id": eval_result.get("run_id"),
                "trace_path": str(path.relative_to(project_root)),
                "aggregate_run_quality": eval_result.get("aggregate_run_quality"),
                "verdict": eval_result.get("verdict"),
                "scorer_summary": {
                    score["name"]: {"passed": score["passed"], "score": score["score"]}
                    for score in eval_result.get("scores", [])
                },
            }
        )

    return {
        key: {
            **rows[0],
            "metric_source": SOURCE_RUNNER,
            "duplicate_count": len(rows),
        }
        for key, rows in sorted(grouped.items())
    }


def _build_warnings(
    *,
    hosted_policies: set[str],
    trace_policies: set[str],
    policy_comparisons: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []

    hosted_only = sorted(hosted_policies - trace_policies)
    if hosted_only:
        warnings.append(
            {
                "code": "hosted_policy_without_trace_fixtures",
                "severity": "info",
                "message": (
                    "Hosted policy comparison rows have no matching curated trace fixtures "
                    "under data/traces/."
                ),
                "policies": hosted_only,
            }
        )

    trace_only = sorted(trace_policies - hosted_policies)
    if trace_only:
        warnings.append(
            {
                "code": "trace_policy_absent_from_hosted_table",
                "severity": "info",
                "message": (
                    "Curated trace policies are scored by pnpm eval:ci but absent from the "
                    "hosted synthetic policy_comparison table."
                ),
                "policies": trace_only,
            }
        )

    unmapped_scorers = sorted(set(ALL_SCORERS) - set(HOSTED_TO_SCORER.values()))
    warnings.append(
        {
            "code": "scorer_metrics_absent_from_hosted_table",
            "severity": "info",
            "message": (
                "Deterministic scorers present on trace fixtures but not represented as hosted "
                "policy comparison columns."
            ),
            "scorers": unmapped_scorers,
        }
    )

    warnings.append(
        {
            "code": "metric_basis_mismatch",
            "severity": "warning",
            "message": (
                "Hosted policy_comparison.json uses synthetic portfolio percentages (32 fictional "
                "tasks). pnpm eval:suite / pnpm eval:ci use real deterministic scorers on 13 curated "
                "trace fixtures. Values are not directly comparable."
            ),
            "hosted_metric_source": SOURCE_SYNTHETIC,
            "trace_metric_source": SOURCE_TRACE,
        }
    )

    for comparison in policy_comparisons:
        if comparison.get("overlap") and comparison.get("hosted_success_pct") is not None:
            trace_pass_pct = comparison.get("trace_tests_passed_pct")
            if trace_pass_pct is not None and comparison["hosted_success_pct"] != trace_pass_pct:
                warnings.append(
                    {
                        "code": "same_policy_divergent_headline_metric",
                        "severity": "warning",
                        "message": (
                            f"Policy {comparison['policy']!r} shows different headline success "
                            "signals between hosted synthetic fixture and curated trace suite."
                        ),
                        "policy": comparison["policy"],
                        "hosted_success_pct": comparison["hosted_success_pct"],
                        "trace_tests_passed_pct": trace_pass_pct,
                    }
                )

    warnings.append(
        {
            "code": "cockpit_static_eval_separate_surface",
            "severity": "info",
            "message": (
                "Hosted cockpit per-task metrics come from apps/web/lib/cockpitFixtures.ts "
                "staticEval maps. Eval table rows come from data/evals/policy_comparison.json. "
                "Scorer ground truth for gates is packages/evals/run_eval.py on data/traces/."
            ),
        }
    )

    return warnings


def build_audit(project_root: Path, *, include_runner: bool = True) -> dict[str, Any]:
    hosted_rows = load_hosted_policy_rows(project_root)
    suite_summary = load_static_suite_summary(project_root)
    trace_rollup = _policy_trace_rollup(suite_summary.get("traces", []))

    runner_paths = discover_runner_traces(project_root) if include_runner else []
    runner_status = "loaded" if runner_paths else "skipped"
    runner_rollup = _runner_rollup(project_root, runner_paths) if runner_paths else {}

    hosted_policies = {row["policy"] for row in hosted_rows}
    trace_policies = set(trace_rollup)

    policy_comparisons: list[dict[str, Any]] = []
    for row in hosted_rows:
        policy = row["policy"]
        trace_stats = trace_rollup.get(policy)
        entry: dict[str, Any] = {
            "policy": policy,
            "hosted": {
                "metric_source": SOURCE_SYNTHETIC,
                "success_pct": row.get("success"),
                "recovery_pct": row.get("recovery"),
                "loop_pct": row.get("loop"),
                "hallucinated_files_pct": row.get("hallucinatedFiles"),
                "unsafe_attempts_pct": row.get("unsafeAttempts"),
            },
            "overlap": policy in trace_policies,
        }
        if trace_stats:
            entry["trace_suite"] = trace_stats
            entry["hosted_success_pct"] = row.get("success")
            entry["trace_tests_passed_pct"] = round(trace_stats["tests_passed_pass_rate"] * 100, 1)
        policy_comparisons.append(entry)

    for policy, stats in trace_rollup.items():
        if policy in hosted_policies:
            continue
        policy_comparisons.append(
            {
                "policy": policy,
                "hosted": None,
                "trace_suite": stats,
                "overlap": False,
            }
        )

    warnings = _build_warnings(
        hosted_policies=hosted_policies,
        trace_policies=trace_policies,
        policy_comparisons=policy_comparisons,
    )

    return {
        "audit_version": AUDIT_VERSION,
        "generated_at": _now_iso(),
        "sources": {
            "hosted_policy_comparison": {
                "path": "data/evals/policy_comparison.json",
                "classification": SOURCE_SYNTHETIC,
                "policy_count": len(hosted_rows),
                "description": "Hosted eval table synthetic portfolio (32 fictional tasks).",
            },
            "static_trace_suite": {
                "path": "data/traces/",
                "classification": SOURCE_TRACE,
                "trace_count": suite_summary.get("trace_count"),
                "gates_ok": suite_summary.get("gates_ok"),
                "description": "Deterministic scorer output from pnpm eval:suite / pnpm eval:ci.",
            },
            "runner_batch": {
                "path": "runs/",
                "classification": SOURCE_RUNNER,
                "status": runner_status,
                "run_count": len(runner_paths),
                "description": "Optional local runner-generated traces (pnpm runner:batch).",
            },
        },
        "policy_coverage": {
            "hosted_only": sorted(hosted_policies - trace_policies),
            "trace_only": sorted(trace_policies - hosted_policies),
            "overlapping": sorted(hosted_policies & trace_policies),
        },
        "metric_inventory": {
            "hosted_columns": list(hosted_rows[0].keys()) if hosted_rows else [],
            "hosted_to_scorer_map": HOSTED_TO_SCORER,
            "hosted_only_metrics": list(HOSTED_ONLY_METRICS),
            "trace_scorers": list(ALL_SCORERS),
            "scorers_not_in_hosted_table": sorted(set(ALL_SCORERS) - set(HOSTED_TO_SCORER.values())),
        },
        "policy_comparisons": policy_comparisons,
        "runner_summary": runner_rollup,
        "warnings": warnings,
        "warning_count": len(warnings),
    }


def format_table(report: dict[str, Any]) -> str:
    lines = [
        "Metric drift audit",
        "=" * 72,
        f"Generated: {report['generated_at']}",
        "",
        "Sources",
        "-" * 72,
    ]
    for name, meta in report["sources"].items():
        lines.append(
            f"  {name}: {meta['classification']} ({meta.get('path', '')}) "
            f"status={meta.get('status', 'n/a')}"
        )

    lines.extend(["", "Policy coverage", "-" * 72])
    coverage = report["policy_coverage"]
    lines.append(f"  overlapping: {', '.join(coverage['overlapping']) or '(none)'}")
    lines.append(f"  hosted only: {', '.join(coverage['hosted_only']) or '(none)'}")
    lines.append(f"  trace only:  {', '.join(coverage['trace_only']) or '(none)'}")

    lines.extend(["", "Warnings", "-" * 72])
    for warning in report["warnings"]:
        lines.append(f"  [{warning['severity']}] {warning['code']}: {warning['message']}")

    lines.extend(["", "Overlapping policy headline metrics", "-" * 72])
    lines.append(f"{'policy':<22} {'hosted success':>14} {'trace pass%':>12}")
    for row in report["policy_comparisons"]:
        if not row.get("overlap"):
            continue
        hosted = row["hosted"]["success_pct"]
        trace_pct = row.get("trace_tests_passed_pct", "n/a")
        lines.append(f"{row['policy']:<22} {hosted:>13}% {str(trace_pct):>12}")

    return "\n".join(lines)


def format_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Metric drift audit",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Metric sources",
        "",
        "| Surface | Classification | Path |",
        "| --- | --- | --- |",
    ]
    for name, meta in report["sources"].items():
        lines.append(
            f"| {name} | `{meta['classification']}` | `{meta.get('path', '')}` |"
        )

    lines.extend(["", "## Warnings", ""])
    for warning in report["warnings"]:
        lines.append(f"- **{warning['code']}** ({warning['severity']}): {warning['message']}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit metric drift between hosted synthetic policy rows and deterministic trace scores."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root (default: auto-detected)",
    )
    parser.add_argument(
        "--format",
        choices=("json", "table", "markdown"),
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--skip-runner",
        action="store_true",
        help="Do not scan runs/ for runner-generated traces",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    args = parser.parse_args()

    report = build_audit(args.project_root.resolve(), include_runner=not args.skip_runner)

    if args.format == "json":
        indent = 2 if args.pretty else None
        print(json.dumps(report, indent=indent, separators=None if args.pretty else (",", ":")))
    elif args.format == "table":
        print(format_table(report))
    else:
        print(format_markdown(report))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
