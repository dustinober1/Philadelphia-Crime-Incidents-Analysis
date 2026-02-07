---
wave: 2
depends_on:
  - 01
files_modified:
  - README.md
  - docs/local-compose.md
autonomous: true
---

# Plan 02: Runtime Mode Documentation and Operator Guidance

## Objective
Document default vs low-power vs high-performance startup clearly so developers can choose the right mode quickly while preserving the baseline startup flow.

<tasks>
  <task id="02.1" title="Document runtime mode commands in README">
    <details>
      Add a focused runtime mode section that keeps baseline startup first and introduces explicit low-power/high-performance commands using the new helper or env-file approach.
    </details>
  </task>
  <task id="02.2" title="Align local runbook with mode-selection guidance">
    <details>
      Update `docs/local-compose.md` with a concise decision guide (when to use default vs low-power vs high-performance), expected tradeoffs, and copy-paste commands.
    </details>
  </task>
  <task id="02.3" title="Preserve baseline command primacy and non-breaking workflow">
    <details>
      Ensure docs continue to present `docker compose up -d --build` as the standard default path and position presets as optional overlays for constrained or heavy-workload scenarios.
    </details>
  </task>
</tasks>

## Verification Criteria
- README and runbook both include low-power and high-performance commands.
- README and runbook explicitly state that default startup command is unchanged.
- Runbook includes a short mode-selection matrix or bullets describing when to pick each mode.

## must_haves
- Mode-selection guidance is clear, concise, and operationally actionable.
- Documentation is consistent across top-level and runbook sources.
- Default workflow remains the first-class documented startup path.
