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

ADAPTER_NAME = "weave"
FORMAT_VERSION = "1"
DEFAULT_PROJECT = "agent-harness-environment"

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


def _weave_packages_installed() -> dict[str, bool]:
    weave = importlib.util.find_spec("weave") is not None
    wandb = importlib.util.find_spec("wandb") is not None
    return {"weave": weave, "wandb": wandb, "any": weave or wandb}


def get_weave_config() -> dict[str, Any]:
    api_key = os.environ.get("WANDB_API_KEY", "").strip()
    packages = _weave_packages_installed()
    return {
        "adapter": ADAPTER_NAME,
        "packages": packages,
        "package_installed": packages["any"],
        "api_key_present": bool(api_key),
        "configured": bool(packages["any"] and api_key),
        "project": os.environ.get("WANDB_PROJECT", DEFAULT_PROJECT),
        "entity": os.environ.get("WANDB_ENTITY", ""),
    }


def agent_trace_event_to_weave_span(event: dict[str, Any]) -> dict[str, Any]:
    """Map an AHE AgentTraceEvent to a Weave-oriented span/call record."""
    run_id = event.get("run_id", "unknown")
    step_id = event.get("step_id", 0)
    actor = event.get("actor", "unknown")
    action_type = event.get("action_type", "UNKNOWN")

    attributes: dict[str, Any] = {
        "actor": actor,
        "action_type": action_type,
        "harness_policy": event.get("harness_policy"),
        "input_summary": event.get("input_summary"),
        "output_summary": event.get("output_summary"),
        "task_id": event.get("task_id"),
        "run_id": run_id,
        "step_id": step_id,
    }
    if event.get("failure_label"):
        attributes["failure_label"] = event["failure_label"]
    if event.get("command"):
        attributes["command"] = event["command"]
    if event.get("files_touched"):
        attributes["files_touched"] = event["files_touched"]
    if event.get("exit_code") is not None:
        attributes["exit_code"] = event["exit_code"]
    if event.get("model"):
        attributes["model"] = event["model"]
    if event.get("latency_ms") is not None:
        attributes["latency_ms"] = event["latency_ms"]

    return {
        "kind": "weave_span",
        "id": f"{run_id}:{step_id}",
        "name": f"{actor}.{action_type}",
        "call_type": action_type.lower(),
        "start_time": event.get("timestamp"),
        "attributes": attributes,
    }


