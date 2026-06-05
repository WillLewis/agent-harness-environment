# Release Checklist

**Doc map:** [INDEX.md](./INDEX.md) · **Audit + backlog:** [FINAL_AUDIT.md](./FINAL_AUDIT.md)

Use this before tagging a release, opening a portfolio PR, or handing the repo to an external reviewer.

---

## 1. Local verification (required)

From repo root, after `pnpm install` and `pip install -r requirements-dev.txt`:

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

Optional but recommended for demos:

```bash
pnpm eval:suite
pnpm export:braintrust:dry-run
pnpm export:weave:dry-run
```

**Expect:** all commands exit 0; `pnpm eval:ci` prints `"gates_ok":true`; pytest reports all tests passing (110+ at last green run).

---

## 2. CI gate expectations

GitHub Actions (`.github/workflows/ci.yml`) runs the same deterministic contract as above on every `push` and `pull_request`.

| Step | Purpose |
| --- | --- |
| `pnpm validate:fixtures` | Trace shape + verdict consistency |
| `pnpm eval:ci` | Full static suite + `suite_gates` expectations |
| `pnpm eval:baseline` / `pnpm eval` | Smoke single-trace scoring |
| `pnpm compare` | Policy comparison fixture loads |
| `python -m pytest` | Evals, runner, MCP helpers, adapters |
| `pnpm typecheck` | Web app types (no prior build required) |
| `pnpm build` | Static Next.js export builds |

**CI does not:** install Braintrust/W&B SDKs, call live LLMs, run the local runner against toy repos, or deploy the hosted app.

---

## 3. Hosted static-demo constraints

Tell reviewers explicitly:

| Claim | Accurate? |
| --- | --- |
| Cockpit replays precomputed traces | Yes — `data/traces/*.json` imported at build time |
| Task/policy toggle updates UI together | Yes — client-side only |
| Eval table shows real production metrics | **No** — synthetic fixture (`data/evals/policy_comparison.json`) |
| RL-lite router is live | **No** — illustrative fixture (`data/router_decisions.json`) |
| Hosted page runs agents | **No** |
| Implementation evidence counts | Yes — derived from static imports (3 tasks, 7 traces) |

**Run hosted demo locally:**

```bash
pnpm dev
# Open printed URL → #cockpit for cockpit, #evals for eval table, #architecture for evidence
```

Walkthrough: [DEMO_SCRIPT.md](./DEMO_SCRIPT.md).

---

## 4. Local-only and dry-run capabilities

These work in a developer checkout but are **not** required for CI or the hosted page:

| Capability | Location | Notes |
| --- | --- | --- |
| Local runner MVP | `services/runner/run_task.py` | Copies toy repo to `runs/sandboxes/`; writes trace JSON |
| MCP tools | `tools/mcp_server.py` | Cursor integration; trace/eval helpers |
| Eval suite report | `pnpm eval:suite` | Human-readable table + JSON |
| Braintrust adapter dry-run | `pnpm export:braintrust:dry-run` | No `BRAINTRUST_API_KEY` needed |
| Weave adapter dry-run | `pnpm export:weave:dry-run` | No `WANDB_API_KEY` needed |
| Real per-trace scoring | `pnpm eval`, `run_eval.py` | Deterministic Python scorers on fixtures |

**Adapter dry-run vs external integration:** dry-run prints JSON describing what *would* be exported. Live upload returns `not_configured` or `live_export_not_implemented` — intentionally not shipped yet.

**Synthetic metrics vs real local scoring:**

- **Hosted eval table** — portfolio-level synthetic percentages for demo narrative.
- **`pnpm eval` / `pnpm eval:ci`** — real scorer output on static trace fixtures (deterministic, reproducible).

---

## 5. Intentionally out of scope (this release)

Do not expect or promise:

- Live Braintrust or W&B Weave upload
- GitHub deployment workflow / hosted URL provisioning
- Live LLM judges as gate criteria
- Production trace ingestion
- Multi-tenant backend or auth
- Automatic fixture generation from live runs in CI
- Hosted demo calling the local runner or MCP

---

## 6. Documentation handoff

| Doc | Audience |
| --- | --- |
| [README.md](../README.md) | Quick start + demo handoff links |
| [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) | Click-by-click hosted walkthrough |
| [EVAL_DESIGN.md](./EVAL_DESIGN.md) | Scorers, suite gates, adapters |
| [PRODUCT_PLAN.md](./PRODUCT_PLAN.md) | Product thesis and phased plan |
| [UX_PLAN.md](./UX_PLAN.md) | Cockpit and eval UX intent |

---

## 7. Pre-handoff smoke (reviewer-facing)

A reviewer with no context should be able to:

1. `pnpm install && pip install -r requirements-dev.txt`
2. `pnpm dev` → click through 3 cockpit tasks and 2 policies each
3. Open eval drawer from baseline loop/unsafe cells
4. Read implementation evidence section
5. Run `pnpm eval:ci` and see green locally
6. Understand that external eval SaaS is **adapter scaffolding only**

If any step fails, fix gates before handoff — do not patch docs to hide failures.
