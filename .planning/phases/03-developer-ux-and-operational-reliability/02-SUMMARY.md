# Plan 02 Summary: Recovery and Reset Operational Runbook

## Status
Completed

## Work Completed
- Expanded `docs/local-compose.md` with scenario-based recovery playbooks for unhealthy dependency chain, stale shared volume artifacts, and dependency/cache drift.
- Added `scripts/reset_local_stack.sh` as a reproducible reset helper with a non-destructive default and optional dangling image prune.
- Extended `scripts/validate_local_stack.py` to support post-recovery validation via `--skip-startup` and configurable endpoint/timeouts.
- Added README recovery/reset section with explicit command sequence and post-recovery validation checklist.

## Verification
- `bash -n scripts/reset_local_stack.sh`
- `./scripts/reset_local_stack.sh --help`
- `python scripts/validate_local_stack.py --help`
- `rg -n "Recovery playbooks|Post-recovery validation checklist|reset_local_stack|validate_local_stack.py --skip-startup" docs/local-compose.md README.md`

## Commits
- `6f12ceb` `feat(03-02): add recovery playbooks and reset helper`
