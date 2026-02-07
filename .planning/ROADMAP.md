# Roadmap: Crime Incidents Philadelphia

## Milestones

- ✅ **v1.0 Local Containerized Dev** — Phases 1-3 shipped February 7, 2026. Full archive: `.planning/milestones/v1.0-ROADMAP.md`
- ✅ **v1.1 Local Workflow Enhancements** — Phases 4-6 completed February 7, 2026.

## Current Milestone: v1.1 Local Workflow Enhancements

**Goal:** Improve local runtime confidence and machine-fit behavior while preserving the default compose startup path.

**Requirements:** 9 total (SMOKE-01..05, PRESET-01..04)

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 4 | ✅ Smoke-Check Productization | Make post-start readiness validation canonical and reliable | SMOKE-01, SMOKE-02, SMOKE-03, SMOKE-04, SMOKE-05 | 4 |
| 5 | ✅ Runtime Preset Modes | Introduce low-power and high-performance runtime modes without changing defaults | PRESET-01, PRESET-02, PRESET-03 | 4 |
| 6 | ✅ Preset and Regression Guardrails | Ensure preset behavior and default-mode safety remain stable over time | PRESET-04 | 4 |

## Phase Details

### Phase 4: Smoke-Check Productization

**Goal:** Standardize and harden the post-start smoke-check workflow.
**Status:** Complete (verified February 7, 2026)
**Depends on:** Phase 3 (shipped baseline)
**Requirements:** SMOKE-01, SMOKE-02, SMOKE-03, SMOKE-04, SMOKE-05

**Success criteria:**
1. A documented canonical command validates a running stack without requiring restart.
2. Smoke check fails when `/api/health` is not ready (`ok != true`).
3. Smoke check fails when required exports are missing and prints actionable details.
4. README/runbook sequence documents startup then validation as standard local flow.

### Phase 5: Runtime Preset Modes

**Goal:** Add explicit low-power and high-performance runtime mode presets while preserving default behavior.
**Status:** Complete (verified February 7, 2026)
**Depends on:** Phase 4
**Requirements:** PRESET-01, PRESET-02, PRESET-03

**Success criteria:**
1. Low-power mode command is documented and renders reduced CPU/memory limits for `pipeline`, `api`, and `web`.
2. High-performance mode command is documented and renders increased CPU/memory limits for `pipeline`, `api`, and `web`.
3. Baseline `docker compose up -d --build` command remains unchanged in docs and behavior.
4. Local runbook includes a concise mode-selection guide (default vs low-power vs high-performance).

### Phase 6: Preset and Regression Guardrails

**Goal:** Lock in preset correctness and default-mode safety with automated checks.
**Status:** Complete (verified February 7, 2026)
**Depends on:** Phase 5
**Requirements:** PRESET-04

**Success criteria:**
1. Automated validation checks assert rendered compose behavior for both runtime presets.
2. Automated checks confirm default-mode runtime budget behavior remains intact.
3. Regression checks are wired into existing test/script pathways and documented.
4. Requirements traceability remains fully mapped with no unmapped v1 requirements.

## Coverage

- Total v1.1 requirements: 9
- Mapped to phases: 9
- Unmapped: 0 ✓

---
*Roadmap created: February 7, 2026 for milestone v1.1*
