#!/usr/bin/env python3
"""Real-model sweep for the headline separation suite (cards A, B, C).

Runs N samples per (task, model, policy) cell, writes one fixture file per task
to data/evals/reliability_{task_id}.json in the same format as the hard/injection
real fixtures.

Usage:
    python scripts/run_separation_sweep.py             # all tasks, N=16
    python scripts/run_separation_sweep.py --n 8 --task idempotent_webhook_001
    python scripts/run_separation_sweep.py --models claude-opus-4-8 claude-sonnet-4-6
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for d in (ROOT / "services" / "runner", ROOT / "packages" / "evals", ROOT / "packages" / "reward"):
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))

from real_agent_runner import RealAgentRunner, load_env_file  # noqa: E402

# Per-task metric extraction: fn(reliability_dict) -> cell_metrics_dict
TASK_METRICS = {
    "completeness_comments_001": lambda r: {
        "visible":  float(r["visible_passed"]),
        "heldOut":  float(r["held_out_passed"]),
    },
    "workspace_safety_001": lambda r: {
        "visible":   float(r["visible_passed"]),
        "safe":      float(r["held_out_passed"]),
        "leakRate":  1.0 - float(r["held_out_passed"]) if r["visible_passed"] else 0.0,
    },
    "idempotent_webhook_001": lambda r: {
        "visible":  float(r["visible_passed"]),
        "heldOut":  float(r["held_out_passed"]),
    },
}

DEFAULT_MODELS   = ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-8",
                    "gpt-5.4-nano", "gpt-5.4-mini"]
DEFAULT_POLICIES = ["baseline", "guarded_recovery"]
DEFAULT_N        = 16
WORKERS          = 8   # parallel sample workers; stay under rate-limit ceiling

_print_lock = threading.Lock()

def tprint(*args, **kwargs):
    with _print_lock:
        print(*args, **kwargs, flush=True)


def run_one(task_id: str, model: str, policy: str, seed: int) -> dict:
    try:
        trace = RealAgentRunner(ROOT, policy, task_id, seed=seed, model=model).run()
        r = trace["reliability"]
        metrics = TASK_METRICS[task_id](r)
        metrics["patch_kind"] = r["patch_kind"]
        metrics["error"] = None
    except Exception as exc:  # noqa: BLE001
        metrics = {"error": str(exc), "patch_kind": "error"}
    metrics.update({"task_id": task_id, "model": model, "policy": policy, "seed": seed})
    return metrics


def aggregate_cells(results: list[dict], task_id: str, models: list[str], policies: list[str], n: int) -> list[dict]:
    cells = []
    for model in models:
        for policy in policies:
            rows = [r for r in results if r["model"] == model and r["policy"] == policy]
            rows = [r for r in rows if not r.get("error")]
            if not rows:
                continue

            patch_kinds: dict[str, int] = defaultdict(int)
            for r in rows:
                patch_kinds[r["patch_kind"]] += 1

            cell: dict = {"model": model, "policy": policy}
            # Average each numeric metric
            num_keys = [k for k in TASK_METRICS[task_id]({
                "visible_passed": True, "held_out_passed": True}).keys()]
            for key in num_keys:
                vals = [r[key] for r in rows if key in r]
                cell[key] = round(sum(vals) / len(vals), 4) if vals else 0.0
            cell["patch_kinds"] = dict(patch_kinds)
            cells.append(cell)
    return cells


def sweep_task(task_id: str, models: list[str], policies: list[str], n: int, out_path: Path) -> None:
    tprint(f"\n=== {task_id}: {len(models)} models × {len(policies)} policies × N={n} ===")
    futures = {}
    results = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for model in models:
            for policy in policies:
                for seed in range(n):
                    f = ex.submit(run_one, task_id, model, policy, seed)
                    futures[f] = (model, policy, seed)
        done = 0
        total = len(futures)
        for f in as_completed(futures):
            model, policy, seed = futures[f]
            r = f.result()
            results.append(r)
            done += 1
            status = r.get("error") or r.get("patch_kind", "?")
            tprint(f"  [{done}/{total}] {model} {policy} s{seed}: {status}")

    # aggregate and write
    cells = aggregate_cells(results, task_id, models, policies, n)
    fixture = {
        "task": task_id,
        "n": n,
        "models": models,
        "policies": policies,
        "cells": cells,
    }
    out_path.write_text(json.dumps(fixture, indent=2), encoding="utf-8")
    tprint(f"  -> wrote {out_path.relative_to(ROOT)}")
    # print table
    tprint(f"  {'model':30s} {'policy':20s} {' '.join(TASK_METRICS[task_id]({'visible_passed':True,'held_out_passed':True}).keys())}")
    for c in cells:
        num_keys = list(TASK_METRICS[task_id]({"visible_passed":True,"held_out_passed":True}).keys())
        vals = "  ".join(f"{c.get(k, 0):.3f}" for k in num_keys)
        tprint(f"  {c['model']:30s} {c['policy']:20s} {vals}  patch={c.get('patch_kinds',{})}")


def main() -> None:
    load_env_file(ROOT)
    os.environ.pop("ANTHROPIC_API_KEY", None)  # let load_env_file win over empty shell export
    load_env_file(ROOT)  # reload now that the empty var is gone

    parser = argparse.ArgumentParser()
    parser.add_argument("--n",       type=int,   default=DEFAULT_N)
    parser.add_argument("--task",    nargs="+",  default=list(TASK_METRICS))
    parser.add_argument("--models",  nargs="+",  default=DEFAULT_MODELS)
    parser.add_argument("--policies",nargs="+",  default=DEFAULT_POLICIES)
    args = parser.parse_args()

    eval_dir = ROOT / "data" / "evals"
    for task_id in args.task:
        out = eval_dir / f"reliability_{task_id}.json"
        sweep_task(task_id, args.models, args.policies, args.n, out)


if __name__ == "__main__":
    main()
