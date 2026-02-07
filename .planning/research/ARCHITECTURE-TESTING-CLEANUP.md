# Architecture Research: Testing & Cleanup Integration

**Domain:** Comprehensive Test Coverage (95%+) and Repository Cleanup  
**Researched:** February 7, 2026  
**Confidence:** HIGH

## Executive Summary

This architecture document describes how comprehensive testing (95%+ coverage) and repository cleanup integrate with the existing Python monorepo for Crime Incidents Philadelphia. The project uses a well-structured monorepo with three main packages (`analysis/`, `api/`, `pipeline/`) and an established test infrastructure (`tests/`, pytest, coverage tracking). The recommended approach is to enhance coverage incrementally while performing cleanup in parallel, leveraging the existing test organization and CI/CD infrastructure.

**Key recommendation:** Tests first, then cleanup. This ensures that cleanup doesn't break functionality and that coverage improvements validate all code paths before removal decisions.

## Current Architecture State

### Existing Monorepo Structure

```
Crime Incidents Philadelphia/
├── analysis/          # 42 Python files - CLI, models, data processing
│   ├── cli/          # Typer-based CLI commands
│   ├── data/         # Loading, validation, preprocessing
│   ├── models/       # Classification, time series, validation
│   ├── utils/        # Spatial, temporal, classification utilities
│   └── visualization/ # Forecast plots, reporting
├── api/              # 11 Python files - FastAPI REST service
│   ├── routers/      # API route handlers
│   ├── services/     # Data loading, business logic
│   └── models/       # API data models
├── pipeline/         # 3 Python files - Data ETL jobs
│   ├── export_data.py
│   └── refresh_data.py
├── tests/            # 22 test files - Unit, integration, API tests
│   ├── conftest.py   # Shared fixtures (sample_crime_df, tmp_output_dir)
│   ├── test_*.py     # Unit tests for data, models, CLI
│   └── integration/  # Integration tests for phases, workflows
├── web/              # Next.js frontend (separate stack)
├── pyproject.toml    # pytest, mypy, black, ruff config
├── requirements-dev.txt  # Dev dependencies including pytest-cov
└── docker-compose.yml    # Local development stack
```

### Current Test Infrastructure

**Test Framework:**
- pytest 8.x with configuration in `pyproject.toml`
- pytest-cov for coverage tracking
- FastAPI TestClient for API tests
- Typer CliRunner for CLI tests

**Current Coverage:** 16% (225/1408 statements)
- Coverage tracked via `coverage.json` and `htmlcov/`
- Tests focused on: data processing, CLI commands, API endpoints, integration workflows
- Gaps: visualization, some models, configuration loaders, orchestrators

**Test Organization:**
- Unit tests: `tests/test_data_*.py`, `tests/test_temporal.py`, `tests/test_classification.py`
- CLI tests: `tests/test_cli_*.py` (chief, patrol, policy, forecasting)
- API tests: `tests/test_api_endpoints.py`
- Integration tests: `tests/integration/test_*.py` (migration, phase validation)

**Key Fixtures (conftest.py):**
- `sample_crime_df`: 100-row synthetic crime dataset for fast tests
- `tmp_output_dir`: Temporary directory for test outputs

## Recommended Architecture for 95% Coverage

### Test Organization Strategy

#### 1. Test File Mapping (Where New Tests Go)

**Principle:** Mirror source structure in tests directory.

| Source Package | Test Location | Coverage Target | Approach |
|----------------|---------------|-----------------|----------|
| `analysis/cli/` | `tests/test_cli_*.py` | 95% | CLI integration tests with CliRunner |
| `analysis/data/` | `tests/test_data_*.py` | 95% | Unit tests with sample fixtures |
| `analysis/models/` | `tests/test_classification.py`, `tests/test_models_*.py` | 95% | Unit + integration tests |
| `analysis/utils/` | `tests/test_temporal.py`, `tests/test_utils_*.py` | 95% | Unit tests for pure functions |
| `analysis/visualization/` | `tests/test_visualization_*.py` | 85% | Visual regression + output validation |
| `api/routers/` | `tests/test_api_endpoints.py` | 95% | FastAPI TestClient integration tests |
| `api/services/` | `tests/test_api_services.py` | 95% | Unit tests with mocked data |
| `pipeline/` | `tests/test_pipeline_*.py` | 90% | Integration tests with sample data |

