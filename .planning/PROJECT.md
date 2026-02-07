# Crime Incidents Philadelphia - Local Containerized Dev

## What This Is

This project provides a Philadelphia crime analytics platform with a Python analysis pipeline, a FastAPI backend, and a Next.js frontend. The scope is now focused on local development hosting only, where the full system runs through Docker Compose. The primary audience is local developers/operators who need to run and iterate on the full stack without cloud dependencies.

## Core Value

One `docker compose up` command reliably brings up the complete stack locally with small, resource-constrained containers.

## Requirements

### Validated

- ✓ User can run analytics and data prep workflows through Python CLI and pipeline commands — existing
- ✓ User can access precomputed crime datasets through versioned FastAPI endpoints — existing
- ✓ User can use a web dashboard with maps/charts backed by API data — existing
- ✓ User can refresh/export API-ready artifacts from pipeline code — existing
- ✓ User can run the system with containerized components already present in repo tooling — existing

### Active

- [ ] Developer can start API, frontend, data refresh/export pipeline, and supporting services entirely locally with one `docker compose up`
- [ ] Containers are split appropriately by service boundary (multiple containers as needed)
- [ ] Container images are minimized for size using slim/multi-stage builds where practical
- [ ] Runtime resource limits are enforced for CPU and memory per service in local compose configuration
- [ ] Local startup/docs make local-only operation the default development path

### Out of Scope

- Cloud hosting and deployment targets (Cloud Run/Firebase/prod infra) — explicitly excluded by scope change to local-only hosting
- Non-local runtime environments and remote managed services — explicitly excluded to reduce complexity for this milestone
- Work not required for local containerized operation — excluded until local-first workflow is complete

## Context

This is a brownfield monorepo with existing analysis, pipeline, API, and frontend layers. Current architecture is batch-first data generation with API-serving cached artifacts and a static-first frontend consuming API endpoints. Existing codebase mapping (`.planning/codebase/`) confirms substantial implemented functionality; this milestone narrows focus to operational packaging and local hosting ergonomics via Docker Compose.

## Constraints

- **Hosting**: Local development only — no non-local hosting in this scope
- **Runtime Footprint**: Low memory/CPU and small image sizes — to keep local runs lightweight
- **Orchestration**: Docker Compose command parity — single-command bring-up is mandatory
- **Architecture**: Preserve existing service boundaries — avoid regressions in analysis/API/frontend capabilities

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Local-only hosting for this scope | Reduce delivery complexity and optimize developer workflow | — Pending |
| Multi-container approach is allowed/expected | System has distinct services that should remain separately operable | — Pending |
| Optimize for both image size and runtime resources | Keep local development fast and practical on modest machines | — Pending |
| Success criterion is one-command startup (`docker compose up`) | Clear, observable definition of done | — Pending |

---
*Last updated: February 7, 2026 after initialization*
