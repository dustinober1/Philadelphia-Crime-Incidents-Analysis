# Testing Patterns

**Analysis Date:** 2026-02-07

## Test Framework

**Runner:**
- pytest 8.x configured in `pyproject.toml`.
- FastAPI tests use `fastapi.testclient.TestClient` (`tests/test_api_endpoints.py`).
- CLI tests use Typer `CliRunner` (`tests/test_cli_*.py`).

**Assertion Library:**
- Built-in pytest `assert` statements.
- No separate matcher framework detected.

**Run Commands:**
```bash
pytest tests/                                        # Run all Python tests
pytest tests/ --cov=analysis --cov-report=term-missing
pytest tests/ -m integration                         # Run integration-marked tests
python -m pytest -q                                  # Quiet mode (documented in README)
cd web && npm run lint && npm run typecheck && npm run build
```

## Test File Organization

**Location:**
- Main tests in `tests/`.
- Integration tests in `tests/integration/`.

**Naming:**
- File names follow `test_*.py`.
- Test classes often use `Test*` naming with grouped scenarios.
- Functions use `test_*` naming.

**Structure:**
```
tests/
  conftest.py
  test_cli_chief.py
  test_cli_patrol.py
  test_cli_policy.py
  test_cli_forecasting.py
  test_api_endpoints.py
  test_pipeline_export.py
  integration/
    test_migration_verification.py
```

## Test Structure

**Suite Organization:**
```python
class TestPolicyRetailTheft:
    def test_policy_retail_theft_basic(self, tmp_output_dir):
        result = runner.invoke(app, ["policy", "retail-theft", "--fast", "--version", "test"])
        assert result.exit_code == 0
```

**Patterns:**
- Heavy use of end-to-end CLI invocation with `CliRunner`.
- Output validation checks expected files and keyword patterns rather than exact numeric fixtures.
- Integration tests emphasize artifact existence/shape and compatibility with legacy notebook outputs.

## Mocking

**Framework:**
- pytest built-in fixtures + `monkeypatch` for environment variables.

**Patterns:**
```python
monkeypatch.setenv("ADMIN_PASSWORD", "test-password")
response = client.get("/api/v1/questions?status=pending")
assert response.status_code == 401
```

**What to Mock:**
- Environment variables for auth/security behavior.
- Optional dependency presence via `pytest.importorskip`.

**What NOT to Mock:**
- Most CLI workflows run with real command execution against sample/full datasets.
- API endpoint tests frequently use real app wiring with in-memory fallbacks.

## Fixtures and Factories

**Test Data:**
- `sample_crime_df` fixture provides deterministic synthetic 100-row crime dataset (`tests/conftest.py`).
- `tmp_output_dir` fixture provides isolated filesystem target for generated outputs.

**Location:**
- Shared fixtures are centralized in `tests/conftest.py`.
- Scenario-specific data setup remains inside each test module.

## Coverage

**Requirements:**
- No explicit minimum percentage gate is enforced in repo config.
- Coverage is reported and used for visibility (`pytest-cov`, `README.md` examples).

**Configuration:**
- pytest options and markers are configured in `pyproject.toml`.
- Markers include `slow` and `integration`.

**View Coverage:**
```bash
pytest tests/ --cov=analysis --cov-report=term-missing
```

## Test Types

**Unit Tests:**
- Data transforms, validation, and utility behavior (`tests/test_data_*.py`, `tests/test_temporal.py`).

**Integration Tests:**
- End-to-end CLI output shape and migration parity checks (`tests/test_integration_output_verification.py`, `tests/integration/test_migration_verification.py`).

**API Tests:**
- FastAPI smoke and auth-path tests (`tests/test_api_endpoints.py`).

**Frontend Tests:**
- No dedicated frontend unit/e2e test suite detected in `web/`.

## Common Patterns

**Async/Optional Dependency Handling:**
- Tests use `pytest.importorskip` for optional ML/geospatial stacks.
- Many CLI tests run with `--fast` and custom `--version` values to isolate artifacts.

**Error Testing:**
```python
response = client.get("/api/v1/questions?status=invalid")
assert response.status_code == 422
assert response.json()["error"] == "http_error"
```

**Snapshot Testing:**
- Not detected.

---

*Testing analysis: 2026-02-07*
*Update when test patterns change*
