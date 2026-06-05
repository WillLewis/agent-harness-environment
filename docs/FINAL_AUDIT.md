# Final Release Audit

**Audit date:** 2026-06-05  
**Scope:** Agent Harness Environment starter repo at release handoff (Phases 0–9a complete).  
**Method:** Static review of `data/`, `packages/evals/`, `apps/web/`, `services/runner/`, `tools/`, `.github/workflows/ci.yml`, and handoff docs. No product code changed for this document.

---

## 1. Executive summary

The repo is **ready for external demo and portfolio review** as a **static, deterministic harness evaluation starter**. It credibly demonstrates trace replay, policy comparison, failure clustering, local scoring, CI gates, a minimal local runner, MCP helpers, and export **shape** previews for Braintrust/W&B.

It is **not** a production agent platform, live eval SaaS integration, or statistically valid benchmark at scale. Documentation and the hosted UI now state those limits explicitly ([DEMO_SCRIPT.md](./DEMO_SCRIPT.md), [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md)).

**Release blocker count (P0):** **0** — assuming CI stays green on `main`.

---

## 2. Implemented capabilities (current state)

| Area | What works | Primary paths |
| --- | --- | --- |
| **Hosted demo** | 3 task classes × baseline/guarded (+ assisted on bugfix); cockpit, eval table, router fixture, implementation evidence | `apps/web/`, `data/traces/` (7 fixtures) |
| **Trace schema** | `AgentTraceEvent` types, fixture validation | `packages/harness/`, `packages/evals/fixture_validation.py` |
| **Scorers** | 10 scorers; `run_eval` aggregate formula; per-trace JSON output | `packages/evals/scorers/`, `run_eval.py` |
| **Eval suite + CI** | All traces scored; `suite_gates` expectations; GitHub Actions mirror local contract | `run_suite.py`, `suite_gates.py`, `.github/workflows/ci.yml` |
| **Policy compare** | CLI + MCP; synthetic hosted table | `policy_compare.py`, `data/evals/policy_comparison.json` |
| **Failure clusters** | 5+ clusters; drawer in hosted UI; MCP lookup | `data/failure_clusters.json` |
| **Local runner** | Deterministic plans for **date-parser only**; sandbox copy; allowlist via `command_rules` | `services/runner/` |
| **MCP** | list traces, get_trace, compare, run_eval, failure cluster, promote dataset, router fixture | `tools/mcp_server.py`, `tools/mcp_helpers.py` |
| **Adapters** | Braintrust + Weave **dry-run** only | `packages/evals/adapters/` |
| **Cursor workflow** | Rules, 4 skills, MCP config, BUGBOT guidance | `.cursor/` |
| **Docs** | Product, UX, eval design, demo script, release checklist | `docs/` |

**Counts (static):** 3 tasks in `data/tasks.json`, 7 trace fixtures, 3 coding-task dataset rows in `coding_tasks.jsonl`, 87+ pytest tests at last green run.

---

## 3. Verification status

### Commands (local = CI contract)

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

### Expected results

| Check | Pass criterion |
| --- | --- |
| `validate:fixtures` | Zero validation errors on all `data/traces/*.json` |
| `eval:ci` | `gates_ok: true`, exit 0 |
| `pytest` | All tests pass (evals, runner, MCP helpers, adapters, suite) |
| `typecheck` / `build` | Next.js static build succeeds |

### Not run in CI

- `pnpm eval:suite` (redundant with `eval:ci` for gates; human-readable table)
- `pnpm export:braintrust:dry-run` / `pnpm export:weave:dry-run`
- Local runner execution
- MCP server integration tests against live Cursor host

**Recommendation:** Run the full block once on a clean clone before any public link; record commit SHA in release notes.

---

## 4. Known limitations and non-claims

Do **not** state or imply:

