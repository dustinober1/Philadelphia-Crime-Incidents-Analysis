# Project Research Summary: Testing & Cleanup

**Project:** Crime Incidents Philadelphia
**Domain:** Comprehensive Test Coverage (95%+) and Repository Cleanup
**Milestone:** v1.3 - Testing & Cleanup
**Researched:** February 7, 2026
**Confidence:** HIGH

## Executive Summary

Milestone v1.3 focuses on achieving 95%+ test coverage across all Python code (analysis/, api/, pipeline/) and performing comprehensive repository cleanup. The research reveals a well-structured brownfield codebase at 16% coverage that requires careful, methodical testing before cleanup to avoid breaking existing functionality. The recommended approach is **tests-first, cleanup-second** to ensure all code paths are validated before making removal decisions.

The key insight is that this project already has solid testing infrastructure (pytest 8.x, pytest-cov, conftest.py with fixtures) but needs enhancement, not replacement. The gap from 16% to 95% requires adding approximately 150-200 new tests while leveraging specialized tools like diff-cover for enforcement, pytest-xdist for speed, and vulture for dead code detection. The critical risk is coverage gaming (hitting percentage targets without meaningful assertions) rather than technical implementation challenges.

The research strongly recommends establishing test quality criteria before writing tests, using mutation testing to validate test effectiveness, and treating cleanup as a safety-gated process requiring manual approval for source code deletions. This milestone will create a sustainable testing culture that supports future development rather than just hitting a one-time coverage number.

## Key Findings

### From STACK.md: Testing & Cleanup Technologies

**Core testing stack (building on existing pytest foundation):**
- **coverage[toml] 7.13.3** + **pytest-cov 7.0.0**: Already integrated; upgrade for Python 3.14 compatibility and TOML configuration support
- **diff-cover 10.2.0**: Critical for 95% goal - enforces coverage on new/changed lines, prevents backsliding via PR-level checks
- **pytest-xdist 3.8.0**: Essential for test suite performance - reduces runtime by 4-8x with parallel execution across CPUs
- **pytest-timeout 2.4.0**: Prevents hanging tests from blocking CI, critical for data pipeline tests with I/O operations

**FastAPI-specific testing:**
- **httpx 0.28.1**: Required for TestClient, supports async route testing
- **pytest-asyncio 1.3.0**: Enables async test functions for FastAPI endpoints
- **pytest-mock 3.15.1**: Simplifies mocking data loaders and external services

**Advanced testing (quality validation):**
- **hypothesis 6.151.5**: Property-based testing for data pipeline edge cases (empty DataFrames, NaN values, timezone issues)
- **mutmut 3.4.0**: Post-95% validation that tests actually catch bugs, not just execute code

**Cleanup tooling:**
- **vulture 2.14**: Primary dead code detection - finds unused functions, classes, variables with low false-positive rate
- **autoflake 2.3.1**: Automated unused import removal with `--in-place` flag
- **pyclean 3.5.0**: Safe Python artifact cleanup (*.pyc, __pycache__, .coverage, etc.)
- **pipreqs 0.5.0**: Audit unused dependencies by comparing declared vs. actually imported packages

**Critical configuration:**
```toml
[tool.coverage.report]
fail_under = 95.0
exclude_lines = ["pragma: no cover", "if __name__ == .__main__.:", "if TYPE_CHECKING:"]

[tool.pytest.ini_options]
addopts = ["--cov-fail-under=95", "-n=auto", "--timeout=30"]
```

**What NOT to use:**
- ❌ codecov.io/coveralls.io for local development (cloud dependency, slower feedback)
- ❌ pytest-parallel (less mature than xdist, worse coverage integration)
- ❌ tox/nox (project uses conda, single Python 3.14 version)
- ❌ Manual cleanup with `find` + `rm` (error-prone, not reproducible)

### From ARCHITECTURE.md: Testing & Cleanup Integration Patterns

**Current infrastructure (validated):**
- 56 Python files across analysis/, api/, pipeline/
- 22 existing test files with shared fixtures (sample_crime_df, tmp_output_dir)
- Coverage tracked via coverage.json (16% baseline) and htmlcov/
- Test organization mirrors source structure

**Recommended test organization:**

