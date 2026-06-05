# Eval Design

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

### GitHub Actions

`.github/workflows/ci.yml` runs `pnpm eval:ci` plus fixture validation, single-trace evals, policy compare, pytest, typecheck, and build. It does not call Braintrust, W&B, or live model APIs.

### Braintrust adapter (local-only default)

`packages/evals/adapters/braintrust_adapter.py` maps AHE tasks, `coding_tasks.jsonl`, trace fixtures, `run_eval` scores, and `run_suite` summaries to Braintrust-oriented shapes. Pure transforms are unit-tested without network access.

```bash
pnpm export:braintrust:dry-run
```

- Default: compact JSON dry-run (`mode: dry_run`); no SDK calls.
- Missing `braintrust` package or `BRAINTRUST_API_KEY`: structured `not_configured` when live export is requested.
- Live upload is reserved for a later phase; CI and `pnpm eval:ci` stay fully local.

### W&B Weave adapter (local-only default)

`packages/evals/adapters/weave_adapter.py` maps trace fixtures to Weave trace/span metadata, `AgentTraceEvent` records to span/call shapes, `run_eval` scores to feedback records, and `run_suite` summaries to evaluation batches.

```bash
pnpm export:weave:dry-run
```

- Default: compact JSON dry-run; no SDK calls or network.
- Missing `weave`/`wandb` package or `WANDB_API_KEY`: structured `not_configured` when live export is requested.
- Live upload is reserved for a later phase; CI remains unchanged.

## Next eval work

1. Add optional `plan_quality` and `final_answer_groundedness` LLM judge interfaces.
2. Implement live Braintrust/Weave upload behind optional configuration.
