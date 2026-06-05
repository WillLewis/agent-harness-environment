# Hosted demo deployment readiness

Prepare the **static hosted demo** (`apps/web`) for deployment review. This repo does **not** ship a deployment workflow, platform secrets, or live URLs — reviewers configure hosting manually.

**Doc map:** [INDEX.md](./INDEX.md) · **Local demo:** [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) · **Pre-ship gates:** [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md)

---

## What you are deploying

| Included in hosted build | Not included (local-only) |
| --- | --- |
| Precomputed traces from `data/traces/` (bundled at build time) | Live LLM or agent execution |
| Synthetic eval table from `data/evals/policy_comparison.json` | `pnpm eval:ci` / Python scorers |
| Failure clusters, router fixture, cockpit UI | Local runner (`runs/`), MCP server |
| Client-side policy/task toggles (static JSON replay) | Braintrust / Weave live upload |

**Claims to keep accurate:** static fixtures, synthetic portfolio table, no browser API calls. See [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) opening narration.

---

## Build audit (current Next.js setup)

| Check | Status |
| --- | --- |
| App Router, single static page | Yes — `apps/web/app/page.tsx` prerenders as static |
| API routes / middleware / SSR data fetching | None |
| `process.env` in `apps/web` | None required |
| Fixture imports | `apps/web/lib/*` imports `data/` JSON via relative paths — **full monorepo checkout required at build** |
| Workspace dependency | `@ahe/harness` via `transpilePackages` in `next.config.mjs` |
| Standard `next build` output | Hybrid static + minimal server handlers (Next 14 default); suitable for Vercel/Netlify Next runtime |

`pnpm build` (root) runs `pnpm --filter @ahe/web build`. CI already runs this on every push/PR.

---

## Recommended host: Vercel

**Why:** Native Next.js 14 support, pnpm monorepo-friendly, no `output: 'export'` changes needed, matches current `next build` behavior.

### Suggested project settings

| Setting | Value |
| --- | --- |
| Framework preset | Next.js |
| Root directory | Repository root (`.`) — **not** `apps/web` alone |
| Install command | `pnpm install --frozen-lockfile` |
| Build command | `pnpm build` |
| Output directory | *(leave default — Vercel detects Next.js in `apps/web`)* |
| Node.js version | 22.x (matches CI) |
| Environment variables | **None required** |

If the platform insists on **Root directory = `apps/web`**, use install from monorepo root so `data/` and `packages/harness` resolve:

```bash
# Install (from apps/web as root dir)
cd ../.. && pnpm install --frozen-lockfile

# Build
cd ../.. && pnpm build
```

### Monorepo note

The web app imports fixtures from `../../../data/` and transpiles `@ahe/harness`. Deploying only the `apps/web` folder without the rest of the repo **will fail** at build time.

---

## Alternative hosts

### Netlify

Use the [Next.js runtime plugin](https://docs.netlify.com/frameworks/next-js/overview/) (not plain static file hosting).

| Setting | Value |
| --- | --- |
| Base directory | Repository root |
| Build command | `pnpm build` |
| Publish directory | Leave to Next.js plugin (typically `apps/web/.next`) |
| Environment variables | **None required** |

Plain “static site” mode (`publish = apps/web/out`) is **not** supported without code changes — this app does not use `output: 'export'`.

### GitHub Pages

**Not recommended without config changes.** GitHub Pages serves static files only. This app uses the default Next.js build (not `output: 'export'`), so there is no `out/` folder to upload.

To use GitHub Pages you would need (out of scope for this repo today):

- `output: 'export'` in `next.config.mjs`
- `basePath` / `assetPrefix` if deploying to `https://<user>.github.io/<repo>/`
- `images.unoptimized: true` if `next/image` is added later

Document for reviewers: use Vercel or Netlify Next runtime instead.

---

## Local preview (post-build smoke)

After a production build, serve the built app locally (no deploy):

```bash
pnpm build
pnpm preview
```

Opens Next.js production server on port **3000** (override with `PORT=3001 pnpm preview`). This mirrors what Vercel/Netlify run after build — still **static fixture replay**, not live agents.

Development server (hot reload): `pnpm dev`.

---

## Pre-deploy checklist (local)

```bash
pnpm deploy:check          # deterministic readiness audit
pnpm repo:status           # generated artifacts not tracked
pnpm validate:fixtures
pnpm eval:ci               # optional; not required for static hosting
pnpm typecheck
pnpm build
pnpm preview               # manual browser smoke
```

`pnpm deploy:check` verifies monorepo layout, fixture paths, no required env vars, and no API routes — it does **not** deploy or call external services.

---

## Post-deploy smoke checklist (browser)

After your platform reports a successful deploy:

1. **Landing** — hero loads; links to `#cockpit`, `#evals`, `#architecture` work.
2. **Cockpit** (`#cockpit`) — default bugfix + baseline shows **Rejected**; trace timeline and evidence tabs populate.
3. **Policy toggle** — switch to **Guarded recovery** on bugfix → **Accepted**, metrics/terminal/diff update together.
4. **Task switch** — adversarial + multi-agent tasks load distinct traces (keyboard `[` `]` optional).
5. **Eval table** (`#evals`) — policy rows render; disclaimer mentions synthetic fixtures.
6. **Failure drawer** — click baseline loop or unsafe metric → cluster drawer opens.
7. **Implementation evidence** (`#architecture`) — static counts (3 tasks, 7 traces) visible.
8. **No network dependency** — disable offline after first load; toggles still work (all data bundled).

Walkthrough detail: [DEMO_SCRIPT.md](./DEMO_SCRIPT.md).

---

## Environment variables

| Variable | Required? | Notes |
| --- | --- | --- |
| *(none)* | No | Hosted demo has no `process.env` usage in `apps/web` |

Do not add API keys to the hosted deployment. Braintrust, W&B, runner, and MCP remain local developer tools.

---

## What CI validates today

`.github/workflows/ci.yml` runs `pnpm build` but does **not** deploy. Optional local `pnpm deploy:check` complements CI with hosting-specific assertions (fixture paths, env audit).

---

## Intentionally out of scope

- Vercel/Netlify/GitHub Actions deploy workflows
- Platform tokens or project linking
- Custom domains or preview URLs in repo docs
- Converting the app to pure static export for GitHub Pages
- Running Python eval gates on the hosting platform
