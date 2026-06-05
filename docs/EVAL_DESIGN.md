# Eval Design

**Doc map:** [INDEX.md](./INDEX.md)

For demo walkthrough and release verification, see [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) and [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md).

## Scoring stack

Use deterministic and heuristic scorers first. LLM-assisted judges are optional and should never be the only success signal.

## Current starter scorers

| Scorer | Type | Purpose |
|---|---|---|
| `tests_passed` | deterministic | Checks target test pass signal. |
| `regression_free` | deterministic | Checks full-suite or regression-free signal. |
| `loop_score` | heuristic | Detects repeated failing commands. |
| `hallucinated_file` | deterministic | Verifies referenced files exist in repo snapshot. |
| `unsafe_tool_use` | deterministic | Detects unsafe commands or secret-access attempts. |
| `patch_minimality` | heuristic | Penalizes unrelated file churn. |
| `recovery_score` | heuristic | Checks whether failed tests are followed by evidence and later pass. |
| `expected_files_touched` | deterministic | Edited files stay within expected or known file set. |
| `command_allowlist` | deterministic | Terminal and test commands conform to allow-list rules. |

## Aggregate starter formula

```text
run_quality =
  0.32 * task_success
+ 0.18 * regression_free
+ 0.14 * recovery_score
+ 0.08 * patch_minimality
+ 0.05 * expected_files_touched
+ 0.05 * command_allowlist
- 0.10 * loop_score
- 0.05 * unsafe_tool_use
- 0.05 * hallucinated_file
```

## Static trace suite and CI gate

`packages/evals/run_suite.py` scores every fixture in `data/traces/*.json`, validates shape, and emits a compact JSON summary. Groupings include `by_task_id`, `by_policy`, `by_verdict`, and `by_failure_label`.

```bash
pnpm eval:suite    # JSON summary + stderr table
pnpm eval:ci       # same run; exit 1 on validation or gate failure
```

Gate contract (`packages/evals/suite_gates.py`):

| Rule | Behavior |
| --- | --- |
| Fixture validation | Every trace must pass `fixture_validation` with no errors. |
| Accepted traces | `tests_passed` and `regression_free` scorers pass; aggregate ≥ `min_accepted_aggregate` (default 0.45). Override per trace via `gate_overrides` if needed. |
| Assisted traces | Per-fixture scorer expectations; aggregate ≥ `min_assisted_aggregate` (default 0.40). |
| Rejected baselines | Retain story failure labels and scorer signals (loop, unsafe tool, contract mismatch). |

Per-fixture expectations are keyed by trace filename stem in `FIXTURE_EXPECTATIONS`. Thresholds are configurable via CLI flags on `run_suite.py`.

### Metric sources (avoid drift confusion)

| Surface | Command / path | Classification | Claims |
| --- | --- | --- | --- |
| Hosted eval table | `data/evals/policy_comparison.json` | `synthetic_benchmark_fixture` | Portfolio-style **synthetic** percentages (32 fictional tasks); not measured from traces |
| Curated trace gates | `pnpm eval:ci` / `pnpm eval:suite` | `deterministic_trace_score` | **Real** scorer output on 7 fixtures in `data/traces/` |
| Cockpit task metrics | `apps/web/lib/cockpitFixtures.ts` | static per-task maps | Demo replay numbers aligned to trace stories; not the eval table |
| Local runner batch | `pnpm runner:batch` → `runs/` | `runner_generated_local_trace` | Generated traces; optional promote to `data/trace_candidates/` |

Run `python packages/evals/audit_metric_drift.py` (optional `--format table`) to compare hosted synthetic policy rows against suite scorer rollups and flag ambiguity (policies without trace fixtures, scorers absent from hosted columns, headline metric divergence).

### GitHub Actions

`.github/workflows/ci.yml` runs `pnpm eval:ci` plus fixture validation, single-trace evals, policy compare, pytest, typecheck, and build. It does not call Braintrust, W&B, or live model APIs.

### Braintrust adapter (dry-run default; opt-in live)

`packages/evals/adapters/braintrust_adapter.py` maps AHE tasks, `coding_tasks.jsonl`, trace fixtures, `run_eval` scores, and `run_suite` summaries to Braintrust-oriented shapes. Pure transforms are unit-tested without network access.

```bash
pnpm export:braintrust:dry-run    # default — compact JSON, no SDK import
pnpm export:braintrust:live       # explicit upload (optional SDK + API key)
```

| Mode | Command | Network | Exit on failure |
| --- | --- | --- | --- |
| Dry-run | `--dry-run` (default) | No | No (always prints JSON) |
| Live | `--live` only | Yes | Yes (`not_configured` or `live_export_failed`) |

**Live setup (optional, not in CI):**

```bash
pip install -r requirements-braintrust.txt
export BRAINTRUST_API_KEY=...          # required
export BRAINTRUST_PROJECT=agent-harness-environment   # optional
pnpm export:braintrust:live
```

Live export uploads the current static suite only: task/coding-task datasets, per-trace fixture examples, and the `run_suite` summary experiment. It does **not** re-run the runner or call LLMs.

**Non-claims:** live export is not production telemetry, not wired to the hosted demo, and not part of `pnpm eval:ci`. Missing `braintrust` or `BRAINTRUST_API_KEY` returns structured `not_configured` (exit 1) only when `--live` is passed.

**Why not in `pnpm eval:ci`:** CI must stay deterministic, secret-free, and dependency-light. Braintrust is an optional operator tool for exporting fixture shapes to an external project.

### W&B Weave adapter (dry-run default; opt-in live)

`packages/evals/adapters/weave_adapter.py` maps trace fixtures to Weave trace/span metadata, `AgentTraceEvent` records to span/call shapes, `run_eval` scores to feedback records, and `run_suite` summaries to evaluation batches.

```bash
pnpm export:weave:dry-run    # default — compact JSON, no SDK import
pnpm export:weave:live       # explicit upload (optional weave + API key)
```

| Mode | Command | Network | Exit on failure |
| --- | --- | --- | --- |
| Dry-run | `--dry-run` (default) | No | No |
| Live | `--live` only | Yes | Yes (`not_configured` or `live_export_failed`) |

**Live setup (optional, not in CI):**

```bash
pip install -r requirements-weave.txt
export WANDB_API_KEY=...
export WANDB_PROJECT=agent-harness-environment   # optional
export WANDB_ENTITY=your-team                    # optional (entity/project path)
pnpm export:weave:live
```

Live export uploads static trace trees (root call + span children), scorer feedback, and suite evaluation rows via `weave.init` + `create_call` / `finish_call`. It does **not** re-run the runner or call LLMs.

**Non-claims:** not production telemetry, not in the hosted demo, not part of `pnpm eval:ci`. Live mode requires the **`weave`** package (not `wandb` alone).

**Why not in `pnpm eval:ci`:** same as Braintrust — deterministic, secret-free CI.

## Next eval work

1. Add optional `plan_quality` and `final_answer_groundedness` LLM judge interfaces.
