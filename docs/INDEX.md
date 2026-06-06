# Documentation index

Canonical map for external reviewers, portfolio walkthroughs, and the next coding agent. **Start here** if you are not sure which file to open.

**Repo maturity (2026-06):** Phases through **13a** — static hosted demo (3 tasks), deterministic eval suite + CI, local runner (3 tasks × 2 policies), MCP tools, opt-in Braintrust/Weave live export, trace promotion + batch runner, metric drift audit. See [FINAL_AUDIT.md](./FINAL_AUDIT.md) for risks and backlog (capabilities table there is partially historical; use [README.md](../README.md) for current commands).

---

## Quick paths

| I want to… | Read first | Then run |
| --- | --- | --- |
| **Demo the product in 5–10 min** | [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) | `pnpm dev` → sticky nav or `#cockpit`, `#evals`, `#architecture` |
| **Deploy hosted demo (review)** | [DEPLOYMENT.md](./DEPLOYMENT.md) | `pnpm deploy:check` → `pnpm build` → `pnpm preview` → `pnpm smoke:hosted:local` |
| **Lovable UI migration (complete)** | [DESIGN_MIGRATION_LOVABLE.md](./DESIGN_MIGRATION_LOVABLE.md) | Numbered IA + operational shell; fixtures unchanged |
| **Verify before handoff / PR** | [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md) | `pnpm repo:status`, CI contract in README |
| **v0.1 release package** | [RELEASE_NOTES_v0.1.md](./RELEASE_NOTES_v0.1.md) | Pre-tag checklist §8; [PRE_TAG_AUDIT_v0.1.md](./PRE_TAG_AUDIT_v0.1.md) |
| **Understand evals vs hosted metrics** | [EVAL_DESIGN.md](./EVAL_DESIGN.md) | `pnpm eval:ci`, `python packages/evals/audit_metric_drift.py --format table` |
| **Pick next implementation work** | [FINAL_AUDIT.md](./FINAL_AUDIT.md) §12–14 | One P1/P2 item + matching `.cursor/skills/` |
| **Onboard a Cursor agent** | [START_HERE_CURSOR.md](../START_HERE_CURSOR.md) | `.cursor/rules/architecture.mdc` |

---

## By use case

### Quick demo / reviewer path

| Document | Purpose | When to read | Commands / artifacts |
| --- | --- | --- | --- |
| [README.md](../README.md) | Repo entry, fast start, command cheat sheet | First open; clone setup | `pnpm install`, `pnpm dev`, `pnpm eval:ci` |
| [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) | Click-by-click hosted walkthrough | Before a live demo or video | `data/traces/`, `data/evals/`, `#cockpit` |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Hosted demo deploy settings + smoke | Before Vercel/Netlify setup | `pnpm deploy:check`, `pnpm build`, `pnpm preview` |
| [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md) | Pre-release / portfolio verification | Before tag, PR, or external link | Full CI contract; §8 v0.1 release readiness |
| [RELEASE_NOTES_v0.1.md](./RELEASE_NOTES_v0.1.md) | v0.1 milestone summary | External reviewer handoff | Capabilities, limits, next phases |

### Local verification / evals

| Document | Purpose | When to read | Commands / artifacts |
| --- | --- | --- | --- |
| [EVAL_DESIGN.md](./EVAL_DESIGN.md) | Scorer list, aggregate formula, suite gates, metric sources | Changing scorers, gates, or explaining CI | `pnpm eval:suite`, `pnpm eval:ci`, `packages/evals/suite_gates.py` |
| [FINAL_AUDIT.md](./FINAL_AUDIT.md) §3, §6 | Verification status, eval quality risks | Auditing eval claims | `python -m pytest`, `packages/evals/audit_metric_drift.py` |
| — | Metric drift audit (no separate doc) | When hosted table vs trace scores confuse reviewers | `pnpm eval:audit` |
| — | Repo hygiene (no separate doc) | Before commit; confirm generated paths stay untracked | `pnpm repo:status` |
| — | Fixture truth | Scoring or adding traces | `data/traces/*.json`, `pnpm validate:fixtures` |

### Architecture / product design

