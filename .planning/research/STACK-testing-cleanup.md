# Technology Stack: Testing & Cleanup for 95% Coverage

**Project:** Crime Incidents Philadelphia Analytics Platform
**Milestone:** v1.3 - Testing & Cleanup
**Researched:** 2026-02-07
**Domain:** Python Testing Infrastructure & Repository Cleanup

## Executive Summary

This document specifies the testing and cleanup stack needed to achieve 95% test coverage across all Python code (analysis/, api/, pipeline/) and perform comprehensive repository cleanup. The stack builds on existing pytest infrastructure while adding coverage enforcement, test acceleration, and dead code detection capabilities.

**Key Decision:** Focus on coverage measurement + enforcement tools rather than wholesale framework changes. The existing pytest/coverage.py foundation is solid; we need specialized plugins and cleanup utilities to reach 95%.

---

## Current State Analysis

**Existing Infrastructure (Validated):**
- pytest 8.0+ with conftest.py
- pytest-cov 6.0+ for coverage measurement
- coverage.py 7.13.3 (generates .coverage, coverage.json, htmlcov/)
- pyproject.toml with pytest configuration
- 56 Python files to test across analysis/, api/, pipeline/
- Existing tests in tests/ covering CLI, API, data processing, integration

**Gap to Close:**
- Current coverage: Unknown (needs measurement)
- Target coverage: 95%+
- Need: Coverage enforcement, gap identification, test acceleration, cleanup automation

---

## Core Testing Stack

### Coverage Measurement & Enforcement

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **coverage[toml]** | 7.13.3 | Coverage measurement engine | Industry standard, supports branch coverage, already integrated. TOML support enables pyproject.toml config. |
| **pytest-cov** | 7.0.0 | pytest-coverage integration | Seamless pytest integration, already in use. Upgrade to 7.0.0 for Python 3.14 compatibility. |
| **diff-cover** | 10.2.0 | Incremental coverage enforcement | **Critical for 95% goal.** Enforces coverage on new/changed lines, prevents backsliding. Integrates with git for PR-level checks. |
| **coverage-badge** | 1.1.2 | Coverage badge generation | Visual coverage tracking for README. Lightweight, no external dependencies. |

**Rationale:** coverage.py is the gold standard for Python coverage measurement. diff-cover is the key tool for *enforcing* 95% - it fails CI if new code drops below threshold, making coverage a quality gate rather than just a metric.

**Configuration:** Add to pyproject.toml:
```toml
[tool.coverage.run]
source = ["analysis", "api", "pipeline"]
omit = [
    "*/tests/*",
    "*/conftest.py",
    "*/__init__.py",
    "analysis/orchestrate_*.py",  # CLI orchestrators tested via integration
]
branch = true
parallel = true  # For pytest-xdist compatibility

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
fail_under = 95.0  # Enforce 95% threshold

[tool.coverage.html]
directory = "htmlcov"

[tool.coverage.json]
output = "coverage.json"
```

**What NOT to use:**
- ❌ codecov.io / coveralls.io for local development (adds cloud dependency, slower feedback)
- ❌ pytest-cover (old, unmaintained - use pytest-cov)

---

### Test Acceleration & Efficiency

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **pytest-xdist** | 3.8.0 | Parallel test execution | **Essential for 56+ Python files.** Runs tests across multiple CPUs, reducing suite runtime by 4-8x. Supports coverage with `--cov` flag. |
| **pytest-timeout** | 2.4.0 | Test timeout enforcement | Prevents hanging tests from blocking CI. Critical for data pipeline tests that may wait indefinitely on I/O. |
| **pytest-sugar** | 1.1.1 | Enhanced test output | Better progress visualization and failure reporting. Improves DX during test development. |

**Rationale:** 95% coverage means writing many new tests. pytest-xdist makes running 200+ tests feasible (<30s instead of 3+ minutes). pytest-timeout prevents a single bad test from breaking CI.

**Usage:**
```bash
# Run tests in parallel with coverage
pytest -n auto --cov=analysis --cov=api --cov=pipeline --cov-report=html --cov-report=term

# Add timeout to all tests
pytest --timeout=30 --timeout-method=thread
```

