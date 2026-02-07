---
wave: 2
depends_on:
  - 01
files_modified:
  - docs/local-compose.md
  - README.md
  - scripts/reset_local_stack.sh
  - scripts/validate_local_stack.py
autonomous: true
---

# Plan 02: Recovery and Reset Operational Runbook

## Objective
Provide deterministic, scenario-based recovery and reset procedures so developers can restore a healthy local stack quickly after common failures.

<tasks>
  <task id="02.1" title="Add failure-mode playbooks to local runbook">
    <details>
      Expand `docs/local-compose.md` with compact playbooks for common failure states: unhealthy pipeline/API dependency chain, stale shared volume artifacts, and rebuild/restart after Docker cache or dependency changes.
    </details>
  </task>
  <task id="02.2" title="Add scripted reset helper for reproducible recovery">
    <details>
      Add `scripts/reset_local_stack.sh` that performs a safe reset sequence (`docker compose down -v`, optional image prune guidance, restart command hints) with clear output and non-destructive defaults.
    </details>
  </task>
  <task id="02.3" title="Define post-recovery validation checklist">
    <details>
      Extend `scripts/validate_local_stack.py` usage guidance and README troubleshooting section so every recovery path ends with explicit health and endpoint verification commands.
    </details>
  </task>
</tasks>

## Verification Criteria
- Each documented failure mode has a tested command sequence and expected recovery signal.
- Reset helper script runs successfully and leaves the stack in a known clean state.
- Post-recovery checks prove pipeline artifacts and API health are restored.

## must_haves
- Recovery paths are actionable, not generic prose.
- Reset workflow is repeatable and script-assisted.
- Developers can confirm success quickly after remediation.
