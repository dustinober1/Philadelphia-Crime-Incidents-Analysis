# Phase 1: Local Compose Baseline - Context

**Gathered:** 2026-02-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver one-command local compose startup for `web`, `api`, `pipeline`, and required supporting services using local-only defaults. This phase defines baseline startup behavior, readiness gating, environment contract, and pipeline/API data handoff for local development.

</domain>

<decisions>
## Implementation Decisions

### Service startup contract
- Default `docker compose up` starts all core services: `web`, `api`, `pipeline`, plus required dependencies.
- If any core service exits during startup, baseline startup is considered failed.
- Pipeline runs as a continuous long-running service in default startup.
- Startup prioritizes strict correctness: fail early on any mismatch or blocker.

### Readiness and dependency gating
- Use explicit health checks as readiness source of truth for service readiness.
- Use hybrid dependency gating: block startup on critical dependencies and allow retry behavior for non-critical dependencies.
- Use moderate healthcheck timing to balance startup speed and false-positive risk.
- Use service-specific unhealthy-dependency behavior after startup: API can degrade, pipeline should fail/retry, web remains up where possible.

### Environment variable contract
- Missing required environment variables fail startup immediately with clear errors.
- `.env.example` includes required variables and common optional toggles.
- Baseline startup must work without cloud credentials; cloud credentials may be optionally supplied.
- Config precedence is `docker compose` environment overrides, then `.env`, then image defaults.

### Pipeline/API data alignment
- Use a named volume as the default shared data handoff path between pipeline and API.
- Persist data across restarts by default.
- Enforce contract mismatches with fail-fast behavior and clear errors.
- API serves the latest successful pipeline snapshot only.

### Claude's Discretion
- Exact healthcheck probe commands/threshold values.
- Which dependencies are classified critical vs non-critical per service.
- Concrete env var naming and defaults for optional toggles.
- Exact directory/path naming inside the shared volume.

</decisions>

<specifics>
## Specific Ideas

No external product references were specified. Priority is strict, deterministic local startup behavior over best-effort convenience.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 01-local-compose-baseline*
*Context gathered: 2026-02-06*
