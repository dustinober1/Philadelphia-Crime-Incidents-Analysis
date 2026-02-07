# Crime Incidents Philadelphia

## Current Milestone: Pending Definition (Post-v1.2)

**Goal:** Define and execute the next milestone after shipping v1.2 deferred workflow enhancements.

## Current State

Shipped `v1.2 Deferred Workflow Enhancements` on February 7, 2026.

Current delivered baseline:
- Compose-first local stack remains the default startup path (`docker compose up -d --build`).
- Validation now supports machine-readable output (`--format json|yaml`) with timing metadata and CI-friendly exit semantics.
- Extended API validation now supports high-value endpoint checks (`--extended`) with data-integrity and performance threshold checks.
- Runtime recommendation flow now supports host-aware preset guidance (`--recommend`) and auto mode selection (`--mode auto`).

## Next Milestone Goals

- Define v2 requirements and roadmap from deferred scope and newly surfaced operator priorities.
- Decide delivery order for: metrics export, API contract validation, historical integrity checks, and dynamic runtime adaptation.
- Close deferred workflow enhancement gaps around standardized error messaging and full preset-consistency validation.

<details>
<summary>Archived Context Through v1.2 Completion</summary>

## Previous Current Milestone: v1.2 Deferred Workflow Enhancements

**Goal:** Address deferred workflow enhancements (LWF-03 to LWF-05) to further improve local development experience and system capabilities.

**Target features:**
- Complete remaining workflow enhancements deferred from previous milestones
- Implement LWF-03, LWF-04, and LWF-05 requirements
- Enhance local development productivity and system usability

## Previous Current State

Shipped `v1.1 Local Workflow Enhancements` on February 7, 2026.

Current delivered baseline:
- Compose-first local stack remains default (`docker compose up -d --build`).
- Canonical smoke-check workflow validates readiness and export health after startup.
- Optional runtime presets (`low-power`, `high-performance`) are available without changing default behavior.
- Canonical runtime guardrail entrypoint (`make check-runtime-guardrails`) protects preset/default regression safety.

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
- ✓ Developer can run automated post-start smoke checks that verify API endpoint readiness and expected artifact availability after compose startup — v1.1
- ✓ Developer can choose low-power vs high-performance local runtime presets through clear compose profile conventions and documented resource defaults — v1.1
- ✓ Default startup path remains `docker compose up` while optional preset modes are explicitly documented and validated — v1.1

### Active

- [ ] Define next milestone requirements (`$gsd-new-milestone`)

### Out of Scope

- Cloud hosting and deployment targets (Cloud Run/Firebase/prod infra) — explicitly excluded by scope change to local-only hosting
- Non-local runtime environments and remote managed services — explicitly excluded to reduce complexity for current local workflow scope

## Context

This is a brownfield monorepo with existing analysis, pipeline, API, and frontend layers. Current architecture remains batch-first data generation with API-serving cached artifacts and a static-first frontend consuming API endpoints.

## Constraints

- **Hosting**: Local development only — no non-local hosting in current scope
- **Runtime Footprint**: Low memory/CPU and small image sizes — to keep local runs lightweight
- **Orchestration**: Docker Compose command parity — single-command bring-up remains mandatory
- **Architecture**: Preserve existing service boundaries — avoid regressions in analysis/API/frontend capabilities

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Local-only hosting for this scope | Reduce delivery complexity and optimize developer workflow | ✓ Good |
| Keep default startup unchanged while adding optional workflow/preset tooling | Preserve operator muscle memory and reduce rollout risk | ✓ Good |
| Add machine-readable and extended validation as opt-in flags | Avoid regressing baseline startup verification path | ✓ Good |
| Introduce resource-aware recommendation before dynamic auto-tuning | Deliver predictable behavior before runtime adaptivity complexity | ✓ Good |

</details>

---
*Last updated: February 7, 2026 after v1.2 milestone completion*
