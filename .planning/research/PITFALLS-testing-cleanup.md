# Testing & Cleanup Pitfalls Research

**Domain:** Adding comprehensive test coverage (95%+) and repository cleanup to brownfield codebases
**Project Context:** Crime Incidents Philadelphia v1.3 milestone
**Current State:** 16% coverage → Target: 95% coverage
**Researched:** February 07, 2026
**Confidence:** HIGH

---

## Critical Pitfalls

### Pitfall 1: Testing Implementation Details Instead of Behavior

**What goes wrong:** Tests couple tightly to internal implementation (private methods, internal state), breaking whenever code is refactored even when behavior remains unchanged.

**Why it happens:** When adding tests to existing code without test-driven experience, developers often test "what the code does" (implementation) rather than "what the code should do" (behavior). This is especially common when trying to hit coverage targets quickly.

**How to avoid:** 
- Test through public APIs only
- Focus on inputs and outputs, not internal state
- Ask "If I refactored this completely but kept the same behavior, would the test still pass?"
- Avoid mocking internal methods of the class under test

**Warning signs:**
- Tests fail when refactoring but behavior hasn't changed
- Tests access private methods/attributes extensively
- Every internal method has a dedicated test
- Excessive use of `unittest.mock.patch` on internal methods

**Phase to address:** Test implementation phase - establish testing patterns early

---

### Pitfall 2: Coverage Gaming Without Quality

**What goes wrong:** Team hits 95% coverage target but tests provide minimal confidence because they don't verify meaningful behavior.

**Why it happens:** Coverage targets create incentive to write tests that execute code without asserting correctness. Common patterns:
- Tests that call functions but don't verify output
- Tests with only trivial assertions (`assert result is not None`)
- Tests that catch all exceptions to "pass"
- Tests that stub/mock everything, testing nothing real

**How to avoid:**
- Require meaningful assertions in all tests
- Code review focusing on test quality, not just coverage numbers
- Use mutation testing (mutmut) to verify tests actually catch bugs
- Track assertion density (assertions per test)
- Establish test quality guidelines before coverage push

**Warning signs:**
- High coverage but low confidence in refactoring
- Tests rarely fail during development
- Many tests with only one trivial assertion
- Test files added rapidly without corresponding bug discovery
- Tests that catch Exception and pass

**Phase to address:** Test planning phase - define quality criteria before writing tests

---

### Pitfall 3: Breaking Existing Functionality While Adding Tests

**What goes wrong:** Adding tests reveals bugs, but "fixing" them breaks existing (incorrect but relied-upon) behavior, causing production issues.

**Why it happens:** Brownfield codebases often have:
- Bugs that users have worked around
- Incorrect behavior that downstream systems depend on
- Edge cases that "work" only by accident

When tests expose these issues, fixing them without coordination causes breakage.

**How to avoid:**
- Document discovered bugs separately from tests
- Add tests that verify current behavior (even if wrong)
- Mark tests for "known incorrect behavior" with `pytest.mark.xfail`
- Coordinate with users before fixing "bugs" that may be relied upon
- Use feature flags for behavior changes
- Separate testing phase from bug-fixing phase

**Warning signs:**
- Tests immediately reveal many "bugs"
- Users report breakage after "bug fixes"
- Production systems depend on documented incorrect behavior
- API consumers complain after "correctness" improvements

**Phase to address:** Test discovery phase - catalog issues before fixing them

---

### Pitfall 4: Deleting "Unused" Code That's Actually Used

**What goes wrong:** During cleanup, code that appears unused is deleted, but it's actually imported by runtime paths, notebooks, or external consumers.

**Why it happens:** Static analysis misses:
- Dynamic imports (`importlib.import_module`, `__import__`)
- String-based references (config files, CLI commands)
- Jupyter notebook dependencies
- External API consumers
- Commented code that's periodically uncommented for debugging