| Source Package | Test Location | Coverage Target | Approach |
|----------------|---------------|-----------------|----------|
| analysis/cli/ | tests/test_cli_*.py | 95% | CLI integration tests with CliRunner |
| analysis/data/ | tests/test_data_*.py | 95% | Unit tests with sample fixtures |
| analysis/models/ | tests/test_classification.py, tests/test_models_*.py | 95% | Unit + integration tests |
| analysis/utils/ | tests/test_temporal.py, tests/test_utils_*.py | 95% | Unit tests for pure functions |
| analysis/visualization/ | tests/test_visualization_*.py | 85% | Output validation (not pixel-perfect) |
| api/routers/ | tests/test_api_endpoints.py | 95% | FastAPI TestClient integration tests |
| api/services/ | tests/test_api_services.py | 95% | Unit tests with mocked data |
| pipeline/ | tests/test_pipeline_*.py | 90% | Integration tests with sample data |

**Build order: Tests first, then cleanup**

Rationale:
1. **Validation before removal**: 95% coverage ensures all code paths tested before deciding what's unused
2. **Safety net**: Tests catch breaking changes from cleanup
3. **Confidence**: High coverage means "0% coverage" files are truly unused, not just untested
4. **Reversibility**: Easy to restore accidentally removed code if tests fail

**Recommended phase structure:**
```
Phase 1: Baseline (Week 1) → Measure current 16% coverage, identify gaps
Phase 2-3: Core modules (Week 2-3) → analysis/data/, analysis/models/ to 60-70%
Phase 4: API & Pipeline (Week 4) → API services, endpoints, pipeline to 80-85%
Phase 5: Remaining gaps (Week 5) → visualization, config loaders, orchestrators to 95%+
Phase 6: Cleanup audit & execution (Week 6) → Audit, review, safely remove dead code
Phase 7: Validation (Week 6) → Verify coverage maintained, run full suite
```

**Coverage-driven cleanup decision matrix:**

| File Coverage | Import References | Test Dependencies | Action |
|---------------|-------------------|-------------------|--------|
| 95%+ | Any | Any | **KEEP** (actively used) |
| 50-95% | Multiple | Yes | **KEEP** (add more tests) |
| 1-50% | None | No | **REVIEW** (might be unused) |
| 0% | None | No | **CANDIDATE** (likely unused) |
| 0% | Any | Any | **KEEP** (tested indirectly) |

**CI/CD integration:**
- GitHub Actions workflow with `pytest --cov-fail-under=95`
- diff-cover enforcement on PRs: `diff-cover coverage.xml --compare-branch=origin/main --fail-under=95`
- Artifacts uploaded: htmlcov/, diff-cover.html, coverage.xml

### From PITFALLS.md: Critical Risks and Mitigations

**Top 10 critical pitfalls:**

1. **Testing Implementation Details Instead of Behavior** 
   - Risk: Tests break on refactoring even when behavior unchanged
   - Mitigation: Test through public APIs only, focus on inputs/outputs not internal state
   - Phase to address: Test implementation phase - establish patterns early

2. **Coverage Gaming Without Quality**
   - Risk: 95% coverage but tests don't verify meaningful behavior
   - Mitigation: Require meaningful assertions, use mutation testing (mutmut) to validate tests catch bugs
   - Phase to address: Test planning phase - define quality criteria before writing tests

3. **Breaking Existing Functionality While Adding Tests**
   - Risk: "Fixing" bugs exposed by tests breaks relied-upon behavior
   - Mitigation: Document discovered bugs separately, use `pytest.mark.xfail` for known incorrect behavior
   - Phase to address: Test discovery phase - catalog issues before fixing

4. **Deleting "Unused" Code That's Actually Used**
   - Risk: Static analysis misses dynamic imports, notebook dependencies, external consumers
   - Mitigation: Runtime import tracking, search string references, check notebooks, use quarantine branch
   - Phase to address: Cleanup planning phase - analyze dependencies thoroughly

5. **Test Pollution and Interdependence**
   - Risk: Tests pass individually but fail together, flaky CI failures
   - Mitigation: Run tests in random order (`pytest-randomly`), use function-scoped fixtures, reset global state
   - Phase to address: Test infrastructure phase - establish isolation patterns early

6. **Slow Test Suite Growth**
   - Risk: Suite runtime grows from seconds to minutes/hours, slowing development
   - Mitigation: Mark slow tests with `@pytest.mark.slow`, use pytest-xdist for parallelization, mock expensive dependencies
   - Phase to address: Test infrastructure phase - optimize from the start

