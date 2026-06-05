#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

EVAL_DIR = Path(__file__).resolve().parents[1]
if str(EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_DIR))

from run_eval import run_eval  # noqa: E402
from run_suite import discover_traces, run_suite  # noqa: E402

ADAPTER_NAME = "braintrust"
FORMAT_VERSION = "1"
DEFAULT_PROJECT = "agent-harness-environment"


def _failure_labels(trace: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for event in trace.get("events", []):
        label = event.get("failure_label")
        if label and label not in labels:
            labels.append(label)
    return labels


def _braintrust_package_installed() -> bool:
    return importlib.util.find_spec("braintrust") is not None


def get_braintrust_config() -> dict[str, Any]:
    api_key = os.environ.get("BRAINTRUST_API_KEY", "").strip()
    package_installed = _braintrust_package_installed()
    return {
        "adapter": ADAPTER_NAME,
        "package_installed": package_installed,
        "api_key_present": bool(api_key),
        "configured": bool(package_installed and api_key),
        "project": os.environ.get("BRAINTRUST_PROJECT", DEFAULT_PROJECT),
    }


def task_to_braintrust_dataset_row(task: dict[str, Any]) -> dict[str, Any]:
    """Map an AHE task fixture (`data/tasks.json` entry) to a Braintrust dataset row."""
    return {
        "id": task["id"],
        "input": {
            "task_id": task["id"],
            "title": task.get("title"),
            "type": task.get("type"),
            "issue": task.get("issue"),
            "repo_snapshot": task.get("repo"),
        },
        "expected": {
            "success_command": task.get("successCommand"),
            "expected_files": task.get("expectedFiles", []),
        },
        "metadata": {
            "tags": task.get("tags", []),
            "failure_modes_to_watch": task.get("failureModes", []),
            "source": "data/tasks.json",
        },
    }


def coding_task_row_to_braintrust_dataset_row(row: dict[str, Any]) -> dict[str, Any]:
    """Map a `coding_tasks.jsonl` record to a Braintrust dataset row."""
    return {
        "id": row["task_id"],
        "input": {
            "task_id": row["task_id"],
            "issue": row.get("issue"),
            "repo_snapshot": row.get("repo_snapshot"),
            "tags": row.get("tags", []),
        },
        "expected": {
            "expected_behavior": row.get("expected_behavior"),
            "success_command": row.get("success_command"),
            "gold_files": row.get("gold_files", []),
        },
        "metadata": {
            "failure_modes_to_watch": row.get("failure_modes_to_watch", []),
            "source": "packages/evals/datasets/coding_tasks.jsonl",
        },
    }


def trace_to_braintrust_example(
    trace: dict[str, Any],
    eval_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Map a trace fixture to a Braintrust experiment/example record (events omitted)."""
    example: dict[str, Any] = {
        "id": trace.get("run_id"),
        "input": {
            "task_id": trace.get("task_id"),
            "task_title": trace.get("task_title"),
            "repo_snapshot": trace.get("repo_snapshot"),
            "policy": trace.get("policy"),
            "success_command": trace.get("success_command"),
            "known_files": trace.get("known_files", []),
        },
        "expected": {
            "verdict": trace.get("verdict"),
        },
        "metadata": {
            "failure_labels": _failure_labels(trace),
            "event_count": len(trace.get("events", [])),
            "source": "ahe_trace_fixture",
        },
    }
    if eval_result is not None:
        example["scores"] = scorer_output_to_braintrust_scores(eval_result)
        example["metadata"]["aggregate_run_quality"] = eval_result.get("aggregate_run_quality")
        example["metadata"]["trace_path"] = eval_result.get("trace_path")
    return example


def scorer_output_to_braintrust_scores(eval_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Map `run_eval` output to Braintrust score metadata records."""
    return [
        {
            "name": score["name"],
            "score": score["score"],
            "metadata": {
                "passed": score["passed"],
                "reason": score.get("reason", ""),
            },
        }
        for score in eval_result.get("scores", [])
    ]


def suite_output_to_export_batch(suite_summary: dict[str, Any]) -> dict[str, Any]:
    """Map `run_suite` JSON summary to a Braintrust-oriented export batch fragment."""
    examples = []
    for row in suite_summary.get("traces", []):
        examples.append(
            {
                "id": row.get("run_id") or row.get("trace_stem"),
                "input": {
                    "task_id": row.get("task_id"),
                    "policy": row.get("policy"),
                    "trace_stem": row.get("trace_stem"),
                },
                "expected": {"verdict": row.get("verdict")},
                "scores": [
                    {
                        "name": name,
                        "score": meta["score"],
                        "metadata": {"passed": meta["passed"]},
                    }
                    for name, meta in (row.get("scorer_summary") or {}).items()
                ],
                "metadata": {
                    "aggregate_run_quality": row.get("aggregate_run_quality"),
                    "failure_labels": row.get("failure_labels", []),
                    "gate_ok": row.get("gate_ok"),
                },
            }
        )

    return {
        "kind": "ahe_suite_export_batch",
        "format_version": FORMAT_VERSION,
        "suite_version": suite_summary.get("suite_version"),
        "trace_count": suite_summary.get("trace_count"),
        "validation_ok": suite_summary.get("validation_ok"),
        "gates_ok": suite_summary.get("gates_ok"),
        "experiments": [
            {
                "name": "ahe_static_suite",
                "examples": examples,
            }
        ],
    }


def _load_tasks(tasks_path: Path) -> list[dict[str, Any]]:
    return json.loads(tasks_path.read_text(encoding="utf-8"))


def _load_coding_tasks_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def build_export_batch(project_root: Path) -> dict[str, Any]:
    """Assemble a full local export batch from static AHE fixtures (no network)."""
    traces_dir = project_root / "data" / "traces"
    tasks = _load_tasks(project_root / "data" / "tasks.json")
    coding_tasks = _load_coding_tasks_jsonl(
        project_root / "packages" / "evals" / "datasets" / "coding_tasks.jsonl"
    )

    trace_examples: list[dict[str, Any]] = []
    for path in discover_traces(traces_dir):
        trace = json.loads(path.read_text(encoding="utf-8"))
        eval_result = run_eval(path)
        trace_examples.append(trace_to_braintrust_example(trace, eval_result))

    suite_summary = run_suite(traces_dir)

    return {
        "adapter": ADAPTER_NAME,
        "format_version": FORMAT_VERSION,
        "project": get_braintrust_config()["project"],
        "datasets": [
            {
                "name": "ahe_tasks",
                "rows": [task_to_braintrust_dataset_row(task) for task in tasks],
            },
            {
                "name": "ahe_coding_tasks",
                "rows": [coding_task_row_to_braintrust_dataset_row(row) for row in coding_tasks],
            },
        ],
        "experiments": [
            {
                "name": "ahe_static_trace_fixtures",
                "examples": trace_examples,
            }
        ],
        "suite_batch": suite_output_to_export_batch(suite_summary),
    }


def export_to_braintrust(
    batch: dict[str, Any],
    *,
    dry_run: bool = True,
) -> dict[str, Any]:
    """
    Export batch to Braintrust when configured, or return a structured status.

    Default is dry-run only (no network, no SDK calls).
    """
    config = get_braintrust_config()
    if dry_run:
        return {
            "ok": True,
            "mode": "dry_run",
            "code": "dry_run",
            "message": "Dry run only; no network calls made.",
            "config": config,
            "batch": batch,
            "summary": {
                "dataset_count": len(batch.get("datasets", [])),
                "dataset_row_count": sum(
                    len(dataset.get("rows", [])) for dataset in batch.get("datasets", [])
                ),
                "experiment_count": len(batch.get("experiments", [])),
                "example_count": sum(
                    len(experiment.get("examples", []))
                    for experiment in batch.get("experiments", [])
                ),
                "suite_trace_count": batch.get("suite_batch", {}).get("trace_count"),
            },
        }

    if not config["configured"]:
        missing: list[str] = []
        if not config["package_installed"]:
            missing.append("braintrust package")
        if not config["api_key_present"]:
            missing.append("BRAINTRUST_API_KEY")
        return {
            "ok": False,
            "mode": "not_configured",
            "code": "not_configured",
            "message": f"Braintrust export not configured; missing: {', '.join(missing)}.",
            "config": config,
        }

    return {
        "ok": False,
        "mode": "not_implemented",
        "code": "live_export_not_implemented",
        "message": "Live Braintrust upload is not implemented yet; use --dry-run.",
        "config": config,
    }


def run_dry_run(project_root: Path) -> dict[str, Any]:
    batch = build_export_batch(project_root)
    return export_to_braintrust(batch, dry_run=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export AHE fixtures to Braintrust (dry-run by default; no network)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print compact JSON of the export batch without uploading (default).",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Repository root (default: auto-detected)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    args = parser.parse_args()

    if args.dry_run:
        result = run_dry_run(args.project_root.resolve())
    else:
        batch = build_export_batch(args.project_root.resolve())
        result = export_to_braintrust(batch, dry_run=False)

    indent = 2 if args.pretty else None
    print(
        json.dumps(
            result,
            indent=indent,
            separators=None if args.pretty else (",", ":"),
        )
    )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
