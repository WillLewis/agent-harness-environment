#!/usr/bin/env python3
from __future__ import annotations

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

from mcp_helpers import (  # noqa: E402
    compare_policies as compare_policies_impl,
    create_failure_cluster as create_failure_cluster_impl,
    get_policy_router_decision as get_policy_router_decision_impl,
    get_trace as get_trace_impl,
    list_eval_runs as list_eval_runs_impl,
    promote_trace_to_dataset as promote_trace_to_dataset_impl,
    run_eval_trace,
)

mcp = FastMCP("agent-harness-environment")


def _run_eval_impl(trace_path: Path) -> dict[str, Any]:
    sys.path.insert(0, str(PROJECT_ROOT / "packages" / "evals"))
    from run_eval import run_eval as run_eval_impl  # type: ignore

    return run_eval_impl(trace_path)


@mcp.tool()
def list_eval_runs() -> dict[str, Any]:
    """List static demo runs available in this project."""
    return list_eval_runs_impl(PROJECT_ROOT)


@mcp.tool()
def get_trace(run_id: str, verbose: bool = False) -> dict[str, Any]:
    """Fetch a trace by run_id. Returns a compact summary by default; set verbose=True for full JSON."""
    return get_trace_impl(PROJECT_ROOT, run_id, verbose=verbose)


@mcp.tool()
def compare_policies(policy_a: str = "baseline", policy_b: str = "guarded_recovery") -> dict[str, Any]:
    """Compare two policy rows from the static eval comparison fixture."""
    return compare_policies_impl(PROJECT_ROOT, policy_a, policy_b)


@mcp.tool()
def run_eval(trace_path: str = "data/traces/guarded_recovery_date_parser.json") -> dict[str, Any]:
    """Run local deterministic scorers against a trace fixture."""
    return run_eval_trace(PROJECT_ROOT, trace_path, _run_eval_impl)


@mcp.tool()
def create_failure_cluster(label: str) -> dict[str, Any]:
    """Return matching failure cluster fixture by label or id."""
    return create_failure_cluster_impl(PROJECT_ROOT, label)


@mcp.tool()
def promote_trace_to_dataset(run_id: str) -> dict[str, Any]:
    """Write a dataset-candidate row from a trace into generated_candidates.jsonl."""
    return promote_trace_to_dataset_impl(PROJECT_ROOT, run_id, _run_eval_impl)


@mcp.tool()
def get_policy_router_decision(task_id: str = "bugfix_date_parser_001") -> dict[str, Any]:
    """Fetch the static RL-lite router decision for a task."""
    return get_policy_router_decision_impl(PROJECT_ROOT, task_id)


if __name__ == "__main__":
    mcp.run()
