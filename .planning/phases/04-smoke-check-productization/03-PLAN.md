---
wave: 2
depends_on:
  - 01
files_modified:
  - tests/integration/test_phase4_smoke_check_productization.py
  - scripts/validate_local_stack.py
  - README.md
  - docs/local-compose.md
autonomous: true
---

# Plan 03: Smoke-Check Regression and Conformance Guardrails

## Objective
Add automated conformance checks that prevent regression of smoke-check behavior and canonical documentation contract over time.

<tasks>
  <task id="03.1" title="Add Phase 4 integration tests for docs command conformance">
    <details>
      Create `tests/integration/test_phase4_smoke_check_productization.py` that asserts the canonical smoke-check command string appears in both README and runbook startup workflow sections.
    </details>
  </task>
  <task id="03.2" title="Add script-behavior tests for key failure conditions">
    <details>
      Add test cases for readiness false/missing export/unreachable web paths and verify failures are explicit enough to guide remediation.
    </details>
  </task>
  <task id="03.3" title="Ensure local validation pathway references remain coherent">
    <details>
      Verify docs and script flags stay aligned (especially `--skip-startup`, endpoint defaults, and timeout semantics) so automation and manual usage do not diverge.
    </details>
  </task>
</tasks>

## Verification Criteria
- New Phase 4 integration tests fail when canonical smoke-check command drifts in docs.
- Script tests fail when readiness/export/web checks become non-blocking.
- Existing phase tests continue passing without changing default startup behavior.

## must_haves
- Smoke-check behavior is regression-protected by automated tests.
- Canonical command documentation cannot silently drift.
- Default compose startup contract remains unchanged.
