# ADR-002 — GitHub Actions as Pipeline Orchestrator

**Status:** Accepted  
**Date:** 2026-05-13  
**Deciders:** Monarqhs

---

## Context

A data pipeline needs scheduled execution, dependency management between tasks, retry logic, observability, and backfill capability. Apache Airflow is the dominant tool for this in data engineering portfolios and job descriptions.

However, Airflow requires 1–2 GB RAM at idle. No free hosting tier comfortably supports this. The two realistic free options are GitHub Actions (for public repos: unlimited minutes) and cron jobs on a shared VPS.

## Decision

Use **GitHub Actions scheduled workflows** as the pipeline orchestrator.

Pipeline Python code is structured as explicit DAG-style tasks with clear dependency ordering:

```
extract → load_raw → transform (dbt) → screen → notify
```

Each task is an isolated Python module in `packages/pipelines/src/tasks/`. The orchestrator script (`run_pipeline.py`) calls them in sequence with explicit error handling and `pipeline_runs` table writes.

Schedules:
- `idx-daily.yml` — `0 11 * * 1-5` UTC → 18:00 WIB weekdays (IDX market close + 1.5 h)
- `us-daily.yml` — `0 23 * * 1-5` UTC → 06:00 WIB weekdays (US pre-market data ready)
- `backfill.yml` — `workflow_dispatch` with date-range inputs
- `keep-alive.yml` — `*/10 22-23,0-17 * * *` UTC → every 10 min during 05:00–24:00 WIB

## Consequences

**Easier:**
- Zero infrastructure cost.
- Built-in secret management (GitHub Secrets).
- PR-linked history: every pipeline run is a workflow run with full logs.
- Backfill via `workflow_dispatch` inputs — no CLI tooling needed.

**Harder:**
- No Airflow UI (visual DAG graph, task history, re-run individual tasks via UI).
- No dynamic task generation (Airflow's `@task.expand`).
- "Airflow" absent from stack in job postings that filter for it.

**Mitigations:**
- Self-built `/pipeline-runs` observability page in Next.js reads `pipeline_runs` table — visually demonstrates the same pipeline health that Airflow UI would show.
- Code is structured for Airflow port-readiness: each task function maps 1:1 to a `@task`-decorated function; dependency graph is explicit in `run_pipeline.py`.
- README section "Why not Airflow?" owns this decision with a clear narrative.

## Alternatives Considered

- **Apache Airflow on free VPS (Oracle Cloud Always Free):** Oracle Cloud provides 2 OCPU + 12 GB RAM ARM instances free. Viable but operationally complex (maintain OS, Docker, networking) and adds 2–3 days of infra setup. Rejected for MVP; documented as upgrade path.
- **Prefect Cloud free tier:** 3 concurrent runs limit on free tier; adequate for MVP. Kept as backup option if GitHub Actions minutes become a constraint.
- **Dagster Cloud free tier:** Similar to Prefect. Kept as backup.

## Migration Path to Airflow

When this project is extended or used as a template for a production environment:

1. Wrap each task function with `@task` decorator.
2. Create `@dag` function with same dependency order as `run_pipeline.py`.
3. Replace GitHub Actions cron with Airflow scheduler.
4. `pipeline_runs` table remains — Airflow writes to it via on-success/on-failure callbacks.
5. Airflow UI replaces the custom observability page (or coexists with it).

Estimated migration effort: 1–2 days.
