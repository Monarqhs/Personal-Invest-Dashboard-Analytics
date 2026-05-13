# ADR-008 — Branching Strategy and Environment Promotion

**Status:** Accepted  
**Date:** 2026-05-13  
**Deciders:** Monarqhs

---

## Context

Single developer, three environments (local → staging → production), public repo used for both portfolio showcase and live tooling. Need a branching model that:

- Keeps `main` always deployable and clean (portfolio visitors land here)
- Provides a staging gate before production to catch integration issues
- Is lightweight enough for solo development (no bureaucracy)

## Decision

Three long-lived branches with a linear promotion flow:

```
feat/* ──► dev-ghali ──► uat ──► main
            (dev)       (staging) (production)
```

### Branch Roles

| Branch | Environment | Protected | Deploy Trigger |
|---|---|---|---|
| `main` | Production (Render prod + Vercel prod) | Yes — PR required, CI must pass | Push to `main` |
| `uat` | Staging (Render staging + Vercel preview) | Yes — PR required, CI must pass | Push to `uat` |
| `dev-ghali` | Local / dev | No — direct push OK | None (local only) |
| `feat/*` | Local | No | None |

### Feature Development Flow

1. Branch from `dev-ghali`: `git checkout -b feat/phase-2-data-layer dev-ghali`
2. Develop and commit on `feat/*`.
3. Open PR: `feat/phase-2-data-layer → dev-ghali`. CI runs. Merge.
4. Open PR: `dev-ghali → uat`. CI runs. Merge → triggers staging deploy.
5. Verify staging (smoke test, manual spot-check).
6. Open PR: `uat → main`. CI runs. Merge → triggers production deploy.

### CI Trigger Matrix

| Event | CI (lint/test/typecheck) | Deploy |
|---|---|---|
| PR to `dev-ghali` | ✓ | — |
| PR to `uat` | ✓ | — |
| PR to `main` | ✓ | — |
| Push to `uat` (merged PR) | ✓ | Staging |
| Push to `main` (merged PR) | ✓ | Production |

### GitHub Branch Protection Rules (configure manually)

**`main`:**
- Require PR before merging (1 approver: self-review allowed for solo dev)
- Require status checks to pass: `lint-python`, `typecheck-python`, `test-python`, `lint-frontend`, `typecheck-frontend`, `test-frontend`, `verify-codegen`
- Do not allow force push

**`uat`:**
- Same checks as `main`
- Force push allowed only for hotfixes (document in commit message)

### Secrets per Environment

| Secret | Used by | Notes |
|---|---|---|
| `RENDER_STAGING_DEPLOY_HOOK` | deploy-staging.yml | Render webhook URL for staging service |
| `RENDER_STAGING_URL` | deploy-staging.yml | Base URL for smoke test |
| `RENDER_PRODUCTION_DEPLOY_HOOK` | deploy-production.yml | Render webhook URL for prod service |
| `RENDER_PRODUCTION_URL` | deploy-production.yml | Base URL for smoke test |
| `RENDER_API_URL` | keep-alive.yml | Production API URL for keep-alive pings |
| `VERCEL_TOKEN` | both deploy workflows | Vercel CLI auth token |
| `VERCEL_ORG_ID` | both deploy workflows | Vercel org/user ID |
| `VERCEL_PROJECT_ID` | both deploy workflows | Vercel project ID for web app |
| `SUPABASE_URL` | keep-alive.yml, pipelines | Supabase project URL |
| `SUPABASE_ANON_KEY` | keep-alive.yml, pipelines | Supabase anon key |

## Consequences

**Easier:**
- `main` is always demo-ready for recruiters.
- Staging catches integration failures before they hit production.
- Clear history: every production deploy is a squash-merged PR from `uat`.

**Harder:**
- Three PRs to ship a feature (feat → dev-ghali → uat → main). For a solo developer this is acceptable overhead given the portfolio value of a clean `main`.
- Staging and production are separate Render services — doubles the free-tier service count. Render free tier allows multiple web services, so this is OK.

## Alternatives Considered

- **Trunk-based (direct push to main):** Simpler but `main` can have broken commits. Rejected — portfolio repo must always be demo-ready.
- **GitFlow (develop + release branches):** More branches than needed for solo dev. Rejected.
- **Single branch with tags for releases:** No staging environment. Rejected — ADR-001 requires staging smoke test to validate free-tier cold start behavior.

## Migration Path

If this project gains collaborators:
1. Add required reviews (≥1 human approver) to `main` and `uat`.
2. Add `feat/*` CI trigger for PRs to `dev-ghali` (already present — no change needed).
3. Consider adding `CODEOWNERS` file to route reviews to domain owners.
