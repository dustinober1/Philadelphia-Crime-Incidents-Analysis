# Safety Gates for Repository Cleanup

This document defines safety checks to prevent accidental removal of active code during repository cleanup operations.

## Before Any Cleanup Operation

### Gate 1: Git Status Check

Verify workspace is clean before cleanup:

```bash
git status --porcelain
```

Expected output: Empty (no uncommitted changes)

If files show as modified:
- Review changes: git diff
- Commit or stash changes before cleanup
- Do NOT proceed with cleanup in dirty state

Rationale: Cleanup should happen on clean baseline. Removes confusion about what files were changed by cleanup operations vs. existing uncommitted work.

### Gate 2: Test Baseline

Verify tests pass before cleanup:

```bash
pytest tests/ -m "not slow" --maxfail=1 -q --no-cov
```

Expected output: All tests pass (no failures)

If tests fail:
- Fix failing tests before cleanup
- Document which tests are failing and why
- Do NOT proceed with cleanup if baseline is broken

Rationale: Cleanup should not be blamed for test failures that existed before cleanup. Establish known-good state.

### Gate 3: Import Validation

Verify package imports work before cleanup:

```bash
python -c "import analysis, api, pipeline; print('OK')"
```

Expected output: No import errors

If imports fail:
- Fix import errors before cleanup
- Check for missing dependencies
- Do NOT proceed with cleanup if packages don't import

Rationale: Ensures cleanup doesn't break on already-broken code.

## During Cleanup Operations

### Gate 4: Quiescent Check (for artifact removal)

Before removing .pyc, __pycache__, or other artifacts:

```bash
make dev-api &
API_PID=$!
sleep 5  # Wait for API to start

# Run checks
curl http://localhost:8000/health
pytest tests/test_api_endpoints.py --fast

# Stop API
kill $API_PID
```

Rationale: Ensure services aren't actively generating artifacts while we're cleaning.

### Gate 5: File Usage Check (for dead code deletion)

Before deleting a function or class:

```bash
grep -r "function_name_or_class_name" . --include="*.py" | grep -v "test_"
```

Expected: Zero matches (not used in non-test code)

If matches found:
- Investigate usage (dynamic import, reflection, string-based imports)
- Mark entry as MANUAL in dead-code-review.md
- Do NOT delete without understanding usage

Rationale: Code may be used dynamically (CLI, FastAPI routes, configuration files). Vulture can't detect all usage patterns.

## After Cleanup Operations

### Gate 6: Post-Cleanup Test Verification

After each cleanup operation, verify tests still pass:

```bash
pytest tests/ -m "not slow" --maxfail=1 -q --no-cov
```

If tests fail:
- Review which tests failed
- Check if failure is related to cleanup changes
- Use git diff to see what changed
- Revert cleanup if tests are broken by deletions

Rationale: Immediate feedback on whether deletions broke functionality.

### Gate 7: Post-Cleanup Import Validation

After removing code, verify imports still work:

```bash
python -c "import analysis, api, pipeline; print('OK')"
ruff check analysis api pipeline --select F401
```

Expected: No import errors, no unused imports (Ruff F401)

If errors appear:
- Investigate missing imports
- Check for cyclic import issues
- Restore deleted code if needed

Rationale: Ensures imports are still valid after deletions.

## Emergency Recovery

### Undo Deletions

If cleanup broke something:

```bash
git status                 # See what was deleted
git checkout HEAD -- .     # Restore all deletions
```

If you committed cleanup changes:
```bash
git revert HEAD            # Revert last commit
git log --oneline -5       # Find cleanup commit hash
git revert <hash>         # Revert specific commit
```

### Test Coverage Rollback

If coverage decreased unexpectedly:
```bash
pytest --cov=analysis --cov=api --cov=pipeline --cov-report=term
```

Compare to baseline coverage (88.95% from Phase 13):
- If coverage dropped < 1%, acceptable variation
- If coverage dropped > 1%, investigate and revert

## Best Practices

1. **Commit after each major cleanup operation** (not after every single file)
2. **Review git diff thoroughly** before committing deletions
3. **Run tests frequently** during multi-file deletions
4. **Keep review documents** (dead-code-review.md, deprecated-content-review.md) for reference
5. **Document reasoning** for KEEP/DELETE decisions in review files
6. **Never delete from dirty workspace** (commit or stash first)

## Cleanup Command Reference

Safe cleanup operations with built-in gates:

```bash
# Full cleanup (all gates)
make clean

# Step-by-step with gates
git status                           # Gate 1: Clean workspace
pytest tests/ -m "not slow" -q --no-cov  # Gate 2: Test baseline
pyclean .                            # Remove artifacts
pytest tests/ -m "not slow" -q --no-cov  # Gate 6: Test after cleanup
git commit -m "chore: remove Python artifacts"  # Commit changes

# Dead code cleanup with gates
git status                           # Gate 1
pytest tests/ -m "not slow" -q --no-cov  # Gate 2
vulture analysis/ api/ pipeline/     # Generate report
# [Manual review in dead-code-review.md]
# [Delete entries marked DELETE, one at a time]
pytest tests/ -m "not slow" -q --no-cov  # Gate 6 after each deletion
git diff                             # Review deletions
git commit -m "refactor: remove dead code"
```
