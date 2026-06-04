#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(os.environ.get("AHE_PROJECT_ROOT", Path(__file__).resolve().parents[1]))

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover - user-facing startup hint
    print(
        "The AHE MCP server requires the Python package `mcp`. "
        "Install with `pip install -r requirements-dev.txt`. "
        f"Original import error: {exc}",
        file=sys.stderr,
    )
    raise

mcp = FastMCP("agent-harness-environment")


def read_json(relative_path: str) -> Any:
    return json.loads((PROJECT_ROOT / relative_path).read_text())


@mcp.tool()
def list_eval_runs() -> list[dict[str, Any]]:
    """List static demo runs available in this project."""
    traces = []
    for path in sorted((PROJECT_ROOT / "data" / "traces").glob("*.json")):
        trace = json.loads(path.read_text())
        traces.append({
            "run_id": trace.get("run_id"),
            "task_id": trace.get("task_id"),
            "policy": trace.get("policy"),
            "verdict": trace.get("verdict"),
            "path": str(path.relative_to(PROJECT_ROOT)),
        })
    return traces


@mcp.tool()
def get_trace(run_id: str) -> dict[str, Any]:
    """Fetch a trace by run_id from static fixtures or local runs."""
    for directory in [PROJECT_ROOT / "data" / "traces", PROJECT_ROOT / "runs"]:
        if not directory.exists():
            continue
        for path in directory.glob("*.json"):
            trace = json.loads(path.read_text())
            if trace.get("run_id") == run_id:
                return trace
    return {"error": f"run_id not found: {run_id}"}


@mcp.tool()
def compare_policies(policy_a: str = "baseline", policy_b: str = "guarded_recovery") -> dict[str, Any]:
    """Compare two policy rows from the static eval comparison fixture."""
    rows = read_json("data/evals/policy_comparison.json")
    by_policy = {row["policy"]: row for row in rows}
    return {"policy_a": by_policy.get(policy_a), "policy_b": by_policy.get(policy_b)}


@mcp.tool()
def run_eval(trace_path: str = "data/traces/guarded_recovery_date_parser.json") -> dict[str, Any]:
    """Run local deterministic scorers against a trace fixture."""
    sys.path.insert(0, str(PROJECT_ROOT / "packages" / "evals"))
    from run_eval import run_eval as run_eval_impl  # type: ignore

    return run_eval_impl(PROJECT_ROOT / trace_path)


@mcp.tool()
def create_failure_cluster(label: str) -> dict[str, Any]:
    """Return matching failure cluster fixture by label or id."""
    clusters = read_json("data/failure_clusters.json")
    for cluster in clusters:
        if label.lower() in {cluster["id"].lower(), cluster["label"].lower()}:
            return cluster
    return {"error": f"No cluster found for {label}"}


@mcp.tool()
def promote_trace_to_dataset(run_id: str) -> dict[str, Any]:
    """Write a dataset-candidate row from a trace into generated_candidates.jsonl."""
    trace = get_trace(run_id)
    if "error" in trace:
        return trace
    candidate = {
        "task_id": f"{trace.get('task_id')}_promoted",
        "source_run_id": run_id,
        "failure_mode": trace.get("events", [{}])[-1].get("failure_label", "needs_review"),
        "expected_policy_behavior": "derive from failure cluster review",
        "success_command": trace.get("success_command"),
    }
    output = PROJECT_ROOT / "data" / "datasets" / "generated_candidates.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(candidate) + "\n")
    return {"written_to": str(output.relative_to(PROJECT_ROOT)), "candidate": candidate}


@mcp.tool()
def get_policy_router_decision(task_id: str = "bugfix_date_parser_001") -> dict[str, Any]:
    """Fetch the static RL-lite router decision for a task."""
    decisions = read_json("data/router_decisions.json")
    return decisions.get(task_id, {"error": f"No router decision found for {task_id}"})


if __name__ == "__main__":
    mcp.run()
