# Start Here in Cursor

## Goal

Build the first polished vertical slice of Agent Harness Environment:

```text
Replay baseline failure → inspect trace → toggle guarded recovery → judge accepts → compare evals → open failure cluster → show router decision
```

## Before coding

Ask Cursor to read these files:

1. `docs/PRODUCT_PLAN.md`
2. `docs/UX_PLAN.md`
3. `.cursor/rules/architecture.mdc`
4. `.cursor/rules/eval-harness-standards.mdc`
5. `.cursor/rules/frontend-dashboard-patterns.mdc`
6. `apps/web/lib/demoData.ts`
7. `data/traces/baseline_date_parser.json`
8. `data/traces/guarded_recovery_date_parser.json`

## Cursor prompt 1 — cockpit vertical slice

```text
Implement the cockpit vertical slice using static data only. The policy toggle must update trace rows, active evidence, terminal output, diff preview, judge notes, metrics, and verdict. Do not add a backend yet. Keep the UX focused on the baseline vs guarded recovery comparison.
```

Acceptance criteria:

- `baseline` shows rejected verdict and loop/ignored-test-output failure labels.
- `guarded_recovery` shows accepted verdict and recovery/test-pass path.
- Trace rows are readable before raw JSON.
- Evidence tabs show file, terminal, diff, and judge state for the active step.
- The page is usable with keyboard controls.

## Cursor prompt 2 — eval report and failure clusters

```text
Add the eval report below the cockpit. Use data/evals/policy_comparison.json and data/failure_clusters.json. Clicking a metric or cluster should open a drawer with pattern, detection rule, recommended harness change, and dataset candidate JSON.
```

Acceptance criteria:

- Policy table compares baseline, test-first, context-first, guarded recovery, and RL-lite router.
- Baseline loop rate opens the repeated-terminal-command cluster.
- Promote-to-dataset renders the dataset candidate.
- Copy clearly says hosted metrics are synthetic fixtures.

## Cursor prompt 3 — local eval scoring

```text
Make packages/evals/run_eval.py produce a clean JSON summary for any trace fixture. Add or improve tests for loop detection, unsafe tool detection, hallucinated file grounding, patch minimality, and recovery score. Keep deterministic scorers primary.
```

Acceptance criteria:

- `pnpm eval` outputs valid JSON.
- `pnpm validate:fixtures` passes.
- Scorer output includes component scores and an aggregate run quality.
- A trace with repeated identical failed commands receives high loop score.

## Cursor prompt 4 — MCP tools

```text
Wire tools/mcp_server.py to read local fixture data and expose list_eval_runs, get_trace, compare_policies, run_eval, create_failure_cluster, promote_trace_to_dataset, and get_policy_router_decision. Keep the MCP server read-only except promote_trace_to_dataset, which should write to data/datasets/generated_candidates.jsonl.
```

Acceptance criteria:

- Cursor can start the project MCP server from `.cursor/mcp.json`.
- MCP tools return compact, structured payloads.
- The server does not require Braintrust or W&B keys.

## Cursor prompt 5 — runner MVP

```text
Implement the smallest local runner MVP in services/runner. It should load one toy repo task, apply a stubbed agent action plan, emit AgentTraceEvent records, enforce safe terminal commands, and write a trace JSON file. Do not attempt a full autonomous agent yet.
```

Acceptance criteria:

- Runner can emit a valid trace for `bugfix_date_parser_001`.
- Commands go through `safe_terminal_use` checks.
- Repeated command detection works.
- Final trace can be scored by `packages/evals/run_eval.py`.

## Keep these product constraints

- Hosted demo uses precomputed traces.
- Trace events are first-class product artifacts.
- Every new policy emits trace events.
- Deterministic scorers anchor the eval system.
- LLM-assisted judges are optional and never the only success criterion.
- RL-lite means policy routing, not model training.
