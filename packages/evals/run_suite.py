#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from fixture_validation import validate_trace  # noqa: E402
from run_eval import run_eval  # noqa: E402
from suite_gates import (  # noqa: E402
    GateFailure,
    SuiteThresholds,
    check_suite_gates,
    check_trace_gate,
)


def discover_traces(traces_dir: Path) -> list[Path]:
    return sorted(traces_dir.glob("*.json"))


def _failure_labels(trace: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for event in trace.get("events", []):
        label = event.get("failure_label")
        if label and label not in labels:
            labels.append(label)
    return labels


def _scorer_summary(scores: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        score["name"]: {"passed": score["passed"], "score": score["score"]}
        for score in scores
    }


def _group_traces(trace_rows: list[dict[str, Any]], key: str) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in trace_rows:
        value = row.get(key) or "unknown"
        grouped[str(value)].append(row["run_id"] or row["trace_stem"])
    return dict(sorted(grouped.items()))


def _group_failure_labels(trace_rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in trace_rows:
        labels = row.get("failure_labels") or []
        if not labels:
            grouped["_none"].append(row["run_id"] or row["trace_stem"])
            continue
        for label in labels:
            grouped[label].append(row["run_id"] or row["trace_stem"])
    return dict(sorted(grouped.items()))


def run_suite(
    traces_dir: Path,
    *,
    thresholds: SuiteThresholds | None = None,
) -> dict[str, Any]:
    thresholds = thresholds or SuiteThresholds()
    validation_errors: list[str] = []
    trace_results: list[dict[str, Any]] = []
    trace_rows: list[dict[str, Any]] = []

    for path in discover_traces(traces_dir):
        validation_errors.extend(validate_trace(path))
        trace = json.loads(path.read_text(encoding="utf-8"))
        eval_result = run_eval(path)
        stem = path.stem
        labels = _failure_labels(trace)
        gate = check_trace_gate(stem, trace, eval_result, thresholds=thresholds)

        item = {
            "trace_stem": stem,
            "trace_path": str(path),
            "trace": trace,
            "eval": eval_result,
            "gate": gate,
        }
        trace_results.append(item)

        trace_rows.append(
            {
                "trace_stem": stem,
                "trace_path": str(path),
                "run_id": eval_result.get("run_id"),
                "task_id": eval_result.get("task_id"),
                "policy": eval_result.get("policy"),
                "verdict": eval_result.get("verdict"),
                "failure_labels": labels,
                "aggregate_run_quality": eval_result.get("aggregate_run_quality"),
                "scorer_summary": _scorer_summary(eval_result.get("scores", [])),
                "gate_ok": gate.ok,
                "gate_failures": [failure.to_dict() for failure in gate.failures],
            }
        )

    gate_result = check_suite_gates(trace_results, thresholds=thresholds)
    all_gate_failures = list(gate_result.failures)
    for error in validation_errors:
        all_gate_failures.append(GateFailure("fixtures", "validation", error))
    gates_ok = gate_result.ok and not validation_errors

    return {
        "suite_version": "1",
        "traces_dir": str(traces_dir),
        "trace_count": len(trace_rows),
        "validation_ok": not validation_errors,
        "validation_errors": validation_errors,
        "gates_ok": gates_ok,
        "gate_failures": [failure.to_dict() for failure in all_gate_failures],
        "thresholds": {
            "min_accepted_aggregate": thresholds.min_accepted_aggregate,
            "min_assisted_aggregate": thresholds.min_assisted_aggregate,
        },
        "by_task_id": _group_traces(trace_rows, "task_id"),
        "by_policy": _group_traces(trace_rows, "policy"),
        "by_verdict": _group_traces(trace_rows, "verdict"),
        "by_failure_label": _group_failure_labels(trace_rows),
        "traces": trace_rows,
    }


def format_table(summary: dict[str, Any]) -> str:
    lines = [
        "Eval suite",
        "-" * 88,
        f"{'trace':<42} {'verdict':<10} {'aggregate':>9}  gate",
    ]
    for row in summary["traces"]:
        gate = "ok" if row["gate_ok"] else "FAIL"
        lines.append(
            f"{row['trace_stem']:<42} {row['verdict']:<10} "
            f"{row['aggregate_run_quality']:>9.3f}  {gate}"
        )
    lines.append("-" * 88)
    lines.append(
        f"validation={'ok' if summary['validation_ok'] else 'FAIL'}  "
        f"gates={'ok' if summary['gates_ok'] else 'FAIL'}  "
        f"traces={summary['trace_count']}"
    )
    if summary["gate_failures"]:
        lines.append("Gate failures:")
        for failure in summary["gate_failures"]:
            lines.append(f"  - [{failure['trace']}] {failure['rule']}: {failure['detail']}")
    return "\n".join(lines)


def format_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Eval suite report",
        "",
        f"- Traces: {summary['trace_count']}",
        f"- Validation: {'pass' if summary['validation_ok'] else 'fail'}",
        f"- Gates: {'pass' if summary['gates_ok'] else 'fail'}",
        "",
        "## Traces",
        "",
        "| Trace | Task | Policy | Verdict | Aggregate | Gate |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for row in summary["traces"]:
        gate = "pass" if row["gate_ok"] else "**fail**"
        lines.append(
            f"| {row['trace_stem']} | {row['task_id']} | {row['policy']} | "
            f"{row['verdict']} | {row['aggregate_run_quality']:.3f} | {gate} |"
        )
    if summary["gate_failures"]:
        lines.extend(["", "## Gate failures", ""])
        for failure in summary["gate_failures"]:
            lines.append(f"- `{failure['trace']}` **{failure['rule']}**: {failure['detail']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run static trace eval suite and optional CI gates.")
    parser.add_argument(
        "--traces-dir",
        type=Path,
        default=Path("data/traces"),
        help="Directory containing trace JSON fixtures (default: data/traces)",
    )
    parser.add_argument(
        "--report",
        choices=("table", "markdown"),
        help="Emit a human-readable report to stderr after the JSON summary",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Exit nonzero when fixture validation or suite gates fail",
    )
    parser.add_argument(
        "--min-accepted-aggregate",
        type=float,
        default=SuiteThresholds.min_accepted_aggregate,
        help="Minimum aggregate_run_quality for accepted traces",
    )
    parser.add_argument(
        "--min-assisted-aggregate",
        type=float,
        default=SuiteThresholds.min_assisted_aggregate,
        help="Minimum aggregate_run_quality for assisted traces",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON summary (default is compact)",
    )
    args = parser.parse_args()

    thresholds = SuiteThresholds(
        min_accepted_aggregate=args.min_accepted_aggregate,
        min_assisted_aggregate=args.min_assisted_aggregate,
    )
    summary = run_suite(args.traces_dir.resolve(), thresholds=thresholds)

    indent = 2 if args.pretty else None
    print(json.dumps(summary, indent=indent, separators=None if args.pretty else (",", ":")))

    if args.report == "table":
        print(format_table(summary), file=sys.stderr)
    elif args.report == "markdown":
        print(format_markdown(summary), file=sys.stderr)

    if args.ci:
        if not summary["validation_ok"] or not summary["gates_ok"]:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