**What NOT to use:**
- ❌ pytest-parallel (less mature than xdist, worse coverage integration)
- ❌ Manual multiprocessing (xdist handles it better)

---

### FastAPI Testing Infrastructure

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **httpx** | 0.28.1 | Async HTTP client for FastAPI | **Required for TestClient.** FastAPI's TestClient uses httpx under the hood. Supports async/await for async route testing. |
| **pytest-asyncio** | 1.3.0 | Async test support | **Required for async FastAPI routes.** Enables `async def test_*` tests and `@pytest.mark.asyncio` decorator. |
| **pytest-mock** | 3.15.1 | Mock/patch utilities for pytest | Simplifies mocking in FastAPI tests (data loaders, external services). Better pytest integration than unittest.mock. |

**Rationale:** FastAPI is async by default. httpx + pytest-asyncio enable testing async routes without blocking. pytest-mock simplifies mocking data_loader.load_all_data() and similar I/O operations.

**Usage:**
```python
# FastAPI async route test
@pytest.mark.asyncio
async def test_api_endpoint(client, mocker):
    mocker.patch("api.services.data_loader.load_all_data")
    response = await client.get("/api/v1/trends")
    assert response.status_code == 200
```

**What NOT to use:**
- ❌ requests library (synchronous only, doesn't work with async FastAPI)
- ❌ aiohttp.ClientSession (httpx has better TestClient integration)

---

### Data & Property-Based Testing

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **hypothesis** | 6.151.5 | Property-based testing | **Recommended for data pipeline tests.** Generates edge cases for pandas/geopandas operations that manual tests miss. Excellent for validation functions. |
| **faker** | 40.4.0 | Test data generation | **Optional.** Generates realistic test data (addresses, dates, names). Useful for CLI output tests and integration tests. |

**Rationale:** Property-based testing with hypothesis catches edge cases (empty DataFrames, NaN values, timezone issues) that 95% coverage requires but manual tests miss. faker is optional but valuable for realistic test scenarios.

**Usage:**
```python
from hypothesis import given, strategies as st
import pandas as pd

@given(st.data())
def test_preprocessing_handles_edge_cases(data):
    """Test preprocessing with generated edge cases."""
    df = data.draw(st.dataframes([
        st.column("incident_date", dtype=pd.Timestamp),
        st.column("text_general_code", dtype=str),
    ]))
    result = preprocess_data(df)
    assert len(result) <= len(df)  # No row duplication
```

**What NOT to use:**
- ❌ Manual edge case enumeration (misses cases, brittle)
- ❌ pytest-randomly (different purpose - test order randomization)

---

### Test Reporting & Monitoring

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **pytest-html** | 4.2.0 | HTML test reports | **Recommended for CI artifacts.** Generates browsable test reports with failure details. Useful for debugging CI failures. |
| **pytest-json-report** | 1.5.0 | JSON test reports | **Optional.** Machine-readable test results for CI integrations or custom reporting dashboards. |

**Rationale:** pytest-html provides human-readable test reports for CI artifacts. pytest-json-report enables custom reporting (e.g., posting results to Slack, tracking test trends over time).

**What NOT to use:**
- ❌ allure-pytest (overkill for this project, requires separate server)
- ❌ pytest-benchmark (for performance testing, not coverage)

---

### Mutation Testing (Quality Gate)

| Technology | Version | Purpose | When to Use |
|------------|---------|---------|-------------|
| **mutmut** | 3.4.0 | Mutation testing | **Post-95% validation.** Verifies that tests actually catch bugs (not just line coverage). Run after achieving 95% to validate test quality. |

**Rationale:** 95% coverage doesn't guarantee good tests - mutation testing does. mutmut mutates code (changes `>` to `>=`, `and` to `or`) and checks if tests catch it. Use *after* achieving 95% to validate test effectiveness.

**Usage:**
```bash
# Run mutation testing (slow - use selectively)
mutmut run --paths-to-mutate=analysis/data/preprocessing.py
mutmut results
mutmut html  # View detailed mutation report
```

**What NOT to use:**
- ❌ cosmic-ray (slower, less maintained)
- ❌ Running mutation testing in CI (too slow for regular runs)

---

## Cleanup & Dead Code Detection

### Dead Code Detection

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **vulture** | 2.14 | Dead code detection | **Primary cleanup tool.** Finds unused functions, classes, variables, imports. Works across all Python files. Low false-positive rate. |
| **autoflake** | 2.3.1 | Unused import removal | **Automated cleanup.** Removes unused imports and variables. Can run with `--in-place` for automatic fixes. Integrates with pre-commit. |

**Rationale:** vulture identifies dead code (unused functions, unreachable code). autoflake automates the easiest cleanup (unused imports). Together they prepare codebase for 95% coverage by removing untestable dead code.

**Usage:**
```bash
# Find dead code
vulture analysis/ api/ pipeline/ --min-confidence 80

# Remove unused imports automatically
autoflake --in-place --remove-all-unused-imports --recursive analysis/ api/ pipeline/
```

**What NOT to use:**
- ❌ pyflakes (finds imports only, not dead functions)
- ❌ Manual inspection (time-consuming, misses cases)

---

### Artifact Cleanup

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **pyclean** | 3.5.0 | Python artifact cleanup | **Safe cleanup.** Removes .pyc, __pycache__, .pytest_cache, .coverage, .mypy_cache. Better than `find` + `rm` because it understands Python structure. |

**Rationale:** pyclean safely removes Python build artifacts. It's safer than shell scripts because it knows what's safe to delete and respects .gitignore patterns.

**Usage:**
```bash
# Clean all Python artifacts
pyclean .

# Dry run to see what would be deleted
pyclean --dry-run .
```

**What NOT to use:**
- ❌ `find . -name "*.pyc" -delete` (misses __pycache__ directories, .coverage, etc.)
- ❌ `git clean -fdx` (too aggressive, deletes venvs and data)

---

### Dependency Cleanup

| Technology | Version | Purpose | When to Use |
|------------|---------|---------|-----|
| **pipreqs** | 0.5.0 | Requirements.txt regeneration | **Audit unused dependencies.** Scans actual imports and generates minimal requirements.txt. Use to find dependencies declared but never imported. |

**Rationale:** pipreqs identifies unused dependencies by scanning imports. Useful for cleanup phase to remove dependencies that inflate environment size or have security vulnerabilities.

**Usage:**
```bash
# Generate minimal requirements from actual imports
pipreqs analysis/ --force --savepath requirements-analysis.txt
pipreqs api/ --force --savepath requirements-api.txt

# Compare with existing requirements.txt to find unused deps
```

**What NOT to use:**
- ❌ pip-autoremove (removes dependencies, can break things)
- ❌ Manual dependency tracking (error-prone)

---

## CI/CD Integration

### Coverage Enforcement in CI

**Recommended CI Configuration:**

```yaml
# .github/workflows/test-coverage.yml
name: Test Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for diff-cover

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
          pip install diff-cover

      - name: Run tests with coverage
        run: |
          pytest -n auto \
            --cov=analysis --cov=api --cov=pipeline \
            --cov-report=xml --cov-report=html --cov-report=term \
            --timeout=30

      - name: Enforce 95% coverage on new code
        run: |
          diff-cover coverage.xml \
            --compare-branch=origin/main \
            --fail-under=95 \
            --html-report=diff-cover.html

      - name: Upload coverage reports
        uses: actions/upload-artifact@v4
        with:
          name: coverage-reports
          path: |
            htmlcov/
            diff-cover.html
            coverage.xml
```

**Rationale:**
- pytest-xdist (`-n auto`) parallelizes tests across all CPUs
- pytest-timeout prevents hanging tests
- diff-cover enforces 95% on *new* code (prevents backsliding)
- Artifacts uploaded for debugging failures

---

## Installation & Setup

### Development Dependencies

**Add to `requirements-dev.txt`:**

```txt
# Testing - Coverage
pytest>=8.0
pytest-cov>=7.0.0
coverage[toml]>=7.13.3
diff-cover>=10.2.0
coverage-badge>=1.1.2

# Testing - Acceleration
pytest-xdist>=3.8.0
pytest-timeout>=2.4.0
pytest-sugar>=1.1.1

# Testing - FastAPI
httpx>=0.28.1
pytest-asyncio>=1.3.0
pytest-mock>=3.15.1

# Testing - Data
hypothesis>=6.151.5
faker>=40.4.0

# Testing - Reporting
pytest-html>=4.2.0
pytest-json-report>=1.5.0

# Testing - Quality Gate (optional)
mutmut>=3.4.0

# Cleanup - Dead Code
vulture>=2.14
autoflake>=2.3.1

# Cleanup - Artifacts
pyclean>=3.5.0

# Cleanup - Dependencies (optional)
pipreqs>=0.5.0
```

### pyproject.toml Configuration

**Add to existing pyproject.toml:**

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "-ra",
    "--cov=analysis",
    "--cov=api",
    "--cov=pipeline",
    "--cov-report=term-missing:skip-covered",
    "--cov-report=html",
    "--cov-report=json",
    "--cov-report=xml",
    "--cov-fail-under=95",  # Fail if coverage < 95%
    "-n=auto",  # pytest-xdist parallel execution
    "--timeout=30",  # 30s timeout per test
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "asyncio: marks tests as async",
]