**New test files needed:**
```bash
tests/test_models_time_series.py      # For analysis/models/time_series.py
tests/test_models_validation.py       # For analysis/models/validation.py
tests/test_visualization_plots.py     # For analysis/visualization/
tests/test_config_loader.py           # For config loaders
tests/test_artifact_manager.py        # For artifact_manager.py
tests/test_report_utils.py            # For report_utils.py
tests/test_spatial_utils.py           # For spatial_utils.py
tests/test_event_utils.py             # For event_utils.py
tests/test_api_services.py            # For api/services/
tests/test_api_models.py              # For api/models/
tests/test_pipeline_refresh.py        # For pipeline/refresh_data.py
```

#### 2. Test Type Distribution

**Unit Tests (70% of coverage):**
- Pure functions in `analysis/utils/`
- Data transformations in `analysis/data/`
- Model logic in `analysis/models/`
- API service layer in `api/services/`

**Integration Tests (25% of coverage):**
- CLI commands end-to-end
- API endpoints with real app context
- Pipeline jobs with sample datasets
- Cross-module workflows

**Smoke Tests (5% of coverage):**
- Import validations
- Configuration loading
- Service health checks

### Coverage Measurement Integration Points

#### 1. Local Development Coverage Workflow

```bash
# Run tests with coverage
pytest tests/ --cov=analysis --cov=api --cov=pipeline --cov-report=term-missing

# Generate HTML report
pytest tests/ --cov=analysis --cov=api --cov=pipeline --cov-report=html

# Check coverage percentage
pytest tests/ --cov=analysis --cov=api --cov=pipeline --cov-report=term | grep "TOTAL"

# Fail if below threshold (for CI)
pytest tests/ --cov=analysis --cov=api --cov=pipeline --cov-fail-under=95
```

#### 2. Coverage Configuration in pyproject.toml

**Add to `[tool.pytest.ini_options]`:**
```toml
[tool.coverage.run]
source = ["analysis", "api", "pipeline"]
omit = [
    "*/tests/*",
    "*/conftest.py",
    "*/__pycache__/*",
    "*/web/*",  # Next.js has separate coverage
]

[tool.coverage.report]
precision = 2
skip_empty = true
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
```

#### 3. Coverage Tracking Automation

**Files tracked:**
- `coverage.json`: Machine-readable coverage data (already exists)
- `htmlcov/`: HTML coverage report (already exists)
- `.coverage`: SQLite database (already exists)

**Coverage delta tracking:**
```bash
# Before changes
pytest --cov=analysis --cov=api --cov=pipeline --cov-report=json
mv coverage.json coverage-before.json

# After changes
pytest --cov=analysis --cov=api --cov=pipeline --cov-report=json

# Compare
python scripts/compare_coverage.py coverage-before.json coverage.json
```

### CI/Automation Hook Points for Coverage

#### 1. GitHub Actions Integration (if CI exists)

**Coverage workflow:**
```yaml
# .github/workflows/test-coverage.yml
name: Test Coverage
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.14'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests with coverage
        run: |
          pytest tests/ --cov=analysis --cov=api --cov=pipeline \
            --cov-report=term-missing \
            --cov-report=json \
            --cov-fail-under=95
      
      - name: Upload coverage report
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.json
```

#### 2. Pre-commit Hook Integration

**Local quality gate:**
```bash
# .git/hooks/pre-commit or .pre-commit-config.yaml
- repo: local
  hooks:
    - id: pytest-coverage
      name: pytest coverage check
      entry: pytest
      args: [
        "tests/",
        "--cov=analysis",
        "--cov=api", 
        "--cov=pipeline",
        "--cov-fail-under=95",
        "-q"
      ]
      language: system
      pass_filenames: false
```

