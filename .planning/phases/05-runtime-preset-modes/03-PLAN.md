---
wave: 2
depends_on:
  - 01
files_modified:
  - tests/integration/test_phase5_runtime_preset_modes.py
  - scripts/validate_compose_runtime_mode.sh
  - scripts/validate_compose_runtime_budget.sh
autonomous: true
---

# Plan 03: Runtime Preset Regression Guardrails

## Objective
Add automated checks that lock in preset behavior and protect baseline defaults from accidental drift.

<tasks>
  <task id="03.1" title="Add Phase 5 integration tests for preset rendering and baseline safety">
    <details>
      Create `tests/integration/test_phase5_runtime_preset_modes.py` to assert low-power and high-performance rendered limits for all three services, and verify default mode still renders baseline values.
    </details>
  </task>
  <task id="03.2" title="Wire preset validation script into reproducible local checks">
    <details>
      Ensure `scripts/validate_compose_runtime_mode.sh` can be executed directly and reused by tests to validate both presets and default-regression guardrails with clear failure messaging.
    </details>
  </task>
  <task id="03.3" title="Keep existing runtime budget checks coherent with new presets">
    <details>
      Update or scope existing budget validation so baseline assertions remain explicit and do not mask preset failures; avoid conflating default budget checks with preset-specific checks.
    </details>
  </task>
</tasks>

## Verification Criteria
- New Phase 5 integration tests fail if low-power/high-performance rendered values are missing or incorrect.
- Tests fail if default compose render diverges from current baseline values.
- Existing runtime budget checks continue to pass for default mode.

## must_haves
- Preset behavior is regression-protected in automated tests.
- Default runtime budget safety is explicitly guarded.
- Validation pathways are scriptable and reproducible for local development.
