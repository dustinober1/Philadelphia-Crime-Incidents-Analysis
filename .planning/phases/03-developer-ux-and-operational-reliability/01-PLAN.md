---
wave: 1
depends_on: []
files_modified:
  - README.md
  - docs/local-compose.md
  - .env.example
autonomous: true
---

# Plan 01: Compose-First Developer Entry Experience

## Objective
Make the compose workflow the unambiguous default local development path while preserving existing analysis guidance as secondary context.

<tasks>
  <task id="01.1" title="Promote compose-first startup to top-level local quickstart">
    <details>
      Reorganize `README.md` so the first operational workflow presented is local compose startup, including env initialization, `docker compose up -d --build`, health verification, and default URLs.
    </details>
  </task>
  <task id="01.2" title="Align README and runbook command contract">
    <details>
      Ensure `README.md` and `docs/local-compose.md` use identical command sequences and variable names for startup and health checks, eliminating drift between docs.
    </details>
  </task>
  <task id="01.3" title="Clarify environment variables required for first run">
    <details>
      Tighten `.env.example` comments and grouping so developers can distinguish required local startup variables from optional cloud-only or analysis-only settings without guesswork.
    </details>
  </task>
</tasks>

## Verification Criteria
- README presents compose-first startup before alternative workflows.
- Copy-paste startup flow from docs succeeds with current compose files.
- Env variable descriptions are consistent across `.env.example`, README, and `docs/local-compose.md`.

## must_haves
- Compose-first path is the documented default local workflow.
- Docs are internally consistent with the actual runtime contract.
- First-run variable requirements are explicit and low-friction.
