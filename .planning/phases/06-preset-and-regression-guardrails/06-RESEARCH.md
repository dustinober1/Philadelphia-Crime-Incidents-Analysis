# Phase 06 Research: Preset and Regression Guardrails

## Objective
Research what remains to fully satisfy PRESET-04: durable automated checks that validate both runtime preset rendering and default-mode regression safety through standard local validation pathways.

## Current Baseline (Observed)
- Preset rendering is already validated by `scripts/validate_compose_runtime_mode.sh` (`default`, `low-power`, `high-performance`).
- Default runtime budgets are already validated by `scripts/validate_compose_runtime_budget.sh`.
- Integration coverage exists in `tests/integration/test_phase5_runtime_preset_modes.py`.
- Documentation references both validation scripts in `README.md` and `docs/local-compose.md`.
- `Makefile` currently lacks a canonical runtime guardrail target, so there is no single stable entrypoint for running the full PRESET-04 check set.
- Requirements traceability still marks `PRESET-04` as pending in `.planning/REQUIREMENTS.md`.

## Design Constraints from Requirements
- PRESET-04 requires automated checks for both preset render correctness and baseline default-mode safety.
- Phase 6 must prioritize long-term safety and reproducible execution, not introduce new runtime modes.
- Existing default startup contract (`docker compose up -d --build`) must remain unchanged.

## Recommended Implementation Direction
1. Introduce a single canonical guardrail entrypoint script (or make target) that runs both existing validators in a deterministic order with actionable output.
2. Add Phase 6 integration tests that exercise this canonical entrypoint and assert docs/reference parity for the guardrail command.
3. Add lightweight requirements traceability assertions to prevent PRESET-04 mapping drift in planning docs.
4. Update README and runbook to present the new guardrail command as the canonical PRESET-04 validation path.

## Tradeoffs
- Consolidating checks under one command improves operability and reduces drift risk, at the cost of one extra wrapper script/target to maintain.
- Adding traceability assertions in tests introduces minor coupling to planning docs, but catches roadmap/requirements contract regressions early.

## Risks and Mitigations
- Risk: duplicate validation logic across scripts.
  - Mitigation: wrapper should orchestrate existing scripts, not reimplement their checks.
- Risk: docs/tests drift from canonical command.
  - Mitigation: add explicit integration assertions for command strings in README/runbook.
- Risk: brittle traceability checks from broad text matching.
  - Mitigation: assert narrow, stable requirement/phase mapping lines rather than large sections.

## Planning Guidance
- Build guardrail orchestration first, then enforce via integration tests, then align docs and requirement traceability references.
- Keep all changes local-first and compatible with existing phase test patterns.
