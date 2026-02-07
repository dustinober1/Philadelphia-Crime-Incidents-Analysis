---
wave: 2
depends_on:
  - 01
files_modified:
  - README.md
  - docs/local-compose.md
autonomous: true
---

# Plan 02: Canonical Smoke-Check Documentation Flow

## Objective
Promote smoke-check usage into the default local startup workflow so the standard path is explicitly start -> verify -> use.

<tasks>
  <task id="02.1" title="Promote canonical smoke-check into README startup sequence">
    <details>
      Update the primary local compose quickstart in `README.md` so post-start verification includes the canonical smoke-check command as the standard validation step, not only manual curl checks.
    </details>
  </task>
  <task id="02.2" title="Align runbook startup and validation sequence with README">
    <details>
      Update `docs/local-compose.md` startup section to mirror README ordering and command text exactly for canonical smoke-check usage, preserving existing troubleshooting and recovery sections.
    </details>
  </task>
  <task id="02.3" title="Add explicit expected-pass and expected-fail signals in docs">
    <details>
      Document what success looks like and what common smoke-check failures indicate (API not ready, missing exports, web endpoint failure) with brief remediation pointers.
    </details>
  </task>
</tasks>

## Verification Criteria
- README default startup flow shows start -> smoke-check -> use.
- Runbook startup flow uses the same canonical command and ordering as README.
- Docs call out that smoke-check validates API health readiness, web reachability, and required exports.

## must_haves
- Smoke-check usage is part of the default workflow, not buried in recovery-only guidance.
- Documentation is consistent across top-level and runbook sources.
- Developers can quickly interpret pass/fail outcomes.
