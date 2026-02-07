---
wave: 2
depends_on:
  - 01
files_modified:
  - docker-compose.yml
  - api/main.py
  - api/services/data_loader.py
  - pipeline/refresh_data.py
  - pipeline/compose_entrypoint.sh
  - scripts/validate_local_stack.py
autonomous: true
---

# Plan 02: Readiness, Dependency Gating, and Data Contract Enforcement

## Objective
Implement strict readiness/dependency gating and enforce the pipeline/API shared data contract with fail-fast startup behavior.

<tasks>
  <task id="02.1" title="Add healthchecks and dependency gating in compose">
    <details>
      Configure healthchecks for `pipeline`, `api`, and `web` with moderate probe intervals/timeouts/start periods. Gate startup order using healthy dependency conditions: API waits on pipeline; web waits on API.
    </details>
  </task>
  <task id="02.2" title="Enforce shared-volume data contract">
    <details>
      Define and use one named volume for pipeline write + API read. Standardize output/read paths and fail startup with clear errors when required artifact files are missing or path contract is broken.
    </details>
  </task>
  <task id="02.3" title="Implement service-specific unhealthy behavior">
    <details>
      Align runtime behavior with context decisions: API can degrade after startup where possible, pipeline should fail/retry, and web stays up if API is temporarily degraded.
    </details>
  </task>
</tasks>

## Verification Criteria
- Compose healthchecks report healthy for all core services under normal startup.
- API does not report healthy until required pipeline artifacts exist.
- Breaking the shared path contract causes clear, fail-fast startup errors.
- Restarting services preserves pipeline artifacts via named volume.

## must_haves
- Healthchecks are source of truth for readiness.
- Startup order is dependency-gated on critical services.
- Pipeline/API handoff is explicit, persistent, and contract-validated.
- Contract mismatches fail fast with actionable messages.
