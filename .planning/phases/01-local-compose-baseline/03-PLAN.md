---
wave: 3
depends_on:
  - 01
  - 02
files_modified:
  - .env.example
  - web/.env.example
  - README.md
  - docs/local-compose.md
  - tests/integration/test_local_compose_baseline.py
autonomous: true
---

# Plan 03: Environment Contract and Local Startup Documentation

## Objective
Define and document the compose-first local environment contract so baseline startup is reproducible, local-only, and operationally clear.

<tasks>
  <task id="03.1" title="Codify required and optional env contract">
    <details>
      Update `.env.example` (and `web/.env.example` if needed) with required compose vars, optional toggles, and defaults aligned to local-only startup. Ensure required missing values fail fast with clear guidance.
    </details>
  </task>
  <task id="03.2" title="Rewrite local runbook around compose-first flow">
    <details>
      Update README and add focused local compose doc that makes `docker compose up` the default path, including startup checks, troubleshooting, reset, and data refresh expectations.
    </details>
  </task>
  <task id="03.3" title="Add baseline integration verification">
    <details>
      Add an integration test/script that validates compose config, startup expectations, and key readiness endpoints/contract checks for Phase 1 acceptance.
    </details>
  </task>
</tasks>

## Verification Criteria
- `.env.example` and docs are sufficient for first-time local startup without cloud credentials.
- README default path is compose-first and matches actual runtime behavior.
- Integration verification covers core startup and readiness contract checks.

## must_haves
- Local env contract is explicit and reproducible.
- One-command startup behavior is documented as default.
- Baseline flow does not require cloud credentials or hosted cloud dependencies.
