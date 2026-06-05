# Agent Harness Environment Starter

Agent Harness Environment is a flight recorder, eval harness, and policy-comparison surface for coding agents. This starter repo is designed to open directly in Cursor and give the agent enough structure to start building without repeatedly re-explaining the product.

## What is included

- Static hosted-demo fixtures for the default `timezone parser regression` story.
- A Next.js/Tailwind cockpit shell using local TypeScript data.
- Trace schema and harness policy primitives.
- Python eval scorer stubs and a local policy comparison script.
- A minimal RL-lite reward router.
- Cursor project rules, skills, MCP config, and PR review guidance.
- Toy repo fixture for the first bugfix task.
- Product, UX, eval, and demo-script docs.

## Fast start

```bash
pnpm install
pnpm dev
```

Then open the app at the local URL printed by Next.js.

For Python evals:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pnpm validate:fixtures
pnpm eval
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
pnpm dev                 # Run hosted demo shell
pnpm validate:fixtures   # Validate trace fixture shape
pnpm eval                # Score guarded recovery trace
pnpm eval:baseline       # Score baseline trace
pnpm eval:suite          # Score all static traces + table summary
pnpm eval:ci             # Suite + deterministic gates (nonzero on regression)
pnpm compare             # Print policy comparison table
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

### Local CI vs external eval adapters

| Surface | Purpose |
| --- | --- |
| `pnpm eval:ci` / GitHub Actions | Deterministic smoke gate: fixture validation, static trace scorers, suite gates, pytest, typecheck, build. |
| Braintrust / W&B (future) | Optional export and experiment tracking when configured; failures there must not block the local demo or this workflow. |

The hosted demo and CI both rely on static fixtures under `data/` only.

## Repo map

```text
apps/web                 Hosted interactive demo shell
packages/harness         TypeScript trace + policy primitives
packages/evals           Python deterministic and heuristic scorers
packages/reward          RL-lite router and reward formula
services/runner          Future local runner/sandbox service
services/trace-store     SQLite trace-store starter
tools/mcp_server.py      Cursor MCP tool surface
.cursor                  Cursor rules, skills, MCP config, review rules
data                    Static hosted-demo fixtures
toy_repos                Minimal repos for local eval tasks
docs                    Product, UX, eval, and demo docs
```

## Design constraint

The hosted page should use static fixtures by default. Live agent execution belongs behind the local runner and should not be required for the portfolio/demo surface.