7. **Breaking Changes to Test Helpers/Fixtures**
   - Risk: Modifying shared fixtures breaks many tests simultaneously
   - Mitigation: Keep fixtures simple, create new fixtures instead of modifying existing, version test utilities
   - Phase to address: Test infrastructure phase - design fixture architecture carefully

8. **Inadequate Test Data Management**
   - Risk: Test data becomes too large for version control, out of sync with formats
   - Mitigation: Generate test data programmatically, use Hypothesis for edge cases, store minimal samples
   - Phase to address: Test planning phase - establish data strategy early

9. **Neglecting Error Path Testing**
   - Risk: Coverage met on happy paths only, error handling untested
   - Mitigation: Explicitly test error conditions, use parametrized tests, verify exception types and messages
   - Phase to address: Test implementation phase - include error testing in requirements

10. **Missing Integration Between Cleanup and Tests**
    - Risk: Tests written for deprecated code, code removed without removing tests
    - Mitigation: Clean up code first OR add tests first to understand usage, remove tests when removing code
    - Phase to address: Planning phase - decide cleanup-first vs test-first approach

**Project-specific high-risk areas (Crime Incidents Philadelphia):**
1. **Notebooks** (notebooks/) - Likely to break when cleaning analysis code; run all notebooks as part of test suite
2. **Analysis orchestration files** - Complex interdependencies in orchestrate_phase*.py; add integration tests before refactoring
3. **CLI tools** - String-based command routing not detected by static analysis; test all commands, search for string references
4. **Configuration schemas** - Complex validation logic with likely untested error paths; test all validation branches
5. **Visualization modules** - Heavy matplotlib/seaborn dependencies; mock plotting, test data preparation separately

