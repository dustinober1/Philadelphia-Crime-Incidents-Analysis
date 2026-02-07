# Crime Incidents Philadelphia

## Current State

Shipped `v1.1 Local Workflow Enhancements` on February 7, 2026.

Current delivered baseline:
- Compose-first local stack remains default (`docker compose up -d --build`).
- Canonical smoke-check workflow validates readiness and export health after startup.
- Optional runtime presets (`low-power`, `high-performance`) are available without changing default behavior.
- Canonical runtime guardrail entrypoint (`make check-runtime-guardrails`) protects preset/default regression safety.

## Next Milestone Goals

To be defined with `$gsd-new-milestone`.

Recommended starting goals:
- Define new requirements for deferred workflow enhancements (`LWF-03`..`LWF-05`) and any product-facing scope updates.
- Reconfirm core value and scope boundaries before selecting next phases.
- Produce a fresh roadmap linked to the new milestone version.

<details>
<summary>Archived Context Through v1.1 Completion</summary>

## Previous Current State

Shipped `v1.0 Local Containerized Dev` on February 7, 2026. The project now has a compose-first local runtime with explicit service boundaries (`web`, `api`, `pipeline`), dependency-gated startup health, resource budget controls, and operational recovery/profile guardrails.

## Previous Current Milestone: v1.1 Local Workflow Enhancements

**Goal:** Improve local runtime confidence and machine-fit behavior without changing the compose-first default path.

**Target features:**
- Automated post-start smoke checks for API endpoint and data artifact readiness.
- Runtime-mode presets for low-power laptop usage vs high-performance local analysis usage.
- Guardrails to keep default `docker compose up` behavior stable while enabling optional profile tuning.

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

- [ ] Developer can run automated post-start smoke checks that verify API endpoint readiness and expected artifact availability after compose startup — v1.1
- [ ] Developer can choose low-power vs high-performance local runtime presets through clear compose profile conventions and documented resource defaults — v1.1
- [ ] Default startup path remains `docker compose up` while optional preset modes are explicitly documented and validated — v1.1

### Out of Scope

- Cloud hosting and deployment targets (Cloud Run/Firebase/prod infra) — explicitly excluded by scope change to local-only hosting
- Non-local runtime environments and remote managed services — explicitly excluded to reduce complexity for this milestone
- Work not required for local containerized operation — excluded until local-first workflow is complete

## Context

This is a brownfield monorepo with existing analysis, pipeline, API, and frontend layers. Current architecture remains batch-first data generation with API-serving cached artifacts and a static-first frontend consuming API endpoints. Milestone v1.0 hardened local packaging and runtime ergonomics without changing the project's core product boundaries.

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

</details>

---
*Last updated: February 7, 2026 after v1.1 milestone completion*
