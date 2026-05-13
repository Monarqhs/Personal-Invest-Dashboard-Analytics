# ADR-005 — Auth-Ready Without Auth-Enforced

**Status:** Accepted  
**Date:** 2026-05-13  
**Deciders:** Monarqhs

---

## Context

This is a single-user personal dashboard for MVP. There is no immediate need for authentication. However, retrofitting multi-user auth into a populated database — adding `user_id` columns, writing RLS policies, threading user context through every query — is high-cost work that breaks running systems.

The cost of adding auth scaffold at Phase 1 is ~3–5 days. The cost of retrofitting it later is 2–4 weeks plus a data migration. This is an asymmetric tradeoff.

## Decision

Implement auth-ready architecture from Phase 1 with enforcement disabled by default.

### Schema
All user-scoped tables include `user_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000001'`. For MVP, all rows belong to the seeded `system` user.

### API
FastAPI `get_current_user` dependency resolves to:
- System user (when `AUTH_ENFORCEMENT_ENABLED=false`, the default)
- Authenticated user (when `AUTH_ENFORCEMENT_ENABLED=true` and valid Supabase JWT is present)

### RLS
Row-level security policies are written in migrations and committed, but disabled. `RLS_ENABLED=false` by default. Enabling is a single `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` per table, controlled by a migration.

### Frontend
Auth context provider exists with `null` user as default. No login UI rendered in MVP. API client has header injection slot for when auth is enabled.

### Auth provider choice
Supabase Auth (bundled with the Supabase project). JWT validation uses `SUPABASE_JWT_SECRET`. Swap path to Clerk or Auth0 documented below.

## Consequences

**Easier:**
- Multi-user support is a config change + UI addition, not a schema migration.
- Security posture is intentional: the decision not to enforce auth is explicit, not accidental.

**Harder:**
- Slightly more complexity in Phase 1 code (auth middleware, user dependency).
- Recruiter reading code sees auth scaffolding and might wonder if it's over-engineering.
  - Mitigation: README explains the decision clearly.

## Alternatives Considered

- **No auth, retrofit later:** Rejected. Retrofitting user_id into a live database with data is painful and error-prone.
- **Enforce auth from day 1:** Adds friction to personal use (need to log in to see your own data). Rejected for MVP — enable via env var when needed.

## Migration Path to Enforced Auth

1. Set `AUTH_ENFORCEMENT_ENABLED=true` in production environment.
2. Create first user account via Supabase Auth dashboard.
3. Run migration to re-assign existing rows from system user to real user UUID.
4. Enable RLS policies via migration.
5. Add login UI to Next.js frontend (NextAuth or Supabase Auth UI).

## Swap Path Away from Supabase Auth

If Supabase Auth becomes a constraint (vendor lock-in, pricing, feature gap):

1. Replace JWT validation in `apps/api/src/auth.py` to verify against new provider's JWKS endpoint. One function, ~10 lines.
2. Update `SUPABASE_JWT_SECRET` → `JWT_PUBLIC_KEY` (or JWKS URL).
3. Supabase Auth tables are in the `auth` schema — if moving off Supabase entirely, migrate users to new provider's user table.
