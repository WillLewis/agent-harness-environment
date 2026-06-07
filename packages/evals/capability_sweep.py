#!/usr/bin/env python3
"""Capability sweep — which harness primitives earn their keep as the model improves.

Sweeps the agent's `capability` and measures, per level, from REAL seeded runs:

  - productivity-primitive lift = held-out pass@1(policy) - held-out pass@1(baseline),
    for test_first and context_first. As capability rises and the baseline
    self-corrects, this lift fades.
  - baseline spec-gaming rate = fraction of baseline runs that edited the visible
    test to go green. P(game) rises with capability, so this climbs — it is the
    failure ONLY a held-out suite / spec-integrity guard catches.

Punchline (emergent, not drawn): capability shrinks the productivity primitives'
value and grows the integrity exposure. The durable harness is the integrity layer.

Magnitudes are illustrative (decision-point weights are hand-set); the directions
are structural. Usage:
    python packages/evals/capability_sweep.py [--n 20]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for directory in (ROOT / "services" / "runner", ROOT / "packages" / "evals", ROOT / "packages" / "reward"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from task_runner import TaskRunner  # noqa: E402

TASK = "bugfix_date_parser_001"
POLICIES = ["baseline", "test_first", "context_first", "guarded_recovery"]
CAPABILITIES = [0.1, 0.3, 0.5, 0.7, 0.9]
DEFAULT_N = 20


def measure_cell(project_root: Path, policy: str, capability: float, n: int) -> dict:
    held_out = visible = gaming = 0
    for seed in range(n):
        trace = TaskRunner(project_root, policy, TASK, seed=seed, capability=capability).run()
        rel = trace.get("reliability") or {}
        if trace.get("verdict") == "accepted":
            held_out += 1
        if rel.get("visible_passed"):
            visible += 1
        if rel.get("patch_kind") == "gaming":
            gaming += 1
    return {"heldOut": held_out / n, "visible": visible / n, "gamingRate": gaming / n}


def sweep(project_root: Path, *, n: int = DEFAULT_N) -> dict:
    curves = []
    for capability in CAPABILITIES:
        cells = {p: measure_cell(project_root, p, capability, n) for p in POLICIES}
        base = cells["baseline"]["heldOut"]
        curves.append(
            {
                "capability": capability,
                "testFirstLift": round(cells["test_first"]["heldOut"] - base, 3),
                "contextFirstLift": round(cells["context_first"]["heldOut"] - base, 3),
                "baselineGamingRate": round(cells["baseline"]["gamingRate"], 3),
                "baselineHeldOut": round(base, 3),
                "guardedHeldOut": round(cells["guarded_recovery"]["heldOut"], 3),
            }
        )
    return {
        "task_id": TASK,
        "n": n,
        "capabilities": CAPABILITIES,
        "metric_note": (
            "Real seeded runs. 'lift' = held-out pass@1 vs baseline (productivity primitives, fades with capability). "
            "'baselineGamingRate' = share of baseline runs that gamed the visible test (rises with capability; only "
            "held-out scoring catches it). Magnitudes illustrative; directions structural."
        ),
        "curves": curves,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=DEFAULT_N, help="seeds per (policy, capability)")
    parser.add_argument("--output", default="data/evals/capability_curves.json")
    args = parser.parse_args()

    result = sweep(ROOT, n=args.n)
    out_path = ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(f"capability sweep · {TASK} · N={args.n}")
    print(f"{'cap':>4} {'tf_lift':>8} {'cf_lift':>8} {'gaming':>8} {'base_ho':>8} {'guard_ho':>8}")
    for row in result["curves"]:
        print(
            f"{row['capability']:>4} {row['testFirstLift']:>8.3f} {row['contextFirstLift']:>8.3f} "
            f"{row['baselineGamingRate']:>8.3f} {row['baselineHeldOut']:>8.3f} {row['guardedHeldOut']:>8.3f}"
        )
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
