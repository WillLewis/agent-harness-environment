# Start Here in Cursor

Onboarding for the **next coding agent** on Agent Harness Environment. The starter vertical slices (cockpit, eval table, scorers, MCP, runner) are **already implemented** through Phase **13a**, plus optional Phase **13b** runner/eval observability (off by default).

**Documentation map:** [docs/INDEX.md](docs/INDEX.md) — demo path, verification, architecture, backlog.

---

## Current repo state (what exists)

| Area | Status | Primary paths |
| --- | --- | --- |
| Hosted demo | Static replay — 3 tasks, cockpit + eval table + router | `apps/web/`, `data/traces/` (13 fixtures) |
| Deterministic evals | 10 scorers, suite gates, CI | `packages/evals/`, `pnpm eval:ci` |
| Local runner | 3 tasks × baseline + guarded_recovery; batch + promote | `services/runner/`, `pnpm runner:batch` |
| MCP | Read fixtures, score, compare, promote dataset | `tools/mcp_server.py` |
| Adapters | Braintrust + Weave dry-run; opt-in `--live` | `packages/evals/adapters/` |
| Observability (13b) | Optional per-run Braintrust/W&B emit + link export (off by default) | `packages/evals/observability.py`, `pnpm observe` |
| Metric drift audit | Hosted synthetic vs trace scorers | `packages/evals/audit_metric_drift.py` |

**Do not re-implement** the baseline cockpit toggle, `run_eval.py`, or runner MVP unless explicitly asked — those are done.

---

## Before coding

Read in this order:

1. [docs/INDEX.md](docs/INDEX.md) — find the right doc for your task
2. [.cursor/rules/architecture.mdc](.cursor/rules/architecture.mdc) — hosted vs runner vs eval boundaries
3. [docs/FINAL_AUDIT.md](docs/FINAL_AUDIT.md) §12–14 — **backlog** and handoff constraints
4. Task-specific rule or skill (e.g. `eval-harness-standards.mdc`, `.cursor/skills/create-task-fixture/SKILL.md`)

For eval or fixture work, also skim [docs/EVAL_DESIGN.md](docs/EVAL_DESIGN.md).

---

## Suggested first prompt (current maturity)

```text
Read docs/INDEX.md, docs/FINAL_AUDIT.md (backlog §12), and .cursor/rules/architecture.mdc.
Pick one P1/P2 backlog item and implement the smallest vertical slice with tests.
Preserve: hosted demo stays static; CI stays deterministic (no live LLM/API in gates).
```

Replace the backlog item with something explicit if the user already chose work (e.g. “Phase 14b: …”).

---

## Hard constraints (unchanged)

- **Hosted demo** (`apps/web`): static fixtures only — no live LLM, runner, or external APIs in the browser.
- **CI** (`pnpm eval:ci`): deterministic trace scoring + gates; no Braintrust/W&B/network required.
- **Trace events** are first-class; every policy path should be traceable.
- **Deterministic scorers** anchor evals; LLM judges are optional and never the sole success signal.
- **RL-lite** = contextual-bandit policy routing, not coding-model training; hosted UI uses exported static fixtures.

---

## Observability (Phase 13b, optional)

Observability is **off by default** and never required for tests, builds, CI, the
hosted demo, or trace replay. The hosted app stays static — it only reads the
exported `data/evals/observability_links.json`, never a vendor SDK.

Local runner/eval runs can optionally emit one structured record per
`task_id::policy_id` to Braintrust and/or W&B, then export safe run links/IDs.

```bash
# Default (off): writes a null-safe links artifact; no network/SDK needed.
pnpm observe

# Build records + artifact without writing the file.
pnpm observe:dry-run

# Live emit (optional SDKs + credentials):
pip install -r requirements-braintrust.txt -r requirements-wandb.txt
AHE_OBSERVABILITY=both BRAINTRUST_API_KEY=... WANDB_API_KEY=... pnpm observe
```

Env vars (see `.env.example`): `AHE_OBSERVABILITY=off|braintrust|wandb|both`,
`BRAINTRUST_API_KEY`, `BRAINTRUST_PROJECT`, `WANDB_API_KEY`, `WANDB_PROJECT`,
`WANDB_ENTITY`, `WANDB_MODE=online|offline|disabled`. Missing SDKs fail softly
unless `--require` is passed. Exported artifacts never contain secrets or
absolute local paths.

---

## Verification before PR

```bash
pnpm validate:fixtures
pnpm eval:ci
python -m pytest
pnpm typecheck
pnpm build
```

Full contract: [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) and [README.md](README.md) Verification section.

---

## Historical build prompts

Early one-shot prompts (cockpit slice, runner MVP, MCP wiring) live in [docs/CURSOR_PROMPTS.md](docs/CURSOR_PROMPTS.md). They are **archived for reference** — use the backlog in [docs/FINAL_AUDIT.md](docs/FINAL_AUDIT.md) for new work.
