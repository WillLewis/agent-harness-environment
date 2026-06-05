# Agent Harness Environment Starter

Agent Harness Environment is a flight recorder, eval harness, and policy-comparison surface for coding agents. This starter repo is designed to open directly in Cursor and give the agent enough structure to start building without repeatedly re-explaining the product.

**Documentation map:** [docs/INDEX.md](docs/INDEX.md) — demo path, verification, eval design, architecture, runner/MCP, backlog.

## What is included

- Static hosted demo: cockpit with **3 task classes** (bugfix, adversarial, multi-agent) and precomputed traces.
- Deterministic Python scorers, static eval suite + CI gate, and synthetic policy-comparison fixture for the hosted table.
- Local runner MVP, MCP tools, and Braintrust/Weave export adapters (dry-run by default; optional live upload).
- Cursor rules, skills, MCP config, and product/UX/eval docs.

## Demo handoff

For external reviewers or portfolio walkthroughs:

| Goal | Command / link |
| --- | --- |
| Run hosted demo locally | `pnpm install` → `pnpm dev` → open `#cockpit`, `#evals`, `#architecture` |
| Deploy hosted demo (review) | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — Vercel recommended; `pnpm deploy:check` then `pnpm build` |
| Click-by-click script | [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) |
| Pre-release verification | [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) |
| Final audit + backlog | [docs/FINAL_AUDIT.md](docs/FINAL_AUDIT.md) |
| Score full static trace suite | `pnpm eval:suite` (table) or `pnpm eval:ci` (CI gate) |
| Audit metric source drift | `pnpm eval:audit` |
| Check local generated artifacts | `pnpm repo:status` |
| Score one trace locally | `pnpm eval` (guarded) · `pnpm eval:baseline` |
| Local runner (optional) | `python services/runner/run_task.py guarded_recovery` |
| Promote runner trace to candidate | `python scripts/promote_run_trace.py runs/<run_id>.json` |
| Export shape previews | `pnpm export:braintrust:dry-run` · `pnpm export:weave:dry-run` |
| Optional Braintrust upload | `pip install -r requirements-braintrust.txt` + `BRAINTRUST_API_KEY` → `pnpm export:braintrust:live` |
| Optional Weave upload | `pip install -r requirements-weave.txt` + `WANDB_API_KEY` → `pnpm export:weave:live` |

**Hosted page:** replays static fixtures only — no live LLM, runner, or external APIs in the browser.  
**Eval table metrics:** synthetic portfolio fixture, not production telemetry.  
**Adapters:** dry-run JSON locally by default. Live Braintrust/Weave upload is opt-in (`--live` + API key + optional requirements files).

## Fast start

```bash
pnpm install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pnpm dev
```

Open the URL Next.js prints. Default cockpit: bugfix task, baseline policy (rejected).

Quick local eval smoke:

```bash
pnpm validate:fixtures
pnpm eval:ci
pnpm compare
```

## Cursor workflow

Open this folder in Cursor and start with [START_HERE_CURSOR.md](START_HERE_CURSOR.md) and [docs/INDEX.md](docs/INDEX.md). The repository includes `.cursor/rules/*.mdc` and `.cursor/skills/*/SKILL.md` for repeatable agent behavior.

Suggested first Cursor prompt:

```text
Read docs/INDEX.md, docs/FINAL_AUDIT.md (backlog §12), and .cursor/rules/architecture.mdc.
Pick one backlog item and implement the smallest vertical slice with tests. Keep the hosted demo static and CI deterministic.
```

## Core commands

```bash
pnpm dev                      # Hosted static demo (Next.js)
pnpm validate:fixtures        # Trace fixture validation
pnpm eval:ci                  # Full suite + gates (matches CI)
pnpm eval:suite               # Same scoring + human-readable table
pnpm eval                     # Score one trace (guarded date-parser)
pnpm eval:baseline            # Score one trace (baseline date-parser)
pnpm compare                  # Synthetic policy comparison table
pnpm eval:audit               # Metric drift report (hosted vs trace scorers)
pnpm repo:status              # Local generated-artifact hygiene (read-only)
pnpm deploy:check             # Hosted demo deployment readiness (local)
pnpm preview                  # Serve production build locally (after pnpm build)
pnpm smoke:hosted:local       # HTML smoke vs http://localhost:3000 (needs preview/dev)
pnpm smoke:hosted -- --url URL  # HTML smoke vs local or deployed demo URL
pnpm export:braintrust:dry-run
pnpm export:braintrust:live       # optional; requires braintrust + BRAINTRUST_API_KEY
pnpm export:weave:dry-run
pnpm export:weave:live            # optional; requires weave + WANDB_API_KEY
```

### Optional Braintrust live export

Not part of `pnpm eval:ci` or GitHub Actions. Install the optional SDK, set an API key, then pass `--live` explicitly:

```bash
pip install -r requirements-braintrust.txt
export BRAINTRUST_API_KEY=your_key
export BRAINTRUST_PROJECT=agent-harness-environment   # optional
pnpm export:braintrust:live
```

