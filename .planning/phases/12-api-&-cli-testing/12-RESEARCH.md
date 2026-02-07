# Phase 12: API & CLI Testing - Research

**Researched:** 2026-02-07
**Domain:** FastAPI API testing, Typer CLI testing, pytest infrastructure
**Confidence:** HIGH

## Summary

Phase 12 focuses on comprehensive testing of FastAPI endpoints (11 routes) and Typer CLI commands (8 commands + 2 main commands). The codebase already has foundational test infrastructure from Phase 11, with existing tests demonstrating the patterns for both API (TestClient) and CLI (CliRunner) testing.

**Primary finding:** The project uses standard FastAPI + Typer testing patterns with TestClient and CliRunner. The existing tests in `test_api_endpoints.py` and CLI test files provide working examples to extend. The main work is systematic coverage of all untested endpoints and commands, plus adding service layer unit tests with mocked data loaders.

**Key recommendations:**
- Use FastAPI's TestClient for all endpoint testing (app has minimal async, no database)
- Use Typer's CliRunner for all CLI command testing (already established pattern)
- Mock data loaders at service layer using pytest fixtures and monkeypatch
- Focus on request/response contracts and error handling for API
- Focus on argument parsing, output files, and exit codes for CLI

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **pytest** | 8.0+ | Test runner | Project already configured, standard for Python testing |
| **FastAPI TestClient** | (from fastapi) | API endpoint testing | Official FastAPI testing tool, handles ASGI app automatically |
| **Typer CliRunner** | (from typer.testing) | CLI command testing | Official Typer testing tool, clean invocation without subprocess |
| **pytest-asyncio** | (optional) | Async test support | NOT needed - API routes are synchronous def functions |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **monkeypatch** | (from pytest) | Mock data loaders | Replace `load_all_data()` and `get_data()` with test fixtures |
| **tmp_path / tmp_output_dir** | (from pytest) | Temporary directories | CLI tests that write output files |
| **MonkeyPatch** | (from pytest) | Environment variable mocking | Override ADMIN_PASSWORD, API_DATA_DIR for tests |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| TestClient | httpx.AsyncClient | Not needed - routes are synchronous def, not async def. TestClient is simpler and sufficient |
| monkeypatch | unittest.mock | monkeypatch is more pytest-idiomatic, cleaner syntax for simple replacements |
| CliRunner | subprocess | CliRunner is cleaner, faster, no process overhead |

**Installation:**
```bash
# Already installed in dev dependencies
pip install pytest>=8.0 pytest-cov>=7.0 pytest-xdist>=3.0
```

## Architecture Patterns

### Test Structure
```
tests/
├── test_api_endpoints.py       # Extend with comprehensive endpoint tests
├── test_api_services.py         # NEW: Service layer unit tests
├── test_cli_chief.py            # Already exists, extend coverage
├── test_cli_patrol.py           # Already exists, extend coverage
├── test_cli_policy.py           # Already exists, extend coverage
├── test_cli_forecasting.py      # Already exists, extend coverage
├── conftest.py                  # Shared fixtures (already exists)
```

### Pattern 1: FastAPI Endpoint Testing with TestClient
**What:** Use TestClient to make HTTP requests to endpoints and validate responses
**When to use:** All 11 API routes (all are synchronous def functions)
**Example:**
```python
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_trends_annual_with_category_filter():
    """Test /api/v1/trends/annual?category=Violence."""
    response = client.get("/api/v1/trends/annual?category=Violence")

    # Validate response contract
    assert response.status_code == 200
    data = response.json()

    # Verify filtering works
    assert isinstance(data, list)
    for row in data:
        assert row.get("crime_category") == "Violence"
```

### Pattern 2: Mock Data Loaders for Service Tests
**What:** Replace `get_data()` with fixture data using monkeypatch
**When to use:** Testing `api/services/data_loader.py` functions
**Example:**
```python
from api.services.data_loader import get_data, load_all_data

def test_get_data_with_missing_key(monkeypatch):
    """Test get_data() raises KeyError for missing key."""
    # Patch cache to have no data
    monkeypatch.setattr("api.services.data_loader._DATA_CACHE", {})

    with pytest.raises(KeyError, match="Data key not loaded"):
        get_data("nonexistent.json")
```

