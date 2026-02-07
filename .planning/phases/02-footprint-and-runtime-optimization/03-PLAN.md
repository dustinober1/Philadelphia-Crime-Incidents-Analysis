---
wave: 3
depends_on:
  - 01
  - 02
files_modified:
  - scripts/benchmark_container_builds.sh
  - scripts/validate_compose_runtime_budget.sh
  - docs/local-compose.md
  - tests/integration/test_phase2_footprint_runtime.py
autonomous: true
---

# Plan 03: Optimization Verification and Regression Guardrails

## Objective
Add repeatable checks that prove footprint/runtime improvements and prevent regressions against Phase 1 startup guarantees.

<tasks>
  <task id="03.1" title="Add reproducible build-cache and footprint benchmark script">
    <details>
      Create `scripts/benchmark_container_builds.sh` to run first-build and warm-build measurements for `api`, `pipeline`, and `web`, capturing timings and context/image size signals for comparison.
    </details>
  </task>
  <task id="03.2" title="Add runtime-budget validation script">
    <details>
      Create `scripts/validate_compose_runtime_budget.sh` to assert compose resource limits are present for core services in rendered config and fail with actionable output if missing.
    </details>
  </task>
  <task id="03.3" title="Extend docs and integration checks for phase acceptance">
    <details>
      Update `docs/local-compose.md` and add/extend integration verification to cover: optimized image builds succeed, compose limits are enforced, and baseline startup/health remains functional.
    </details>
  </task>
</tasks>

## Verification Criteria
- Benchmark script runs successfully and produces comparable cold/warm build metrics.
- Runtime-budget validation script fails when limits are removed and passes when present.
- Integration checks confirm phase-1 startup contract still works after optimization changes.

## must_haves
- Optimization claims are backed by repeatable, scriptable checks.
- Resource-budget enforcement is automatically verifiable.
- Regression guardrails protect one-command startup behavior.
