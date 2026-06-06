# Release notes — v0.1 (static / demo milestone)

**Milestone:** `v0.1` — reviewer-ready static demo and deterministic eval starter  
**Status:** Documentation package prepared; **no git tag or GitHub Release created by this repo step**  
**Doc map:** [INDEX.md](./INDEX.md)

---

## Summary

Agent Harness Environment **v0.1** is a portfolio-grade **static hosted demo** plus a **deterministic local eval harness**. It shows how harness policy changes agent outcomes on the same coding tasks, scores precomputed traces with Python scorers, and compares policies — without live LLMs in the browser or CI.

This milestone is for **review, demo, and extension** — not production agent hosting, live benchmarking at scale, or eval SaaS integration in CI.

---

## What v0.1 includes

### Hosted demo (static)

| Capability | Detail |
| --- | --- |
| Interactive cockpit | 3 task classes × policies; trace replay, evidence tabs, verdict |
| Eval report table | Synthetic portfolio fixture (`data/evals/policy_comparison.json`) |
| Failure clusters | Drawer from baseline loop / unsafe metrics |
| RL-lite router | Illustrative static fixture — not live routing |
| Implementation evidence | In-repo capability map (`#architecture`) |
| Build | Next.js 14 static prerender; fixtures bundled at build time |

### Deterministic evals (local + CI)

| Capability | Detail |
| --- | --- |
| 10 scorers | `packages/evals/scorers/` + aggregate formula |
| 7 trace fixtures | `data/traces/` with `suite_gates` expectations |
| CI gate | `pnpm eval:ci` — same contract as GitHub Actions |
| Metric drift audit | `pnpm eval:audit` — hosted synthetic vs trace scorers |
| Policy compare CLI | `pnpm compare` |

### Local execution (optional, not in CI)

| Capability | Detail |
| --- | --- |
| Runner | 3 tasks × baseline + guarded_recovery; `pnpm runner:batch` |
| Trace promotion | `scripts/promote_run_trace.py` → `data/trace_candidates/` |
| MCP tools | `tools/mcp_server.py` for Cursor |
| Adapters | Braintrust / Weave dry-run default; **opt-in** `--live` + API key |

### Reviewer / ops tooling

| Command | Purpose |
| --- | --- |
| `pnpm repo:status` | Generated-artifact hygiene |
| `pnpm deploy:check` | Deployment readiness (monorepo, fixtures, no env vars) |
| `pnpm smoke:hosted` | URL-based HTML smoke (no Playwright) |

---

## Demo path (5–10 minutes)

1. `pnpm install` && `pip install -r requirements-dev.txt`
2. `pnpm dev` → use sticky nav or open `#cockpit`, `#evals`, `#architecture`
3. Follow [DEPLOYMENT.md](./DEPLOYMENT.md) manual browser checklist — numbered IA from hero through takeaways; cockpit baseline → guarded recovery; failure taxonomy + eval drawer

**Narration anchor:** same model, same repo, same task — different harness, different outcome. Hosted page is **fixture replay only**.

### Hosted demo UI (post–v0.1 baseline)

After the v0.1 release baseline, the hosted app received a **Lovable-style shell** (design tokens, sticky chapter nav, numbered sections, operational dashboard surfaces). Fixture data, cockpit behavior, eval semantics, and HTML smoke signals are unchanged. See [DESIGN_MIGRATION_LOVABLE.md](./DESIGN_MIGRATION_LOVABLE.md) for slice history and verification.

---

## Local verification (CI contract)

From repo root:

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

**Optional before handoff:**

```bash
pnpm repo:status
pnpm deploy:check
pnpm eval:suite
pnpm build && pnpm preview   # terminal 1
pnpm smoke:hosted:local      # terminal 2
```

Full checklist: [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md)

---

## Deployment guidance

v0.1 does **not** ship deploy workflows or platform secrets.

| Step | Command / doc |
| --- | --- |
| Readiness audit | `pnpm deploy:check` |
| Build | `pnpm build` (monorepo root; requires `data/` + `packages/harness`) |
| Recommended host | **Vercel** (Next.js native) — see [DEPLOYMENT.md](./DEPLOYMENT.md) |
| Post-deploy smoke | `pnpm smoke:hosted -- --url https://your-url` |
| Env vars | **None** for hosted demo |

---

## Known limitations / non-claims

Do **not** claim v0.1 is or does:

| Non-claim | Reality |
| --- | --- |
| Live agents in the browser | Static JSON replay |
| Production eval metrics in hosted table | Synthetic 32-task portfolio fixture |
| Live RL-lite router | Static `router_decisions.json` |
| Benchmark at scale | 7 curated traces / 3 tasks |
| LLM judges gate quality | Not implemented |
| CI runs runner or live export | Deterministic fixtures only |
| Hosted deploy URL in repo | Reviewer configures hosting manually |
| MCP / runner required for demo | Optional local tools |

**Accurate claims:** deterministic scoring on fixtures, static multi-task cockpit, local runner for scripted traces, adapter dry-run JSON, opt-in live export locally.

Risks and backlog detail: [FINAL_AUDIT.md](./FINAL_AUDIT.md)

---

## Next recommended phases

Prioritized from [FINAL_AUDIT.md](./FINAL_AUDIT.md) §12 (updated for post–v0.1 state):

### Near term

| ID | Item | Notes |
| --- | --- | --- |
| P1-5 | Align hosted cockpit metrics with `run_eval` | Reduce dual-surface drift; audit exists (`pnpm eval:audit`) |
| P1-6 | Optional LLM judge interfaces (non-gating) | Env-gated; never sole success signal |
| P1-7 | pip lock / constraints file | Stronger Python reproducibility |
| P2-1 | Deploy workflow (Vercel) | Separate from product logic; settings in DEPLOYMENT.md |
| P2-3 | Deep-link cockpit state | Shareable demo URLs |

### Medium term

| ID | Item |
| --- | --- |
| P2-2 | Expand task/fixture set (10–20+ rows) |
| P2-4 | Playwright or extended smoke in CI (if server bootstrap is acceptable) |
| P2-7 | Functional RL-lite router beyond static fixture |
| P2-8 | Activate `services/trace-store` for local runs |

**Completed since original audit (included in v0.1):** live Braintrust/Weave export (opt-in), runner for all 3 tasks, promote + batch runner, metric drift audit, deployment readiness + HTML smoke.

---

## Reviewer quick links

| Doc | Use |
| --- | --- |
| [README.md](../README.md) | Fast start + v0.1 reviewer path |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Manual browser walkthrough |
| [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md) | Pre-tag / handoff gates |
| [FINAL_AUDIT.md](./FINAL_AUDIT.md) | Risks + backlog |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Host settings + smoke |
| [EVAL_DESIGN.md](./EVAL_DESIGN.md) | Scorers, gates, metric sources |
| [INDEX.md](./INDEX.md) | Full documentation map |

---

## Tagging note (manual)

When maintainers create `v0.1` externally:

1. Confirm [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md) §8 release readiness
2. Record commit SHA in the GitHub Release description
3. Do not commit `.env`, `runs/`, or other generated artifacts
4. Keep live adapter exports opt-in and out of CI
