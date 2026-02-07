# Plan 02 Summary: Canonical Smoke-Check Documentation Flow

## Status
Completed

## Work Completed
- Updated `README.md` startup readiness flows to include the canonical command: `python scripts/validate_local_stack.py --skip-startup`.
- Updated `docs/local-compose.md` one-command startup flow with the same canonical command and ordering.
- Added explicit pass/fail interpretation guidance in both docs for:
  - API readiness not ready (`ok!=true`)
  - missing required exports
  - unreachable web endpoint

## Verification
- `rg -n "python scripts/validate_local_stack.py --skip-startup|Local compose smoke check passed|API health check failed ... ok!=true|API health missing required exports ...|Web endpoint check failed ..." README.md docs/local-compose.md`

## Commits
- `2f6b639` `docs(04-02): standardize startup smoke-check workflow`
