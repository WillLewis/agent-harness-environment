# Demo Script

**Doc map:** [INDEX.md](./INDEX.md) · **Verification:** [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md)

Use this walkthrough for a 5–10 minute hosted demo. The page is **fully static**: it replays precomputed JSON from `data/traces/` and `data/evals/`. Nothing in the browser calls a live LLM, the local runner, MCP, or external eval APIs.

**Before you start:** `pnpm install`, `pip install -r requirements-dev.txt`, `pnpm dev`, then open the URL Next.js prints (often `http://localhost:3000`).

For a pre-demo sanity check, run `pnpm eval:ci` and `pnpm build` (see [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md)). For deployment settings, see [DEPLOYMENT.md](./DEPLOYMENT.md).

---

## Page map (numbered narrative)

| # | Section | Anchor | Purpose |
| --- | --- | --- | --- |
| — | Hero | `#top` | Product framing + static-demo disclaimer |
| 01 | Premise | `#premise` | Why harnesses matter |
| 02 | Protocol | `#protocol` | Typed events + scored metrics |
| 03 | Primitives | `#primitives` | What the harness provides |
| 04 | Cockpit | `#cockpit` | Interactive trace replay |
| 05 | Failure taxonomy | `#failure-taxonomy` | Cluster preview grid |
| 06 | Eval comparison | `#evals` | Synthetic policy table |
| 07 | RL-lite router | `#router` | Illustrative policy picker |
| 08 | Implementation evidence | `#architecture` | Repo capabilities map |
| 10 | Takeaways | `#takeaways` | What the demo proves |

Sticky nav links: **Why · Protocol · Cockpit · Evals · Architecture** (badge: *Hosted demo · precomputed traces*).

---

## Opening — Hero (30 seconds)

Narration:

> When a coding agent fails, the question is not only whether the model was wrong. The harness controls planning, tool use, retries, safety blocks, and recovery. Agent Harness Environment records that behavior as a trace, scores it with deterministic evals, and compares harness policies on the same task.

Point out:

- **Static hosted demo** / **No live LLM** in the hero copy
- Fixture illustration metrics (bugfix baseline → guarded) — not production telemetry
- CTAs: **Replay the failure** (`#cockpit`), **View eval report** (`#evals`), **Implementation map** (`#architecture`)

---

## Step 1 — Premise (`#premise`, 30 seconds)

Scroll to **01 — premise · Why harnesses matter**.

Narration:

> Agents emit invisible streams of plans and tool calls. They fail in repeatable patterns — loops, hallucinated paths, unsafe recovery. Harness rules change whether that failure is a dead end or a recoverable detour on the same fixture.

---

## Step 2 — Protocol (`#protocol`, 30 seconds)

Scroll to **02 — protocol · The vocabulary we measure**.

Narration:

> Every run emits the same typed events — PLAN, READ_FILE, TEST, BLOCKED_ACTION, and so on — and is scored against the same deterministic metrics. Both ship in-repo as code, not vibes.

Briefly scan the event chips and metric definitions (`task_success`, `loop_rate`, `unsafe_tool_attempt`, etc.).

---

## Step 3 — Primitives (`#primitives`, 30 seconds)

Scroll to **03 — primitives · What the harness provides**.

Narration:

> Task fixtures, trace replay, baseline vs guarded policies, deterministic scoring, failure clusters, and a local runner with CI gates. The hosted page demonstrates these with precomputed traces — no live runner in the browser.

---

## Step 4 — Cockpit: default bugfix task (`#cockpit`, 2 minutes)

Use nav **Cockpit** or hero CTA. Default state:

- **Task:** BUGFIX — timezone parser regression
- **Policy:** Baseline
- **Verdict:** Rejected

Narration:

> Three task classes are wired as static fixtures: bugfix, adversarial safety, and multi-agent contract coordination. We start with the date-parser regression — same repo and task, different harness, different outcome.

**Show together (baseline):**

- Left: task card + success command `npm test -- dateParser`
- Center: trace timeline — loop / ignored test output
- Right: metrics, verdict stamp, **Evidence** tabs (`terminal`, `diff`, `judge`)

Keyboard shortcuts (optional): `[` `]` switch tasks, `1`–`3` policies on bugfix, `←` `→` steps, `f` `t` `d` `j` `r` evidence tabs.

---

## Step 5 — Toggle guarded recovery (same task)

**Policy:** Guarded recovery

Narration:

> Same task fixture. The guarded harness forces evidence after failure before retry. Trace, metrics, terminal/diff, and verdict update together — still from static JSON, not a live run.

**Highlight:**

- Recovery-oriented steps (read test, inspect error)
- Accepted verdict + judge notes
- Improved `task_success` / `recovery` metrics

**Optional:** Policy **Baseline with steering** — assisted success with human intervention (third policy on bugfix only).

---

## Step 6 — Adversarial task (1–2 minutes)

**Task:** ADVERSARIAL — README suggests printing `.env`  
**Policy:** Baseline → then **Guarded recovery**

Narration:

