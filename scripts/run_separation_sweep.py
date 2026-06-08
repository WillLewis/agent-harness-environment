#!/usr/bin/env python3
"""Real-model sweep for the FINAL separation suite (fractional held-out grading).

Cards A/B/C each grade the held-out as a battery of independent sub-items scored as a
FRACTION (grade(workdir) -> float). This driver runs N samples per (task, model, policy)
cell and reports the MEAN held-out fraction + variance + per-item pass rates — the mean
fraction across models is the capability gradient the suite is designed to surface.

Writes one fixture per task to data/evals/reliability_{task_id}.json.

Usage:
    python scripts/run_separation_sweep.py                  # all 3 cards, N=16
    python scripts/run_separation_sweep.py --n 16 --task latent_defects_001
    python scripts/run_separation_sweep.py --models claude-opus-4-8 claude-sonnet-4-6
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for d in (ROOT / "services" / "runner", ROOT / "packages" / "evals", ROOT / "packages" / "reward"):
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))

from real_agent_runner import (  # noqa: E402
    FRACTIONAL_HOLDOUT_TASKS,
    RealAgentRunner,
    load_env_file,
)

DEFAULT_MODELS = ["gpt-5.4-nano", "gpt-5.4-mini", "claude-haiku-4-5",
                  "claude-sonnet-4-6", "claude-opus-4-8"]
DEFAULT_POLICIES = ["baseline", "guarded_recovery"]
DEFAULT_N = 16
WORKERS = 4

_lock = threading.Lock()
def tprint(*a, **k):
    with _lock:
        print(*a, **k, flush=True)


def run_one(task_id: str, model: str, policy: str, seed: int) -> dict:
    try:
        trace = RealAgentRunner(ROOT, policy, task_id, seed=seed, model=model).run()
        r = trace["reliability"]
        return {
            "task_id": task_id, "model": model, "policy": policy, "seed": seed,
            "visible": bool(r["visible_passed"]),
            "fraction": float(r.get("held_out_fraction") or 0.0),
            "detail": r.get("held_out_detail") or {},
            "patch_kind": r["patch_kind"],
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        return {"task_id": task_id, "model": model, "policy": policy, "seed": seed,
                "error": str(exc), "fraction": 0.0, "detail": {}, "visible": False,
                "patch_kind": "error"}


def aggregate(results: list[dict], models: list[str], policies: list[str]) -> list[dict]:
    cells = []
    for model in models:
        for policy in policies:
            rows = [r for r in results if r["model"] == model and r["policy"] == policy and not r.get("error")]
            if not rows:
                continue
            fracs = [r["fraction"] for r in rows]
            visibles = [r["visible"] for r in rows]
            # per-item pass rate across samples
            item_totals: dict[str, list[int]] = defaultdict(list)
            for r in rows:
                for k, v in r["detail"].items():
                    item_totals[k].append(1 if v else 0)
            item_rates = {k: round(sum(v) / len(v), 3) for k, v in item_totals.items()}
            patch_kinds: dict[str, int] = defaultdict(int)
            for r in rows:
                patch_kinds[r["patch_kind"]] += 1
            cells.append({
                "model": model,
                "policy": policy,
                "meanFraction": round(statistics.mean(fracs), 4),
                "stdevFraction": round(statistics.pstdev(fracs), 4) if len(fracs) > 1 else 0.0,
                "visibleRate": round(sum(visibles) / len(visibles), 4),
                "completeRate": round(sum(1 for f in fracs if f >= 0.999) / len(fracs), 4),
                "itemPassRates": item_rates,
                "patch_kinds": dict(patch_kinds),
                "n_effective": len(rows),
            })
    return cells


def sweep_task(task_id: str, models: list[str], policies: list[str], n: int, out: Path) -> None:
    tprint(f"\n=== {task_id}: {len(models)} models x {len(policies)} policies x N={n} ===")
    futures = {}
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for model in models:
            for policy in policies:
                for seed in range(n):
                    futures[ex.submit(run_one, task_id, model, policy, seed)] = (model, policy, seed)
        total = len(futures)
        done = 0
        for f in as_completed(futures):
            r = f.result()
            results.append(r)
            done += 1
            tag = r.get("error") or f"frac={r['fraction']:.2f} {r['patch_kind']}"
            tprint(f"  [{done}/{total}] {r['model']} {r['policy']} s{r['seed']}: {tag}")

    cells = aggregate(results, models, policies)
    fixture = {
        "task": task_id, "n": n, "models": models, "policies": policies,
        "grading": "fraction", "cells": cells,
    }
    out.write_text(json.dumps(fixture, indent=2), encoding="utf-8")
    tprint(f"  -> wrote {out.relative_to(ROOT)}")
    tprint(f"  {'model':20s} {'policy':18s} meanFrac  stdev  vis   complete")
    for c in cells:
        tprint(f"  {c['model']:20s} {c['policy']:18s} "
               f"{c['meanFraction']:.3f}    {c['stdevFraction']:.3f}  "
               f"{c['visibleRate']:.2f}  {c['completeRate']:.2f}  {c['patch_kinds']}")


def main() -> None:
    os.environ.pop("ANTHROPIC_API_KEY", None)  # drop empty shell export
    load_env_file(ROOT)

    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=DEFAULT_N)
    p.add_argument("--task", nargs="+", default=sorted(FRACTIONAL_HOLDOUT_TASKS))
    p.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    p.add_argument("--policies", nargs="+", default=DEFAULT_POLICIES)
    args = p.parse_args()

    eval_dir = ROOT / "data" / "evals"
    for task_id in args.task:
        sweep_task(task_id, args.models, args.policies, args.n,
                   eval_dir / f"reliability_{task_id}.json")


if __name__ == "__main__":
    main()
