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
pnpm repo:status
```

**Expect:** all commands exit 0; `pnpm eval:ci` prints `"gates_ok":true`; pytest reports all tests passing (110+ at last green run). `pnpm repo:status` should report `ok=true` and no tracked generated files.

### Local generated artifacts (do not commit)

These paths are **gitignored** and recreated by local tools. They should never appear in `git status` as tracked files:

| Path | Produced by |
| --- | --- |
| `runs/` | `services/runner/`, `pnpm runner:batch` |
| `data/trace_candidates/` | `scripts/promote_run_trace.py`, `pnpm runner:batch:promote` |
| `data/datasets/generated_candidates.jsonl` | MCP `promote_trace_to_dataset` or promote script |
| `apps/web/.next/` | `pnpm dev` / `pnpm build` |
| `**/*.tsbuildinfo`, `__pycache__/`, `.pytest_cache/` | TypeScript / Python tooling |

Before handoff, run `pnpm repo:status` (read-only; does not delete files). If generated files were ever committed, remove from the index with `git rm --cached <path>` — do not use `git clean` on a developer checkout.

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

**Deployment review (optional):** [DEPLOYMENT.md](./DEPLOYMENT.md) — run `pnpm deploy:check`, `pnpm build`, and `pnpm preview` locally before connecting a host. No platform secrets or deploy workflows are included in this repo.

---

## 4. Local-only and dry-run capabilities

These work in a developer checkout but are **not** required for CI or the hosted page:

| Capability | Location | Notes |
| --- | --- | --- |
| Local runner | `services/runner/run_task.py`, `pnpm runner:batch` | Writes traces under `runs/` (gitignored) |
| Trace promotion | `scripts/promote_run_trace.py` | Optional `data/trace_candidates/` (gitignored) |
| MCP tools | `tools/mcp_server.py` | Cursor integration; trace/eval helpers |
| Eval suite report | `pnpm eval:suite` | Human-readable table + JSON |
| Metric drift audit | `pnpm eval:audit` | Hosted synthetic vs trace scorer report |
| Repo hygiene check | `pnpm repo:status` | Lists local generated artifacts; flags accidental tracking |
| Braintrust adapter | `pnpm export:braintrust:dry-run` / `:live` | Dry-run default; live opt-in + API key |
| Weave adapter | `pnpm export:weave:dry-run` / `:live` | Dry-run default; live opt-in + API key |
| Real per-trace scoring | `pnpm eval`, `run_eval.py` | Deterministic Python scorers on fixtures |

**Adapter dry-run vs live:** dry-run prints JSON with no network. Live upload is opt-in (`:live` + SDK + API key) and is **not** part of CI.

**Synthetic metrics vs real local scoring:**

- **Hosted eval table** — portfolio-level synthetic percentages for demo narrative.
- **`pnpm eval` / `pnpm eval:ci`** — real scorer output on static trace fixtures (deterministic, reproducible).

---

## 5. Intentionally out of scope (this release)

Do not expect or promise:

- Live Braintrust or W&B Weave upload **in CI** (opt-in locally only)
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
| [RELEASE_NOTES_v0.1.md](./RELEASE_NOTES_v0.1.md) | v0.1 milestone handoff |
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

---

## 8. v0.1 release readiness (pre-tag)

Use before creating git tag `v0.1` or a GitHub Release **manually**. This repo does not create tags or releases automatically.

Release notes: [RELEASE_NOTES_v0.1.md](./RELEASE_NOTES_v0.1.md)

| Check | How to verify | Expect |
| --- | --- | --- |
| CI green | GitHub Actions on target commit | All deterministic-gates steps pass |
| Local CI contract | §1 commands | Exit 0; `gates_ok: true` |
| Hosted smoke | `pnpm preview` then `pnpm smoke:hosted:local` | `ok=True`; 11/11 HTML checks |
| Repo hygiene | `pnpm repo:status` | `ok=true`; no tracked generated files |
| Deploy readiness | `pnpm deploy:check` | `ok=True`; no required env vars |
| No generated artifacts staged | `git status --short` | No `runs/`, `.next/`, `trace_candidates/`, `generated_candidates.jsonl` |
| No secrets / env files | `git status --short` | No `.env`, `.env.local`, or credential files staged |
| Live adapters opt-in only | Read `package.json` + CI | `export:*:live` not in `.github/workflows/ci.yml` |
| Claims grounded | [RELEASE_NOTES_v0.1.md](./RELEASE_NOTES_v0.1.md) § limitations | No live-agent / production-metrics overclaim |

**Record at tag time:** commit SHA, date, and pointer to `RELEASE_NOTES_v0.1.md` in the GitHub Release body.
