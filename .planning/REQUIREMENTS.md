# Requirements: Crime Incidents Philadelphia - v1.1 Local Workflow Enhancements

**Defined:** February 7, 2026
**Core Value:** One `docker compose up` command reliably brings up the complete stack locally with small, resource-constrained containers.

## v1 Requirements

### Smoke Checks

- [x] **SMOKE-01**: Developer can run one documented post-start smoke-check command that validates a running local compose stack without requiring a restart.
- [x] **SMOKE-02**: Smoke check verifies API health endpoint reports ready (`ok=true`) before passing.
- [x] **SMOKE-03**: Smoke check verifies the local web endpoint is reachable and returns a successful HTTP response.
- [x] **SMOKE-04**: Smoke check fails when API reports missing required exports/artifacts and prints actionable failure details.
- [x] **SMOKE-05**: Local docs place smoke-check usage in the standard startup workflow (start -> verify -> use).

### Runtime Presets

- [ ] **PRESET-01**: Developer can run a documented low-power runtime mode that applies explicit reduced CPU/memory limits for pipeline, API, and web services.
- [ ] **PRESET-02**: Developer can run a documented high-performance runtime mode that applies explicit increased CPU/memory limits for heavier local analysis workflows.
- [ ] **PRESET-03**: Default startup command (`docker compose up -d --build`) remains unchanged and still uses the documented baseline runtime budget values.
- [ ] **PRESET-04**: Automated validation checks verify both preset render behavior and default-mode regression safety.

## v2 Requirements

Deferred to future milestone planning.

### Local Workflow Enhancements (Deferred)

- **LWF-03**: Smoke-check script can emit machine-readable structured output for CI and automation consumers.
- **LWF-04**: Smoke-check workflow validates additional high-value API endpoints beyond baseline health/readiness.
- **LWF-05**: Runtime mode can be auto-selected from host resource detection.

## Out of Scope

Explicitly excluded for this milestone.

| Feature | Reason |
|---------|--------|
| Cloud deployment/runtime presets | Scope remains local-hosting only |
| New product-facing API/frontend capabilities unrelated to local workflow reliability | Milestone is operational hardening only |
| More than two non-default runtime presets | Adds complexity before validating low-power/high-performance split |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SMOKE-01 | Phase 4 | Complete |
| SMOKE-02 | Phase 4 | Complete |
| SMOKE-03 | Phase 4 | Complete |
| SMOKE-04 | Phase 4 | Complete |
| SMOKE-05 | Phase 4 | Complete |
| PRESET-01 | Phase 5 | Pending |
| PRESET-02 | Phase 5 | Pending |
| PRESET-03 | Phase 5 | Pending |
| PRESET-04 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 9 total
- Mapped to phases: 9
- Unmapped: 0 ✓

---
*Requirements defined: February 7, 2026*
*Last updated: February 7, 2026 after Phase 4 completion*
