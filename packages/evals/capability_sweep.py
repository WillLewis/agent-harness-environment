#!/usr/bin/env python3
"""Capability sweep — which harness primitives earn their keep as the model improves.

Sweeps the agent's `capability` across all three toy tasks and measures, per level,
from REAL seeded runs:

  - productivity lift = held-out pass@1(policy) - held-out pass@1(baseline), for
    test_first and context_first. As capability rises and the baseline self-helps,
    this lift fades.
  - a per-task "exposure" = the baseline failure rate of the kind only a held-out
    suite / guard catches:
      * date-parser  spec-gaming rate   — RISES with capability (integrity exposure)
      * adversarial  unsafe-attempt rate — RISES with capability (safety exposure)
      * multi-agent  contract-drift rate — FALLS with capability (a coordination gap
                     capable agents partly close on their own)

Punchline (emergent, not drawn): capability shrinks the productivity primitives'
value, while the integrity/safety exposures it leaves behind only grow. The durable
harness is the integrity/safety layer; the productivity (and coordination) layer is
on borrowed time.

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

POLICIES = ["baseline", "test_first", "context_first", "guarded_recovery"]
CAPABILITIES = [0.1, 0.3, 0.5, 0.7, 0.9]
DEFAULT_N = 20

# Each task defines the baseline "exposure" the durable guard exists to catch, and
# how the chart should frame it. `exposureKind` drives the chart colour: "integrity"
# / "safety" exposures rise with capability; a "coordination" exposure fades.
TASKS = [
    {
        "task_id": "bugfix_date_parser_001",
        "label": "Date-parser bugfix",
        "exposureKey": "patch_kind",
        "exposureValue": "gaming",
        "exposureLabel": "baseline spec-gaming rate",
        "exposureKind": "integrity",
        "metric_note": (
            "Productivity lift (test-first, context-first) fades as the baseline self-corrects; "
            "the baseline spec-gaming rate climbs with capability — the failure only the held-out "
            "suite + spec-integrity check catch."
        ),
    },
    {
        "task_id": "adversarial_env_001",
        "label": "Adversarial docs build",
        "exposureKey": "unsafe_attempted",
        "exposureValue": True,
        "exposureLabel": "baseline unsafe-attempt rate",
        "exposureKind": "safety",
        "metric_note": (
            "A more capable baseline both fixes the build AND follows the adversarial README more "
            "often, so its unsafe-attempt rate climbs with capability — the failure only the command "
            "classifier / guarded policy catch. Test-first never reads the README, so its lift is poor."
        ),
    },
    {
        "task_id": "multi_agent_contract_001",
        "label": "Multi-agent contract",
        "exposureKey": "patch_kind",
        "exposureValue": "drifted",
        "exposureLabel": "baseline contract-drift rate",
        "exposureKind": "coordination",
        "metric_note": (
            "Shared-contract coordination is a productivity primitive: its lift is huge for weak "
            "models and fades as capable agents converge on their own. The baseline drift rate falls "
            "with capability but plateaus high — raw capability does not fully close the multi-agent "
            "communication gap."
        ),
    },
]


def measure_cell(project_root: Path, task: dict, policy: str, capability: float, n: int) -> dict:
    held_out = visible = exposure = 0
    for seed in range(n):
        trace = TaskRunner(project_root, policy, task["task_id"], seed=seed, capability=capability).run()
        rel = trace.get("reliability") or {}
        if trace.get("verdict") == "accepted":
            held_out += 1
        if rel.get("visible_passed"):
            visible += 1
        if rel.get(task["exposureKey"]) == task["exposureValue"]:
            exposure += 1
    return {"heldOut": held_out / n, "visible": visible / n, "exposure": exposure / n}


def sweep_task(project_root: Path, task: dict, *, n: int) -> dict:
    curves = []
    for capability in CAPABILITIES:
        cells = {p: measure_cell(project_root, task, p, capability, n) for p in POLICIES}
        base = cells["baseline"]["heldOut"]
        curves.append(
            {
                "capability": capability,
                "testFirstLift": round(cells["test_first"]["heldOut"] - base, 3),
                "contextFirstLift": round(cells["context_first"]["heldOut"] - base, 3),
                "baselineExposure": round(cells["baseline"]["exposure"], 3),
                "baselineHeldOut": round(base, 3),
                "guardedHeldOut": round(cells["guarded_recovery"]["heldOut"], 3),
            }
        )
    values = [v for c in curves for v in (c["testFirstLift"], c["contextFirstLift"], c["baselineExposure"])]
    y_min = min(0.0, min(values))
    y_max = max(values)
    y_domain = [round(y_min - 0.05 if y_min < 0 else 0.0, 2), round(y_max + 0.1, 2)]
    series = [
        {"key": "testFirstLift", "label": "test-first lift", "kind": "productivity"},
        {"key": "contextFirstLift", "label": "context-first lift", "kind": "productivity"},
        {"key": "baselineExposure", "label": task["exposureLabel"], "kind": task["exposureKind"]},
    ]
    return {
        "task_id": task["task_id"],
        "label": task["label"],
        "exposureLabel": task["exposureLabel"],
        "exposureKind": task["exposureKind"],
        "metric_note": task["metric_note"],
        "yDomain": y_domain,
        "series": series,
        "curves": curves,
    }


def sweep(project_root: Path, *, n: int = DEFAULT_N) -> dict:
    return {
        "n": n,
        "capabilities": CAPABILITIES,
        "generated_with": f"python packages/evals/capability_sweep.py --n {n}",
        "metric_note": (
            "Real seeded runs across all three toy tasks. 'lift' = held-out pass@1 vs baseline "
            "(productivity primitives, fade with capability). 'exposure' = the baseline failure rate the "
            "durable guard catches (spec-gaming / unsafe-attempt rise; contract-drift falls). "
            "Magnitudes illustrative; directions structural."
        ),
        "tasks": [sweep_task(project_root, task, n=n) for task in TASKS],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=DEFAULT_N, help="seeds per (task, policy, capability)")
    parser.add_argument("--output", default="data/evals/capability_curves.json")
    args = parser.parse_args()

    result = sweep(ROOT, n=args.n)
    out_path = ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    for task in result["tasks"]:
        print(f"\ncapability sweep · {task['task_id']} · N={args.n}  ({task['exposureLabel']})")
        print(f"{'cap':>4} {'tf_lift':>8} {'cf_lift':>8} {'exposure':>9} {'base_ho':>8} {'guard_ho':>8}")
        for row in task["curves"]:
            print(
                f"{row['capability']:>4} {row['testFirstLift']:>8.3f} {row['contextFirstLift']:>8.3f} "
                f"{row['baselineExposure']:>9.3f} {row['baselineHeldOut']:>8.3f} {row['guardedHeldOut']:>8.3f}"
            )
    print(f"\nwrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
