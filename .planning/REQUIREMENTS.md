# Requirements: Crime Incidents Philadelphia - Local Containerized Dev

**Defined:** February 7, 2026
**Core Value:** One `docker compose up` command reliably brings up the complete stack locally with small, resource-constrained containers.

## v1 Requirements

### Orchestration

- [ ] **ORCH-01**: Developer can start required local services (`web`, `api`, `pipeline`, and supporting services) with one `docker compose up` command from repository root.
- [ ] **ORCH-02**: Each major service boundary (`web`, `api`, `pipeline`) runs in its own container so services can be started, stopped, and debugged independently.
- [ ] **ORCH-03**: Local startup uses health checks and dependency gating so services wait for required dependencies before accepting traffic.

### Runtime Footprint

- [ ] **FOOT-01**: API, web, and pipeline images use slim and/or multi-stage build patterns to reduce final image size compared with naive single-stage builds.
- [ ] **FOOT-02**: Compose configuration enforces CPU and memory limits for each long-running service in the default local profile.
- [ ] **FOOT-03**: Docker build layers are structured to maximize dependency caching and reduce rebuild time for iterative local development.

### Local Config and Data Contract

- [ ] **CONF-01**: Project provides a reproducible local environment variable contract (documented variables and example file) required for compose startup.
- [ ] **CONF-02**: Pipeline and API share an explicit, documented artifact path/volume contract so freshly exported data is what API serves locally.
- [ ] **CONF-03**: Local default startup path does not require cloud credentials or hosted cloud services for baseline functionality.

### Developer UX

- [ ] **DEVX-01**: README local development section makes the compose-first workflow the default path for running the system.
- [ ] **DEVX-02**: Documentation includes local recovery/reset procedures for common failure modes (rebuild, volume reset, re-export data).
- [ ] **DEVX-03**: Compose configuration supports optional profiles for non-default advanced workflows without changing the default startup command.

## v2 Requirements

### Local Workflow Enhancements

- **LWF-01**: Add automated local smoke checks that run after compose startup to verify endpoint and artifact readiness.
- **LWF-02**: Add per-profile presets for low-power laptop mode vs high-performance local analysis mode.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Cloud deployment changes (Cloud Run/Firebase/prod infra) | Scope is explicitly local-hosted only for this milestone |
| Non-local managed services as required startup dependencies | Violates local-only goal and increases setup friction |
| Features unrelated to local containerized operation | Deferred until local-first runtime is complete |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| ORCH-01 | Unmapped | Pending |
| ORCH-02 | Unmapped | Pending |
| ORCH-03 | Unmapped | Pending |
| FOOT-01 | Unmapped | Pending |
| FOOT-02 | Unmapped | Pending |
| FOOT-03 | Unmapped | Pending |
| CONF-01 | Unmapped | Pending |
| CONF-02 | Unmapped | Pending |
| CONF-03 | Unmapped | Pending |
| DEVX-01 | Unmapped | Pending |
| DEVX-02 | Unmapped | Pending |
| DEVX-03 | Unmapped | Pending |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 0
- Unmapped: 12 ⚠️

---
*Requirements defined: February 7, 2026*
*Last updated: February 7, 2026 after initial definition*
