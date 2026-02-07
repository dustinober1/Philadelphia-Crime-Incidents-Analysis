---
wave: 3
depends_on:
  - 01
  - 02
files_modified:
  - docker-compose.yml
  - .env.example
  - README.md
  - docs/local-compose.md
  - scripts/validate_compose_profiles.sh
  - tests/integration/test_phase3_devx_reliability.py
autonomous: true
---

# Plan 03: Optional Compose Profiles and UX Regression Guardrails

## Objective
Introduce optional compose profiles for advanced local workflows and add regression checks that protect default startup behavior and documentation accuracy.

<tasks>
  <task id="03.1" title="Add optional advanced compose profiles without altering default stack">
    <details>
      Update `docker-compose.yml` to include profile-gated auxiliary workflow(s) (for example, one-shot pipeline refresh and/or troubleshooting utility container) while keeping default `docker compose up` behavior unchanged.
    </details>
  </task>
  <task id="03.2" title="Document profile usage and boundaries">
    <details>
      Update README and `docs/local-compose.md` with profile names, when to use them, and explicit confirmation that profiles are optional overlays on top of the default startup path.
    </details>
  </task>
  <task id="03.3" title="Add profile and documentation conformance checks">
    <details>
      Add `scripts/validate_compose_profiles.sh` and `tests/integration/test_phase3_devx_reliability.py` to assert: default config remains stable, profile config renders correctly, and docs mention the supported profile commands and recovery workflow.
    </details>
  </task>
</tasks>

## Verification Criteria
- `docker compose config` (default) still renders core baseline services unchanged.
- `docker compose --profile <name> config` renders valid optional services.
- Integration tests fail if profile names/commands in docs diverge from compose configuration.

## must_haves
- Advanced workflows are opt-in via compose profiles.
- Default one-command startup remains intact.
- Automated checks guard against doc/config drift.
