# Phase 10: Test Infrastructure & Baseline - Research

**Researched:** February 7, 2026
**Domain:** Python Testing Infrastructure (pytest, pytest-xdist, coverage.py, diff-cover)
**Confidence:** HIGH

## Summary

Phase 10 establishes the testing foundation before writing tests. Research confirms a mature, well-documented ecosystem with clear best practices. The standard stack uses pytest-xdist for parallelization (4-8x speedup), coverage.py with pyproject.toml enforcement for threshold management, and diff-cover for PR-level coverage validation. Mutation testing tools (mutmut, pytest-gremlins) address coverage gaming by validating test quality beyond line coverage.

**Key findings:**
- pytest-xdist's `-n auto` provides optimal worker detection but needs explicit worker count in CI for predictable resource usage
- Coverage enforcement requires `[tool.coverage.report] fail_under = 95.0` in pyproject.toml, NOT pytest addopts
- diff-cover integrates with coverage.py's XML output and requires git branch comparison for PR validation
- Mutation testing (mutmut) prevents coverage gaming by introducing code mutations tests should catch
- Current 60% coverage (from actual run) differs from stated 16% - requires verification baseline
- 45 non-init modules need testing prioritization by complexity and business criticality

**Primary recommendation:** Use pytest-xdist with explicit worker count (e.g., `-n 4` for CI), configure coverage.py's `fail_under` in pyproject.toml's `[tool.coverage.report]` section, integrate diff-cover in GitHub Actions for PR validation, and use mutmut for mutation testing quality validation.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **pytest** | 8.4.2 | Test runner | De facto standard Python test framework, mature ecosystem, fixture system |
| **pytest-xdist** | Latest (install) | Parallel test execution | Official pytest plugin, 4-8x speedup, seamless integration |
| **coverage.py** | 7.10.7 | Coverage measurement | Standard Python coverage tool, pyproject.toml native support |
| **pytest-cov** | 7.0.0 | pytest/coverage integration | Official bridge between pytest and coverage.py |
| **diff-cover** | Latest (install) | Diff coverage enforcement | Git-aware coverage validation for PRs, supports XML reports |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **mutmut** | Latest (install) | Mutation testing | Validate test quality, prevent coverage gaming (optional but recommended) |
| **pytest-gremlins** | Latest (install) | Fast mutation testing | Alternative to mutmut, faster-first approach (alternative) |
| **cosmic-ray** | Latest (install) | Mutation testing | Another mutation testing option (alternative) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| **pytest-xdist** | pytest-parallel | Less mature, fewer features, xdist is official plugin |
| **diff-cover** | codecov, coveralls | External services, more complex setup, diff-cover is local/git-aware |
| **mutmut** | cosmic-ray, pytest-gremlins | Different mutation strategies, mutmut is more widely used |

**Installation:**
```bash
# Core testing infrastructure (pytest, pytest-cov already installed)
pip install pytest-xdist diff-cover

# Optional: mutation testing for quality validation
pip install mutmut
```

## Architecture Patterns

### Recommended Project Structure

```
tests/
├── conftest.py                 # Shared fixtures (already exists)
├── unit/                       # Unit tests by module
│   ├── test_data_loading.py    # Already exists
│   ├── test_data_preprocessing.py
│   ├── test_classification.py
│   └── ...
├── integration/                # Integration tests (already exists)
│   └── test_*.py
└── .coverage_baseline          # Baseline coverage measurement (new)

pyproject.toml                  # Coverage configuration (modify existing)
.github/workflows/
└── test.yml                    # CI workflow with parallel execution (new)
```

### Pattern 1: pytest-xdist Parallel Execution Configuration

**What:** Configure pytest to run tests in parallel across multiple worker processes for 4-8x faster execution.

**When to use:** Always, for all test runs. Tests must be independent (no shared state).

**Configuration:**
```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = [
    "-nauto",                      # Auto-detect CPU count (local development)
    # OR for CI:
    # "-n4",                       # Explicit worker count for CI
    "--cov=analysis",
    "--cov=api",
    "--cov=pipeline",
    "--cov-report=xml",            # Required for diff-cover
    "--cov-report=term-missing",   # Show missing lines in terminal
    "--cov-report=html",           # Generate HTML report
    "--strict-markers",
    "--strict-config",
    "-ra",
]
```

