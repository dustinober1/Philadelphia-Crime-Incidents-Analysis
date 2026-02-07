# Project Research Summary

**Project:** Crime Incidents Philadelphia - Local Containerized Dev
**Domain:** Local-first container orchestration for an existing analytics platform
**Researched:** February 7, 2026
**Confidence:** HIGH

## Executive Summary

This is a brownfield analytics platform with established Python analysis/pipeline code, a FastAPI backend, and a Next.js frontend. Research confirms the right approach is not architectural reinvention, but operational standardization around Docker Compose as the default local runtime contract.

The recommended strategy is a service-per-boundary container model (web, api, pipeline, supporting services) with one-command startup as a strict requirement. That should be paired with image slimming and per-service resource limits so local development remains fast and reliable on typical laptops.

The largest risks are hidden manual steps, cloud-coupled defaults, and pipeline/API artifact contract drift. These are mitigated by explicit compose service design, local-default fallbacks, and verification checks that exercise fresh-clone startup.

## Key Findings

### Recommended Stack

Use Docker Compose v2 as the local orchestrator, preserve existing FastAPI and Next.js stacks, and split runtime concerns across focused containers. Continue with Python slim runtime images and introduce service-specific Dockerfiles/multi-stage builds to improve size and rebuild speed.

**Core technologies:**
- Docker Compose: service orchestration and one-command startup contract.
- FastAPI/Uvicorn container: local API serving precomputed artifacts.
- Next.js container: local dashboard runtime.
- Pipeline job container: deterministic artifact refresh/export.

### Expected Features

**Must have (table stakes):**
- One-command startup for all required local services.
- Service boundaries aligned to web/api/pipeline responsibilities.
- Healthchecks + startup gating.
- Reproducible local env/config and persistent artifact storage.

**Should have (competitive):**
- Multi-stage image optimization and smaller runtime footprints.
- CPU/memory limits per service with documented override path.
- Compose profiles for optional workflows.

**Defer (v2+):**
- Cloud deployment parity and non-local infrastructure concerns.

### Architecture Approach

Retain current codebase architecture and wrap it in a compose-first operational layer: pipeline writes to a stable artifact volume, API serves from that contract, and web consumes API endpoints on the internal compose network. Supporting external dependencies should be optional or locally emulated to preserve local-only scope.

**Major components:**
1. `pipeline` service/job — data refresh and export.
2. `api` service — endpoint serving from exported artifacts.
3. `web` service — local dashboard runtime.
4. `supporting` optional services — local substitutes for external dependencies.

### Critical Pitfalls

1. **Hidden manual startup steps** — make pipeline/export part of compose contract.
2. **Image bloat** — use multi-stage builds and tighter copy/dependency layers.
3. **Resource limits that are too strict** — tune with workload-aware defaults and overrides.
4. **Cloud-coupled defaults** — enforce local fallbacks in default path.
5. **Artifact path drift** — enforce and verify a shared pipeline->API volume contract.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Local Compose Baseline
**Rationale:** Core value depends on one-command local startup first.
**Delivers:** Full service graph in compose, local-default config, health-gated startup.
**Addresses:** startup, service separation, local-only execution.
**Avoids:** hidden manual steps and cloud coupling.

### Phase 2: Footprint and Runtime Optimization
**Rationale:** After baseline works, optimize size and resource predictability.
**Delivers:** slim/multi-stage Dockerfiles, tuned CPU/memory limits, rebuild improvements.
**Uses:** existing stack versions and service-specific build patterns.
**Implements:** image and runtime budget controls.

### Phase 3: Verification and Developer UX Hardening
**Rationale:** lock reliability and onboarding confidence.
**Delivers:** startup verification checks, docs updates, reset/recovery workflows.
**Implements:** artifact contract validation and operator guidance.

### Phase Ordering Rationale

- Baseline orchestration must precede optimization.
- Optimization must precede final verification so benchmarks/tests measure target design.
- Pitfall prevention maps naturally to this order (manual/cloud issues first, bloat/limits second, drift/UX third).

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** service-specific optimization tactics for Python geospatial dependencies.

Phases with standard patterns (skip research-phase):
- **Phase 1:** compose orchestration and local config hardening are well-established.
- **Phase 3:** documentation and verification flow patterns are standard.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Strongly grounded in existing repository stack and constraints |
| Features | HIGH | Directly derived from explicit user scope and local-only objective |
| Architecture | HIGH | Current boundaries already exist; changes are operational, not structural |
| Pitfalls | HIGH | Common failure modes are directly relevant to compose-first local stacks |

**Overall confidence:** HIGH

### Gaps to Address

- Confirm exact supporting services to include in default compose vs optional profiles.
- Validate final resource limits against real local workload runs.

## Sources

### Primary (HIGH confidence)
- `.planning/PROJECT.md` — scope and constraints
- `.planning/codebase/ARCHITECTURE.md` — current architecture
- `.planning/codebase/STACK.md` — current technology baseline
- `docker-compose.yml`, `api/Dockerfile`, `web/package.json` — current local/container implementation

### Secondary (MEDIUM confidence)
- `README.md` — local run conventions and current command surface

---
*Research completed: February 7, 2026*
*Ready for roadmap: yes*
