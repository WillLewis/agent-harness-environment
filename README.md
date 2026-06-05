# Agent Harness Environment Starter

Agent Harness Environment is a flight recorder, eval harness, and policy-comparison surface for coding agents. This starter repo is designed to open directly in Cursor and give the agent enough structure to start building without repeatedly re-explaining the product.

## What is included

- Static hosted demo: cockpit with **3 task classes** (bugfix, adversarial, multi-agent) and precomputed traces.
- Deterministic Python scorers, static eval suite + CI gate, and synthetic policy-comparison fixture for the hosted table.
- Local runner MVP, MCP tools, and Braintrust/Weave **dry-run** export adapters (no live external upload).
- Cursor rules, skills, MCP config, and product/UX/eval docs.

## Demo handoff

For external reviewers or portfolio walkthroughs:

| Goal | Command / link |
| --- | --- |
| Run hosted demo locally | `pnpm install` → `pnpm dev` → open `#cockpit`, `#evals`, `#architecture` |
| Click-by-click script | [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) |
| Pre-release verification | [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) |
| Score full static trace suite | `pnpm eval:suite` (table) or `pnpm eval:ci` (CI gate) |
| Score one trace locally | `pnpm eval` (guarded) · `pnpm eval:baseline` |
| Local runner (optional) | `python services/runner/run_task.py guarded_recovery` |
| Export shape previews | `pnpm export:braintrust:dry-run` · `pnpm export:weave:dry-run` |

**Hosted page:** replays static fixtures only — no live LLM, runner, or external APIs in the browser.  
**Eval table metrics:** synthetic portfolio fixture, not production telemetry.  
**Adapters:** dry-run JSON locally; live Braintrust/W&B upload is not implemented.

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

Open this folder in Cursor and start with `START_HERE_CURSOR.md`. The repository intentionally includes both `.cursor/rules/*.mdc` and `.cursor/skills/*/SKILL.md` because the product depends on repeatable agent behavior, not one-off prompting.

Suggested first Cursor prompt:

```text
Read START_HERE_CURSOR.md, docs/PRODUCT_PLAN.md, docs/UX_PLAN.md, and the Cursor rules. Then implement the next smallest slice: make the cockpit policy toggle update trace, metrics, terminal output, diff, and verdict together. Keep data static and deterministic.
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
pnpm export:braintrust:dry-run
pnpm export:weave:dry-run
```

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
| `services/runner/` | Toy repos → `runs/` | Local execution; not used by hosted page |
| Adapter dry-runs | Fixtures → export JSON | Shape preview only; not external integration |
| Braintrust / W&B live upload | — | **Not implemented**; adapters return `not_configured` without SDK + API key |

Details: [docs/EVAL_DESIGN.md](docs/EVAL_DESIGN.md) · [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md)

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
