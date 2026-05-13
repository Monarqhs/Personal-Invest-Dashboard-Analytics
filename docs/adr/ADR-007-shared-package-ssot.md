# ADR-007 — Shared Package as Cross-Language SSOT

**Status:** Accepted  
**Date:** 2026-05-13  
**Deciders:** Monarqhs

---

## Context

A monorepo with a Python API, Python pipelines, and a TypeScript frontend creates schema drift risk: a field renamed in the API silently breaks the frontend because TypeScript types were hand-maintained in parallel. This is a common source of runtime bugs in data products.

## Decision

`/packages/shared` is the single source of truth for cross-boundary contracts.

### Python (`/packages/shared/python`)
- Pydantic models used by both `apps/api` and `packages/pipelines`.
- Abstract interfaces: `MarketDataProvider`, `Notifier`, `CacheProvider`, `BaseStrategy`.
- Shared utilities: timezone helpers, idempotency keys, retry decorators.
- Installed as a local package in both API and pipelines `pyproject.toml`.

### TypeScript (`/packages/shared/typescript`)
- Auto-generated from FastAPI's OpenAPI spec via `openapi-typescript`.
- Hand-written enums/constants mirrored from Python (with codegen verification in CI).
- Consumed by `apps/web` as a workspace package.

### Codegen Flow
```
FastAPI (running ephemerally)
  → /openapi.json
    → openapi-typescript
      → packages/shared/typescript/src/generated/api.d.ts
```

Script: `packages/shared/scripts/codegen.sh`  
Trigger: `pnpm codegen` or CI `verify-codegen` job.

### CI Enforcement
The `verify-codegen` CI job:
1. Runs `codegen.sh`.
2. Checks `git diff packages/shared/typescript/src/generated/`.
3. Fails build if diff is non-empty (means a developer changed the API without regenerating types).

This makes schema drift a CI failure, not a runtime surprise.

## Consequences

**Easier:**
- API contract changes automatically propagate to TypeScript.
- Interfaces are reviewable in one place.
- New services (e.g., a CLI tool) can consume shared types immediately.

**Harder:**
- Codegen adds a build step; local dev requires running `pnpm codegen` after API changes.
- Ephemeral FastAPI startup in CI adds ~10 s to verify-codegen job.

## Alternatives Considered

- **Hand-written TypeScript types:** Simple but drifts. Rejected — a 5-minute codegen prevents hours of debugging.
- **tRPC:** Type-safe RPC between Next.js and a Node.js backend. Rejected — the API is Python/FastAPI; adding a Node proxy layer is complexity without benefit.
- **GraphQL with codegen:** Would work but adds significant complexity (schema, resolvers, graphql-codegen). Rejected for MVP scope.

## Migration Path

If the OpenAPI-based approach becomes limiting (e.g., complex discriminated unions that openapi-typescript doesn't handle well):
- Evaluate `zod` schemas as the SSOT with `zod-to-json-schema` → OpenAPI export.
- The codegen shell script is the single integration point; swap the generator without touching consumers.
