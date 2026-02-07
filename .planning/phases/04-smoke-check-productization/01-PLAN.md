---
wave: 1
depends_on: []
files_modified:
  - scripts/validate_local_stack.py
  - tests/test_validate_local_stack.py
autonomous: true
---

# Plan 01: Canonical Smoke-Check Contract and Validator Hardening

## Objective
Define and harden a single post-start smoke-check command contract around the existing validator so readiness failures are explicit, actionable, and test-covered.

<tasks>
  <task id="01.1" title="Lock canonical post-start validation command semantics">
    <details>
      Confirm `python scripts/validate_local_stack.py --skip-startup` is the canonical smoke-check entrypoint and ensure script behavior is stable for post-start checks (no restart path when `--skip-startup` is set, deterministic exit codes, and clear success output).
    </details>
  </task>
  <task id="01.2" title="Improve actionable failure details for health and export errors">
    <details>
      Refine validator error handling so failures include actionable context (which endpoint failed, readiness payload when `ok != true`, and missing export names). Keep output concise and script-friendly.
    </details>
  </task>
  <task id="01.3" title="Add focused validator tests for readiness, web reachability, and missing exports">
    <details>
      Add test coverage that isolates core behavior without requiring Docker runtime: `ok == true` gating, web HTTP success gating, and explicit failure when `missing_exports` is non-empty.
    </details>
  </task>
</tasks>

## Verification Criteria
- Script exits non-zero when API readiness does not report `ok=true`.
- Script exits non-zero when `missing_exports` is present and prints artifact names.
- Script exits non-zero when web endpoint is unreachable/non-success.
- `--skip-startup` path never invokes compose startup.

## must_haves
- One stable smoke-check command contract exists and is test-backed.
- API readiness and export integrity are strict pass/fail gates.
- Failure output is actionable for local remediation.