[tool.coverage.run]
source = ["analysis", "api", "pipeline"]
omit = [
    "*/tests/*",
    "*/conftest.py",
    "*/__init__.py",
    "analysis/orchestrate_*.py",
]
branch = true
parallel = true

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
fail_under = 95.0
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]

[tool.coverage.html]
directory = "htmlcov"

[tool.coverage.json]
output = "coverage.json"

[tool.coverage.xml]
output = "coverage.xml"
```

---

## Makefile Targets

**Add to existing Makefile:**

```makefile
.PHONY: test test-cov test-fast test-cov-html test-diff-cover clean-test clean-dead-code cleanup

# Run tests with coverage
test:
	pytest

# Run tests with full coverage reporting
test-cov:
	pytest --cov-report=term-missing --cov-report=html --cov-report=json --cov-report=xml

# Run tests fast (parallel, no coverage)
test-fast:
	pytest -n auto --no-cov

# Open HTML coverage report
test-cov-html: test-cov
	open htmlcov/index.html

# Check coverage on changed files only
test-diff-cover: test-cov
	diff-cover coverage.xml --compare-branch=main --fail-under=95

# Clean test artifacts
clean-test:
	pyclean .
	rm -rf .pytest_cache htmlcov .coverage coverage.xml coverage.json

# Find and report dead code
dead-code:
	@echo "=== Finding dead code with vulture ==="
	vulture analysis/ api/ pipeline/ --min-confidence 80
	@echo "\n=== Finding unused imports with autoflake ==="
	autoflake --check --recursive analysis/ api/ pipeline/