Dry-run (`pnpm export:braintrust:dry-run`) prints the same compact JSON as before — no SDK import, no network. Live mode uploads static task datasets, trace fixture examples, and the suite summary experiment from local fixtures only; it does not run the runner or claim production eval coverage.

### Optional Weave live export

Not part of `pnpm eval:ci` or GitHub Actions. Requires the **`weave`** package (install via `requirements-weave.txt`; `wandb` alone is not enough):

```bash
pip install -r requirements-weave.txt
export WANDB_API_KEY=your_key
export WANDB_PROJECT=agent-harness-environment   # optional
export WANDB_ENTITY=your-team                    # optional
pnpm export:weave:live
```

Dry-run (`pnpm export:weave:dry-run`) is unchanged. Live mode uploads static trace spans and suite scorer feedback only.

### Run all local runner tasks (optional)

Batch every supported task/policy pair (6 runs: 3 tasks × baseline + guarded_recovery), score each trace, and print a compact JSON summary:

```bash
pnpm runner:batch
pnpm runner:batch:promote   # also promote to data/trace_candidates/ (idempotent)
```

Not part of CI. Use after runner or promotion logic changes to smoke all deterministic paths locally.

### Promote local runner traces (optional)

After `services/runner/` writes a trace under `runs/`, promote it to a reviewable candidate without touching curated `data/traces/`:

```bash
python services/runner/run_task.py guarded_recovery multi_agent_contract_001
python scripts/promote_run_trace.py runs/run_local_guarded_recovery_multi_agent_contract_001.json
python packages/evals/run_eval.py data/trace_candidates/run_local_guarded_recovery_multi_agent_contract_001.json
```

Promotion validates the trace, scores it, normalizes transient fields (timestamps, sandbox paths, long terminal output), writes `data/trace_candidates/<run_id>.json`, and appends metadata to `data/datasets/generated_candidates.jsonl` (idempotent by `source_run_id`). Both directories are gitignored by default. To copy into curated fixtures, pass `--write-fixture --fixture-name <name>.json` explicitly (refuses overwrite).

## Verification

Run from the repo root after `pnpm install` and `pip install -r requirements-dev.txt`.

**CI command contract** — GitHub Actions (`.github/workflows/ci.yml`) runs the same deterministic gates on every push and pull request, in this order:

```bash
pnpm validate:fixtures
pnpm eval:ci
pnpm eval:baseline
pnpm eval
pnpm compare
python -m pytest
pnpm typecheck
pnpm build
```

No secrets, live LLM calls, or external eval services are required. `pnpm eval:ci` scores the full static trace suite and enforces fixture gate expectations (see `docs/EVAL_DESIGN.md`).

**Local before PR** — run the CI contract above, then optionally:

```bash
pnpm eval:suite          # full suite table + JSON summary (same scoring as eval:ci)
```

`pnpm test` is an alias for `python -m pytest`. `pnpm typecheck` does not require a prior build. Generated TypeScript metadata (`*.tsbuildinfo`) is gitignored.

### Static fixtures vs live local tools

| Surface | Data source | Use |
| --- | --- | --- |
| Hosted cockpit / eval table / router | `data/traces/`, `data/evals/` JSON | Demo replay; no network |
| `pnpm eval` / `pnpm eval:ci` | Same fixtures | **Real** deterministic scorer output |
| Hosted eval table (`#evals`) | `data/evals/policy_comparison.json` | **Synthetic** portfolio fixture — not `eval:ci` output |
| `python …/audit_metric_drift.py` | Compares sources above | Drift/ambiguity report; does not change fixtures |
| `services/runner/` | Toy repos → `runs/` | Local execution; not used by hosted page |
| Adapter dry-runs | Fixtures → export JSON | Shape preview; no network |
| Braintrust live upload | `pnpm export:braintrust:live` | Opt-in; static fixtures only; not in CI |
| W&B Weave live upload | `pnpm export:weave:live` | Opt-in; static traces only; not in CI |

Details: [docs/INDEX.md](docs/INDEX.md) · [docs/EVAL_DESIGN.md](docs/EVAL_DESIGN.md) · [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md)

## Repo map

```text
apps/web                 Hosted interactive demo shell
packages/harness         TypeScript trace + policy primitives
packages/evals           Python deterministic and heuristic scorers
packages/reward          RL-lite router and reward formula
services/runner          Local runner MVP (sandbox + trace emission)
services/trace-store     SQLite trace-store starter
tools/mcp_server.py      Cursor MCP tool surface
.cursor                  Cursor rules, skills, MCP config, review rules
data                    Static hosted-demo fixtures
toy_repos                Minimal repos for local eval tasks
docs                    Product, UX, eval, and demo docs
```

## Design constraint

The hosted page should use static fixtures by default. Live agent execution belongs behind the local runner and should not be required for the portfolio/demo surface.
