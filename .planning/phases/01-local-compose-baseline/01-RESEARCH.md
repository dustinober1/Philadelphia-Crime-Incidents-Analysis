# Phase 1 Research: Local Compose Baseline

**Phase:** 01 - Local Compose Baseline  
**Date:** 2026-02-07

## Scope and Locked Decisions

This research is constrained by `.planning/phases/01-local-compose-baseline/01-CONTEXT.md`.

Locked decisions that drive planning:
- Default `docker compose up` must start `web`, `api`, `pipeline`, and required dependencies.
- Baseline startup is failed if any core service exits.
- Readiness is healthcheck-driven with dependency gating.
- Startup is fail-fast for contract mismatches.
- `.env.example` must define required vars and common optional toggles.
- Baseline startup must work without cloud credentials.
- Pipeline/API handoff uses a persistent named volume and API serves latest successful snapshot.

## Current State Audit

## Compose and service topology
- `docker-compose.yml` currently defines only one service (`api`).
- `web` and `pipeline` services are not containerized in compose.
- No supporting services are currently defined.
- No healthchecks and no `depends_on` readiness conditions are present.

## Container assets
- Present: `api/Dockerfile`.
- Missing: `web` Dockerfile and `pipeline` Dockerfile.

## Startup and data contract
- Pipeline export is run manually via `python -m pipeline.refresh_data --output-dir api/data`.
- API reads local JSON/GeoJSON payloads from `api/data` at startup.
- No explicit shared runtime volume contract exists between pipeline and API in compose.

## Env contract
- Root `.env.example` is focused on API keys and cloud/server env; it does not document a compose-first local contract.
- `web/.env.example` exists for frontend env values.
- README documents multi-step local startup (manual pipeline run + separate API + web) and only optional `docker compose up --build api`.

## Findings and Implications

1. Phase 1 requires baseline compose architecture work, not incremental tweaks.
2. Data handoff contract must move from implicit local filesystem assumptions to explicit shared-volume paths.
3. Healthcheck/dependency gating can be implemented with `depends_on: condition: service_healthy` and service-specific health probes.
4. Local-only startup is feasible now because question endpoints degrade to in-memory mode when Firestore is unavailable.
5. Fail-fast behavior must be enforced for required env and path contract mismatches (entrypoint checks or startup validation script).

## Implementation Recommendations (Constrained by Context)

## Service set for default startup
- `web` (Next.js dev server) - core.
- `api` (FastAPI/Uvicorn) - core.
- `pipeline` (long-running loop that refreshes exports) - core.
- No cloud-hosted dependency required for baseline.

## Shared data contract
- Add named volume (e.g., `pipeline_api_data`) mounted to:
  - pipeline write path: `/shared-data`
  - api read path: `/app/api/data`
- Pipeline writes complete artifact set atomically (temp dir + move/swap).
- API serves latest successful snapshot by reading mounted data directory.

## Dependency gating and healthchecks
- `pipeline` health: verify required export files exist in shared volume.
- `api` health: `/api/health` returns OK and loaded keys.
- `web` health: HTTP probe to local web endpoint.
- Use moderate healthcheck timing with startup grace (`start_period`) to reduce false negatives.
- `depends_on` rules:
  - `api` waits for `pipeline` to be healthy.
  - `web` waits for `api` to be healthy.

## Env contract
- Root `.env.example` should include compose-required vars with safe local defaults.
- Required vars should be validated at container start with clear errors.
- Keep precedence: compose override > `.env` > image defaults.

## Risks to address in plans
- Pipeline process currently appears batch-oriented and may need a durable run loop for long-running compose behavior.
- Frontend container startup time and node_modules handling can cause false healthcheck failures if probes are too aggressive.
- Data snapshot consistency must avoid partially-written API reads.

## Phase Planning Inputs

Plan set should produce:
1. Container and compose baseline for all core services.
2. Readiness/dependency gating plus shared-volume contract and fail-fast checks.
3. Local env contract and README updates aligned with real runtime behavior.