**Source:** [How to Configure pytest for Python Testing](https://oneuptime.com/blog/post/2026-01-24-configure-pytest-python-testing/view) (January 24, 2026)

**Worker count strategy:**
- **Local development:** Use `-nauto` to automatically detect and use all available CPUs
- **CI/GitHub Actions:** Use explicit `-n4` for predictable resource allocation
- **Current system:** 8 CPUs detected, ideal for `-n4` to `-n8` range

**Evidence:**
- Pytest-xdist supports `-n auto` for automatic CPU detection [source](https://dag7.it/appunti/dev/Pytest/Parallel-Testing-Made-Easy-With-pytest-xdist) (January 7, 2026)
- CPU detection issues exist in containerized environments, requiring explicit counts in CI [source](https://github.com/pytest-dev/pytest-xdist/issues/1103)

### Pattern 2: Coverage Threshold Enforcement

**What:** Configure coverage.py to fail builds when coverage falls below 95% threshold.

**When to use:** Always, to enforce coverage standards in CI.

**Configuration:**
```toml
# pyproject.toml
[tool.coverage.run]
source = ["analysis", "api", "pipeline"]
branch = true                    # Enable branch coverage
omit = [
    "*/tests/*",
    "*/__init__.py",
]

[tool.coverage.report]
fail_under = 95.0                # Exit with status 2 if coverage < 95%
precision = 2                    # Report 2 decimal places
show_missing = true              # Show missing line numbers
skip_covered = false             # Show all files, even 100% covered
exclude_also = [
    # Don't complain about missing debug-only code:
    "def __repr__",
    "if self\\.debug",
    # Don't complain if tests don't hit defensive assertion code:
    "raise AssertionError",
    "raise NotImplementedError",
    # Don't complain if non-runnable code isn't run:
    "if 0:",
    "if __name__ == .__main__.:",
    # Don't complain about abstract methods:
    "@(abc\\.)?abstractmethod",
]

[tool.coverage.html]
directory = "htmlcov"
```

**Source:** [Configuration reference — Coverage.py 7.11.2 documentation](https://coverage.readthedocs.io/en/latest/config.html)

**CRITICAL:** The `fail_under` setting goes in `[tool.coverage.report]`, NOT in pytest's `addopts`. Setting `--cov-fail-under` in pytest addopts works but is less maintainable.

### Pattern 3: diff-cover Integration for PR Validation

**What:** Validate coverage only on changed lines in a PR using diff-cover.

**When to use:** In CI pull request workflows to prevent coverage backsliding on new code.

**Installation & Setup:**
```bash
pip install diff-cover
```

**Usage:**
```bash
# Generate coverage.xml (pytest-cov does this with --cov-report=xml)
pytest --cov --cov-report=xml

# Run diff-cover to check PR coverage
diff-cover coverage.xml --compare-branch=origin/main --fail-under=95
```

**GitHub Actions Integration:**
```yaml
# .github/workflows/test.yml
- name: Check coverage on diff
  run: |
    diff-cover coverage.xml \
      --compare-branch=origin/main \
      --fail-under=95 \
      --fail-under=90  # Optional: different threshold for diff
```

**Source:** [Bachmann1234/diff_cover GitHub repository](https://github.com/Bachmann1234/diff_cover)

**Key capabilities:**
- Compares XML coverage report against `git diff`
- Reports coverage percentage for changed lines only
- Supports `--fail-under` threshold enforcement
- Generates HTML, JSON, or Markdown reports
- Can ignore staged/unstaged files with flags

### Anti-Patterns to Avoid

- **Coverage gaming:** Writing tests that hit lines without meaningful assertions (use mutation testing to detect)
- **Shared state in tests:** Tests that depend on execution order or global state break pytest-xdist
- **Setting fail_under in pytest addopts:** Puts configuration in wrong place, harder to maintain
- **Using `-n auto` in CI:** Unpredictable worker counts, use explicit number like `-n4`
- **Measuring total coverage instead of diff coverage in PRs:** Requires 95% total before PR, blockers development

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| **Parallel test execution** | Custom multiprocessing or threading scripts | pytest-xdist with `-n` flag | Handles test collection, distribution, fixture isolation, result aggregation |
| **Coverage enforcement** | Custom coverage parsing scripts | coverage.py `[tool.coverage.report] fail_under` | Standard format, CI integration, HTML reports |
| **Diff coverage validation** | Git diff + coverage parsing logic | diff-cover | Handles edge cases, supports multiple coverage formats, configurable thresholds |
| **Mutation testing** | Custom code mutation scripts | mutmut or pytest-gremlins | Comprehensive mutation operators, pytest integration, survival analysis |
| **Test quality validation** | Manual test reviews | Mutation testing with mutmut | Automated validation, catches assertion gaps, prevents coverage gaming |

**Key insight:** Testing infrastructure has well-solved problems. Building custom solutions introduces maintenance burden, edge cases, and integration complexity. Use established tools with proven track records.

## Common Pitfalls

### Pitfall 1: Tests Break Under Parallel Execution

**What goes wrong:** Tests pass when run sequentially but fail with pytest-xdist's `-n` flag due to shared state, file conflicts, or fixture ordering issues.

**Why it happens:** Tests write to shared files/directories, use global variables, or depend on execution order. Pytest-xdist runs tests in separate processes without shared memory.

**How to avoid:**
- Use `tmp_path` or `tmpdir` fixtures for file operations (already in conftest.py)
- Ensure fixtures are `function` scoped (default), not `session` scoped with side effects
- Don't write to shared directories like `data/` or `reports/` in tests
- Use unique identifiers in test data (e.g., `f"test_{uuid4()}"`)

**Warning signs:** Tests pass with `pytest` but fail with `pytest -n4`, intermittent failures, "file not found" or "permission denied" errors.

### Pitfall 2: Coverage Gaming Without Meaningful Assertions

**What goes wrong:** Tests achieve 95% coverage but don't catch bugs because assertions are missing or ineffective (e.g., just calling functions without checking results).

**Why it happens:** Coverage measures execution, not validation. A test can execute code without asserting expected behavior.

**How to avoid:**
- Use mutation testing (mutmut) to detect weak assertions
- Require at least one assertion per test
- Test both success and failure paths
- Validate edge cases and error conditions
- Review tests for "assertion smell" (no asserts, trivial asserts like `assert True`)

**Warning signs:** Tests pass with mutations (mutmut shows 0% killed), tests with no assertions, tests that only call functions without checking return values.

**Evidence:** [Mutation Testing: Its Concepts With Best Practices](https://www.testmuai.com/learning-hub/mutation-testing/) (January 11, 2026) confirms mutation testing as the solution to coverage gaming.

### Pitfall 3: Incorrect Coverage Baseline Measurement

**What goes wrong:** Coverage baseline doesn't reflect actual state due to test configuration issues, excluded files, or measurement errors.

**Why it happens:** Coverage configuration excludes too many files, tests don't import modules, or coverage runs on wrong codebase.

**How to avoid:**
- Run coverage with full configuration before documenting baseline
- Verify coverage report lists all expected modules
- Check that tests actually import and exercise target modules
- Document both overall coverage and per-module coverage
- Save coverage.xml snapshot for future comparison

**Warning signs:** Coverage percentage changes without code changes, missing modules in report, 0% or 100% coverage for complex modules.

### Pitfall 4: diff-cover Fails with "No lines with coverage information"

**What goes wrong:** diff-cover reports "No lines with coverage information in this diff" even when coverage.xml exists.

**Why it happens:** Path mismatch between coverage.xml and git diff. Coverage uses absolute paths, diff uses relative paths, or working directory is wrong.

**How to avoid:**
- Run coverage and diff-cover from same working directory
- Use `[tool.coverage.run] relative_files = true` in pyproject.toml
- Ensure coverage.xml paths match git repository structure
- Verify git branch comparison target exists (e.g., `origin/main`)

**Evidence:** [diff-cover troubleshooting](https://github.com/Bachmann1234/diff_cover) documents path matching issues.

### Pitfall 5: Overly Aggressive Coverage Targets

**What goes wrong:** Setting 95% or 100% coverage targets leads to unmaintainable tests, testing implementation details, or skipping hard-to-test code.

**Why it happens:** High coverage requirements without considering diminishing returns, test maintenance cost, and business value.

**How to avoid:**
- Target 95% for business-critical modules (data validation, preprocessing)
- Accept lower coverage for difficult-to-test code (visualization, CLI entry points)
- Use `# pragma: no cover` sparingly and with justification
- Focus on behavior coverage over line coverage
- Use branch coverage (`branch = true`) for better quality measurement

**Evidence:** Prior decisions from STATE.md confirm "Target 95% coverage (not 100%): Optimal quality/effort balance, diminishing returns above 95%."

## Code Examples

### Example 1: pytest-xdist Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# Local development: auto-detect CPUs
# CI: override to explicit worker count
addopts = [
    "-nauto",                      # Changed to "-n4" in CI
    "--strict-markers",
    "--strict-config",
    "-ra",
    "--cov=analysis",
    "--cov=api",
    "--cov=pipeline",
    "--cov-report=xml",            # For diff-cover
    "--cov-report=term-missing",
    "--cov-report=html",
]
```

**Source:** [pytest-xdist documentation](https://github.com/pytest-dev/pytest-xdist) and [Parallel Testing Made Easy](https://dag7.it/appunti/dev/Pytest/Parallel-Testing-Made-Easy-With-pytest-xdist)

### Example 2: Coverage Threshold Enforcement

```toml
# pyproject.toml
[tool.coverage.run]
source = ["analysis", "api", "pipeline"]
branch = true
parallel = true                   # Required for pytest-xdist
omit = [
    "*/tests/*",
    "*/__init__.py",
]

[tool.coverage.report]
fail_under = 95.0
precision = 2
show_missing = true
exclude_also = [
    "def __repr__",
    "if self\\.debug",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "@(abc\\.)?abstractmethod",
]
```

**Source:** [Coverage.py Configuration reference](https://coverage.readthedocs.io/en/latest/config.html)

### Example 3: GitHub Actions Workflow with Parallel Execution

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.14"]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for diff-cover

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install pytest-xdist diff-cover

      - name: Run tests in parallel
        run: |
          pytest -n4 --cov --cov-report=xml --cov-report=term-missing

      - name: Check coverage on diff
        if: github.event_name == 'pull_request'
        run: |
          diff-cover coverage.xml \
            --compare-branch=origin/main \
            --fail-under=90 \
            --coverage-file-name=coverage.xml

      - name: Upload coverage reports
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: htmlcov/
```

**Source:** [How to Build Testing Workflows with GitHub Actions](https://oneuptime.com/blog/post/2026-01-26-testing-workflows-github-actions/view) (January 26, 2026)

### Example 4: Mutation Testing with mutmut

```bash
# Install mutmut
pip install mutmut

# Initialize mutation testing
mutmut init

# Run mutation testing on all tests
mutmut run

# View results
mutmut results

# HTML report
mutmut html

# Check specific mutation score threshold
mutmut run --paths-to-mutate=analysis/
```

**Source:** [boxed/mutmut GitHub repository](https://github.com/boxed/mutmut) and [Getting Started with Mutation Testing](https://about.codecov.io/blog/getting-started-with-mutation-testing-in-python-with-mutmut/)

### Example 5: Baseline Coverage Measurement

```bash
# Measure baseline coverage
pytest --cov=analysis --cov=api --cov=pipeline \
  --cov-report=xml \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-report=json:coverage_baseline.json

# Generate per-module breakdown
coverage report --sort=cover > .coverage_baseline

# Count untested modules
coverage report | awk 'NR>2 && $4 < 50 {print $1}' | wc -l

# Save for comparison
cp .coverage .coverage.baseline
cp coverage.xml coverage.baseline.xml
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| **Sequential test execution** | **pytest-xdist parallel execution** | pytest-xdist mature (2020-2024) | 4-8x faster test execution, CI feedback loops |
| **Coverage in .coveragerc** | **Coverage in pyproject.toml** | Python 3.11+ native TOML support (2023) | Single config file, better tooling integration |
| **Total coverage enforcement** | **Diff coverage for PRs** | diff-cover adoption (2019-present) | Prevents backsliding, allows incremental improvement |
| **Manual test quality reviews** | **Mutation testing automation** | mutmut, pytest-gremlins maturity (2022-2025) | Detects coverage gaming, validates test assertions |
| **Setting workers via environment** | **Explicit `-n` flag in config** | pytest-xdist best practices (2024-2025) | Predictable CI resource usage, reproducible runs |

**Deprecated/outdated:**
- **Setup.cfg for coverage:** Prefer pyproject.toml for modern Python projects
- **`--cov-fail-under` in pytest addopts:** Move to `[tool.coverage.report] fail_under`
- **Codecov for PR coverage:** Diff-cover provides local, git-aware alternative without external service
- **Manual coverage diff scripts:** Use diff-cover for battle-tested edge case handling

## Open Questions

### Q1: Actual Coverage Baseline Discrepancy

**What we know:**
- Phase context states "Current coverage: 16% (225/1408 statements)"
- Running `python -m coverage report` shows "TOTAL: 2074 statements, 828 missed, 60% cover"
- Significant discrepancy between stated and measured coverage

**What's unclear:**
- Is the 16% figure outdated or measured differently?
- Does 16% refer to a subset of modules (e.g., excluding tests)?
- Was 16% measured before recent test additions?

**Recommendation:**
Run fresh baseline measurement with consistent configuration:
```bash
pytest --cov=analysis --cov=api --cov=pipeline --cov-report=term-missing
```
Document both overall coverage and per-module breakdown. Use measured baseline (likely 60%) rather than outdated 16% figure.

### Q2: Optimal Worker Count for CI

**What we know:**
- Local system has 8 CPUs
- pytest-xdist's `-n auto` detects all CPUs
- GitHub Actions runners have 2-core (standard) or variable CPUs

**What's unclear:**
- What GitHub Actions runner tier will be used?
- Should workers match physical cores (4) or logical cores (8)?
- What's the memory per worker constraint?

**Recommendation:**
Start with `-n4` for CI (conservative, fits most runners). Monitor execution time and adjust based on actual performance. Consider matrix strategy to test with different worker counts.

### Q3: Mutation Testing Integration Strategy

**What we know:**
- mutmut is the most mature mutation testing tool
- pytest-gremlins offers "fast-first" approach
- Cosmic-ray is another alternative

**What's unclear:**
- Should mutation testing run on every commit or only in nightly builds?
- What mutation score threshold is acceptable?
- Which mutation operators are most relevant for this codebase?

**Recommendation:**
Start with mutmut in development-only mode (not blocking CI). Run mutation testing on a subset of critical modules first. Set initial target of 80% mutation score (meaning tests catch 80% of mutations). Adjust based on results and maintenance burden.

## Sources

### Primary (HIGH confidence)

- **[pytest-xdist GitHub repository](https://github.com/pytest-dev/pytest-xdist)** - Parallel test execution plugin
- **[Coverage.py 7.11.2 Configuration Documentation](https://coverage.readthedocs.io/en/latest/config.html)** - Authoritative coverage.py configuration reference
- **[diff-cover GitHub repository](https://github.com/Bachmann1234/diff_cover)** - Diff coverage tool documentation and examples
- **[pytest 8.4.2 installed in project](/Users/dustinober/Projects/Crime Incidents Philadelphia/)** - Verified local installation
- **[coverage.py 7.10.7 installed in project](/Users/dustinober/Projects/Crime Incidents Philadelphia/)** - Verified local installation
- **[Project pyproject.toml configuration](/Users/dustinober/Projects/Crime Incidents Philadelphia/pyproject.toml)** - Existing pytest configuration
- **[Existing test infrastructure conftest.py](/Users/dustinober/Projects/Crime Incidents Philadelphia/tests/conftest.py)** - Current fixture setup

### Secondary (MEDIUM confidence)

- **[How to Configure pytest for Python Testing](https://oneuptime.com/blog/post/2026-01-24-configure-pytest-python-testing/view)** (January 24, 2026) - Covers pytest configuration including project setup, fixtures, markers, and CI/CD integration
- **[Parallel Testing Made Easy With pytest-xdist](https://dag7.it/appunti/dev/Pytest/Parallel-Testing-Made-Easy-With-pytest-xdist)** (January 7, 2026) - Explains using `pytest -n auto` to automatically utilize CPUs
- **[Python Code Review Checklist: 25 Things to Check for...](https://www.augmentcode.com/guides/python-code-review-checklist)** (January 16, 2026) - Mentions automation: "Configure pytest with --cov=src --cov-fail-under=80 in pyproject.toml"
- **[How to Build Testing Workflows with GitHub Actions](https://oneuptime.com/blog/post/2026-01-26-testing-workflows-github-actions/view)** (January 26, 2026) - Comprehensive guide on structuring testing in GitHub Actions
- **[Concurrent tests in GitHub Actions](https://warpbuild.com/blog/concurrent-tests)** (January 28, 2026) - Details concurrent tests and test sharding in GitHub Actions
- **[Making PyPI's test suite 81% faster](https://blog.trailofbits.com/2025/05/01/making-pypis-test-suite-81-faster/)** (May 1, 2025) - Real-world optimization case study
- **[pytest-gremlins GitHub repository](https://github.com/mikelane/pytest-gremlins)** (Updated Jan 2026) - Fast-first mutation testing for pytest
- **[boxed/mutmut GitHub repository](https://github.com/boxed/mutmut)** - Mutation testing system for Python
- **[Getting Started with Mutation Testing in Python with mutmut](https://about.codecov.io/blog/getting-started-with-mutation-testing-in-python-with-mutmut/)** (March 2023) - Step-by-step mutmut tutorial
- **[Mutation testing in Python using Mutmut](https://medium.com/@dead-pixel.club/mutation-testing-in-python-using-mutmut-a094ad486050)** - Implementation guide with practical examples
- **[Effective Python Testing With pytest](https://realpython.com/pytest-python-testing/)** - Comprehensive pytest guide covering fixtures, test structure, and assertions
- **[How to write and report assertions in tests](https://docs.pytest.org/en/stable/how-to/assert.html)** - Official pytest documentation on assertions
- **[Detailed Guide to Writing Efficient Unit Tests in Python with pytest](https://medium.com/@ydmarinb/detailed-guide-to-writing-efficient-unit-tests-in-python-with-pytest-2e56b33cb7dc)** - Best practices for legible asserts, test independence, and input range testing
- **[Python Testing with Pytest: Features & Best Practices](https://keploy.io/blog/community/python-testing-with-pytest-features-best-practices)** (January 17, 2025) - Discusses behavior-focused testing approaches
- **[Concrete Testing Strategies to Put Into Practice](https://dagster.io/blog/pytest-for-agent-generated-code-concrete-testing-strategies-to-put-into-practice)** (January 26, 2026) - 2026 article covering pytest strategies with explicit test levels
- **[Hybrid Fault-Driven Mutation Testing for Python](https://arxiv.org/pdf/2601.19088)** (2026) - Research on PyTation for Python test suite gap identification
- **[Mutation Testing: Its Concepts With Best Practices](https://www.testmuai.com/learning-hub/mutation-testing/)** (January 11, 2026) - Comprehensive guide on mutation testing concepts to prevent coverage gaming

### Tertiary (LOW confidence)

- **[Mastering Parallel Execution in Pytest](https://medium.com/ai-qa-nexus/supercharging-your-test-runs-mastering-parallel-execution-in-pytest-3124e166fd60)** - Medium article on parallel execution
- **[How to run pytest tests in parallel? - Stack Overflow](https://stackoverflow.com/questions/45733763/how-to-run-pytest-tests-in-parallel)** - Community discussion
- **[Code Coverage Reports with GitHub Actions](https://oneuptime.com/blog/post/2026-01-27-code-coverage-reports-github-actions/view)** (January 27, 2026) - Covers Codecov, Jest, and native solutions
- **[Coverage Diff · GitHub Marketplace](https://github.com/marketplace/actions/coverage-diff)** - GitHub Action for diff coverage
- **[pytest-xdist worker count auto detection](https://github.com/pytest-dev/pytest-xdist/issues/1103)** - Ongoing issue about CPU detection

## Metadata

**Confidence breakdown:**
- Standard stack: **HIGH** - All tools are industry standards with extensive documentation and adoption
- Architecture: **HIGH** - Patterns verified with official documentation and recent 2025-2026 sources
- Pitfalls: **HIGH** - Well-documented issues with official guidance on avoidance
- Module prioritization: **MEDIUM** - Requires codebase-specific analysis for 45 modules

**Research date:** February 7, 2026
**Valid until:** March 9, 2026 (30 days - stable ecosystem, but fast-moving tooling)

**Verification performed:**
- Checked installed pytest version (8.4.2) and coverage.py version (7.10.7)
- Verified existing pyproject.toml configuration structure
- Counted actual Python modules (45 non-init files)
- Ran coverage report to verify current state (60% measured vs 16% stated)
- Detected 8 CPU cores for optimal worker count configuration