#### 3. Make Target for Coverage Checks

**Add to Makefile:**
```makefile
.PHONY: test test-cov test-cov-html coverage-report

test:
	pytest tests/

test-cov:
	pytest tests/ --cov=analysis --cov=api --cov=pipeline --cov-report=term-missing

test-cov-html:
	pytest tests/ --cov=analysis --cov=api --cov=pipeline --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

coverage-report:
	@pytest tests/ --cov=analysis --cov=api --cov=pipeline --cov-report=term | grep "TOTAL"
```

## Repository Cleanup Architecture

### Cleanup Workflow (Audit → Review → Remove)

#### Phase 1: Audit (Identify Candidates)

**Files to audit:**
1. **Python cache files** (143 __pycache__ directories, *.pyc files)
2. **Build artifacts** (htmlcov/, .mypy_cache/, .ruff_cache/, .pytest_cache/)
3. **Unused source files** (identified via coverage analysis)
4. **Dead code** (functions/classes with 0% coverage after reaching 95%)
5. **Deprecated scripts** (scripts/ directory inspection)
6. **Temporary data** (data/external/.cache/, *.parquet files)

**Audit commands:**
```bash
# Find all cache files
find . -type d -name "__pycache__" > cleanup-audit-cache.txt
find . -name "*.pyc" >> cleanup-audit-cache.txt

# Find build artifacts
du -sh htmlcov .mypy_cache .ruff_cache .pytest_cache > cleanup-audit-build.txt

# Find files with 0% coverage (after 95% target reached)
python scripts/find_dead_code.py coverage.json > cleanup-audit-dead-code.txt

# Find large data files
find data/ -name "*.parquet" -size +100M > cleanup-audit-large-files.txt

# Find potentially unused scripts
ls -la scripts/*.py scripts/*.sh > cleanup-audit-scripts.txt
```

**Audit script: `scripts/audit_cleanup_candidates.py`**
```python
"""Identify files and directories safe to remove."""
import json
from pathlib import Path

def audit_cache_files():
    """Find all Python cache files."""
    root = Path(".")
    cache_dirs = list(root.rglob("__pycache__"))
    pyc_files = list(root.rglob("*.pyc"))
    return {"cache_dirs": cache_dirs, "pyc_files": pyc_files}

def audit_build_artifacts():
    """Find build and test artifact directories."""
    artifacts = ["htmlcov", ".mypy_cache", ".ruff_cache", ".pytest_cache"]
    return {name: Path(name).exists() for name in artifacts}

def audit_zero_coverage_files(coverage_json_path):
    """Find source files with 0% coverage."""
    with open(coverage_json_path) as f:
        cov_data = json.load(f)
    
    zero_cov_files = []
    for file_path, file_data in cov_data.get("files", {}).items():
        if file_data.get("summary", {}).get("percent_covered", 0) == 0:
            zero_cov_files.append(file_path)
    
    return zero_cov_files

# Generate audit report
```

#### Phase 2: Review (Safety Gates)

**Safety checks before removal:**
1. **Git status check**: Ensure no uncommitted changes
2. **Import validation**: Check if any "unused" files are imported
3. **Test dependency check**: Verify files aren't used by tests
4. **Manual review**: Human approval for source file deletions

**Review script: `scripts/review_cleanup_safety.py`**
```python
"""Safety checks for cleanup operations."""
import subprocess
import ast
from pathlib import Path

def check_git_clean():
    """Ensure working directory is clean."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True
    )
    if result.stdout.strip():
        raise RuntimeError("Git working directory not clean. Commit or stash changes.")

def check_imports(file_to_remove):
    """Check if file is imported anywhere."""
    # Search for imports of this module
    module_name = file_to_remove.replace("/", ".").replace(".py", "")
    grep_result = subprocess.run(
        ["git", "grep", f"import.*{module_name}"],
        capture_output=True,
        text=True
    )
    if grep_result.returncode == 0:
        return False, f"File imported in: {grep_result.stdout}"
    return True, "No imports found"

def generate_review_report(audit_results):
    """Generate human-readable review report."""
    # Format audit results for manual review
    pass
```