**How to avoid:**
- Use runtime import tracking (Python's `sys.modules`, importlib hooks)
- Search codebase for string references to module/function names
- Check all notebooks for imports
- Review git history for patterns of code being uncommented
- Start with clearly dead code (unused test utilities, old experiments)
- Keep a "quarantine" branch for deleted code that's easily restorable
- Communicate cleanup plans to team

**Warning signs:**
- Code has no obvious callers but exists for years
- Functions referenced only in strings or config files
- Notebooks break after cleanup
- External teams report missing functionality
- Git blame shows code being added/removed repeatedly

**Phase to address:** Cleanup planning phase - analyze dependencies thoroughly before deletion

---

### Pitfall 5: Test Pollution and Interdependence

**What goes wrong:** Tests pass individually but fail when run together, or test order matters, causing flaky CI failures.

**Why it happens:** When adding tests to existing code:
- Shared global state modified by tests
- Database/file fixtures not properly isolated
- Tests depend on execution order
- Fixtures with session/module scope that accumulate state
- Monkeypatching that affects subsequent tests

**How to avoid:**
- Run tests in random order (`pytest-randomly`)
- Use function-scoped fixtures by default
- Reset global state in setup/teardown
- Use separate test databases per test (or transactions with rollback)
- Verify tests pass both individually and in full suite
- Use `pytest --lf` to catch order-dependent failures

**Warning signs:**
- Tests pass individually but fail in CI
- Test failures appear and disappear randomly
- Test results change based on which tests ran before
- CI builds are unreliable
- Developers run single tests to avoid flakiness

**Phase to address:** Test infrastructure phase - establish isolation patterns early

---

### Pitfall 6: Slow Test Suite Growth

**What goes wrong:** Adding comprehensive tests increases suite runtime from seconds to minutes/hours, slowing development velocity.

**Why it happens:** As coverage grows from 16% to 95%:
- Integration tests are easier to write than unit tests for brownfield code
- Tests hit real databases/APIs/filesystems
- Fixtures load large datasets
- No parallelization strategy
- Tests repeat expensive setup operations

**How to avoid:**
- Mark slow tests with `@pytest.mark.slow`, exclude from default runs
- Use `pytest-xdist` for parallel execution
- Optimize fixture scope (session > module > function)
- Mock expensive external dependencies
- Use in-memory databases for tests
- Establish performance budget (e.g., "suite runs in <2min locally")
- Profile test suite to find bottlenecks

**Warning signs:**
- Developers stop running full test suite locally
- CI builds take progressively longer
- Red-green-refactor cycle slows down
- Tests wait on network/disk IO
- Team complains about test speed

**Phase to address:** Test infrastructure phase - optimize from the start

---

### Pitfall 7: Breaking Changes to Test Helpers/Fixtures

**What goes wrong:** Modifying shared test fixtures or conftest.py breaks many tests simultaneously, requiring widespread updates.

**Why it happens:** As test coverage grows:
- Shared fixtures become complex
- Different tests need conflicting fixture variations
- Fixtures accumulate parameters and conditional logic
- No versioning/deprecation strategy for test utilities

**How to avoid:**
- Keep fixtures simple and focused
- Create new fixtures instead of modifying existing ones
- Version test utilities (e.g., `create_sample_data_v2`)
- Deprecate fixtures gradually, don't modify in place
- Document fixture contracts clearly
- Minimize fixture interdependencies

**Warning signs:**
- Changes to conftest.py cause cascading test failures
- Fixtures have many parameters and conditional branches
- Tests break when unrelated fixtures change
- Developers fear modifying shared test code

**Phase to address:** Test infrastructure phase - design fixture architecture carefully

---

### Pitfall 8: Inadequate Test Data Management

**What goes wrong:** Tests rely on specific test data files that become:
- Too large to version control
- Out of sync with actual data formats
- Missing edge cases
- Bloated with redundant examples

**Why it happens:** When testing data-heavy applications (like crime analytics):
- Real data is copied into test fixtures
- Edge cases are added incrementally without cleanup
- Test data generation is inconsistent
- No test data strategy established

**How to avoid:**
- Generate test data programmatically instead of storing files
- Use property-based testing (Hypothesis) for edge cases
- Store only minimal representative samples
- Document test data generation strategy
- Use data factories/builders
- Separate small unit test data from large integration test datasets

**Warning signs:**
- `tests/fixtures/` directory grows to megabytes
- Test data files committed without review
- Tests fail when data format changes
- Unclear which test uses which data file
- Git diffs full of test data changes

**Phase to address:** Test planning phase - establish data strategy early

---

### Pitfall 9: Neglecting Error Path Testing

**What goes wrong:** Coverage targets are met by testing only happy paths, leaving error handling untested and buggy.

**Why it happens:** When rushing to hit coverage percentage:
- Happy paths are easier to test
- Error paths require complex setup
- Coverage tools count lines, not paths
- Error handling is boring to test

**How to avoid:**
- Explicitly test error conditions
- Use parametrized tests for error cases
- Test exception messages and types
- Verify cleanup happens on errors (context managers, resource cleanup)
- Code review checklist: "Are error paths tested?"
- Track branch coverage, not just line coverage

**Warning signs:**
- High line coverage but untested exception handling
- Production errors from scenarios "that should never happen"
- Try/except blocks with no corresponding tests
- Error messages untested and unhelpful

**Phase to address:** Test implementation phase - include error testing in requirements

---

### Pitfall 10: Missing Integration Between Cleanup and Tests

**What goes wrong:** Code is cleaned up without updating tests, or tests are added without cleaning up deprecated code, creating inconsistency.

**Why it happens:** Testing and cleanup treated as independent tasks:
- Tests written for deprecated code that should be removed
- Code removed without removing its tests
- Duplicate code exists with duplicate tests
- No single source of truth

**How to avoid:**
- Clean up code first, then add tests to cleaned code
- Or: add tests first to understand what code is actually used
- Remove tests when removing corresponding code
- Consolidate duplicate tests when consolidating code
- Use test coverage to identify truly unused code

**Warning signs:**
- Tests for code that no longer exists
- Multiple test files testing the same functionality
- Unclear which tests correspond to which code
- Test count grows faster than code

**Phase to address:** Planning phase - decide cleanup-first vs test-first approach

---

## Moderate Pitfalls

### Pitfall 11: Inconsistent Testing Patterns

**What goes wrong:** Different parts of codebase tested with incompatible patterns (unittest vs pytest, different mocking libraries, different assertion styles).

**Why it happens:** Multiple developers adding tests without coordination, or evolving testing practices without refactoring old tests.

**How to avoid:**
- Establish testing standards document
- Use linters to enforce patterns (pytest-style, no unittest.TestCase)
- Refactor existing tests to match new patterns
- Code review for testing style consistency

**Prevention:** Create testing style guide before adding tests

---

### Pitfall 12: Over-Mocking

**What goes wrong:** Tests mock so many dependencies they become meaningless unit tests that verify mocks, not real behavior.

**Why it happens:** Following "unit testing" dogma too strictly for brownfield code, mocking every dependency to isolate code.

**How to avoid:**
- Balance unit and integration tests
- Mock only slow/external dependencies
- Test larger chunks of real code together when possible
- Ask "What confidence does this test actually give me?"

**Prevention:** Define mocking strategy early, prefer integration tests for brownfield code

---

### Pitfall 13: Ignoring Test Maintenance Cost

**What goes wrong:** Tests become brittle and require constant updates, eventually being ignored or deleted.

**Why it happens:** Tests written quickly to hit coverage targets without considering maintainability.

**How to avoid:**
- Factor out common setup patterns
- Use page object pattern for complex interfaces
- Keep tests readable and simple
- Refactor tests alongside production code

**Prevention:** Code review tests for maintainability, not just coverage

---

### Pitfall 14: Missing Documentation for Test Setup

**What goes wrong:** Developers can't run tests locally because setup is undocumented or overly complex.

**How to avoid:**
- Document test dependencies clearly
- Provide simple test setup scripts
- Use docker-compose for complex dependencies
- Keep local test running simple

**Prevention:** Include "running tests" documentation from start

---

### Pitfall 15: Configuration Drift Between Test and Production

**What goes wrong:** Tests pass but production fails due to configuration differences.

**How to avoid:**
- Use same configuration loading code in tests
- Test with production-like configuration
- Document configuration differences explicitly
- Test configuration parsing itself

**Prevention:** Use real config loading in tests

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Testing implementation instead of behavior | Faster test writing | Brittle tests that break on refactoring | Never; always test through public APIs |
| Copying production data as test fixtures | Easy test setup | Large repository, slow tests, stale data | Only as interim step; replace with generators |
| Mocking everything for "pure" unit tests | Fast isolated tests | Tests verify mocks, not real behavior | When testing truly isolated logic |
| Skipping slow tests in CI | Faster CI feedback | Slow tests never run, bugs slip through | Temporarily if scheduled for optimization |
| Writing tests without assertions | Quick coverage gains | False confidence, bugs not caught | Never; always verify behavior |
| Deleting code without grep'ing for references | Fast cleanup | Breaking runtime dependencies | Never; always search for string references |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| pytest + coverage | Not configuring source paths, inflated coverage from test code | Configure `[coverage:run] source = analysis,api,pipeline` explicitly |
| pytest-cov | Running coverage on installed packages accidentally | Use `--cov=analysis --cov=api --cov=pipeline` with explicit paths |
| pytest fixtures | Using module/session scope for stateful fixtures | Default to function scope, carefully document shared state |
| pytest markers | Not registering custom markers, warnings in output | Define all markers in `pyproject.toml` `[tool.pytest.ini_options]` |
| Test discovery | Tests not discovered due to naming conventions | Follow pytest conventions: `test_*.py`, `*_test.py`, functions starting with `test_` |
| Import errors in tests | Circular imports when testing appears | Restructure imports or use lazy imports |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Loading large datasets in fixtures | Slow test startup | Use lazy loading, generate minimal test data | When test suite exceeds 5 minutes |
| Running integration tests by default | Slow local development cycle | Mark with `@pytest.mark.slow`, exclude by default | When developers stop running tests locally |
| Sequential test execution | Underutilized CPU during test runs | Use `pytest-xdist` for parallel execution | When suite exceeds 2 minutes |
| Real file I/O in unit tests | Slow tests, disk wear | Use `tmp_path` fixture, in-memory alternatives | Immediately; use temp dirs from start |
| Real database queries | Extremely slow tests | Use in-memory SQLite, transaction rollback, or mocks | When individual tests exceed 1 second |

---

## Cleanup Safety Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Deleting without git safety net | Permanent data loss | Create cleanup branch, don't delete permanently | 
| Removing files based on static analysis alone | Missing dynamic imports | Search for string references, check notebooks |
| Bulk deletion without testing | Breaking multiple things at once | Delete incrementally, test after each removal |
| Removing deprecated code still in git history | Users can't revert if needed | Keep for one release cycle, deprecate first |
| Cleaning up test files without verifying | Removing tests for active code | Check test-to-code mapping before deletion |
| Removing config files that are environment-specific | Breaking production or other environments | Check all environments, not just local |

---

## Test Quality Anti-Patterns

| Anti-Pattern | What It Looks Like | Better Approach |
|--------------|-------------------|-----------------|
| **No-op tests** | `test_function_runs()` with no assertions | Test actual behavior with meaningful assertions |
| **Catch-all exception tests** | `try: func() except: pass` | Test specific exceptions and messages |
| **Testing private methods directly** | `test__private_method()` | Test through public API |
| **Assertion roulette** | Many unrelated assertions in one test | One concept per test |
| **Mystery guest** | Test depends on external state not in test | Make all dependencies explicit |
| **Erratic test** | Test passes/fails randomly | Fix non-determinism, use freezegun for time, seed random |
| **Test doubles for everything** | Every dependency mocked | Mock only external/slow dependencies |

---

## Coverage Blind Spots

Areas where coverage metrics lie about test quality:

| Blind Spot | Why Coverage Doesn't Help | What To Do |
|------------|---------------------------|-----------|
| Exception handling | `except: pass` counts as covered | Test exception paths explicitly |
| Configuration branches | `if config.feature_enabled:` | Test all configuration combinations |
| Error messages | String formatting counts as covered | Assert on actual error messages |
| Type validation | Type hints don't enforce runtime checks | Test invalid types |
| Edge cases | Happy path gives 100% line coverage | Use property-based testing (Hypothesis) |
| Concurrency bugs | Sequential tests miss race conditions | Add concurrency tests for shared state |

---

## Brownfield-Specific Challenges

| Challenge | Why It's Harder Than Greenfield | Mitigation |
|-----------|--------------------------------|------------|
| **No test infrastructure** | Must add pytest, coverage, CI integration all at once | Start with minimal setup, expand incrementally |
| **Code not designed for testing** | Tight coupling, global state, hard dependencies | Refactor minimally to enable testing |
| **Unknown behavior** | Tests must verify behavior you don't fully understand | Document expected behavior before testing |
| **Existing bugs** | Tests expose bugs that may be relied upon | Document bugs separately, don't fix immediately |
| **Large modules** | Testing requires understanding entire complex system | Test at integration level first, refactor later |
| **Missing documentation** | No spec to test against | Reverse-engineer spec from code behavior |

---

## UX Pitfalls (Developer Experience)

| Pitfall | Developer Impact | Better Approach |
|---------|-----------------|-----------------|
| Verbose test output | Important failures lost in noise | Configure pytest `-q` for quiet mode, use `-v` only when debugging |
| Unclear test names | Can't understand what failed from name | Use descriptive names: `test_temporal_analysis_handles_missing_dates` |
| Generic assertion errors | `assert result == expected` with no message | Add assertion messages: `assert result == expected, f"Expected {expected}, got {result}"` |
| Slow feedback loop | Waiting minutes to see test results | Run subset with `pytest -k pattern`, optimize common paths |
| Test files far from source | Hard to find tests for code | Mirror source structure in tests directory |
| No test isolation | One failure causes cascade | Fix isolation so failures are independent |

---

## "Looks Done But Isn't" Checklist

- [ ] 95% coverage achieved with meaningful assertions (not just code execution)
- [ ] Tests verify behavior, not implementation details
- [ ] Error paths and edge cases tested, not just happy paths
- [ ] Test suite runs in reasonable time (<5min full, <30s subset)
- [ ] Tests are isolated and can run in any order
- [ ] Cleanup removed truly unused code without breaking dependencies
- [ ] All notebooks still function after cleanup
- [ ] Test data is manageable and version-controlled appropriately
- [ ] Testing patterns are consistent across codebase
- [ ] Tests are maintainable and readable
- [ ] CI integration works reliably
- [ ] Documentation updated for removed code
- [ ] Deprecation warnings added before deletion

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Broke existing functionality with "fix" | HIGH | Revert fix, add test for current behavior, coordinate behavior change |
| Deleted used code | HIGH | Restore from git, add explicit deprecation, communicate before removal |
| Test suite too slow | MEDIUM | Profile with `pytest --durations=10`, parallelize with xdist, mark slow tests |
| Brittle tests breaking on refactoring | MEDIUM | Refactor tests to test behavior via public API, reduce mocking |
| Low quality coverage gaming | MEDIUM | Add mutation testing, manual review, add meaningful assertions |
| Test pollution/flakiness | MEDIUM | Add `pytest-randomly`, fix shared state, isolate fixtures |
| Missing test infrastructure | LOW | Add pytest, coverage, CI configs incrementally |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification Phase | Remediation Phase |
|---------|-----------------|-------------------|-------------------|
| Testing implementation vs behavior | Test planning - establish patterns | Code review | Refactor tests to use public API |
| Coverage gaming | Test planning - define quality criteria | Mutation testing | Add meaningful assertions |
| Breaking existing functionality | Test discovery - catalog bugs | Integration testing | Coordinate behavior changes |
| Deleting used code | Cleanup planning - analyze dependencies | Smoke testing | Restore and deprecate properly |
| Test pollution | Infrastructure setup | CI - random order testing | Fix shared state |
| Slow test suite | Infrastructure setup | Performance monitoring | Parallelize and optimize |
| Breaking test fixtures | Infrastructure design | Regression testing | Version fixtures, deprecate gradually |
| Inadequate test data | Test planning | Data validation | Generate programmatically |
| Missing error path tests | Implementation | Code coverage analysis | Add error scenario tests |
| Cleanup/test inconsistency | Planning - decide approach | Cross-verification | Synchronize code and tests |

---

## Phase-Specific Warnings

### Phase 1: Test Infrastructure Setup
**Likely pitfall:** Setting up overly complex test infrastructure that slows initial progress
**Mitigation:** Start with minimal pytest + coverage, add complexity only as needed

### Phase 2: Test Planning
**Likely pitfall:** Not defining test quality criteria, only coverage targets
**Mitigation:** Establish assertion requirements, behavior-focus, and test review process

### Phase 3: Test Implementation
**Likely pitfall:** Writing tests too quickly to hit coverage targets, sacrificing quality
**Mitigation:** Code review all tests, require meaningful assertions, use test quality checklist

### Phase 4: Cleanup Execution
**Likely pitfall:** Deleting code without verifying all dependencies
**Mitigation:** Search for string references, test after each deletion, keep git safety net

### Phase 5: Integration & Optimization
**Likely pitfall:** Ignoring test suite performance until it's a major problem
**Mitigation:** Monitor test runtime from start, parallelize early, optimize proactively

---

## Project-Specific Risks

Based on Crime Incidents Philadelphia codebase analysis:

### High Risk Areas

1. **Notebooks (`notebooks/`)** - Likely to break when cleaning up analysis code
   - **Warning:** Check all .ipynb files for imports before deleting modules
   - **Mitigation:** Run all notebooks as part of test suite

2. **Analysis orchestration files** - Complex interdependencies
   - **Current:** `analysis/orchestrate_phase1.py`, `orchestrate_phase2.py`
   - **Risk:** Heavy use of imports and dynamic paths
   - **Mitigation:** Add integration tests before refactoring

3. **CLI tools** - String-based command routing
   - **Current:** CLI tools in `analysis/`
   - **Risk:** Commands referenced by string, not detected by static analysis
   - **Mitigation:** Test all CLI commands, search for string references

4. **Configuration schemas** - Complex validation logic
   - **Current:** `analysis/config/schemas/`
   - **Risk:** Error paths likely untested
   - **Mitigation:** Test all validation branches, invalid inputs

5. **Visualization modules** - Heavy matplotlib/seaborn dependencies
   - **Current:** `analysis/visualization/`
   - **Risk:** Slow tests if generating actual plots
   - **Mitigation:** Mock plotting, test data preparation separately from rendering

### Coverage Gaps (from 16% current)

Based on existing tests, likely untested areas:
- Data preprocessing edge cases
- Configuration validation
- Error handling in pipeline
- Visualization data transformations
- API error responses
- CLI argument validation

---

## Sources

**Project Analysis:**
- `pyproject.toml` - Current pytest configuration
- `tests/` - Existing test structure (3,805 lines)
- `coverage.json` - Current 16% coverage baseline
- Project structure analysis

**Testing Best Practices (HIGH confidence):**
- pytest official documentation (test isolation, fixtures, markers)
- Python testing patterns (unittest → pytest migration)
- Coverage.py documentation (branch coverage, configuration)

**Brownfield Testing Patterns (MEDIUM confidence):**
- Working Effectively with Legacy Code principles (Michael Feathers)
- Characterization testing approach for brownfield code
- Test-after-development patterns

**Repository Cleanup (HIGH confidence):**
- Git workflow best practices (safety nets, incremental deletion)
- Python import analysis (static vs dynamic imports)
- Dependency tracking strategies

---

*Research for: v1.3 Testing & Cleanup milestone*  
*Focus: Brownfield testing and safe repository cleanup*  
*Researched: February 07, 2026*