| Claim | Reality |
| --- | --- |
| Hosted page runs live agents | Replays JSON only |
| Eval table % are measured outcomes | Synthetic `policy_comparison.json` (32 fictional tasks) |
| RL-lite router trains or routes live | Static `router_decisions.json` + hosted copy |
| Braintrust/W&B export works with API key | Returns `live_export_not_implemented` / `not_configured` |
| Runner covers all 3 demo tasks | Hardcoded `bugfix_date_parser_001` only |
| MCP promotes to production dataset | Appends to `data/datasets/generated_candidates.jsonl` locally |
| LLM judges gate quality | Not implemented |
| Hosted deploy URL | No deployment workflow in repo |

**Accurate claims:** deterministic local scoring on fixtures, CI smoke gate, static multi-task cockpit, local runner MVP for one task, adapter dry-run JSON.

---

## 5. Architecture risks

| Risk | Severity | Notes |
| --- | --- | --- |
| **Dual surfaces drift** | Medium | Hosted metrics (`cockpitFixtures.ts` static eval numbers) can diverge from Python scorers if fixtures update without updating TS maps. |
| **Runner vs eval split** | Medium | Runner emits traces under `runs/`; hosted uses `data/traces/`. No automated promote path from run → fixture. |
| **Policy catalog mismatch** | Low | `data/policies.json` lists 5 policies; cockpit uses 3 (+ steering). Eval table shows 5; runner knows 2 plans. |
| **Trace store** | Low | `services/trace-store` starter exists but is not on critical path for demo or CI. |
| **Monorepo path hacks** | Low | Python `sys.path` inserts in scripts/runner/MCP — works in CI but fragile for packaging as installable libs. |
| **No versioned package publish** | Low | Root is app + scripts, not published `@ahe/*` wheels beyond internal web package. |

---

## 6. Eval quality risks

| Risk | Severity | Notes |
| --- | --- | --- |
| **`contract_consistency` excluded from aggregate** | Low | Scorer runs in `run_eval` but not in `aggregate()` — intentional to avoid shifting date-parser headline metric; can confuse readers of full JSON. |
| **Heuristic scorers** | Medium | `loop_score`, `recovery_score`, `patch_minimality` are trace-pattern heuristics, not ground truth. |
| **Gate expectations keyed by filename** | Medium | `FIXTURE_EXPECTATIONS` in `suite_gates.py` must be updated for every new trace stem — easy to forget. |
| **Small fixture set** | High (for science) | 7 traces / 3 tasks — fine for demo, insufficient for benchmark claims. |
| **No LLM judge interface** | Low | Documented as future in `EVAL_DESIGN.md`; do not use subjective quality as release gate. |
| **Assisted trace policy** | Low | Only on bugfix; gates include separate assisted aggregate threshold. |

---

## 7. Hosted UX risks

| Risk | Severity | Notes |
| --- | --- | --- |
| **Synthetic vs real metrics confusion** | Medium | Mitigated in copy; reviewers may still conflate table with cockpit metrics. |
| **Mobile timeline length** | Low | Scroll region added (Phase 8c); long traces still require scrolling. |
| **Eval table horizontal scroll** | Low | Expected on narrow viewports; hint text present. |
| **No deep-link per task/policy** | Low | URL hash only to sections, not shareable cockpit state. |
| **Keyboard shortcuts undocumented in UI** | Low | Documented in cockpit sidebar only. |

---

## 8. Runner / MCP / adapter risks

| Risk | Severity | Notes |
| --- | --- | --- |
| **Runner single-task** | High for “full local product” story | `TASK_ID = bugfix_date_parser_001` in `task_runner.py`. |
| **Runner plans are scripted** | Medium | Not LLM-driven; good for determinism, limits “real agent” narrative. |
| **Sandbox mutates only copy** | Low | Correct design; `runs/sandboxes/` gitignored. |
| **MCP not in CI** | Low | Covered by `tools/tests/test_mcp_helpers.py` unit tests. |
| **MCP verbose trace size** | Low | `get_trace(verbose=True)` can be large; compact default is safe. |
| **Adapter live export** | N/A | Explicitly unimplemented — risk is **expectation management**, not runtime failure. |
| **Optional SDK confusion** | Low | Neither `braintrust` nor `weave` in `requirements-dev.txt` — correct for zero-dep CI. |

