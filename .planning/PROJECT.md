# Crime Incidents Philadelphia - Local Containerized Dev

## Current State

Shipped `v1.0 Local Containerized Dev` on February 7, 2026. The project now has a compose-first local runtime with explicit service boundaries (`web`, `api`, `pipeline`), dependency-gated startup health, resource budget controls, and operational recovery/profile guardrails.

## What This Is

This project provides a Philadelphia crime analytics platform with a Python analysis pipeline, a FastAPI backend, and a Next.js frontend. The current delivery focus is local development hosting only, where the full system runs through Docker Compose without mandatory cloud dependencies.

## Core Value

One `docker compose up` command reliably brings up the complete stack locally with small, resource-constrained containers.

## Requirements

### Validated

- ✓ User can run analytics and data prep workflows through Python CLI and pipeline commands — existing
- ✓ User can access precomputed crime datasets through versioned FastAPI endpoints — existing
- ✓ User can use a web dashboard with maps/charts backed by API data — existing
- ✓ User can refresh/export API-ready artifacts from pipeline code — existing
- ✓ User can run the system with containerized components already present in repo tooling — existing
- ✓ Developer can start API, frontend, data refresh/export pipeline, and supporting services entirely locally with one `docker compose up` — v1.0
- ✓ Containers are split appropriately by service boundary (multiple containers as needed) — v1.0
- ✓ Container images are minimized for size using slim/multi-stage builds where practical — v1.0
- ✓ Runtime resource limits are enforced for CPU and memory per service in local compose configuration — v1.0
- ✓ Local startup/docs make local-only operation the default development path — v1.0

### Active

- [ ] Add automated local smoke checks that run after compose startup to verify endpoint and artifact readiness
- [ ] Add per-profile presets for low-power laptop mode vs high-performance local analysis mode

### Out of Scope

- Cloud hosting and deployment targets (Cloud Run/Firebase/prod infra) — explicitly excluded by scope change to local-only hosting
- Non-local runtime environments and remote managed services — explicitly excluded to reduce complexity for this milestone
- Work not required for local containerized operation — excluded until local-first workflow is complete

## Context

This is a brownfield monorepo with existing analysis, pipeline, API, and frontend layers. Current architecture remains batch-first data generation with API-serving cached artifacts and a static-first frontend consuming API endpoints. Milestone v1.0 hardened local packaging and runtime ergonomics without changing the project's core product boundaries.

## Next Milestone Goals

- Add automated post-start smoke checks for API/data readiness.
- Add explicit runtime-mode presets for constrained vs high-performance local machines.
- Preserve default compose startup behavior while extending advanced profile ergonomics.

## Constraints

- **Hosting**: Local development only — no non-local hosting in this scope
- **Runtime Footprint**: Low memory/CPU and small image sizes — to keep local runs lightweight
- **Orchestration**: Docker Compose command parity — single-command bring-up is mandatory
- **Architecture**: Preserve existing service boundaries — avoid regressions in analysis/API/frontend capabilities

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Local-only hosting for this scope | Reduce delivery complexity and optimize developer workflow | ✓ Good |
| Multi-container approach is allowed/expected | System has distinct services that should remain separately operable | ✓ Good |
| Optimize for both image size and runtime resources | Keep local development fast and practical on modest machines | ✓ Good |
| Success criterion is one-command startup (`docker compose up`) | Clear, observable definition of done | ✓ Good |

---
*Last updated: February 7, 2026 after v1.0 milestone completion*