#### Phase 3: Remove (Automated with Safeguards)

**Removal categories:**

| Category | Safety Level | Removal Method | Requires Approval |
|----------|--------------|----------------|-------------------|
| Cache files (`__pycache__`, `*.pyc`) | SAFE | Automated | No |
| Build artifacts (`htmlcov/`, etc.) | SAFE | Automated | No |
| Large data files in `.cache/` | SAFE | Automated (if in .gitignore) | No |
| Unused scripts | MEDIUM | Manual review | Yes |
| Dead source code (0% coverage) | HIGH RISK | Manual review + tests | Yes |
| Deprecated modules | HIGH RISK | Manual review + migration | Yes |

**Removal script: `scripts/cleanup.py`**
```python
"""Safe cleanup operations."""
import shutil
from pathlib import Path
from enum import Enum

class CleanupLevel(Enum):
    SAFE = "safe"           # Auto-remove, no approval needed
    REVIEW = "review"       # Manual approval required
    DANGEROUS = "dangerous" # Manual approval + extra checks

def cleanup_cache_files():
    """Remove all Python cache files (SAFE)."""
    count = 0
    for pycache in Path(".").rglob("__pycache__"):
        shutil.rmtree(pycache)
        count += 1
    for pyc in Path(".").rglob("*.pyc"):
        pyc.unlink()
        count += 1
    return count

def cleanup_build_artifacts():
    """Remove build and test artifacts (SAFE)."""
    artifacts = ["htmlcov", ".mypy_cache", ".ruff_cache", ".pytest_cache"]
    removed = []
    for artifact in artifacts:
        path = Path(artifact)
        if path.exists():
            shutil.rmtree(path)
            removed.append(artifact)
    return removed

def cleanup_with_approval(file_path, reason):
    """Remove file after manual approval (REVIEW/DANGEROUS)."""
    print(f"Prepare to remove: {file_path}")
    print(f"Reason: {reason}")
    approval = input("Confirm removal [y/N]: ")
    if approval.lower() == 'y':
        Path(file_path).unlink()
        return True
    return False
```

**Make targets for cleanup:**
```makefile
.PHONY: clean clean-cache clean-build clean-all audit-cleanup

clean-cache:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

clean-build:
	rm -rf htmlcov .mypy_cache .ruff_cache .pytest_cache .coverage coverage.json

clean-all: clean-cache clean-build

audit-cleanup:
	python scripts/audit_cleanup_candidates.py
```

### Integration with Existing .gitignore

**Current .gitignore already excludes:**
- `.cache/`, `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`
- `htmlcov/`, `.coverage`
- `__pycache__/`, `*.pyc`
- `data/external/.cache/`, `data/external/*.parquet`

**No .gitignore changes needed** — cleanup preserves existing patterns.

## Build Order: Tests First vs Cleanup First

### Recommended: Tests First, Then Cleanup

**Rationale:**
1. **Validation before removal**: 95% coverage ensures all code paths are tested before deciding what's unused
2. **Safety**: Tests catch breaking changes from cleanup
3. **Confidence**: High coverage means "0% coverage" files are truly unused
4. **Reversibility**: Easy to restore accidentally removed code if tests fail

**Recommended Build Order:**

