---
wave: 1
depends_on: []
files_modified:
  - scripts/validate_runtime_guardrails.sh
  - Makefile
  - scripts/validate_compose_runtime_mode.sh
  - scripts/validate_compose_runtime_budget.sh
autonomous: true
---

# Plan 01: Canonical Runtime Guardrail Entry Point

## Objective
Create one canonical command pathway that deterministically validates preset rendering and default runtime-budget regression safety using existing validators.

<tasks>
  <task id="01.1" title="Add canonical guardrail wrapper script">
    <details>
      Add `scripts/validate_runtime_guardrails.sh` that runs `validate_compose_runtime_mode.sh` and `validate_compose_runtime_budget.sh` in sequence, preserves non-zero exits, and prints concise stage-level pass/fail output.
    </details>
  </task>
  <task id="01.2" title="Expose guardrail execution through Makefile target">
    <details>
      Add a Make target (for example `check-runtime-guardrails`) that invokes the canonical wrapper script so operators have a stable entrypoint in standard project commands.
    </details>
  </task>
  <task id="01.3" title="Harden validator script contract for orchestration use">
    <details>
      Normalize script output and exit semantics as needed so both existing validators can be safely composed by wrapper/test pathways without ambiguous success conditions.
    </details>
  </task>
</tasks>

## Verification Criteria
- `./scripts/validate_runtime_guardrails.sh` runs both validator scripts and fails fast on first error.
- `make check-runtime-guardrails` executes the same validation pathway.
- Existing validator scripts remain independently executable and backward-compatible.

## must_haves
- A single canonical PRESET-04 validation command exists.
- Preset render checks and default-regression checks are both included in the canonical path.
- Guardrail command has deterministic non-zero behavior on failure.
