# Pre-tag audit — v0.1

**Audit date:** 2026-06-05  
**Purpose:** Verify the repo as a reviewer / GitHub runner would see it before a **manual** `v0.1` tag.  
**No tag, push, deploy, or GitHub Release was created by this audit.**

**Related:** [RELEASE_NOTES_v0.1.md](./RELEASE_NOTES_v0.1.md) · [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md) §8

---

## Audited commit

| Field | Value |
| --- | --- |
| **SHA (clean-clone source)** | `1d2d2e5eca301f1b1b33650ab42f4edd45529ff3` |
| **Message** | `add release tag prep and reviewer package` |
| **This document** | Added in a follow-up commit; **tag `v0.1` on the commit that includes this file** after re-running § verification below |

---

## Verification scope

| Environment | What ran |
| --- | --- |
| **Clean clone** (`git clone` → `/tmp/ahe-pre-tag-audit-*/clone`) | Full CI-equivalent contract + hygiene + deploy check |
| **Developer checkout** | Same CI contract re-run after adding this audit doc |
| **Not run (either)** | `pnpm smoke:hosted` (requires HTTP server), GitHub Actions live poll, `pnpm runner:batch`, live Braintrust/Weave export |

**Clean-clone setup:** `pnpm install --frozen-lockfile`, `python3 -m venv .venv`, `pip install -r requirements-dev.txt` (PEP 668 requires venv on macOS; matches README, differs from CI Ubuntu global pip).

---

## Clean-clone results

Clone had **no** `runs/`, `data/trace_candidates/`, `generated_candidates.jsonl`, or `apps/web/.next/` before install.

| Check | Result |
| --- | --- |
| `pnpm repo:status` | `ok=True`; all artifact paths `exists=False`; no tracked generated files |
| `pnpm deploy:check` | `ok=True`; env vars required: none |
| `pnpm validate:fixtures` | passed |
| `pnpm eval:ci` | `gates_ok: true` |
| `pnpm eval:baseline` | exit 0 |
| `pnpm eval` | exit 0 |
| `pnpm compare` | exit 0 |
| `python -m pytest` | **122 passed** |
| `pnpm typecheck` | exit 0 |
| `pnpm build` | static prerender OK (`○ /`) |

---

## CI status expectation

`.github/workflows/ci.yml` **deterministic-gates** job should pass on the tag commit:

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

**CI does not run:** `pnpm repo:status`, `pnpm deploy:check`, `pnpm smoke:hosted`, runner batch, adapter live export.

**Python version note:** CI uses **3.12**; clean-clone audit used **3.13** via local venv. Both passed pytest/eval gates at audit time.

---

## Generated artifact hygiene

| Path | Clean clone | Developer checkout (typical) |
| --- | --- | --- |
| `runs/` | absent | may exist (gitignored) |
| `data/trace_candidates/` | absent | may exist (gitignored) |
| `data/datasets/generated_candidates.jsonl` | absent | may exist (gitignored) |
| `apps/web/.next/` | absent until `pnpm build` | may exist (gitignored) |

**Pre-tag:** `git status --short` must not stage generated paths or `.env*`. Run `pnpm repo:status` — expect `ok=true`, no tracked generated files.

---

## Deployment readiness

| Check | Result |
| --- | --- |
| `pnpm deploy:check` | `ok=True` (clean clone) |
| Hosted env vars | none required |
| Recommended host | Vercel (see [DEPLOYMENT.md](./DEPLOYMENT.md)) |
| Post-deploy smoke | `pnpm smoke:hosted -- --url <url>` (manual; not audited here) |

---

## Release caveats (do not overclaim)

| Topic | v0.1 reality |
| --- | --- |
| Hosted demo | Static fixture replay — no live LLM/runner in browser |
| Eval table | Synthetic portfolio fixture — not `eval:ci` output |
| Benchmark scale | 7 traces / 3 tasks — demo, not production benchmark |
| RL-lite router | Static fixture |
| Live export | Opt-in locally; not in CI |
| Deploy URL | Not provisioned by this repo |

Full list: [RELEASE_NOTES_v0.1.md](./RELEASE_NOTES_v0.1.md) § limitations.

---

## Manual tag commands (run later — not executed)

After this document is committed and § verification passes on **that** commit:

```bash
# 1. Confirm clean index
git status --short
pnpm repo:status

# 2. Re-run CI contract (or confirm GitHub Actions green)
pnpm validate:fixtures && pnpm eval:ci && python -m pytest && pnpm typecheck && pnpm build

# 3. Annotated tag (adjust SHA if needed)
git tag -a v0.1 -m "v0.1: static hosted demo and deterministic eval starter"

# 4. Push tag when ready (not done by this audit)
# git push origin v0.1

# 5. GitHub Release (manual UI or gh CLI)
# gh release create v0.1 --notes-file docs/RELEASE_NOTES_v0.1.md
```

Record tag SHA and date in the GitHub Release body alongside [RELEASE_NOTES_v0.1.md](./RELEASE_NOTES_v0.1.md).

---

## Auditor conclusion

**Clean-clone CI contract: PASS** at `1d2d2e5`. Repo is suitable for a manual `v0.1` tag once this audit doc is committed, local gates re-confirmed, and GitHub Actions is green on the final commit.