```
Phase 1: Baseline Coverage Assessment (Week 1)
├── Run current tests: pytest tests/ --cov=analysis --cov=api --cov=pipeline
├── Generate coverage report: coverage.json, htmlcov/
├── Identify coverage gaps: Files/functions with <95% coverage
└── Document current state: 16% → 95% gap analysis

Phase 2: Coverage Improvement - Core Modules (Week 2-3)
├── Add unit tests for analysis/data/ (highest impact)
├── Add unit tests for analysis/models/
├── Add tests for analysis/utils/
└── Target: 60-70% coverage

Phase 3: Coverage Improvement - API & Pipeline (Week 4)
├── Add API service tests
├── Add API endpoint tests (extend existing)
├── Add pipeline integration tests
└── Target: 80-85% coverage

Phase 4: Coverage Improvement - Remaining Gaps (Week 5)
├── Add tests for visualization (output validation, not pixel-perfect)
├── Add tests for config loaders
├── Add tests for orchestrators
└── Target: 95%+ coverage

Phase 5: Cleanup Audit (Week 6)
├── Run cleanup audit: scripts/audit_cleanup_candidates.py
├── Review 0% coverage files: Are they truly unused?
├── Check for deprecated scripts
└── Generate cleanup plan

Phase 6: Safe Cleanup (Week 6)
├── Remove cache files: make clean-cache
├── Remove build artifacts: make clean-build
├── Review and remove dead code (with approval)
└── Verify tests still pass: pytest tests/

Phase 7: Validation (Week 6)
├── Run full test suite: pytest tests/
├── Verify coverage maintained: pytest --cov-fail-under=95
├── Run CI/CD pipeline (if exists)
└── Manual smoke testing
```

**Why not cleanup first?**
- Risk: Might remove code that's actually used but untested
- False positives: Low coverage doesn't mean unused (might be integration-tested)
- Rework: If cleanup breaks something, need to restore and retest

## Component Integration: Coverage + Cleanup

### Coverage-Driven Cleanup Decision Matrix

| File Coverage | Import References | Test Dependencies | Action |
|---------------|-------------------|-------------------|--------|
| 95%+ | Any | Any | **KEEP** (actively used) |
| 50-95% | Multiple | Yes | **KEEP** (add more tests) |
| 1-50% | None | No | **REVIEW** (might be unused) |
| 0% | None | No | **CANDIDATE** (likely unused) |
| 0% | Any | Any | **KEEP** (tested indirectly) |

### Tooling Integration

**Coverage + Cleanup Pipeline:**
```bash
# 1. Measure coverage
pytest tests/ --cov=analysis --cov=api --cov=pipeline --cov-report=json

# 2. Identify cleanup candidates
python scripts/find_cleanup_candidates.py coverage.json

# 3. Review candidates (manual)
python scripts/review_cleanup_safety.py cleanup-candidates.txt

# 4. Execute safe cleanup
make clean-cache clean-build

# 5. Execute reviewed cleanup (manual approval)
python scripts/cleanup.py --candidates cleanup-approved.txt

# 6. Verify coverage maintained
pytest tests/ --cov-fail-under=95
```

