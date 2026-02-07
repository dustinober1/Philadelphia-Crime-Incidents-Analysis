# Phase 4 Research: Smoke-Check Productization

## Objective
Identify what is already implemented versus what must be productized to satisfy Phase 4 requirements (SMOKE-01..05) with minimal churn.

## Current Baseline

### Existing smoke-check implementation
- `scripts/validate_local_stack.py` already validates:
  - Compose rendering (`docker compose config`)
  - API readiness via `ok == true` (`wait_for_health`)
  - Web reachability via HTTP status (`wait_for_http_ok`)
  - Missing export detection via `missing_exports` with explicit failure
- Script already supports `--skip-startup`, which enables post-start validation without restart.

### Current docs placement
- `README.md` and `docs/local-compose.md` document startup + basic readiness checks (`docker compose ps`, `curl /api/health`).
- `python scripts/validate_local_stack.py --skip-startup` is currently documented in recovery/post-recovery sections, not as the canonical startup verification command.

### Existing quality guardrails
- Integration tests exist for Phase 3 doc/config drift patterns in `tests/integration/test_phase3_devx_reliability.py`.
- No dedicated Phase 4 integration checks currently enforce smoke-check command contract in docs and behavior.

## Gap Analysis vs Requirements

- SMOKE-01: Partially met in capability; not yet canonicalized as the primary post-start verification command.
- SMOKE-02: Behavior is implemented (`ok == true`) but not protected by focused tests.
- SMOKE-03: Behavior is implemented (web URL HTTP success) but not protected by focused tests.
- SMOKE-04: Missing exports fail currently; failure detail could be made more actionable/consistent.
- SMOKE-05: Docs include command, but not in the default startup flow as standard start -> verify -> use.

## Implementation Guidance

- Productize around the existing validator instead of introducing a second smoke-check mechanism.
- Preserve backwards compatibility of `scripts/validate_local_stack.py` while improving failure detail clarity.
- Add Phase 4-specific tests that:
  - enforce docs contain one canonical post-start smoke-check command
  - validate script behavior for readiness and missing-export failure paths
- Keep default compose startup command unchanged (`docker compose up -d --build`) and position smoke-check immediately after startup.

## Risks and Mitigations

- Risk: Doc drift between README and runbook.
  - Mitigation: Add tests that assert command parity in both files.
- Risk: Integration tests become flaky if they require live compose startup.
  - Mitigation: Prefer unit/integration tests with mocks for script behavior plus lightweight doc assertions.
- Risk: Ambiguous "canonical command" if multiple alternatives are documented equally.
  - Mitigation: Use one named command sequence and mirror exact string across docs.
