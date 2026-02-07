---
wave: 2
depends_on:
  - 01
files_modified:
  - docker-compose.yml
  - .env.example
  - README.md
autonomous: true
---

# Plan 02: Runtime Resource Budgets in Default Compose Profile

## Objective
Enforce predictable CPU and memory consumption for long-running local services without breaking default `docker compose up` startup behavior.

<tasks>
  <task id="02.1" title="Define per-service CPU and memory limits for default services">
    <details>
      Add explicit CPU and memory budgets for `pipeline`, `api`, and `web` in `docker-compose.yml` using compose-supported resource keys that apply in local non-swarm usage.
    </details>
  </task>
  <task id="02.2" title="Make resource values configurable with sensible defaults">
    <details>
      Introduce environment-backed resource settings in `.env.example` (or inline defaults) so developers can tune budgets while preserving predictable defaults for first-run local startup.
    </details>
  </task>
  <task id="02.3" title="Document budget behavior and tuning guidance">
    <details>
      Update `README.md` with a compact section explaining default limits, symptoms of under-allocation, and safe adjustment workflow.
    </details>
  </task>
</tasks>

## Verification Criteria
- `docker compose config` renders valid configuration with resource limits applied.
- `docker compose up` still starts `pipeline`, `api`, and `web` with Phase 1 health/dependency behavior intact.
- Resource limit overrides via `.env` take effect and are reflected in rendered compose config.

## must_haves
- Default profile enforces explicit CPU and memory limits for all long-running core services.
- Limits are adjustable without editing compose structure.
- Phase 1 one-command startup behavior remains intact.