---

## 9. Security and safety considerations

| Topic | Status |
| --- | --- |
| **Hosted attack surface** | Static site; no server routes; no user input persisted. |
| **Secrets in repo** | `.env` not in toy repos as real secrets; adversarial task demonstrates blocked `cat .env`. |
| **Runner command execution** | Subprocess, no shell; allowlist in `command_rules` shared with eval scorer. |
| **MCP file access** | Reads project files only; promote writes JSONL under `data/datasets/`. |
| **Dependency audit** | No automated `pnpm audit` / `pip audit` in CI — manual periodic review advised. |
| **CI tokens** | Standard GitHub Actions checkout only; no deploy secrets required. |

**Paper cut:** Adversarial README in `toy_repos/docs_site` intentionally suggests unsafe commands — fine for demo, warn anyone running runner against untrusted repos without sandbox review.

---

## 10. Dependency and CI considerations

| Item | Detail |
| --- | --- |
| **Node** | 22.x in CI; pnpm 9.15.0 via `packageManager` |
| **Python** | 3.12 in CI; dev deps: pytest, mcp, pyyaml, pydantic |
| **Next.js** | 14.x; static prerender |
| **Caches** | pnpm + pip caches in workflow — low risk |
| **No lockfile for pip** | Only `requirements-dev.txt` pins loosely (`mcp`, `pytest`, etc.) — reproducibility slightly weaker than npm |
| **No Playwright/visual CI** | Visual QA is manual (Phase 8c) |
| **No deployment job** | Build artifact not published to hosting |

---

## 11. Paper cuts (non-blocking)

- `baseline_with_steering` missing from `data/policies.json` — cockpit uses hardcoded label in `cockpitFixtures.ts`.
- Failure cluster `affectedTasks` references tasks not in `data/tasks.json` (e.g. `api_validation_error_003`) — narrative-only.
- `services/runner` README absent at service root — discoverability via main README only.
- `pnpm eval:suite` not in CI (optional redundancy).
- Aggregate formula weights undocumented on hosted UI (only in `EVAL_DESIGN.md`).
- `contract_consistency` in scorer list but not aggregate — document when adding multi-agent traces to headline metrics.

---

## 12. Prioritized backlog

### P0 — Release blockers

*None identified* if verification commands pass on target commit.

| ID | Item | Action |
| --- | --- | --- |
| — | — | Ship when CI green; tag or document commit SHA in handoff |

---

### P1 — High-value next implementation

| ID | Item | Rationale | Suggested acceptance |
| --- | --- | --- | --- |
| P1-1 | **Live Braintrust export (opt-in)** | Completes adapter boundary started in Phase 7a | Upload behind env + SDK; CI stays dry-run only |
| P1-2 | **Live Weave export (opt-in)** | Same for observability story | Same pattern as P1-1 |
| P1-3 | **Generalize local runner to 3 tasks** | Closes runner vs hosted gap | `run_task.py <policy> <task_id>` for all tasks in `tasks.json` |
| P1-4 | **Promote run → fixture workflow** | Connects local execution to eval suite | CLI or MCP: validate + copy trace into `data/traces/` with review step |
| P1-5 | **Align hosted cockpit metrics with `run_eval`** | Reduces dual-surface drift | Generate or sync metric summary from Python in build script, or document single source |
| P1-6 | **Optional LLM judge interfaces (non-gating)** | Product plan gap | Stub scorer + skipped-by-default CI; never sole success signal |
| P1-7 | **pip lock / constraints file** | Reproducible CI Python deps | `requirements-dev.txt` + lock or upper pins |

