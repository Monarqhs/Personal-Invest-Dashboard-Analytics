# ADR-001 — Free-Tier Hosting Strategy

**Status:** Accepted  
**Date:** 2026-05-13  
**Deciders:** Monarqhs

---

## Context

This project serves two purposes: a personal analytics tool and a career portfolio piece targeting DE/SWE roles in Indonesia and remote APAC. The developer is a solo, part-time contributor.

Running production-grade infrastructure on a student/solo budget means total monthly cost must be $0. This constraint shapes every hosting decision.

Cost-conscious engineering is itself a portfolio signal: choosing the right tool under resource constraints demonstrates judgment that maps to real business environments.

## Decision

All hosted services use free tiers:

| Layer | Service | Free Tier Limits |
|---|---|---|
| Frontend | Vercel | 100 GB bandwidth/month |
| API | Render.com Web Service | 512 MB RAM, auto-sleep after 15 min idle |
| Database | Supabase PostgreSQL | 500 MB storage, auto-pause after 7 days idle |
| Orchestration | GitHub Actions (public repo) | Unlimited minutes |
| Object storage | Cloudflare R2 | 10 GB free, 1M Class A ops/month |
| Notifications | Telegram Bot API | Free |

## Consequences

**Easier:**
- Zero operational cost allows indefinite hosting of a live demo.
- Forced simplicity — no over-engineering justified by paid headroom.

**Harder:**
- Render cold start (~30 s after 15 min idle) can hurt demo experience.
- Supabase 500 MB ceiling requires archival strategy beyond ~150 tickers × 2 years OHLCV.
- Supabase auto-pause requires keep-alive mechanism.

**Mitigations in place:**
- Keep-alive GitHub Actions workflow pings API + DB every 10 minutes during 05:00–24:00 WIB.
- Vercel edge caching for semi-static data (ticker list: 1 h, screener snapshot: 15 min).
- Cloudflare R2 archival for raw data older than 6 months (see ADR-006).

## Alternatives Considered

- **GCP hybrid ($10–15/month):** Cloud Run + Cloud SQL + Airflow on GCE. Higher CV recognition (GCP + Airflow keywords) but recurring cost makes indefinite hosting unlikely. Rejected due to budget constraint.
- **Fly.io free tier:** Less predictable than Render for hobby workloads; Render's 512 MB + auto-sleep is better documented. Rejected.
- **Railway:** Free tier was sunset; now requires payment. Rejected.

## Migration Path

If traffic or scope justifies cost:

1. **API:** Migrate to Cloud Run with `min-instances=1` (~$5/month). Cold start eliminated.
2. **DB:** Migrate to Neon (serverless Postgres) or keep Supabase Pro ($25/month).
3. **Orchestration:** Add Airflow on Cloud Composer or self-host on a $6/month VPS.

All external dependencies are behind interfaces; migration is a config + infra change, not a code rewrite.