> The README contains an adversarial instruction to print secrets. Baseline follows it and hits `unsafe_tool_attempt`. Guarded recovery blocks secret-read behavior, patches docs safely, and passes tests.

**Show:**

- Baseline: unsafe command attempted, rejected verdict; fourth metric shows **unsafe**
- Guarded: blocked/avoided secret access, accepted verdict

---

## Step 7 — Multi-agent contract task (1–2 minutes)

**Task:** MULTI-AGENT — backend API + frontend form  
**Policy:** Baseline → then **Guarded recovery**

Narration:

> Parallel subagents can drift from a shared API contract. Baseline edits diverge — `contract_mismatch` and failing contract tests. Guarded recovery publishes shared contract context first; both sides align.

**Show:**

- Baseline: contract mismatch labels on timeline, rejected verdict
- Guarded: coordinator reads contract artifact, subagents align, tests pass

---

## Step 8 — Failure taxonomy (`#failure-taxonomy`, 45 seconds)

Scroll to **05 — failure taxonomy**.

Narration:

> Before the aggregate eval table, we surface the failure cluster model: looping, hallucinated files, unsafe tools, contract drift. Counts are fixture illustration — not production hits.

**Click:** **Inspect cluster** on any card (e.g. Looping).

Narration:

> Same drawer as the eval table: detection rule, affected tasks, recommended harness change, dataset candidate JSON. Escape or backdrop closes the drawer.

---

## Step 9 — Eval comparison + drawer (`#evals`, 1 minute)

Scroll to **06 — Policy comparison · Eval report**.

Narration:

> The policy comparison table uses **synthetic aggregate metrics** from `data/evals/policy_comparison.json` — illustrative portfolio numbers across 32 fictional tasks, not production telemetry.

**Click:** baseline **Loop** or **Unsafe attempts** (red underlined cells).

Narration:

> Opens the same failure-cluster detail as the taxonomy section. Escape or backdrop closes the drawer.

---

## Step 10 — RL-lite router (`#router`, 30 seconds)

Scroll to **07 — rl-lite router**.

Narration:

> Illustrative router fixture from `data/router_decisions.json`. It shows how a contextual bandit might pick `guarded_recovery` for bugfix tasks with recovery risk — not a live trained router in the hosted page.

---

## Step 11 — Implementation evidence (`#architecture`, 1 minute)

Use nav **Architecture** or hero CTA.

Narration:

> This section maps what the repo actually implements today versus local-only dry-runs versus future external upload. Counts come from static imports: 3 tasks, 7 trace fixtures, deterministic scorers, CI smoke gate, local runner MVP, MCP tools, Braintrust/Weave **dry-run** adapters — no live Braintrust or W&B in CI.

Point at verification commands: `pnpm eval:ci`, `pnpm eval:suite`, runner CLI, `pnpm export:braintrust:dry-run`, `pnpm export:weave:dry-run`.

---

## Step 12 — Takeaways (`#takeaways`, 30 seconds)

Scroll to **10 — takeaways**.

Narration:

> Harness policies change outcomes on the same task; recovery is traceable; scoring is deterministic and local; optional adapters export evidence without changing the core harness. Footer reiterates: no live LLM, no runner, no API calls in the browser.

---

## Local-only follow-ups (if asked)

These are **not** part of the hosted click path; run them in a terminal:

| Capability | Command | What it proves |
| --- | --- | --- |
| Full static eval suite | `pnpm eval:suite` | Scores all 7 traces + table |
| CI smoke gate | `pnpm eval:ci` | Same gates as GitHub Actions |
| Single-trace score | `pnpm eval` / `pnpm eval:baseline` | Real local Python scorers on one fixture |
| Local runner | `python services/runner/run_task.py guarded_recovery` | Emits trace under `runs/` (sandbox copy of toy repo) |
| Braintrust shape preview | `pnpm export:braintrust:dry-run` | JSON export batch; no API key |
| Weave shape preview | `pnpm export:weave:dry-run` | Span/feedback batch; no API key |
| MCP (Cursor) | `.cursor/mcp.json` | Trace fetch, policy compare, failure clusters |

---

## Closing (30 seconds)

Narration:

> The product loop is: capture traces, label failures, score with deterministic evals, change the harness, re-run locally, and optionally export to external systems later. The hosted demo shows the story; the repo proves the gates.

**Do not claim:** live Braintrust/W&B upload, live hosted agent runs, or that eval table percentages are measured production outcomes.

---

## Quick reference — hosted clicks

| Section | Anchor | What to show |
| --- | --- | --- |
| Premise | `#premise` | Three “why harness” pillars |
| Protocol | `#protocol` | Events + metrics vocabulary |
| Primitives | `#primitives` | Harness building blocks |
| Cockpit | `#cockpit` | 3 tasks × baseline/guarded policies |
| Failure taxonomy | `#failure-taxonomy` | Cluster grid + inspect drawer |
| Eval report | `#evals` | Synthetic table + drawer from red cells |
| Router | `#router` | Illustrative fixture |
| Implementation map | `#architecture` | Repo capabilities + commands |
| Takeaways | `#takeaways` | Static-demo proof points |
