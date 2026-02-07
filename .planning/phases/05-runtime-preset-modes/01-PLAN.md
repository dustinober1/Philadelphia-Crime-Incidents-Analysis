---
wave: 1
depends_on: []
files_modified:
  - docker-compose.yml
  - .env.example
  - .env.runtime.low-power
  - .env.runtime.high-performance
  - scripts/compose_with_runtime_mode.sh
  - scripts/validate_compose_runtime_mode.sh
autonomous: true
---

# Plan 01: Runtime Preset Contract and Rendering Tooling

## Objective
Introduce explicit runtime preset contracts (`default`, `low-power`, `high-performance`) that render deterministic CPU/memory limits for `pipeline`, `api`, and `web` without altering default startup behavior.

<tasks>
  <task id="01.1" title="Define preset budget contract and source of truth">
    <details>
      Establish concrete CPU/memory values for low-power and high-performance presets and codify them in versioned env templates (for example `.env.runtime.low-power` and `.env.runtime.high-performance`) while preserving existing baseline values in `.env.example`.
    </details>
  </task>
  <task id="01.2" title="Add preset-aware compose helper command">
    <details>
      Add `scripts/compose_with_runtime_mode.sh` to wrap compose startup/config rendering with explicit mode selection and safe defaults. The helper must keep `docker compose up -d --build` as the unchanged baseline path and only apply preset env files when mode is explicitly requested.
    </details>
  </task>
  <task id="01.3" title="Add preset rendering validator for service-level budgets">
    <details>
      Add `scripts/validate_compose_runtime_mode.sh` that asserts rendered `cpus` and `mem_limit` for `pipeline`, `api`, and `web` match expected preset values for both low-power and high-performance modes.
    </details>
  </task>
</tasks>

## Verification Criteria
- `docker compose up -d --build` with baseline env renders current default runtime limits unchanged.
- Preset helper renders lower limits for low-power mode across all three services.
- Preset helper renders higher limits for high-performance mode across all three services.
- Validation script fails with actionable output when rendered limits diverge from preset contract.

## must_haves
- Two explicit non-default runtime presets exist with deterministic budgets.
- Preset selection is opt-in; default startup contract is unchanged.
- Preset correctness is machine-verifiable from rendered compose config.