def trace_to_weave_trace(
    trace: dict[str, Any],
    eval_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Map a trace fixture to a Weave trace/call metadata tree."""
    weave_trace: dict[str, Any] = {
        "kind": "weave_trace",
        "id": trace.get("run_id"),
        "op_name": f"ahe.run/{trace.get('policy', 'unknown')}",
        "attributes": {
            "task_id": trace.get("task_id"),
            "task_title": trace.get("task_title"),
            "repo_snapshot": trace.get("repo_snapshot"),
            "policy": trace.get("policy"),
            "verdict": trace.get("verdict"),
            "success_command": trace.get("success_command"),
            "failure_labels": _failure_labels(trace),
            "known_files": trace.get("known_files", []),
            "source": "ahe_trace_fixture",
        },
        "spans": [agent_trace_event_to_weave_span(event) for event in trace.get("events", [])],
    }
    if eval_result is not None:
        weave_trace["feedback"] = scorer_output_to_weave_feedback(eval_result)
        weave_trace["attributes"]["aggregate_run_quality"] = eval_result.get(
            "aggregate_run_quality"
        )
        weave_trace["attributes"]["trace_path"] = eval_result.get("trace_path")
    return weave_trace


def scorer_output_to_weave_feedback(eval_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Map `run_eval` output to Weave feedback / evaluation score records."""
    return [
        {
            "kind": "weave_feedback",
            "feedback_type": "score",
            "name": score["name"],
            "value": score["score"],
            "attributes": {
                "passed": score["passed"],
                "reason": score.get("reason", ""),
            },
        }
        for score in eval_result.get("scores", [])
    ]


def reliability_cell_to_weave_evaluation(
    task_id: str, cell: dict[str, Any], source_file: str
) -> dict[str, Any]:
    """Map one cell from a reliability_*_001.json file to a Weave evaluation record."""
    eval_id = f"{task_id}::{cell['model']}::{cell['policy']}"
    return {
        "kind": "weave_evaluation",
        "id": eval_id,
        "attributes": {
            "task_id": task_id,
            "model": cell["model"],
            "policy": cell["policy"],
            "n_effective": cell["n_effective"],
            "meanFraction": cell["meanFraction"],
            "completeRate": cell["completeRate"],
            "visibleRate": cell["visibleRate"],
            "source": source_file,
        },
        "feedback": [
            {
                "kind": "weave_feedback",
                "feedback_type": "score",
                "name": "meanFraction",
                "value": cell["meanFraction"],
                "attributes": {"passed": cell["completeRate"] > 0.0},
            }
        ],
    }


def suite_output_to_weave_eval_batch(suite_summary: dict[str, Any]) -> dict[str, Any]:
    """Map `run_suite` JSON summary to a Weave-oriented evaluation batch."""
    evaluations = []
    for row in suite_summary.get("traces", []):
        evaluations.append(
            {
                "kind": "weave_evaluation",
                "id": row.get("run_id") or row.get("trace_stem"),
                "attributes": {
                    "task_id": row.get("task_id"),
                    "policy": row.get("policy"),
                    "verdict": row.get("verdict"),
                    "trace_stem": row.get("trace_stem"),
                    "failure_labels": row.get("failure_labels", []),
                    "aggregate_run_quality": row.get("aggregate_run_quality"),
                    "gate_ok": row.get("gate_ok"),
                },
                "feedback": [
                    {
                        "kind": "weave_feedback",
                        "feedback_type": "score",
                        "name": name,
                        "value": meta["score"],
                        "attributes": {"passed": meta["passed"]},
                    }
                    for name, meta in (row.get("scorer_summary") or {}).items()
                ],
            }
        )

    return {
        "kind": "ahe_weave_eval_batch",
        "format_version": FORMAT_VERSION,
        "suite_version": suite_summary.get("suite_version"),
        "trace_count": suite_summary.get("trace_count"),
        "validation_ok": suite_summary.get("validation_ok"),
        "gates_ok": suite_summary.get("gates_ok"),
        "evaluations": evaluations,
    }


def _build_seeded_export_batch(project_root: Path) -> dict[str, Any]:
    """Assemble a Weave export batch from seeded (curated) AHE fixtures."""
    traces_dir = project_root / "data" / "traces"
    weave_traces: list[dict[str, Any]] = []

    for path in discover_traces(traces_dir):
        trace = json.loads(path.read_text(encoding="utf-8"))
        eval_result = run_eval(path)
        weave_traces.append(trace_to_weave_trace(trace, eval_result))

    suite_summary = run_suite(traces_dir)
    config = get_weave_config()

    return {
        "adapter": ADAPTER_NAME,
        "format_version": FORMAT_VERSION,
        "project": config["project"],
        "entity": config["entity"],
        "source": "seeded",
        "traces": weave_traces,
        "eval_batch": suite_output_to_weave_eval_batch(suite_summary),
    }


def _build_real_export_batch(project_root: Path) -> dict[str, Any]:
    """Assemble a Weave export batch from real-model run data (cockpit traces + reliability aggregates)."""
    cockpit_dir = project_root / "data" / "cockpit_traces"
    evals_dir = project_root / "data" / "evals"
    config = get_weave_config()

    weave_traces: list[dict[str, Any]] = []
    for path in sorted(cockpit_dir.glob("*.json")):
        trace = json.loads(path.read_text(encoding="utf-8"))
        eval_result = run_eval(path)
        wt = trace_to_weave_trace(trace, eval_result)
        wt["attributes"]["model"] = trace.get("model")
        wt["attributes"]["source"] = "data/cockpit_traces"
        weave_traces.append(wt)

    evaluations: list[dict[str, Any]] = []
    for fname in REAL_CARD_FILES:
        rf_path = evals_dir / fname
        if not rf_path.exists():
            continue
        data = json.loads(rf_path.read_text(encoding="utf-8"))
        task_id = data["task"]
        for cell in data["cells"]:
            evaluations.append(
                reliability_cell_to_weave_evaluation(task_id, cell, rf_path.name)
            )

    return {
        "adapter": ADAPTER_NAME,
        "format_version": FORMAT_VERSION,
        "project": config["project"],
        "entity": config["entity"],
        "source": "real",
        "traces": weave_traces,
        "eval_batch": {
            "kind": "ahe_weave_eval_batch",
            "format_version": FORMAT_VERSION,
            "suite_version": None,
            "trace_count": None,
            "validation_ok": None,
            "gates_ok": None,
            "evaluations": evaluations,
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
    """Assemble a full local Weave export batch from AHE fixtures (no network).

    source="real" (default): uses data/cockpit_traces + data/evals/reliability_*_001.json.
    source="seeded": uses data/traces (curated static fixtures).
    """
    if source == "seeded":
        return _build_seeded_export_batch(project_root)
    return _build_real_export_batch(project_root)


def _not_configured_result(config: dict[str, Any]) -> dict[str, Any]:
    missing: list[str] = []
    if not config["packages"]["weave"]:
        missing.append("weave package")
    if not config["api_key_present"]:
        missing.append("WANDB_API_KEY")
    return {
        "ok": False,
        "mode": "not_configured",
        "code": "not_configured",
        "message": f"Weave export not configured; missing: {', '.join(missing)}.",
        "config": config,
    }


def _dry_run_summary(batch: dict[str, Any]) -> dict[str, Any]:
    """Summary fields for dry-run JSON (stable contract)."""
    span_count = sum(len(trace.get("spans", [])) for trace in batch.get("traces", []))
    feedback_count = sum(len(trace.get("feedback", [])) for trace in batch.get("traces", []))
    return {
        "trace_count": len(batch.get("traces", [])),
        "span_count": span_count,
        "feedback_count": feedback_count,
        "suite_trace_count": batch.get("eval_batch", {}).get("trace_count"),
        "suite_evaluation_count": len(batch.get("eval_batch", {}).get("evaluations", [])),
    }


def _weave_project_name(config: dict[str, Any], batch: dict[str, Any]) -> str:
    entity = (batch.get("entity") or config.get("entity") or "").strip()
    project = batch.get("project") or config["project"]
    if entity:
        return f"{entity}/{project}"
    return project


def _import_weave_module() -> Any:
    import weave  # noqa: PLC0415

    return weave


def _attach_weave_feedback(call: Any, feedback: dict[str, Any]) -> None:
    """Best-effort score feedback on a Weave call (skipped when API unavailable)."""
    feedback_api = getattr(call, "feedback", None)
    if feedback_api is None or not hasattr(feedback_api, "add"):
        return
    name = feedback.get("name", "score")
    payload: dict[str, Any] = {"value": feedback.get("value")}
    attributes = feedback.get("attributes")
    if isinstance(attributes, dict):
        payload.update(attributes)
    feedback_api.add(name, payload)


def perform_live_export(
    batch: dict[str, Any],
    *,
    weave_module: Any | None = None,
) -> dict[str, Any]:
    """
    Upload the static export batch to W&B Weave (network; requires weave + WANDB_API_KEY).

    `weave_module` is injectable for unit tests (fake client; no network).
    """
    config = get_weave_config()
    if not config["packages"]["weave"] or not config["api_key_present"]:
        return _not_configured_result(config)

    weave = weave_module if weave_module is not None else _import_weave_module()
    project_name = _weave_project_name(config, batch)

    uploaded_traces: list[dict[str, Any]] = []
    uploaded_evaluations: list[dict[str, Any]] = []
    try:
        client = weave.init(project_name)

        for trace in batch.get("traces", []):
            attributes = dict(trace.get("attributes") or {})
            root = client.create_call(
                op=trace.get("op_name", "ahe.run"),
                inputs={
                    "trace_id": trace.get("id"),
                    "task_id": attributes.get("task_id"),
                    "policy": attributes.get("policy"),
                    "verdict": attributes.get("verdict"),
                },
                attributes={"source": "ahe_static_export", "ahe_trace_id": trace.get("id")},
            )
            span_count = 0
            for span in trace.get("spans", []):
                client.create_call(
                    op=span.get("name", "ahe.span"),
                    inputs=dict(span.get("attributes") or {}),
                    parent=root,
                    attributes={"ahe_span_id": span.get("id")},
                )
                span_count += 1
            client.finish_call(
                root,
                output={
                    "trace_id": trace.get("id"),
                    "verdict": attributes.get("verdict"),
                    "failure_labels": attributes.get("failure_labels", []),
                    "aggregate_run_quality": attributes.get("aggregate_run_quality"),
                },
            )
            for feedback in trace.get("feedback", []):
                _attach_weave_feedback(root, feedback)
            uploaded_traces.append(
                {
                    "id": trace.get("id"),
                    "span_count": span_count,
                    "feedback_count": len(trace.get("feedback", [])),
                }
            )

        for evaluation in batch.get("eval_batch", {}).get("evaluations", []):
            attrs = dict(evaluation.get("attributes") or {})
            call = client.create_call(
                op="ahe.suite_evaluation",
                inputs=attrs,
                attributes={"source": "ahe_static_suite", "ahe_eval_id": evaluation.get("id")},
            )
            client.finish_call(
                call,
                output={
                    "evaluation_id": evaluation.get("id"),
                    "verdict": attrs.get("verdict"),
                    "gate_ok": attrs.get("gate_ok"),
                },
            )
            for feedback in evaluation.get("feedback", []):
                _attach_weave_feedback(call, feedback)
            uploaded_evaluations.append(
                {
                    "id": evaluation.get("id"),
                    "feedback_count": len(evaluation.get("feedback", [])),
                }
            )

        if hasattr(client, "flush"):
            client.flush()
    except Exception as exc:  # noqa: BLE001 — surface SDK/network failures to CLI
        return {
            "ok": False,
            "mode": "live",
            "code": "live_export_failed",
            "message": f"Weave live export failed: {exc}",
            "config": config,
        }

    eval_batch = batch.get("eval_batch") or {}
    return {
        "ok": True,
        "mode": "live",
        "code": "live_export_ok",
        "message": "Static AHE fixtures uploaded to W&B Weave.",
        "config": config,
        "summary": {
            "project": project_name,
            "url": f"https://wandb.ai/{project_name}/weave",
            "traces": uploaded_traces,
            "evaluations": uploaded_evaluations,
            "suite_trace_count": eval_batch.get("trace_count"),
        },
    }


def export_to_weave(
    batch: dict[str, Any],
    *,
    dry_run: bool = True,
) -> dict[str, Any]:
    """
    Export batch to W&B Weave when configured, or return a structured status.

    Default is dry-run only (no network, no SDK import).
    Live upload requires dry_run=False plus weave package and WANDB_API_KEY.
    """
    config = get_weave_config()
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

    if not config["packages"]["weave"] or not config["api_key_present"]:
        return _not_configured_result(config)

    return perform_live_export(batch)


def run_dry_run(project_root: Path, source: str = "real") -> dict[str, Any]:
    batch = build_export_batch(project_root, source=source)
    return export_to_weave(batch, dry_run=True)


def run_live_export(project_root: Path, source: str = "real") -> dict[str, Any]:
    batch = build_export_batch(project_root, source=source)
    return export_to_weave(batch, dry_run=False)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export AHE fixtures to W&B Weave (dry-run by default; no network)."
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
        help="Upload fixtures to Weave (requires --live, weave package, WANDB_API_KEY).",
    )
    parser.add_argument(
        "--source",
        choices=["seeded", "real"],
        default="real",
        help=(
            "Data source: 'real' (default) uses data/cockpit_traces + reliability aggregates; "
            "'seeded' uses curated data/traces."
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
