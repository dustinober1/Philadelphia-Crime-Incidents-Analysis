# Roadmap: Crime Incidents Philadelphia - Local Containerized Dev

**Created:** February 7, 2026
**Source Requirements:** `.planning/REQUIREMENTS.md`
**Total v1 Requirements:** 12
**Coverage:** 12/12 mapped (100%)

## Phase Overview

| # | Phase | Goal | Requirements | Status |
|---|-------|------|--------------|--------|
| 1 | Local Compose Baseline | Deliver one-command local bring-up of all required services with local-only defaults | ORCH-01, ORCH-02, ORCH-03, CONF-01, CONF-02, CONF-03 | Complete |
| 2 | Footprint and Runtime Optimization | Reduce image size/build latency and enforce predictable runtime resource budgets | FOOT-01, FOOT-02, FOOT-03 | Complete |
| 3 | Developer UX and Operational Reliability | Make local workflow clear, recoverable, and flexible for advanced local scenarios | DEVX-01, DEVX-02, DEVX-03 | Pending |

## Phase Details

## Phase 1: Local Compose Baseline

**Goal:** A clean clone can bring up web, API, pipeline, and required supporting services using one `docker compose up` command and local defaults.
**Status:** Complete (verified February 7, 2026)

**Requirements:** ORCH-01, ORCH-02, ORCH-03, CONF-01, CONF-02, CONF-03

**Success Criteria:**
1. Running `docker compose up` from repository root starts required local services without extra manual commands.
2. `web`, `api`, and `pipeline` run as distinct services with clear compose service definitions.
3. Healthchecks/dependency gating prevent premature service readiness.
4. Local env contract (`.env.example` and documented variables) is sufficient for baseline startup.
5. Pipeline output location and API read location are explicitly aligned and documented.
6. Baseline local startup works without cloud credentials or mandatory hosted cloud dependencies.

## Phase 2: Footprint and Runtime Optimization

**Goal:** Optimize local containers for size and predictable machine impact while preserving phase 1 functionality.
**Status:** Complete (verified February 7, 2026)

**Requirements:** FOOT-01, FOOT-02, FOOT-03

**Success Criteria:**
1. API, web, and pipeline images use slim and/or multi-stage patterns where practical.
2. Compose file defines CPU and memory limits for long-running default services.
3. Docker build steps are ordered for effective dependency caching during iterative local changes.
4. Optimization changes do not break one-command startup behavior from Phase 1.

## Phase 3: Developer UX and Operational Reliability

**Goal:** Ensure developers can consistently run, troubleshoot, and extend the local compose workflow.

**Requirements:** DEVX-01, DEVX-02, DEVX-03

**Success Criteria:**
1. README documents compose-first local startup as the default development path.
2. README includes tested recovery/reset guidance for common failure states.
3. Optional compose profiles are available for advanced local workflows without changing default startup behavior.
4. Documentation and compose config stay consistent with actual runtime behavior.

## Requirement-to-Phase Validation

| Requirement | Phase |
|-------------|-------|
| ORCH-01 | Phase 1 |
| ORCH-02 | Phase 1 |
| ORCH-03 | Phase 1 |
| CONF-01 | Phase 1 |
| CONF-02 | Phase 1 |
| CONF-03 | Phase 1 |
| FOOT-01 | Phase 2 |
| FOOT-02 | Phase 2 |
| FOOT-03 | Phase 2 |
| DEVX-01 | Phase 3 |
| DEVX-02 | Phase 3 |
| DEVX-03 | Phase 3 |

**Validation:** Every v1 requirement maps to exactly one phase.

---
*Roadmap status: Phase 1 and Phase 2 complete and verified; Phase 3 pending*