### Pattern 3: CLI Testing with CliRunner
**What:** Use CliRunner to invoke commands and validate output/exit codes
**When to use:** All 8 CLI commands (chief, patrol, policy, forecasting)
**Example:**
```python
from typer.testing import CliRunner
from analysis.cli.main import app

runner = CliRunner()

def test_cli_chief_trends_output_format(tmp_output_dir, monkeypatch):
    """Test 'chief trends' creates correct output files."""
    result = runner.invoke(
        app,
        ["chief", "trends", "--fast", "--output-format", "svg", "--version", "test"],
        env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
    )

    assert result.exit_code == 0
    assert "Annual Trends" in result.stdout

    # Verify output file
    figure_path = tmp_output_dir / "test/chief/annual_trends_report_trend.svg"
    assert figure_path.exists()
```

### Anti-Patterns to Avoid
- **Using httpx.AsyncClient unnecessarily:** Only needed for async def routes. All routes are synchronous def, TestClient is sufficient
- **Testing CLI with subprocess:** Slower, harder to capture output. Use CliRunner instead
- **Not mocking data loaders:** Loading full dataset makes tests slow. Use fixtures and monkeypatch
- **Asserting on internal state:** Test behavior (outputs, files, exit codes) not implementation

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CLI invocation | subprocess.Popen | typer.testing.CliRunner | Cleaner, faster, built for Typer apps |
| HTTP client | requests or httpx manually | fastapi.testclient.TestClient | Handles ASGI app, context, errors automatically |
| Mock objects | Custom Mock classes | pytest.monkeypatch | Simpler, more pytest-idiomatic |
| Temporary files | Manual mkdir/cleanup | pytest.tmp_path fixture | Auto-cleanup, isolated per test |

**Key insight:** The FastAPI and Typer ecosystems provide purpose-built testing tools. Custom solutions add complexity and miss edge cases (e.g., ASGI context, exception handling).

## Common Pitfalls

### Pitfall 1: Using httpx.AsyncClient for Synchronous Routes
**What goes wrong:** Adds unnecessary complexity when TestClient handles both sync and async routes
**Why it happens:** Documentation emphasizes AsyncClient for async tests, but doesn't clarify when it's needed
**How to avoid:**
- Check route function signature: if `def endpoint()` (not `async def`), use TestClient
- Only use AsyncClient if you need to call other async functions in the test
**Warning signs:** Importing httpx.AsyncClient but not using any async operations in test

### Pitfall 2: Not Mocking Data Loaders
**What goes wrong:** Tests load full 3.4M-row dataset, making them slow (minutes instead of seconds)
**Why it happens:** Tests call endpoints that trigger `load_all_data()` via lifespan
**How to avoid:**
- Use `monkeypatch` to replace `load_all_data` with a no-op or cache-populating function
- Pre-populate `_DATA_CACHE` with fixture data in test setup
**Warning signs:** Tests take longer than 5 seconds, Phase 11 tests already solved this

### Pitfall 3: Testing Implementation Instead of Behavior
**What goes wrong:** Tests assert on internal state (e.g., cache contents) rather than outputs (responses, files)
**Why it happens:** Easier to access internals than validate behavior
**How to avoid:**
- Test API responses: status codes, JSON structure, data correctness
- Test CLI: exit codes, stdout content, output files
- Avoid importing private modules (e.g., `_DATA_CACHE`)
**Warning signs:** Tests import internal modules, assert on `__` attributes

### Pitfall 4: Not Isolating CLI Output Directories
**What goes wrong:** Multiple tests write to `reports/`, causing file conflicts and pollution
**Why it happens:** Tests don't override output directory, use default
**How to avoid:**
- Always use `tmp_output_dir` fixture and pass via `--version` or env var
- Check for `CRIME_OUTPUT_DIR` env var in CLI commands
**Warning signs:** Tests create files in project directories, tests fail when run in parallel

### Pitfall 5: Ignoring Error Handling Paths
**What goes wrong:** Only happy path tested, errors crash production
**Why it happens:** Error cases are harder to trigger (missing data, invalid input)
**How to avoid:**
- Test 400/422/500 responses for API
- Test CLI with invalid arguments, missing files
- Mock failures (e.g., missing data keys)
**Warning signs:** 100% coverage but no error handling tests

## Code Examples

Verified patterns from official sources:

### API Test: Request/Response Contract
```python
# Source: https://fastapi.tiangolo.com/tutorial/testing/
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_spatial_geojson_structure():
    """Test /api/v1/spatial/districts returns valid GeoJSON."""
    response = client.get("/api/v1/spatial/districts")

    assert response.status_code == 200
    geojson = response.json()

    # Validate GeoJSON structure
    assert "type" in geojson
    assert geojson["type"] == "FeatureCollection"
    assert "features" in geojson
    assert isinstance(geojson["features"], list)
```

### API Test: Error Handling
```python
# Source: https://fastapi.tiangolo.com/tutorial/testing/
def test_api_validation_error():
    """Test API returns 422 for invalid query parameters."""
    response = client.get("/api/v1/trends/annual?category=InvalidCategory")

    # FastAPI auto-validates, returns 422 for enum/validation errors
    assert response.status_code == 422
    payload = response.json()
    assert "detail" in payload
```

### CLI Test: Argument Parsing
```python
# Source: https://typer.tiangolo.com/tutorial/testing/
from typer.testing import CliRunner
from analysis.cli.main import app

runner = CliRunner()

def test_cli_version_command():
    """Test 'version' command outputs version info."""
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "CLI Version" in result.stdout
    assert "typer" in result.stdout
```

### Service Test: Mock Data Loader
```python
# Source: https://docs.pytest.org/en/stable/how-to/monkeypatch.html
from api.services.data_loader import get_data

def test_get_data_returns_cached_value(monkeypatch):
    """Test get_data() returns value from cache."""
    # Pre-populate cache
    test_data = {"key": "value"}
    monkeypatch.setattr(
        "api.services.data_loader._DATA_CACHE",
        {"test.json": test_data}
    )

    result = get_data("test.json")
    assert result == test_data
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| subprocess for CLI | typer.testing.CliRunner | Typer 0.4+ (2021) | Faster tests, cleaner output capture |
| Manual HTTP requests | fastapi.testclient.TestClient | FastAPI 0.60+ (2019) | ASGI-aware, automatic error handling |
| unittest.mock | pytest.monkeypatch | pytest 2.0+ (2015) | More Pythonic, better cleanup |

**Deprecated/outdated:**
- **subprocess.Popen for CLI testing:** Replaced by CliRunner. subprocess has overhead, harder to assert on output
- **requests for API testing:** Replaced by TestClient. requests doesn't handle ASGI apps
- **pytest.mark.asyncio for FastAPI:** Only needed for async def routes. All routes are synchronous def

## Current Test Inventory

### API Endpoints (11 routes to test)
**Already tested (3):**
- ✅ `/api/health` - `test_health()`
- ✅ `/api/v1/trends/annual` - `test_trends_annual()`
- ✅ `/api/v1/metadata` - `test_metadata()`
- ✅ `/api/v1/questions` (POST) - `test_questions_pending_requires_admin_auth()`

**Need tests (7 endpoints):**
- ❌ `/api/v1/trends/monthly` - Query params: start_year, end_year
- ❌ `/api/v1/trends/covid` - COVID comparison data
- ❌ `/api/v1/trends/seasonality` - Seasonality dict
- ❌ `/api/v1/trends/robbery-heatmap` - Robbery heatmap data
- ❌ `/api/v1/spatial/*` - 4 GeoJSON endpoints (districts, tracts, hotspots, corridors)
- ❌ `/api/v1/policy/*` - 4 policy endpoints (retail-theft, vehicle-crimes, composition, events)
- ❌ `/api/v1/forecasting/*` - 2 forecasting endpoints (time-series, classification)

### CLI Commands (8 commands + 2 main)
**Already tested (12 tests across 4 files):**
- ✅ `chief trends` - 4 tests (basic, output files, format, date range)
- ✅ `chief seasonality` - 2 tests (basic, output files)
- ✅ `chief covid` - 2 tests (basic, output files)
- ✅ `patrol hotspots` - 2 tests (basic, output files)
- ✅ `patrol robbery-heatmap` - 2 tests (basic, output files)
- ✅ `patrol district-severity` - 2 tests (basic, output files)
- ✅ `patrol census-rates` - 2 tests (basic, output files)
- ✅ `policy retail-theft` - 2 tests (basic, output files)
- ✅ `policy vehicle-crimes` - 2 tests (basic, output files)
- ✅ `policy composition` - 2 tests (basic, output files)
- ✅ `policy events` - 2 tests (basic, output files)
- ✅ `forecasting time-series` - 2 tests (basic, graceful degradation)
- ✅ `forecasting classification` - 2 tests (basic, output files)

**Need tests (2 commands):**
- ❌ `version` - Main app command
- ❌ `info` - Main app command

### Service Layer (api/services/)
**No tests yet:**
- ❌ `data_loader.py` - `load_all_data()`, `get_data()`, `contract_status()`, `cache_keys()`
- ❌ Edge cases: missing keys, missing files, invalid data directory

## Open Questions

1. **Question:** Should API tests load real data or mock it completely?
   - **What we know:** Phase 11 tests use fixtures and mocking. Current `test_api_endpoints.py` calls `load_all_data()` in `setup_module()`.
   - **What's unclear:** Whether to load minimal test data or mock all responses.
   - **Recommendation:** Mock at service layer (replace `get_data()`), not at HTTP layer. Pre-populate cache with minimal test data.

2. **Question:** Should CLI tests validate output file content or just existence?
   - **What we know:** Existing tests check for file existence and some content keywords.
   - **What's unclear:** How deeply to validate generated figures and reports.
   - **Recommendation:** Check file existence + basic content (headers, key phrases). Don't validate figure pixel-perfectness.

3. **Question:** How to handle admin authentication in tests?
   - **What we know:** Existing tests monkeypatch env vars (`ADMIN_PASSWORD`, `ADMIN_TOKEN_SECRET`).
   - **What's unclear:** Whether to test token generation logic.
   - **Recommendation:** Test happy path with mocked env vars. Don't test JWT/crypto internals (library's responsibility).

## Sources

### Primary (HIGH confidence)
- [FastAPI Official Docs - Async Tests](https://fastapi.tiangolo.com/advanced/async-tests/) - Verified TestClient vs AsyncClient usage
- [Typer Official Docs - Testing](https://typer.tiangolo.com/tutorial/testing/) - CliRunner patterns and examples
- [Pytest Official Docs - Good Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html) - Temporary directories, monkeypatching
- Project codebase:
  - `/Users/dustinober/Projects/Crime Incidents Philadelphia/tests/test_api_endpoints.py` - Existing TestClient patterns
  - `/Users/dustinober/Projects/Crime Incidents Philadelphia/tests/test_cli_*.py` - Existing CliRunner patterns
  - `/Users/dustinober/Projects/Crime Incidents Philadelphia/tests/conftest.py` - Shared fixtures

### Secondary (MEDIUM confidence)
- [ pytest-mock Tutorial: A Beginner's Guide to Mocking](https://www.datacamp.com/tutorial/pytest-mock) - Published Dec 2024, covers mocking basics
- [Mastering Pytest: Advanced Fixtures, Parameterization and Mocking](https://medium.com/@abhayda/mastering-pytest-advanced-fixtures-parameterization-and-mocking-explained-108a7a2ab82d) - Fixture patterns for external dependencies
- [FastAPI Best Practices](https://auth0.com/blog/fastapi-best-practices/) - Published Jan 2026, async understanding
- [Hypermodern Python 2: Testing](https://medium.com/@cjolowicz/hypermodern-python-2-testing-ae907a920260) - Pytest best practices

### Tertiary (LOW confidence)
- [What Is FastAPI Testing? Tools, Frameworks, and Best Practices](https://www.frugaltesting.com/blog/what-is-fastapi-testing-tools-frameworks-and-best-practices) - Published June 2025, mentions async testing but not verified
- Various StackOverflow posts on FastAPI/Typer testing - Community knowledge, not official sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official documentation confirms TestClient and CliRunner are standard tools
- Architecture: HIGH - Existing codebase demonstrates working patterns, official docs validate
- Pitfalls: MEDIUM - Some based on official docs, some inferred from common testing mistakes

**Research date:** 2026-02-07
**Valid until:** 2026-05-07 (3 months - testing tooling evolves slowly)

**Key observations:**
1. Project uses Python 3.13, pytest 8.0+ - all tooling is current
2. All API routes are synchronous `def` functions - TestClient is correct choice, no AsyncClient needed
3. Existing tests use `--fast` flag for CLI commands - pattern established for quick execution
4. Phase 11 achieved 81.75% coverage for core modules - testing infrastructure is mature
5. No async routes, no database - simpler than typical FastAPI apps, focus on request/response contracts
