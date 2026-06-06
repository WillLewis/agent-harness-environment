# Design migration plan — Lovable reference → AHE hosted app

**Status:** Plan only (no implementation in this phase)  
**Reference:** [harness-inspector.lovable.app](https://harness-inspector.lovable.app)  
**Target:** `apps/web` static hosted demo  
**Constraint:** Preserve data model, interactions, and static/local-only claims

**Related:** [UX_PLAN.md](./UX_PLAN.md) · [DEPLOYMENT.md](./DEPLOYMENT.md) · [DEMO_SCRIPT.md](./DEMO_SCRIPT.md)

---

## Executive summary

Migrate the hosted AHE app from its current single-page layout to the **Lovable reference’s design language and narrative pacing** — sticky chapter nav, numbered sections, tighter visual system, and clearer progressive disclosure — while **keeping all fixture-driven behavior** (`cockpitFixtures.ts`, `evalFixtures.ts`, keyboard shortcuts, failure-cluster drawer, smoke-check anchors).

**Do not port Lovable copy literally** where it overclaims (24 tasks, live runner implied, fictional hero deltas as production). **Do port** structure, typography rhythm, surface treatment, and section order.

---

## 1. Visual system migration

### 1.1 Palette / tokens

| Token | Current AHE | Lovable reference (observed) | Migration target |
| --- | --- | --- | --- |
| Page background | `#070a0f` body | Near-black, cool gray-blue | `--color-bg-page` (~`#06080d`–`#0a0e14`) |
| Surface / card | `bg-white/[0.03]`, `border-white/10` | Slightly elevated panels, subtle border | `--color-surface`, `--color-surface-raised`, `--color-border-subtle` |
| Accent | Cyan (`cyan-300`, `cyan-200/80`) | Teal/cyan accent on CTAs and labels | Keep cyan family; add `--color-accent`, `--color-accent-muted` |
| Text primary | `text-white`, `text-slate-300` | High-contrast headings, muted body | `--color-text`, `--color-text-muted`, `--color-text-faint` |
| Semantic | emerald/amber/red in badges | Red cells in eval table, severity chips | Map to `--color-success`, `--color-warning`, `--color-danger` |
| Code bg | `bg-black/40` in hero pre | Inline `code` chips + dark panels | `--color-code-bg`, `--color-code-border` |

**Implementation:** Add CSS variables in `globals.css`; extend `tailwind.config.ts` `theme.extend.colors` to reference vars. No runtime theme switch.

### 1.2 Typography

| Role | Current | Lovable | Target |
| --- | --- | --- | --- |
| Display / H1 | `text-4xl`–`7xl font-black` | Large, tight headline | Keep scale; add `tracking-tight` consistently |
| Section H2 | `text-3xl font-semibold` | Chapter titles with number prefix | `text-2xl`–`3xl` + optional `font-semibold` |
| Chapter label | `text-xs uppercase tracking-[0.3em] text-cyan-200/80` | `01 — premise` mono labels | Standardize as `.section-label` component |
| Body | `text-sm`–`base leading-7` | Shorter paragraphs, more scan-friendly | `text-sm`/`text-base` with `leading-relaxed` |
| Mono / protocol | `font-mono text-xs` on metrics | Backtick event names in vocabulary | `.font-mono` for events, metrics, paths |

**Fonts:** Keep Inter + JetBrains Mono (already aligned). Optionally load via `next/font` for consistency.

### 1.3 Borders / radii

| Element | Current | Target |
| --- | --- | --- |
| Cards | `rounded-3xl` | `rounded-2xl` outer, `rounded-xl` inner (Lovable slightly tighter) |
| Buttons | `rounded-full` pills | Primary pill; secondary `rounded-lg` or outline pill |
| Tables | inside `rounded-3xl` container | Same; add row hover `bg-white/[0.02]` |
| Drawer | right sheet | Keep; match border `border-l border-white/10` |

### 1.4 Cards / surfaces

Introduce shared primitives (new `components/ui/` or local helpers):

- `SectionShell` — max-width container + vertical rhythm (`py-20`/`py-24`)
- `SurfaceCard` — border + subtle bg + optional header slot
- `StatTile` — implementation evidence / hero stat blocks
- `Chip` — event/metric vocabulary pills (`PLAN`, `task_success`)

Reduce one-off `bg-white/[0.03]` repetition; centralize in tokens.

### 1.5 Buttons / links

| Type | Current | Lovable | Target |
| --- | --- | --- | --- |
| Primary CTA | `bg-cyan-300 text-slate-950 rounded-full` | Similar solid accent | Keep; ensure contrast ≥ 4.5:1 |
| Secondary | `border border-white/15` | Ghost / outline | Unify secondary style |
| Nav links | hash anchors in hero only | sticky nav hash links | New `SiteNav` component |
| In-table | cyan underline buttons | red/metric click affordance | Keep clickable cells; add subtle red tint for “bad” metrics |

Preserve `.focus-ring` and skip-link in `layout.tsx`.

### 1.6 Code blocks

| Use | Current | Target |
| --- | --- | --- |
| Hero trace story | large `<pre class="code-panel">` | Lovable uses metric comparison cards | **Option A:** keep pre block but restyle; **Option B:** add hero stat comparison using **static** bugfix baseline vs guarded metrics from fixtures (not Lovable’s 42%/78% fiction) |
| Cursor artifacts | pre in ImplementationEvidence | fenced blocks with filename headers | Add file tab header (`// .cursor/rules/...`) |
| Drawer dataset JSON | pre wrap | same with `rounded-lg border` |

---

## 2. Page IA migration

### 2.1 Target section map

Map Lovable chapters → AHE content (preserve smoke anchors):

| # | Lovable section | AHE source | DOM anchor (keep for smoke) |
| --- | --- | --- | --- |
| — | **Sticky nav** | new `SiteNav` | links to `#premise`, `#cockpit`, `#evals`, `#architecture` |
| — | **Hero** | `page.tsx` hero | retain `#cockpit`, `#evals`, `#architecture` CTAs + **keep** “Static hosted demo” / “No live LLM” copy |
| 01 | Why Harnesses Matter | expand current premise | `id="premise"` (new; optional smoke add later) |
| 02 | Protocol / vocabulary | split protocol cards → events + metrics columns | `id="protocol"` |
| 03 | Harness primitives | **new** static copy (planner, gateway, recovery, judge, router) | `id="primitives"` |
| 04 | Cockpit | `Cockpit.tsx` | **`id="cockpit"`** + “Interactive cockpit” heading |
| 05 | Eval report | `EvalTable.tsx` | **`id="evals"`** + “Policy comparison” |
| 06 | Failure taxonomy | **new** grid from `failure_clusters.json` | `id="failure-taxonomy"`; links open same drawer |
| 07 | RL-lite router | move from `page.tsx` inline block | `id="router"`; keep static fixture disclaimer |
| 08 | Repo evidence | split from `ImplementationEvidence` | `id="repo-evidence"` (cursor rules, MCP, commands) |
| 09 | Architecture | system map + diagram | **`id="architecture"`** + “Implementation evidence” |
| 10 | Takeaways | **new** footer bullets + static disclaimer | `id="takeaways"` |

### 2.2 Sticky nav

```
[ AHE logo/wordmark ]  Why · Protocol · Cockpit · Evals · Architecture     Hosted demo · precomputed traces
```

- `position: sticky; top: 0; backdrop-blur; border-b`
- Mobile: horizontal scroll or collapsible menu
- Include skip-link behavior unchanged

### 2.3 Hero changes

- Keep headline: “A flight recorder for coding agents.”
- Keep tagline: “Same model. Same repo…”
- **Add** Lovable-style hero metrics row using **AHE static data** (e.g. bugfix baseline vs guarded from `cockpitFixtures` staticEval) — labeled “fixture illustration”
- Right column: either restyled trace pre **or** metric comparison cards (preferred for Lovable parity)
- CTAs: “Replay the failure” → `#cockpit`; “View eval report” → `#evals`; third → `#architecture` or GitHub repo link

### 2.4 Sections to add (static copy only)

| Section | Content source | Overclaim guard |
| --- | --- | --- |
| Primitives | `UX_PLAN.md` + `packages/harness` names | “Conceptual primitives demonstrated by traces” |
| Failure taxonomy | `data/failure_clusters.json` | Counts from fixture metadata; not production hits |
| Takeaways | product narrative from README | Repeat static-demo footer |

### 2.5 Sections to reorder

Current order: Hero → Premise → Cockpit → Evals → Router → ImplementationEvidence  

Target order: Hero → Premise → Protocol → Primitives → Cockpit → Evals → Failure taxonomy → Router → Repo evidence → Architecture → Takeaways

**Smoke impact:** `id="cockpit"`, `id="evals"`, `id="architecture"` and strings `Interactive cockpit`, `Policy comparison`, `Implementation evidence` must remain in SSR HTML (move with components, do not rename without updating `scripts/smoke_hosted_demo.py`).

---

## 3. Component migration

### 3.1 Cockpit (`Cockpit.tsx`)

| Area | Current | Lovable target | Behavior unchanged |
| --- | --- | --- | --- |
| Layout | 3-column grid | Similar: task/policy left, timeline center, metrics+evidence right | task/policy state, keyboard shortcuts |
| Section header | “Interactive cockpit” | “04 — cockpit” + subtitle about replay | copy can add chapter label; **keep** “Interactive cockpit” substring for smoke |
| Task selector | vertical list, BUGFIX/ADVERSARIAL labels | card-style task row | same `cockpitTaskOrder`, `selectTask` |
| Policy selector | 2–3 policies per task | vertical policy cards with descriptions | same `policyOrder`; show unavailable policies as disabled/not listed (not Lovable’s 5-policy fiction on every task) |
| Timeline | `TraceTimeline` step list | numbered events with type badges | same `activeStep`, `selectStep` |
| Controls | prev/next step | optional **Reset** button (reset to step 1 / default policy) — cosmetic only | no autoplay unless explicitly scoped later |
| Evidence | `EvidencePanel` tabs | Files / Term / Diff / Judge tabs | same tab state + keyboard `f/t/d/j` |
| Metrics | `MetricCard` grid | compact stat row under timeline | same `run.metrics` from fixtures |
| Verdict | `VerdictStamp` | integrated stamp | same verdict strings |

**Do not add** Lovable “Press play” autoplay in v1 unless it only advances precomputed steps without new data.

### 3.2 TraceTimeline (`TraceTimeline.tsx`)

- Event row: step number + action chip (`TEST_FAIL`) + label + optional file path
- Active step: left border accent (cyan) + raised bg
- Failure labels: small badge on relevant steps
- Preserve `role="list"`, `aria-label`, focusable step buttons

### 3.3 EvidencePanel (`EvidencePanel.tsx`)

- Tab bar: pill tabs matching Lovable (Files, Term, Diff, Judge)
- File tree: monospace paths from `known_files` / trace events
- Terminal/diff/judge panels: `SurfaceCard` + `code-panel` styling
- Keep `role="tablist"` / `aria-selected`

### 3.4 EvalTable (`EvalTable.tsx`)

- Header: “05 — eval report” + **keep** “Policy comparison” + synthetic disclaimer
- Table: tighter row height; baseline loop/unsafe cells stay clickable
- Column headers: align with Lovable naming where cosmetic (`unsafe shell` vs `unsafeAttempts` display label only)
- Footer note: “32 synthetic coding tasks” (not Lovable’s 24)
- Mobile: keep horizontal scroll hint

### 3.5 FailureClusterDrawer (`FailureClusterDrawer.tsx`)

- Restyle sheet header, severity chip, sections (pattern, detection rule, harness change, dataset candidate)
- Optional: open from new **Failure taxonomy** section cards (same `setClusterId` / `getFailureCluster`)
- Keep focus trap, Escape, `aria-labelledby`, body scroll lock

### 3.6 ImplementationEvidence → split

| New surface | Content from |
| --- | --- |
| `RepoEvidence` (§08) | `cursorArtifacts`, `keyCommands` from `implementationEvidence.ts` |
| `ArchitectureSection` (§09) | stats grid + `systemCapabilities` + diagram (new ASCII/SVG static) |
| Footer stats | `implementationStats` (3 tasks, 7 traces, 10 scorers) |

**Keep** `id="architecture"`, `architecture-heading`, and “Implementation evidence” text for smoke (can be subtitle under “Architecture”).

### 3.7 New shared components (planned)

| Component | Responsibility |
| --- | --- |
| `SiteNav` | sticky nav + demo badge |
| `SectionHeader` | `01 — premise` pattern |
| `HeroMetrics` | static fixture comparison strip |
| `ProtocolVocabulary` | events + metrics chips |
| `HarnessPrimitives` | 5 primitive cards |
| `FailureTaxonomyGrid` | cluster cards → drawer |
| `RouterSection` | extract from `page.tsx` |
| `TakeawaysFooter` | 4 bullets + disclaimer |

---

## 4. What must remain unchanged

### 4.1 Data & fixtures

| Asset | Path | Rule |
| --- | --- | --- |
| Trace fixtures | `data/traces/*.json` | No edits for design migration |
| Eval table data | `data/evals/policy_comparison.json` | Same rows; UI labels only |
| Failure clusters | `data/failure_clusters.json` | Same IDs for drawer wiring |
| Cockpit assembly | `apps/web/lib/cockpitFixtures.ts` | Same task/policy/run mapping |
| Eval imports | `apps/web/lib/evalFixtures.ts` | Same |
| Router fixture | `demoData.ts` / `data/router_decisions.json` | Same |

### 4.2 Behavior

- Task switch (`[`, `]`) and policy switch (`1`–`3` on bugfix)
- Step navigation (`←`, `→`) and evidence tabs (`f`, `t`, `d`, `j`, `r`)
- Policy toggle updates trace, metrics, evidence, verdict together
- Eval drawer opens on baseline loop + unsafe cells only (existing cluster IDs)
- `baseline_with_steering` path on bugfix only
- No network calls, no API routes, no `process.env` in hosted app

### 4.3 Out of repo scope (do not touch in design phase)

- `packages/evals/*`, CI, runner, MCP, adapters
- `scripts/smoke_hosted_demo.py` check list (unless headings/ids intentionally updated in sync)
- Scorer weights, suite gates, hosted task selector backend (N/A)

### 4.4 Copy constraints (static / local-only)

Every migrated section must retain or strengthen:

- “Static hosted demo” / “precomputed traces”
- “No live LLM, runner, or API calls in the browser”
- Eval table = **synthetic** fixture
- Router = illustrative fixture
- Implementation evidence = in-repo capabilities, not deployed SaaS

---

## 5. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| **Overclaiming vs Lovable copy** | Reviewers think 24 tasks / live runner / production metrics | Never import Lovable numbers; use AHE fixture counts; label hero metrics “illustration” |
| **Smoke check regressions** | `pnpm smoke:hosted` fails | Keep required strings/ids; run smoke after each phase; update smoke only with explicit checklist |
| **Accessibility regression** | Lose keyboard nav, focus rings, SR labels | Migrate styles via tokens; do not remove ARIA; test with keyboard-only pass |
| **Mobile layout breaks** | Cockpit 3-column collapse, table overflow | Test `md`/`lg` breakpoints; keep timeline scroll region; sticky nav collapse |
| **SSR shell drift** | Smoke checks server HTML | Prefer static section headers in server components; client-only wrappers inside |
| **Scope creep** | Autoplay, 5-policy cockpit, live GitHub API | Defer autoplay; policies per task from fixtures; GitHub link is static URL |
| **Dual UX plans** | `UX_PLAN.md` vs Lovable diverge | Add note at top of UX_PLAN: Lovable reference supersedes visual IA for v0.2 hosted |
| **Bundle size** | New fonts/illustrations | Use `next/font` subset; SVG inline for architecture diagram |

---

## 6. Recommended implementation phases

### Phase D1 — Design tokens & global shell (1 PR)

**Scope:** `globals.css`, `tailwind.config.ts`, `layout.tsx`, new `SiteNav`, `SectionHeader`, footer shell  

**Deliverables:**
- CSS token layer + Tailwind extensions
- Sticky nav with section links
- Skip link + focus-ring preserved
- Takeaways footer stub with static disclaimer

**Exit:** `pnpm typecheck`, `pnpm build`, `pnpm smoke:hosted:local` pass; visual change minimal except nav

---

### Phase D2 — Page section restructure (1 PR)

**Scope:** `app/page.tsx` — reorder sections, add Protocol, Primitives, Failure taxonomy, Router extract, Takeaways  

**Deliverables:**
- Chapter-numbered sections
- Hero metrics from fixture staticEval (not Lovable fiction)
- Move router out of inline block
- All smoke anchors preserved

**Exit:** smoke 11/11; `DEMO_SCRIPT.md` section numbers updated

---

### Phase D3 — Cockpit restyle (1 PR)

**Scope:** `Cockpit.tsx`, `TraceTimeline.tsx`, `EvidencePanel.tsx`, `MetricCard.tsx`, `VerdictStamp.tsx`  

**Deliverables:**
- Lovable-like layout and chips
- Optional Reset button (state reset only)
- No behavior change to keyboard handlers

**Exit:** manual cockpit script in DEMO_SCRIPT; smoke pass

---

### Phase D4 — Eval & drawer restyle (1 PR)

**Scope:** `EvalTable.tsx`, `FailureClusterDrawer.tsx`, new `FailureTaxonomyGrid`  

**Deliverables:**
- Table styling + taxonomy grid opening same drawer
- Synthetic disclaimer prominent

**Exit:** click loop/unsafe cells + taxonomy cards; smoke pass

---

### Phase D5 — Architecture & repo evidence restyle (1 PR)

**Scope:** Split `ImplementationEvidence.tsx` → `RepoEvidence` + `ArchitectureSection`  

**Deliverables:**
- §08 cursor/MCP/eval command cards
- §09 stats + system map + static architecture diagram
- `id="architecture"` retained

**Exit:** smoke pass; implementation counts still correct

---

### Phase D6 — Visual QA & documentation (1 PR)

**Scope:** responsive pass, `prefers-reduced-motion`, docs  

**Deliverables:**
- Update `DEMO_SCRIPT.md`, `DEPLOYMENT.md` post-deploy smoke notes if headings changed
- Optional screenshot checklist in `RELEASE_CHECKLIST.md`
- Run full verification: `pnpm typecheck`, `pnpm build`, `pnpm smoke:hosted:local`

**Exit criteria (implementation complete):**
- [ ] Existing app functionality unchanged (task/policy/trace/eval drawer)
- [ ] UI visibly aligned with Lovable reference (nav, chapters, surfaces, cockpit density)
- [ ] `pnpm smoke:hosted` passes without relaxing checks
- [ ] `pnpm typecheck` and `pnpm build` pass
- [ ] Static/local-only claims explicit in hero, eval, footer

---

## Appendix A — Smoke check contract (do not break)

These must remain in SSR HTML unless `scripts/smoke_hosted_demo.py` is updated in the same PR:

| Check ID | Required signal |
| --- | --- |
| `title_brand` | `Agent Harness Environment` |
| `hero_headline` | `A flight recorder for coding agents.` |
| `static_demo_copy` | `Static hosted demo`, `No live LLM` |
| `task_classes_hero` | `bugfix`, `adversarial`, `multi-agent` |
| `anchor_cockpit` | `id="cockpit"`, `href="#cockpit"` |
| `anchor_evals` | `id="evals"` |
| `anchor_architecture` | `id="architecture"`, `href="#architecture"` |
| `cockpit_section` | `Interactive cockpit` |
| `eval_section` | `Policy comparison` |
| `implementation_section` | `Implementation evidence` |
| `task_class_labels` | `BUGFIX`, `ADVERSARIAL`, `MULTI-AGENT` |

---

## Appendix B — Lovable → AHE content mapping (do not copy literally)

| Lovable claim | AHE truth |
| --- | --- |
| 24 fixture tasks | 7 trace fixtures; 32-task **synthetic** eval table |
| Hero 42% → 78% | Use bugfix staticEval or disclaimer “illustration” |
| 5 policies always in cockpit | 2–3 policies per task from `cockpitFixtures` |
| “Press play” timeline | Step-based replay (optional reset only in v1) |
| packages/evals/run.ts | `packages/evals/run_eval.py` (show real paths in repo evidence) |
| Live MCP servers in JSON | Show actual `tools/mcp_server.py` surface; mark dry-run/local |

---

## Appendix C — File touch list (implementation reference)

```
apps/web/app/globals.css
apps/web/app/layout.tsx
apps/web/app/page.tsx
apps/web/tailwind.config.ts
apps/web/components/SiteNav.tsx          (new)
apps/web/components/SectionHeader.tsx   (new)
apps/web/components/Cockpit.tsx
apps/web/components/TraceTimeline.tsx
apps/web/components/EvidencePanel.tsx
apps/web/components/EvalTable.tsx
apps/web/components/FailureClusterDrawer.tsx
apps/web/components/ImplementationEvidence.tsx  (split)
apps/web/components/MetricCard.tsx
apps/web/components/VerdictStamp.tsx
docs/DEMO_SCRIPT.md                    (phase D6)
```

**Explicitly out of scope:** `data/**`, `packages/evals/**`, `services/runner/**`, CI workflows.
