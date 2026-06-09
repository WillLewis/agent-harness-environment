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

# This adapter powers a PUBLIC hosted demo: experiments are uploaded with
# is_public=True so anonymous visitors can open the dashboard link without
# signing in. Braintrust experiments default to private otherwise.
EXPERIMENTS_PUBLIC = True

REAL_CARD_FILES = (
    "reliability_completeness_comments_001.json",
    "reliability_compat_alias_migration_001.json",
    "reliability_latent_defects_001.json",
)


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


def reliability_cell_to_braintrust_dataset_row(
    task_id: str, cell: dict[str, Any], source_file: str
) -> dict[str, Any]:
    """Map one cell from a reliability_*_001.json file to a Braintrust dataset row."""
    row_id = f"{task_id}::{cell['model']}::{cell['policy']}"
    return {
        "id": row_id,
        "input": {
            "task_id": task_id,
            "model": cell["model"],
            "policy": cell["policy"],
            "n_effective": cell["n_effective"],
        },
        "expected": {
            "meanFraction": cell["meanFraction"],
            "completeRate": cell["completeRate"],
        },
        "metadata": {
            "visibleRate": cell["visibleRate"],
            "stdevFraction": cell["stdevFraction"],
            "source": source_file,
            "card": task_id,
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


def _build_seeded_export_batch(project_root: Path) -> dict[str, Any]:
    """Assemble an export batch from seeded (curated) AHE fixtures."""
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
        "source": "seeded",
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


def _build_real_export_batch(project_root: Path) -> dict[str, Any]:
    """Assemble an export batch from real-model run data (cockpit traces + reliability aggregates)."""
    cockpit_dir = project_root / "data" / "cockpit_traces"
    evals_dir = project_root / "data" / "evals"

    trace_examples: list[dict[str, Any]] = []
    for path in sorted(cockpit_dir.glob("*.json")):
        trace = json.loads(path.read_text(encoding="utf-8"))
        eval_result = run_eval(path)
        example = trace_to_braintrust_example(trace, eval_result)
        example["metadata"]["model"] = trace.get("model")
        example["metadata"]["source"] = "data/cockpit_traces"
        trace_examples.append(example)

    reliability_rows: list[dict[str, Any]] = []
    for fname in REAL_CARD_FILES:
        rf_path = evals_dir / fname
        if not rf_path.exists():
            continue
        data = json.loads(rf_path.read_text(encoding="utf-8"))
        task_id = data["task"]
        for cell in data["cells"]:
            reliability_rows.append(
                reliability_cell_to_braintrust_dataset_row(task_id, cell, rf_path.name)
            )

    return {
        "adapter": ADAPTER_NAME,
        "format_version": FORMAT_VERSION,
        "project": get_braintrust_config()["project"],
        "source": "real",
        "datasets": [
            {
                "name": "ahe_real_reliability",
                "rows": reliability_rows,
            }
        ],
        "experiments": [
            {
                "name": "ahe_real_cockpit_traces",
                "examples": trace_examples,
            }
        ],
        "suite_batch": {
            "kind": "ahe_suite_export_batch",
            "format_version": FORMAT_VERSION,
            "suite_version": None,
            "trace_count": None,
            "validation_ok": None,
            "gates_ok": None,
            "experiments": [],
        },
    }



def _load_dot_env(project_root: Path) -> None:
    """Load .env into os.environ, filling only absent-or-empty keys (no dotenv dep)."""
    env_path = project_root / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and not os.environ.get(key):
            os.environ[key] = value

def build_export_batch(project_root: Path, source: str = "real") -> dict[str, Any]:
    """Assemble a full local export batch from AHE fixtures (no network).

    source="real" (default): uses data/cockpit_traces + data/evals/reliability_*_001.json.
    source="seeded": uses data/traces + data/tasks.json (curated static fixtures).
    """
    if source == "seeded":
        return _build_seeded_export_batch(project_root)
    return _build_real_export_batch(project_root)


def _not_configured_result(config: dict[str, Any]) -> dict[str, Any]:
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


def _dry_run_summary(batch: dict[str, Any]) -> dict[str, Any]:
    """Summary fields for dry-run JSON (stable contract; excludes suite_batch experiments)."""
    return {
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
    }


def _import_braintrust_module() -> Any:
    import braintrust  # noqa: PLC0415

    return braintrust


def _dataset_insert_kwargs(row: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(row.get("metadata") or {})
    if row.get("id") is not None:
        metadata.setdefault("ahe_row_id", row["id"])
    kwargs: dict[str, Any] = {
        "input": row["input"],
        "expected": row.get("expected"),
        "metadata": metadata or None,
    }
    return {key: value for key, value in kwargs.items() if value is not None}


def _example_log_kwargs(example: dict[str, Any]) -> dict[str, Any]:
    scores_list = example.get("scores") or []
    scores = {item["name"]: item["score"] for item in scores_list if "name" in item}
    metadata = dict(example.get("metadata") or {})
    if example.get("id") is not None:
        metadata.setdefault("ahe_example_id", example["id"])
    # Braintrust requires output; use verdict + quality as the agent's actual result
    expected = example.get("expected") or {}
    output: dict[str, Any] = {"verdict": expected.get("verdict")}
    if metadata.get("aggregate_run_quality") is not None:
        output["aggregate_run_quality"] = metadata["aggregate_run_quality"]
    kwargs: dict[str, Any] = {
        "input": example.get("input"),
        "output": output,
        "expected": example.get("expected"),
        "scores": scores or None,
        "metadata": metadata or None,
    }
    return {key: value for key, value in kwargs.items() if value is not None}


def perform_live_export(
    batch: dict[str, Any],
    *,
    braintrust_module: Any | None = None,
) -> dict[str, Any]:
    """
    Upload the static export batch to Braintrust (network; requires SDK + API key).

    `braintrust_module` is injectable for unit tests (fake client; no network).
    """
    config = get_braintrust_config()
    if not config["configured"]:
        return _not_configured_result(config)

    bt = braintrust_module if braintrust_module is not None else _import_braintrust_module()
    project = batch.get("project") or config["project"]

    uploaded_datasets: list[dict[str, Any]] = []
    try:
        for dataset_spec in batch.get("datasets", []):
            dataset = bt.init_dataset(project=project, name=dataset_spec["name"])
            row_count = 0
            for row in dataset_spec.get("rows", []):
                dataset.insert(**_dataset_insert_kwargs(row))
                row_count += 1
            dataset.flush()
            uploaded_datasets.append({"name": dataset_spec["name"], "row_count": row_count})

        experiment_specs = list(batch.get("experiments", []))
        suite_batch = batch.get("suite_batch") or {}
        experiment_specs.extend(suite_batch.get("experiments", []))

        uploaded_experiments: list[dict[str, Any]] = []
        for experiment_spec in experiment_specs:
            experiment = bt.init(
                project=project,
                experiment=experiment_spec["name"],
                is_public=EXPERIMENTS_PUBLIC,
            )
            example_count = 0
            for example in experiment_spec.get("examples", []):
                experiment.log(**_example_log_kwargs(example))
                example_count += 1
            experiment.flush()
            exp_url = None
            summarize_fn = getattr(experiment, "summarize", None)
            if callable(summarize_fn):
                try:
                    summary = summarize_fn()
                    exp_url = getattr(summary, "experiment_url", None)
                except Exception:  # noqa: BLE001
                    pass
            uploaded_experiments.append(
                {
                    "name": experiment_spec["name"],
                    "example_count": example_count,
                    "url": exp_url,
                }
            )
    except Exception as exc:  # noqa: BLE001 — surface SDK/network failures to CLI
        return {
            "ok": False,
            "mode": "live",
            "code": "live_export_failed",
            "message": f"Braintrust live export failed: {exc}",
            "config": config,
        }

    return {
        "ok": True,
        "mode": "live",
        "code": "live_export_ok",
        "message": "Static AHE fixtures uploaded to Braintrust.",
        "config": config,
        "summary": {
            "project": project,
            "datasets": uploaded_datasets,
            "experiments": uploaded_experiments,
            "suite_trace_count": suite_batch.get("trace_count"),
        },
    }


def export_to_braintrust(
    batch: dict[str, Any],
    *,
    dry_run: bool = True,
) -> dict[str, Any]:
    """
    Export batch to Braintrust when configured, or return a structured status.

    Default is dry-run only (no network, no SDK import).
    Live upload requires dry_run=False plus configured SDK and BRAINTRUST_API_KEY.
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
            "summary": _dry_run_summary(batch),
        }

    if not config["configured"]:
        return _not_configured_result(config)

    return perform_live_export(batch)


def run_dry_run(project_root: Path, source: str = "real") -> dict[str, Any]:
    batch = build_export_batch(project_root, source=source)
    return export_to_braintrust(batch, dry_run=True)


def run_live_export(project_root: Path, source: str = "real") -> dict[str, Any]:
    batch = build_export_batch(project_root, source=source)
    return export_to_braintrust(batch, dry_run=False)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export AHE fixtures to Braintrust (dry-run by default; no network)."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Print compact JSON of the export batch without uploading (default).",
    )
    mode.add_argument(
        "--live",
        action="store_true",
        help="Upload fixtures to Braintrust (requires --live, braintrust package, BRAINTRUST_API_KEY).",
    )
    parser.add_argument(
        "--source",
        choices=["seeded", "real"],
        default="real",
        help=(
            "Data source: 'real' (default) uses data/cockpit_traces + reliability aggregates; "
            "'seeded' uses curated data/traces + data/tasks.json."
        ),
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

    root = args.project_root.resolve()
    if args.live:
        _load_dot_env(root)
        result = run_live_export(root, source=args.source)
    else:
        result = run_dry_run(root, source=args.source)

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
