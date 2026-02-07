---
wave: 2
depends_on:
  - 01
files_modified:
  - tests/integration/test_phase6_preset_regression_guardrails.py
  - tests/integration/test_phase5_runtime_preset_modes.py
  - scripts/validate_runtime_guardrails.sh
autonomous: true
---

# Plan 02: Regression Automation and Test Wiring

## Objective
Wire Phase 6 guardrails into repeatable integration checks so regressions in preset behavior or default-mode safety are caught automatically.

<tasks>
  <task id="02.1" title="Add Phase 6 integration tests for canonical guardrail command">
    <details>
      Create `tests/integration/test_phase6_preset_regression_guardrails.py` to execute `./scripts/validate_runtime_guardrails.sh` (docker-gated) and assert it is the canonical PRESET-04 automation path.
    </details>
  </task>
  <task id="02.2" title="Add requirements/traceability regression assertions">
    <details>
      Add narrow assertions that PRESET-04 remains mapped to Phase 6 in `.planning/REQUIREMENTS.md` and that phase naming in roadmap/requirements remains coherent.
    </details>
  </task>
  <task id="02.3" title="Keep phase 5 runtime preset tests aligned with canonical pathway">
    <details>
      Update `tests/integration/test_phase5_runtime_preset_modes.py` where needed so existing coverage references the canonical guardrail path without dropping granular checks.
    </details>
  </task>
</tasks>

## Verification Criteria
- New Phase 6 integration tests fail when canonical guardrail command is missing or broken.
- Tests fail if PRESET-04 traceability mapping drifts from Phase 6.
- Existing preset-mode and default-budget checks remain covered and passing.

## must_haves
- PRESET-04 is enforced by automated integration tests.
- Runtime guardrail validation is runnable through a single stable command.
- Traceability regressions are machine-detected, not manual-only.
