#!/usr/bin/env python3
"""Reliability aggregation — pass@1 and pass^k on the visible vs held-out metric.

Runs the seeded local runner N times per policy and reports BOTH signals, measured
from real execution (never tuned):

  - visible  : the agent's own test passed (`npm test`). This is what a naive eval
               that only runs the agent-visible suite would report. Brittle and
               gamed patches pass here.
  - held_out : the harness-only generalization suite passed AND the spec was not
               edited (i.e. the run was actually accepted). This is the true metric.

The visible-vs-held-out gap is the overfitting / spec-gaming signal; the pass^k
collapse is the reliability signal. Magnitudes are illustrative (the runner's
decision-point weights are hand-set), but the orderings are structural:
held_out <= visible, and guarded pass^k >> baseline pass^k.

Usage:
    python packages/evals/pass_k.py                 # write data/evals/reliability.json
    python packages/evals/pass_k.py --n 30 --capability 0.7
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for directory in (ROOT / "services" / "runner", ROOT / "packages" / "evals", ROOT / "packages" / "reward"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from task_runner import TaskRunner  # noqa: E402

DATE_PARSER_TASK = "bugfix_date_parser_001"
POLICIES = ["baseline", "test_first", "context_first", "guarded_recovery"]
DEFAULT_N = 20
DEFAULT_CAPABILITY = 0.7
KS = (1, 2, 3, 5)


def pass_pow_k(successes: int, n: int, k: int) -> float:
    """Unbiased P(a random k-subset of n attempts all pass) = C(c,k)/C(n,k)."""
    if k > n or successes < k:
        return 0.0
    return math.comb(successes, k) / math.comb(n, k)


def wilson_ci(successes: int, n: int, z: float = 1.96) -> list[float]:
    """95% Wilson score interval for a binomial proportion."""
    if n == 0:
        return [0.0, 0.0]
    p = successes / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return [round(max(0.0, center - half), 4), round(min(1.0, center + half), 4)]


def summarize(flags: list[bool], ks=KS) -> dict:
    c = sum(1 for f in flags if f)
    n = len(flags)
    return {
        "pass1": round(c / n, 4) if n else 0.0,
        "passK": {str(k): round(pass_pow_k(c, n, k), 4) for k in ks},
        "ci95": wilson_ci(c, n),
        "successes": c,
        "n": n,
    }


def run_policy(project_root: Path, policy: str, *, n: int, capability: float) -> dict:
    visible: list[bool] = []
    held_out: list[bool] = []
    for seed in range(n):
        trace = TaskRunner(
            project_root, policy, DATE_PARSER_TASK, seed=seed, capability=capability
        ).run()
        rel = trace.get("reliability") or {}
        visible.append(bool(rel.get("visible_passed")))
        # True success: held-out generalization passed and the spec was not gamed.
        held_out.append(trace.get("verdict") == "accepted")
    return {
        "policy": policy,
        "visible": summarize(visible),
        "heldOut": summarize(held_out),
        "seedResults": {"visible": visible, "heldOut": held_out},
    }


def aggregate(project_root: Path, *, n: int = DEFAULT_N, capability: float = DEFAULT_CAPABILITY) -> dict:
    policies = [run_policy(project_root, p, n=n, capability=capability) for p in POLICIES]
    return {
        "task_id": DATE_PARSER_TASK,
        "n": n,
        "capability": capability,
        "ks": list(KS),
        "metric_note": (
            "Real seeded local-runner executions (npm test + held-out node). "
            "'visible' = the agent's own test (naive metric; brittle/gamed patches pass). "
            "'heldOut' = generalization suite passed and spec untouched (true metric). "
            "Magnitudes illustrative; orderings (heldOut <= visible, guarded passK >> baseline) are structural."
        ),
        "policies": policies,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=DEFAULT_N, help="seeds per policy")
    parser.add_argument("--capability", type=float, default=DEFAULT_CAPABILITY)
    parser.add_argument("--output", default="data/evals/reliability.json")
    parser.add_argument("--print", action="store_true", help="also print a compact table")
    args = parser.parse_args()

    result = aggregate(ROOT, n=args.n, capability=args.capability)
    out_path = ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    if args.print:
        print(f"reliability · {DATE_PARSER_TASK} · N={args.n} · capability={args.capability}")
        print(f"{'policy':<20} {'visible@1':>9} {'heldout@1':>9} {'heldout^5':>9}")
        for row in result["policies"]:
            print(
                f"{row['policy']:<20} "
                f"{row['visible']['pass1']:>9.2f} "
                f"{row['heldOut']['pass1']:>9.2f} "
                f"{row['heldOut']['passK']['5']:>9.3f}"
            )
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
