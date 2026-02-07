# Phase 2 Research: Footprint and Runtime Optimization

**Phase:** 02 - Footprint and Runtime Optimization  
**Date:** 2026-02-07

## Scope and Inputs

This phase targets requirement IDs `FOOT-01`, `FOOT-02`, and `FOOT-03` from `.planning/REQUIREMENTS.md` while preserving the working compose baseline established in Phase 1.

No phase-specific `CONTEXT.md` exists for phase 02, so roadmap and requirements are the primary constraints.

## Current State Audit

## Container build patterns
- `api/Dockerfile` and `pipeline/Dockerfile` are single-stage Python builds and copy broad directories from repo root.
- `web/Dockerfile` installs dependencies with `npm ci`, but compose command still runs `npm install` at container startup.
- No root `.dockerignore` exists, so build context can include heavy, irrelevant artifacts (`web/node_modules`, `.next`, `web/out`, `__pycache__`, local data outputs).

## Compose runtime budget controls
- `docker-compose.yml` includes healthchecks and dependency gating from Phase 1.
- No explicit CPU or memory limits are set for long-running default services (`pipeline`, `api`, `web`).
- Without limits, laptop resource pressure can become unpredictable during long sessions.

## Build-cache efficiency
- Dockerfiles already copy dependency manifests before source in some places, but context breadth and startup `npm install` reduce practical gains.
- Large context transfer invalidates cache frequently even when app code changes are small.

## Findings and Implications

1. The biggest immediate footprint and build-latency win is reducing build context via `.dockerignore`.
2. Runtime stability needs compose-level CPU/memory caps so the default profile behaves predictably across machines.
3. Cache structure should isolate dependency install layers from code layers and avoid container-start dependency installs.
4. Optimization changes must be validated with compose config/build checks to ensure no regression in one-command startup.

## Implementation Recommendations

## Image and build-context optimization (`FOOT-01`, `FOOT-03`)
- Add root `.dockerignore` tuned for this repo:
  - Exclude `web/node_modules`, `web/.next`, `web/out`, `**/__pycache__`, `.git`, local virtualenvs, and transient logs.
  - Keep required runtime/config/data directories that are intentionally copied by Dockerfiles.
- Refactor Python Dockerfiles to keep dependency layers isolated and deterministic:
  - Use slim base images, single dependency install step, and copy only required directories.
  - Prefer pinned requirements/lock-driven installs where available.
- Refactor web runtime path to avoid `npm install` at container start in normal flow; dependency installation should happen at image build time.

## Runtime limits (`FOOT-02`)
- Add explicit memory and CPU limits for `pipeline`, `api`, and `web` in compose defaults.
- Pair hard limits with reservations where helpful to keep startup behavior stable.
- Keep limits conservative enough for typical laptops and documented for adjustment.

## Verification and guardrails
- Use `docker compose config` as schema/contract validation.
- Use `docker compose build` timing/verbosity comparison checkpoints to confirm cache effectiveness after first build.
- Preserve Phase 1 behavior by confirming default `docker compose up` still starts all core services and healthchecks pass.

## Risks to Address in Planning

- Too-aggressive limits can cause healthcheck failures or restart loops.
- Over-pruning `.dockerignore` can remove files needed during image build.
- Changes to web startup path must remain compatible with bind mounts used for local development.

## Phase Planning Inputs

Plan set should produce:
1. Build-context and Dockerfile optimization for all three core services.
2. Compose CPU/memory budgets for long-running default services.
3. Verification steps/scripts/docs to prove cache and runtime improvements without startup regression.