| Document | Purpose | When to read | Commands / artifacts |
| --- | --- | --- | --- |
| [.cursor/rules/architecture.mdc](../.cursor/rules/architecture.mdc) | **Current** package boundaries (hosted vs runner vs evals) | Before any feature that crosses surfaces | `apps/web`, `packages/evals`, `services/runner` |
| [PRODUCT_PLAN.md](./PRODUCT_PLAN.md) | Long-range vision, thesis, phased roadmap | **Planning** new product scope; not a literal implementation spec | `data/tasks.json`, `data/policies.json` |
| [UX_PLAN.md](./UX_PLAN.md) | Hosted IA, interaction patterns, progressive disclosure | **Planning** UI changes; most cockpit/eval UX is already built | `apps/web/components/` |
| [DESIGN_MIGRATION_LOVABLE.md](./DESIGN_MIGRATION_LOVABLE.md) | Lovable reference → AHE hosted restyle (complete) | Hosted demo shell/IA context | [harness-inspector.lovable.app](https://harness-inspector.lovable.app) |
| [FINAL_AUDIT.md](./FINAL_AUDIT.md) §5–8 | Architecture, eval, UX, runner risks | Release review or scope negotiation | — |

### Runner / MCP / adapters

| Document | Purpose | When to read | Commands / artifacts |
| --- | --- | --- | --- |
| [README.md](../README.md) § Runner, MCP, adapters | Operational commands for local execution and export | Running or promoting traces | `pnpm runner:batch`, `scripts/promote_run_trace.py` |
| [EVAL_DESIGN.md](./EVAL_DESIGN.md) § Adapters | Braintrust / Weave dry-run vs live | Adapter or export work | `pnpm export:braintrust:*`, `pnpm export:weave:*` |
| [FINAL_AUDIT.md](./FINAL_AUDIT.md) §8 | Runner / MCP / adapter risks | Before claiming “full local product” | `services/runner/`, `tools/mcp_server.py` |
| — | MCP tool surface | Cursor integration | `.cursor/mcp.json`, `tools/mcp_server.py` |

### Next-agent prompts / backlog

| Document | Purpose | When to read | Commands / artifacts |
| --- | --- | --- | --- |
| [START_HERE_CURSOR.md](../START_HERE_CURSOR.md) | **Current** agent onboarding and constraints | First message in a new Cursor session | Links to audit + skills |
| [FINAL_AUDIT.md](./FINAL_AUDIT.md) §12–14 | Prioritized P1/P2 backlog, handoff checklist | Choosing the next vertical slice | — |
| [CURSOR_PROMPTS.md](./CURSOR_PROMPTS.md) | **Historical** one-shot build prompts | Reference only; do not treat as current state | — |
| [.cursor/skills/](../.cursor/skills/) | Task-specific workflows (fixture, scorer, eval, trace analysis) | Implementing eval/runner/fixture changes | `create-task-fixture`, `add-new-scorer`, etc. |

---

## Cursor rules (implementation guardrails)

| Rule | When to read |
| --- | --- |
| [architecture.mdc](../.cursor/rules/architecture.mdc) | Any cross-package change |
| [eval-harness-standards.mdc](../.cursor/rules/eval-harness-standards.mdc) | Scorers, gates, fixtures |
| [trace-schema.mdc](../.cursor/rules/trace-schema.mdc) | Trace events and validation |
| [frontend-dashboard-patterns.mdc](../.cursor/rules/frontend-dashboard-patterns.mdc) | Hosted UI components |
| [safe-terminal-use.mdc](../.cursor/rules/safe-terminal-use.mdc) | Runner commands / allowlist |
| [scorer-quality-bar.mdc](../.cursor/rules/scorer-quality-bar.mdc) | New scorer quality |

---

## Key artifacts (not markdown)

| Path | Role |
| --- | --- |
| `data/traces/*.json` | Curated trace fixtures (7); CI gate input |
| `data/evals/policy_comparison.json` | **Synthetic** hosted eval table — not `eval:ci` output |
| `data/failure_clusters.json` | Failure cluster drawer + MCP |
| `data/tasks.json`, `data/policies.json` | Task/policy catalog |
| `runs/` | Local runner output (gitignored); check with `pnpm repo:status` |
| `data/trace_candidates/` | Promoted runner traces (gitignored) |
| `.github/workflows/ci.yml` | Deterministic CI contract |

---

## Historical / planning docs

These remain useful for context but **do not** describe the repo line-by-line today:

| Document | Status | Notes |
| --- | --- | --- |
| [PRODUCT_PLAN.md](./PRODUCT_PLAN.md) | Planning | Full product vision; many phases are aspirational |
| [UX_PLAN.md](./UX_PLAN.md) | Planning | UX spec; hosted demo implements core flows |
| [CURSOR_PROMPTS.md](./CURSOR_PROMPTS.md) | Historical | Early vertical-slice prompts (cockpit, runner MVP) |
| [FINAL_AUDIT.md](./FINAL_AUDIT.md) | Audit + backlog | §2 limitations partly superseded (runner 3 tasks, live export, promote path exist); §12 backlog still authoritative |

When in doubt: **commands in README** and **gates in `pnpm eval:ci`** beat older narrative in planning docs.