---

### P2 — Polish and future integrations

| ID | Item | Notes |
| --- | --- | --- |
| P2-1 | Deploy hosted demo (Vercel/静态) | Add workflow; separate from product logic |
| P2-2 | Expand to 20–50 tasks + generated failure clusters | PRODUCT_PLAN Phase 8 scale |
| P2-3 | Deep-link cockpit state (`?task=&policy=&step=`) | Shareable demos |
| P2-4 | Playwright smoke in CI | Catch layout regressions |
| P2-5 | `pnpm audit` / Dependabot | Supply chain hygiene |
| P2-6 | Wire `contract_consistency` into aggregate for multi-agent-only views | UX clarity |
| P2-7 | Functional RL-lite router (bandit update loop) | Beyond static fixture |
| P2-8 | Trace-store SQLite path for local runs | `services/trace-store` activation |
| P2-9 | Hallucination demo trace + hosted policy | Only 3 tasks today; cluster exists without trace |
| P2-10 | Add `baseline_with_steering` to `policies.json` | Catalog consistency |

---

## 13. Recommended next 3 implementation phases

These follow naturally after the current release handoff and preserve architecture boundaries (static hosted default, local deterministic gates, optional external adapters).

### Phase A — External export (opt-in, non-blocking CI)

**Goal:** Implement live Braintrust and Weave upload behind configuration, keeping `pnpm eval:ci` and hosted demo unchanged.

**Deliverables:**
- `export_to_braintrust(..., dry_run=False)` with SDK + `BRAINTRUST_API_KEY`
- `export_to_weave(..., dry_run=False)` with SDK + `WANDB_API_KEY`
- Integration tests mocked; CI continues dry-run only
- `docs/EVAL_DESIGN.md` section on env vars and failure modes

**Exit criteria:** Dry-run still default; live export documented; external failure does not break local dev.

---

### Phase B — Local execution loop (runner + promote)

**Goal:** Make “run locally → score → optionally promote to fixture” real for all three task classes.

**Deliverables:**
- Runner plans for `adversarial_env_001` and `multi_agent_contract_001` (deterministic scripts)
- CLI: `run_task.py <policy> <task_id>`
- Promote command: validate trace, write to `data/traces/` or `runs/` with human-readable diff summary
- MCP tool alias for promote
- Suite gates updated when new stems added

**Exit criteria:** One command produces a valid trace for each task; `pnpm eval:ci` passes after intentional fixture updates.

---

### Phase C — Eval scale and optional judges

**Goal:** Grow eval credibility without breaking the static demo contract.

**Deliverables:**
- 10–20 additional `coding_tasks.jsonl` rows (can be fictional but structurally valid)
- Script or skill to generate failure-cluster candidates from scored traces
- Optional `plan_quality` / `groundedness` LLM judge scorers (off by default; env-gated)
- Hosted eval table: either per-task-class breakdown or clear “synthetic portfolio” labeling retained

**Exit criteria:** Policy comparison reflects multiple task classes; docs state N fixtures; no claim of production benchmark.

---

## 14. Handoff checklist for next agent

1. Read [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md) and run verification commands.
2. Walk [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) once in browser.
3. Pick **one P1 item**; do not expand scope to hosted live agents or CI secrets for adapters without explicit ask.
4. Preserve: `data/traces/` verdicts unless intentionally updating story + `suite_gates.py`.
5. Add tests for any new scorer, gate stem, or runner task.

---

## 15. Document index

| Document | Use |
| --- | --- |
| [README.md](../README.md) | Entry point |
| [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) | Hosted click path |
| [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md) | Pre-ship gates |
| [EVAL_DESIGN.md](./EVAL_DESIGN.md) | Scorers and CI contract |
| [PRODUCT_PLAN.md](./PRODUCT_PLAN.md) | Long-range vision |
| **This file** | Audit + backlog |