**Coverage blind spots where metrics lie:**
- Exception handling (`except: pass` counts as covered but meaningless)
- Configuration branches (need to test all config combinations)
- Error messages (string formatting covered but not validated)
- Type validation (type hints don't enforce runtime checks)
- Edge cases (happy path gives 100% line coverage but misses edge cases)
- Concurrency bugs (sequential tests miss race conditions)

## Implications for Roadmap

Based on combined research, suggested phase structure with rationale:

### Phase 1: Test Infrastructure & Baseline Assessment (Week 1)
**Rationale:** Establish foundation before writing tests; prevent infrastructure pitfalls that slow all future work.

**Delivers:**
- Enhanced pytest configuration with coverage enforcement, parallelization, timeouts
- Baseline coverage measurement (current 16% → documented gaps)
- Testing quality criteria and patterns documented
- Make targets for common test operations

**Key technologies:** pytest-cov 7.0.0, pytest-xdist 3.8.0, pytest-timeout 2.4.0, coverage[toml] 7.13.3

**Features from research:**
- Coverage configuration in pyproject.toml with fail_under=95
- Test isolation patterns (function-scoped fixtures)
- Test naming and organization standards

**Pitfalls avoided:**
- Pitfall #5: Test pollution and interdependence (establish isolation early)
- Pitfall #6: Slow test suite growth (optimize from start with xdist)
- Pitfall #7: Breaking test fixtures (design fixture architecture carefully)

**Research flag:** ✅ Standard patterns - no deep research needed

---

### Phase 2: Core Module Testing - Data & Models (Week 2-3)
**Rationale:** Highest impact modules (data processing, models) first; establishes testing patterns for team.

**Delivers:**
- Unit tests for analysis/data/ (loading, validation, preprocessing)
- Unit + integration tests for analysis/models/ (classification, time series, validation)
- Unit tests for analysis/utils/ (spatial, temporal, classification utilities)
- Target: 60-70% overall coverage

**Key technologies:** pytest-mock 3.15.1 (for mocking I/O), hypothesis 6.151.5 (for edge cases)

**Features from research:**
- Tests mirror source structure: tests/test_data_*.py, tests/test_models_*.py
- Sample fixtures reused from existing conftest.py (sample_crime_df, tmp_output_dir)
- Property-based testing with Hypothesis for pandas edge cases

**Pitfalls avoided:**
- Pitfall #1: Testing implementation vs behavior (test through public APIs)
- Pitfall #2: Coverage gaming (require meaningful assertions, code review quality)
- Pitfall #8: Inadequate test data management (generate programmatically with Hypothesis)
- Pitfall #9: Neglecting error paths (test exceptions explicitly)

**Research flag:** ✅ Standard patterns - data processing tests well-documented

---

### Phase 3: API & Pipeline Testing (Week 4)
**Rationale:** Service layer validation before final coverage push; builds on established patterns from Phase 2.

**Delivers:**
- API service tests (unit tests for api/services/ with mocked data)
- API endpoint tests (extend existing tests/test_api_endpoints.py with FastAPI TestClient)
- Pipeline integration tests (tests/test_pipeline_*.py with sample datasets)
- Target: 80-85% overall coverage

**Key technologies:** httpx 0.28.1, pytest-asyncio 1.3.0 (for async FastAPI routes)

**Features from research:**
- Async route testing with `@pytest.mark.asyncio`
- Mock data loaders with pytest-mock
- Integration tests with realistic sample data

**Pitfalls avoided:**
- Pitfall #3: Breaking existing functionality (document discovered bugs, don't fix immediately)
- Pitfall #12: Over-mocking (balance unit and integration tests, mock only slow/external deps)

**Research flag:** ⚠️ May need deeper research for complex pipeline integration scenarios

---

### Phase 4: Remaining Gaps - Visualization, Config, Orchestration (Week 5)
**Rationale:** Complete coverage to 95% with harder-to-test modules; final coverage push.

**Delivers:**
- Visualization tests (output validation, not pixel-perfect matching)
- Config loader tests (all validation branches, error paths)
- Orchestrator tests (CLI integration tests with CliRunner)
- Target: 95%+ overall coverage

**Key technologies:** faker 40.4.0 (for realistic test data), pytest-html 4.2.0 (for test reports)

**Features from research:**
- Visualization tests validate data preparation, not rendering
- Config tests cover all branches and error scenarios
- CLI tests use Typer's CliRunner for end-to-end validation

**Pitfalls avoided:**
- Pitfall #9: Neglecting error paths (explicit error condition testing)
- High-risk area: Notebooks (verify all notebooks still function)
- High-risk area: CLI tools (test string-based command routing)

**Research flag:** ✅ Standard patterns - visualization and config testing well-established

---

### Phase 5: Cleanup Audit & Execution (Week 6)
**Rationale:** Tests provide safety net; cleanup decisions based on validated coverage data.

**Delivers:**
- Dead code audit (vulture report on 0% coverage files)
- Unused import removal (autoflake automated cleanup)
- Dependency audit (pipreqs comparison with requirements.txt)
- Safe artifact cleanup (pyclean for *.pyc, __pycache__, etc.)
- Source code cleanup with manual approval

**Key technologies:** vulture 2.14, autoflake 2.3.1, pyclean 3.5.0, pipreqs 0.5.0

**Features from research:**
- Coverage-driven cleanup decision matrix (see above)
- Safety gates: git status check, import validation, test dependency check
- Incremental cleanup with testing after each removal
- Quarantine branch for easily restorable deletions

**Pitfalls avoided:**
- Pitfall #4: Deleting used code (search string references, check notebooks, runtime import tracking)
- Pitfall #10: Missing cleanup/test integration (synchronize code and tests)
- High-risk areas: Notebooks, orchestrators, CLI string references

**Research flag:** ✅ Standard patterns - cleanup tooling well-documented

---

### Phase 6: Quality Validation & CI Integration (Week 6)
**Rationale:** Validate test effectiveness, not just coverage percentage; enforce in CI for sustainability.

**Delivers:**
- Mutation testing on critical modules (mutmut validation)
- CI/CD workflow with coverage enforcement (GitHub Actions)
- diff-cover for PR-level coverage checks
- Coverage badge for README
- Make targets for all test operations

**Key technologies:** mutmut 3.4.0, diff-cover 10.2.0, pytest-html 4.2.0, coverage-badge 1.1.2

**Features from research:**
- GitHub Actions workflow: `pytest --cov-fail-under=95`
- diff-cover on PRs: `--compare-branch=origin/main --fail-under=95`
- Mutation testing to verify tests catch bugs
- HTML test reports as CI artifacts

**Pitfalls avoided:**
- Pitfall #2: Coverage gaming (mutation testing validates quality)
- Pitfall #5: Test pollution (CI runs with random order via pytest-randomly)
- Pitfall #6: Slow test suite (parallel execution with pytest-xdist)

**Research flag:** ✅ Standard patterns - CI integration well-established

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack (Testing) | **HIGH** | Official PyPI versions verified; pytest/coverage.py industry standard |
| Stack (Cleanup) | **HIGH** | Mature tools (vulture 2.14, autoflake 2.3.1) with stable releases |
| Architecture | **HIGH** | Based on validated current project structure (56 Python files, 22 test files) |
| Pitfalls | **HIGH** | Brownfield testing patterns well-documented; project-specific risks identified from codebase analysis |
| Features | **MEDIUM** | FEATURES.md not available, but stack and architecture research implies features |

**Overall confidence:** HIGH

### Gaps to Address During Planning

1. **Specific test coverage gap priorities**: After baseline measurement in Phase 1, prioritize uncovered files by impact (most-used modules first)

2. **Notebook testing strategy**: Determine whether to run all notebooks in CI or use smoke tests; notebooks/ directory not analyzed in depth

3. **Mutation testing scope**: Decide which modules warrant mutation testing (slow process, use selectively on critical code)

4. **Performance budgets**: Establish acceptable test suite runtime (<5min full suite?, <30s subset?)

5. **Cleanup approval process**: Define who reviews and approves source code deletions, quarantine branch duration

6. **CI/CD integration details**: Verify cloudbuild.yaml compatibility with pytest coverage workflow, determine artifact storage strategy

## Success Criteria Checklist

Based on research synthesis, milestone v1.3 is complete when:

- [ ] 95%+ line coverage across analysis/, api/, pipeline/
- [ ] 90%+ branch coverage (not just line coverage)
- [ ] 0 files with <80% coverage (enforced by diff-cover)
- [ ] Coverage badge shows 95%+ in README
- [ ] Tests verify behavior through public APIs, not implementation details
- [ ] Meaningful assertions in all tests (validated by code review)
- [ ] Test suite runs in <5min full, <30s subset (parallel execution with pytest-xdist)
- [ ] Tests isolated and can run in any order (verified with pytest-randomly)
- [ ] 0 unused imports (verified by autoflake)
- [ ] <10 vulture warnings for dead code
- [ ] requirements.txt matches actual imports (verified by pipreqs audit)
- [ ] 0 build artifacts in git (verified by pyclean + .gitignore)
- [ ] All notebooks still function after cleanup
- [ ] CI enforces 95% coverage threshold (pytest --cov-fail-under=95)
- [ ] diff-cover enforces 95% on new code in PRs
- [ ] Mutation testing validates test quality on critical modules
- [ ] Documentation updated for removed code

## Sources

### Primary Sources (HIGH confidence)
- `.planning/research/STACK-testing-cleanup.md` - Testing and cleanup technology stack
- `.planning/research/ARCHITECTURE-TESTING-CLEANUP.md` - Test organization and integration patterns
- `.planning/research/PITFALLS-testing-cleanup.md` - Brownfield testing risks and mitigations
- Project structure analysis (analysis/, api/, pipeline/, tests/)
- Existing test infrastructure (pyproject.toml, tests/conftest.py, requirements-dev.txt)
- Current coverage data (coverage.json - 16% baseline)

### Secondary Sources (MEDIUM confidence)
- pytest official documentation (https://docs.pytest.org/)
- coverage.py documentation (https://coverage.readthedocs.io/)
- pytest-cov documentation (https://pytest-cov.readthedocs.io/)
- FastAPI testing guide (https://fastapi.tiangolo.com/tutorial/testing/)
- Hypothesis documentation (https://hypothesis.readthedocs.io/)
- Python testing best practices (2026 industry standards)

### PyPI Versions (verified February 7, 2026)
- coverage: 7.13.3, pytest-cov: 7.0.0, pytest-xdist: 3.8.0, pytest-asyncio: 1.3.0
- httpx: 0.28.1, hypothesis: 6.151.5, vulture: 2.14, autoflake: 2.3.1
- diff-cover: 10.2.0, mutmut: 3.4.0, pyclean: 3.5.0, pipreqs: 0.5.0

---

## Ready for Roadmap

**Status:** ✅ READY

This SUMMARY.md provides the roadmapper agent with:
- Clear phase structure (6 phases with dependencies and rationale)
- Technology decisions with version specifics and rationale
- Critical pitfalls mapped to prevention phases
- Confidence assessment with identified gaps
- Success criteria checklist
- Research flags indicating which phases need deeper research (Phase 3 pipeline integration only)

**Next step:** Orchestrator can proceed to roadmap creation with `/gsd-roadmapper` agent.

---

*Research synthesis completed: February 7, 2026*
*Confidence: HIGH*
*Files synthesized: 3 (STACK, ARCHITECTURE, PITFALLS for testing-cleanup)*
