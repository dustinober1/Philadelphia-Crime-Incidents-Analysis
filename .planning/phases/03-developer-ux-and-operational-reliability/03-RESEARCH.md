# Phase 03 Research: Developer UX and Operational Reliability

## Scope
Phase 03 covers DEVX-01, DEVX-02, and DEVX-03:
- DEVX-01: README makes compose-first local workflow the default
- DEVX-02: Recovery/reset procedures are documented and usable
- DEVX-03: Optional compose profiles support advanced workflows without changing default startup

## Current State Snapshot

### What already exists
- `docker-compose.yml` already defines a solid default stack (`pipeline`, `api`, `web`) with health/dependency gating and resource limits.
- `docs/local-compose.md` already includes startup, troubleshooting logs, and reset (`docker compose down -v`).
- `README.md` has a "Philadelphia Crime Explorer Web Stack" section with local compose startup commands.

### Gaps against Phase 03 goals
- README default narrative is still analysis/CLI-first; compose workflow appears late and does not clearly establish "default local run path" at first touch.
- Recovery guidance exists but is split and lacks explicit scenario-oriented runbooks (e.g., stale volume artifacts, build cache mismatch, unhealthy dependency chain).
- No `profiles` blocks are present in `docker-compose.yml`, so advanced local workflows are not discoverable via compose-native profile controls.

## Implementation Considerations

### DEVX-01 (compose-first README path)
- Promote a concise "Local Compose Quickstart" near the top of README.
- Keep analysis-only workflows, but position them as secondary/alternate modes.
- Ensure command sequence is consistent with actual runtime contract (`cp .env.example .env`, `docker compose up -d --build`, health checks, URLs).

### DEVX-02 (recovery/reset reliability)
- Document high-frequency recovery scenarios with deterministic commands and expected outcomes:
  - Service unhealthy after dependency timeouts
  - Corrupt/missing shared volume artifacts
  - Rebuild after dependency/image drift
- Keep one minimal reset path and one targeted recovery path; avoid over-complicated branching.
- Include a small verification checklist after recovery so developers can quickly confirm stack health.

### DEVX-03 (optional compose profiles)
- Use compose `profiles` for non-default workflows while preserving `docker compose up` default behavior.
- Profiles should be additive and local-only, for example:
  - `ops`: utility/inspection service (e.g., shell toolbox) for troubleshooting
  - `pipeline-once`: one-shot data refresh mode for manual export runs
- Default services must remain unprofiled so baseline command behavior is unchanged.
- Document profile usage and boundaries clearly in README and local runbook.

## Risks and Mitigations
- Risk: README drift from real compose behavior.
  - Mitigation: add integration checks that assert critical README/runbook commands and profile names match compose definitions.
- Risk: profile additions accidentally alter default startup behavior.
  - Mitigation: test both `docker compose config` (default) and `docker compose --profile ... config` outputs to ensure baseline service set remains stable.
- Risk: recovery instructions become stale.
  - Mitigation: include script-backed checks and keep docs tied to tested commands used in integration tests.

## Recommended Plan Shape
- Plan 01 (Wave 1): Reframe README + runbook so compose-first flow is explicit and default.
- Plan 02 (Wave 2): Add operational recovery runbook sections and helper script(s) for repeatable reset/repair.
- Plan 03 (Wave 3): Introduce optional compose profiles plus automated validation/tests to prevent regression.

## Acceptance Signals for Planning
- Clear one-command startup appears as primary local path in README.
- Recovery playbooks are actionable and tested against current compose behavior.
- At least one optional compose profile exists and is documented, with baseline `docker compose up` unchanged.