# Remove dead code (use with caution)
clean-dead-code:
	@echo "Removing unused imports..."
	autoflake --in-place --remove-all-unused-imports --recursive analysis/ api/ pipeline/
	@echo "Run 'vulture' output manually for dead function removal"

# Full cleanup (artifacts + dead code check)
cleanup: clean-test dead-code
	@echo "\nCleanup complete. Review vulture output for dead code."
```

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Coverage Engine | coverage.py | pytest-coverage (old name) | Deprecated, unmaintained |
| Parallel Testing | pytest-xdist | pytest-parallel | Less mature, poor coverage integration |
| Async Testing | pytest-asyncio | trio-pytest | FastAPI uses asyncio, not trio |
| Property Testing | hypothesis | QuickCheck ports | Hypothesis is Pythonic, excellent pandas support |
| Dead Code | vulture | pyflakes | Pyflakes only finds unused imports, not functions |
| Mutation Testing | mutmut | cosmic-ray | Cosmic-ray slower, less actively maintained |
| Test Client | httpx | requests | requests is sync-only, FastAPI is async |
| Mock Framework | pytest-mock | unittest.mock | pytest-mock better pytest integration |

---

## What NOT to Add

**Tools to avoid (feature bloat, wrong fit, or duplicative):**

❌ **pytest-benchmark** - For performance testing, not coverage. Wrong milestone.
❌ **tox** - Multi-environment testing. Project uses conda, single Python 3.14 version.
❌ **nox** - Same as tox. Adds complexity without value for this project.
❌ **codecov.io / coveralls.io** - Cloud services add latency. Use diff-cover locally + in CI.
❌ **pytest-randomly** - Test order randomization. Not needed for coverage goal.
❌ **pytest-repeat** - Flakiness detection. Not a current project issue.
❌ **locust / pytest-bdd** - Load testing / BDD framework. Wrong scope for this milestone.
❌ **safety / pip-audit** - Dependency security scanning. Different concern, separate milestone.
❌ **bandit / semgrep** - Security linting. Different concern, separate milestone.

---

## Success Metrics

**Coverage achievement:**
- [ ] 95%+ line coverage across analysis/, api/, pipeline/
- [ ] 90%+ branch coverage
- [ ] 0 files with <80% coverage (use diff-cover to enforce)
- [ ] Coverage badge shows 95%+ in README

**Cleanup metrics:**
- [ ] 0 unused imports (via autoflake)
- [ ] <10 vulture warnings (dead code)
- [ ] requirements.txt matches actual imports (via pipreqs audit)
- [ ] 0 build artifacts in git (via pyclean + .gitignore)

**Performance metrics:**
- [ ] Full test suite runs in <60s (via pytest-xdist)
- [ ] No tests timeout (via pytest-timeout)
- [ ] CI runs tests + coverage in <3 minutes

---

## Confidence Assessment

| Category | Confidence | Source |
|----------|-----------|--------|
| Coverage tooling (pytest-cov, coverage.py) | **HIGH** | Official PyPI versions verified, widely used standard |
| Test acceleration (pytest-xdist) | **HIGH** | Proven tool, 3.8.0 stable release |
| FastAPI testing (httpx, pytest-asyncio) | **HIGH** | FastAPI official testing recommendations |
| Dead code detection (vulture, autoflake) | **HIGH** | Mature tools, 2.14 and 2.3.1 stable |
| Property testing (hypothesis) | **MEDIUM** | Recommended best practice, learning curve exists |
| Mutation testing (mutmut) | **MEDIUM** | Valuable but slow, use sparingly |
| Cleanup utilities (pyclean, pipreqs) | **HIGH** | Standard utilities, well-documented |

---

## Next Steps

**Phase 1: Measure Baseline**
1. Run `pytest --cov=analysis --cov=api --cov=pipeline --cov-report=html`
2. Review htmlcov/index.html to identify coverage gaps
3. Document current coverage % in milestone tracking

**Phase 2: Cleanup Before Testing**
1. Run vulture to find dead code
2. Run autoflake to remove unused imports
3. Run pipreqs to audit dependencies
4. Remove identified dead code manually

**Phase 3: Write Tests to 95%**
1. Use diff-cover to enforce 95% on new code
2. Focus on uncovered files first (biggest impact)
3. Use hypothesis for data pipeline edge cases
4. Mock I/O operations with pytest-mock

**Phase 4: Enforce in CI**
1. Add coverage enforcement to CI workflow
2. Add diff-cover to PR checks
3. Generate coverage badge for README
4. Run mutation testing on critical modules

---

## Sources

**Official Documentation (HIGH confidence):**
- pytest: https://docs.pytest.org/
- coverage.py: https://coverage.readthedocs.io/
- pytest-cov: https://pytest-cov.readthedocs.io/
- FastAPI Testing: https://fastapi.tiangolo.com/tutorial/testing/
- hypothesis: https://hypothesis.readthedocs.io/

**PyPI Versions (verified 2026-02-07):**
- coverage: 7.13.3
- pytest-cov: 7.0.0
- pytest-xdist: 3.8.0
- pytest-asyncio: 1.3.0
- httpx: 0.28.1
- hypothesis: 6.151.5
- vulture: 2.14
- autoflake: 2.3.1
- diff-cover: 10.2.0
- mutmut: 3.4.0

**Community Best Practices (MEDIUM confidence):**
- Python Testing Best Practices (2026): Use pytest-xdist for large test suites
- FastAPI Testing Patterns: httpx TestClient for async routes
- Coverage Enforcement: diff-cover for incremental coverage gates