## Data Flow: Testing & Cleanup Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Developer Workflow                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Add Tests (Increase Coverage)                         │
│  ├── Write new test files (tests/test_*.py)                    │
│  ├── Run pytest --cov to measure coverage                      │
│  ├── Iterate until 95%+ coverage reached                       │
│  └── Commit tests + coverage reports                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Audit Cleanup Candidates                              │
│  ├── Run audit script: scripts/audit_cleanup_candidates.py     │
│  ├── Analyze coverage.json for 0% coverage files               │
│  ├── Check for unused imports/dependencies                     │
│  └── Generate cleanup-candidates.txt                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Review Safety Gates                                   │
│  ├── Manual review of candidates                               │
│  ├── Check import references: git grep                         │
│  ├── Verify not used in tests                                  │
│  └── Approve for removal: cleanup-approved.txt                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Execute Cleanup                                       │
│  ├── Safe cleanup: make clean-cache clean-build                │
│  ├── Reviewed cleanup: scripts/cleanup.py --approved           │
│  ├── Verify tests pass: pytest tests/                          │
│  └── Commit cleanup changes                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: Continuous Validation                                 │
│  ├── CI runs pytest --cov-fail-under=95                        │
│  ├── Pre-commit hooks check coverage                           │
│  └── Coverage tracked over time                                │
└─────────────────────────────────────────────────────────────────┘
```

## Scaling Considerations

### Current Scale (1-2 developers)
- **Tests:** Run full suite locally (~5-10 minutes estimated with 95% coverage)
- **Coverage:** Local HTML reports sufficient
- **Cleanup:** Manual review feasible

### Medium Scale (3-5 developers)
- **Tests:** Parallel test execution (`pytest -n auto` with pytest-xdist)
- **Coverage:** Centralized coverage tracking (Codecov, Coveralls)
- **Cleanup:** Automated audit in CI, manual approval via PR review

### Large Scale (5+ developers)
- **Tests:** Distributed test execution, test result caching
- **Coverage:** Coverage diffs on PRs, branch coverage requirements
- **Cleanup:** Automated dead code detection, periodic cleanup sprints

## Integration with Existing Infrastructure

### Docker Compose Integration

**Test execution in containers:**
```yaml
# docker-compose.test.yml
services:
  test:
    build:
      context: .
      dockerfile: pipeline/Dockerfile
    command: pytest tests/ --cov=analysis --cov=api --cov=pipeline
    volumes:
      - ./tests:/app/tests
      - ./analysis:/app/analysis
      - ./api:/app/api
      - ./pipeline:/app/pipeline
      - ./coverage.json:/app/coverage.json
      - ./htmlcov:/app/htmlcov
```

**Usage:**
```bash
docker compose -f docker-compose.test.yml up test
```

### CI/CD Integration (Cloud Build)

**cloudbuild.yaml addition:**
```yaml
# Test step before deployment
steps:
  # Existing build steps...
  
  # Add test + coverage step
  - name: 'python:3.14'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install -r requirements-dev.txt
        pytest tests/ --cov=analysis --cov=api --cov=pipeline --cov-fail-under=95
    id: 'test-coverage'
  
  # Existing deployment steps only if tests pass...
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Coverage Theater
**What:** Writing tests that execute code but don't validate behavior
**Why wrong:** High coverage number, but tests don't catch bugs
**Do instead:** Write meaningful assertions that validate expected behavior

### Anti-Pattern 2: Deleting Untested Code
**What:** Removing files with 0% coverage before writing tests
**Why wrong:** Code might be used indirectly or in production-only paths
**Do instead:** Increase coverage first, then identify truly unused code

### Anti-Pattern 3: Ignoring Integration Tests
**What:** Focusing only on unit test coverage
**Why wrong:** Misses integration issues, real workflow bugs
**Do instead:** Balance unit tests (70%) with integration tests (25%)

### Anti-Pattern 4: Manual Cleanup
**What:** Manually deleting cache files without scripts
**Why wrong:** Error-prone, not reproducible, might delete wrong files
**Do instead:** Use scripted cleanup with safety checks

### Anti-Pattern 5: Coverage Without CI
**What:** Tracking coverage locally but not in CI
**Why wrong:** Coverage can regress without visibility
**Do instead:** Enforce coverage threshold in CI/CD pipeline

## Sources

### Primary Sources (HIGH confidence)
- Project structure analysis: `analysis/`, `api/`, `pipeline/`, `tests/`
- Existing test infrastructure: `pyproject.toml`, `tests/conftest.py`, `requirements-dev.txt`
- Current coverage data: `coverage.json` (16% baseline)
- Docker Compose configuration: `docker-compose.yml`
- CI/CD configuration: `cloudbuild.yaml`
- Existing documentation: `.planning/codebase/TESTING.md`

### Secondary Sources (MEDIUM confidence)
- pytest documentation: https://docs.pytest.org/
- pytest-cov documentation: https://pytest-cov.readthedocs.io/
- Python testing best practices (industry standard patterns)

---
*Architecture research for: Comprehensive test coverage (95%+) and repository cleanup*
*Researched: February 7, 2026*
*Confidence: HIGH*
