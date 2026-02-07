# Requirements: Crime Incidents Philadelphia v1.3 Testing & Cleanup

## Milestone Goal

Achieve 95% test coverage across Python codebase (analysis/, api/, pipeline/, CLI) and remove all unused/deprecated files to establish a clean quality baseline.

## Current State

- **Current coverage:** 16% (225/1408 statements)
- **Target coverage:** 95%
- **Coverage gap:** 79 percentage points
- **Modules requiring tests:** 56 total (42 analysis/ + 11 api/ + 3 pipeline/)
- **Existing test foundation:** ~40 tests with good fixture infrastructure

## Requirements

### Test Infrastructure (INFRA)

- [ ] **INFRA-01**: Developer can run tests in parallel using pytest-xdist for 4-8x faster test execution
- [ ] **INFRA-02**: Build system enforces 95% coverage threshold via pyproject.toml fail_under configuration
- [ ] **INFRA-03**: CI pipeline validates coverage with diff-cover to prevent backsliding on new code
- [ ] **INFRA-04**: Test suite includes quality criteria requiring meaningful assertions and behavior-focused tests

### Core Module Testing (CORE)

- [ ] **CORE-01**: analysis/models/ modules have comprehensive unit tests covering ML and statistical logic
- [ ] **CORE-02**: analysis/data/ modules have unit tests covering data loading and validation logic
- [ ] **CORE-03**: analysis/utils/ modules have unit tests covering core utility functions
- [ ] **CORE-04**: Core module tests achieve 60-70% overall coverage milestone

### API Testing (API)

- [ ] **API-01**: All 11 FastAPI router endpoints have integration tests using TestClient
- [ ] **API-02**: API tests validate request/response contracts and error handling
- [ ] **API-03**: API tests mock external dependencies and data loaders appropriately
- [ ] **API-04**: API tests achieve 80-85% overall coverage milestone

### CLI Testing (CLI)

- [ ] **CLI-01**: All 8 Typer CLI commands have tests using CliRunner
- [ ] **CLI-02**: CLI tests validate argument parsing and command invocation
- [ ] **CLI-03**: CLI tests verify output formatting and exit codes
- [ ] **CLI-04**: CLI tests mock file I/O and external dependencies

### Pipeline Testing (PIPE)

- [ ] **PIPE-01**: Pipeline export operations have tests with mocked external APIs
- [ ] **PIPE-02**: Pipeline refresh operations have tests validating data integrity
- [ ] **PIPE-03**: Pipeline error handling paths are covered by tests

### Supporting Module Testing (SUPP)

- [ ] **SUPP-01**: analysis/config/ modules have tests for configuration parsing and validation
- [ ] **SUPP-02**: analysis/visualization/ modules have tests for chart generation logic
- [ ] **SUPP-03**: Remaining analysis/ modules have comprehensive test coverage
- [ ] **SUPP-04**: All Python modules achieve 95%+ overall coverage milestone

### Repository Cleanup (CLEAN)

- [ ] **CLEAN-01**: Automated cleanup removes all cache files (.pyc, __pycache__, .DS_Store)
- [ ] **CLEAN-02**: Dead code detection with vulture identifies unused functions and classes
- [ ] **CLEAN-03**: Automated import cleanup with autoflake removes unused imports
- [ ] **CLEAN-04**: Manual review process evaluates scripts/, docs/, notebooks/ for deprecated content
- [ ] **CLEAN-05**: Cleanup operations have safety gates preventing accidental removal of active code
- [ ] **CLEAN-06**: Gitignore updated to prevent future accumulation of temporary files

### Quality Validation (QUAL)

- [ ] **QUAL-01**: Coverage reports generate HTML and JSON outputs for review
- [ ] **QUAL-02**: Mutation testing with mutmut validates test quality on critical modules
- [ ] **QUAL-03**: Coverage badge generated for README to display current coverage percentage

## Future Requirements

*No requirements deferred to future milestones at this time.*

## Out of Scope

- **UI/E2E tests for Next.js frontend** — Frontend testing not in scope for quality milestone
- **Load/stress testing** — Performance testing deferred to future milestone
- **100% coverage obsession** — 95% is optimal, pursuing 100% creates diminishing returns
- **Testing framework internals** — Trust pytest, FastAPI, pandas; don't test library code

## Success Criteria

This milestone is complete when:

1. ✅ All Python modules in analysis/, api/, pipeline/ have tests
2. ✅ Coverage reports show 95%+ across entire Python codebase
3. ✅ Test suite runs in parallel with acceptable performance (<5 min total)
4. ✅ CI enforces coverage thresholds on all PRs
5. ✅ Repository contains no cache/build artifacts or deprecated files
6. ✅ All tests are behavior-focused with meaningful assertions
7. ✅ Cleanup safety gates prevent accidental code removal

## Traceability

*This section will be populated by roadmap creation to map requirements to phases.*

| Requirement | Phase | Status |
|-------------|-------|--------|
| *(To be filled by roadmapper)* | | |

---

*Version: v1.3 Testing & Cleanup*  
*Created: February 7, 2026*  
*Total Requirements: 30*
