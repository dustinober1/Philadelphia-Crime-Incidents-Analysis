# Testing Patterns

**Analysis Date:** 2026-02-02

## Test Framework

Runner
- Recommended: `pytest` (present in `requirements.txt`). There is no test harness or `tests/` directory currently in the repository.
- No `pytest.ini`, `tox.ini`, or `pyproject.toml` with test configuration detected.

Assertion & Coverage
- `pytest` and `pytest-cov` are listed in `requirements.txt` (lines show `pytest` and `pytest-cov==7.0.0`). Use `pytest` with `--cov` for coverage reporting.

Run Commands
```bash
pytest                 # run all tests (when tests/ exists)
pytest -q              # quiet
pytest --maxfail=1     # fail fast
pytest --cov=analysis  # coverage for analysis modules
```

## Test File Organization

Location
- Add unit tests under `tests/` at the project root. For modules under `analysis/`, mirror the package path: e.g. tests for `analysis/utils.py` should be `tests/analysis/test_utils.py`.
- Notebooks are not directly unit-tested; instead, extract logic into `analysis/` modules and test those modules. The README and `AGENTS.md` instruct to keep heavy processing out of notebooks.

Naming
- Test files use `test_*.py` prefix (Pytest default). Example: `tests/analysis/test_temporal_analysis.py`.

Structure
- Each test module should follow pattern:

  - setup fixtures at module or function scope using `pytest.fixture`
  - small, fast unit tests for pure functions
  - integration tests for IO-bound steps that interact with `data/` should be marked with `@pytest.mark.integration` and run separately

Example test file: `tests/analysis/test_utils.py`

```python
import pytest
from analysis.utils import load_data

def test_load_data_sample(tmp_path):
    data_file = tmp_path / "sample.parquet"
    # create a minimal parquet-compatible file or mock read
    # assert load_data returns expected DataFrame schema

```

## Mocking

Framework
- Use `unittest.mock` (stdlib) for mocking I/O, external services, and time.
- `pytest-mock` is not present in `requirements.txt`; prefer `unittest.mock` for portability unless `pytest-mock` is added.

Patterns
- Mock file/data reads for unit tests of ingesters: patch `pandas.read_parquet`, `pandas.read_csv`, or helper functions in `analysis.utils`.
- For external HTTP calls (if added), mock `requests` or `httpx` calls with `responses` or `requests-mock` (not currently in `requirements.txt`).

What to Mock
- IO: file reads/writes under `data/` for unit tests. Use `tmp_path` fixtures to create sample files.
- Time: use `freezegun` if deterministic dates needed (not present in deps). Alternatively, inject clock or pass date arguments.

What Not to Mock
- Do not mock pure computational functions; test them directly with representative inputs.

## Fixtures & Factories

Test data fixtures
- Place reusable test fixtures in `tests/conftest.py` (e.g., `sample_crime_df`, `tmp_data_dir`).
- Example `conftest.py` fixtures: provide a sample DataFrame with expected columns (`incident_datetime`, `offense_code`, `lat`, `lon`).

Factories
- For repeated row-level objects, create small factories in `tests/fixtures.py` or use `hypothesis` for property-based tests (not currently in requirements).

## Coverage

Requirements
- No enforced coverage threshold found. Add `--cov-fail-under=80` to CI if coverage enforcement is desired.

View coverage
```bash
pytest --cov=analysis --cov-report=term-missing
```

## Test Types

Unit Tests
- Scope: pure functions in `analysis/` (data cleaning, aggregations, date parsing). Fast and deterministic.

Integration Tests
- Scope: end-to-end small workflows that read small sample files from `data/processed/` or `data/external/` and run script-level functions (e.g., `analysis/06_generate_report.py` main flow).
- Mark with `@pytest.mark.integration`.

Notebook Tests / Validation
- Notebooks should be validated by executing them headless in CI using `jupyter nbconvert --execute` in a fast/sampled mode. The `AGENTS.md` describes a recommended CI approach. Export executed notebooks to `reports/` for review.

## Common Patterns

Async code
- No async code in analysis modules was detected. If adding async (e.g., data fetch with `httpx`), use `pytest.mark.asyncio` or `anyio` for tests.

Error testing

Example pattern to assert exceptions
```python
import pytest
from analysis.utils import parse_date

def test_parse_date_raises():
    with pytest.raises(ValueError):
        parse_date('not-a-date')
```

## Recommended Starter Test Files (to add now)

- `tests/conftest.py` — fixtures: `sample_crime_df`, `tmp_data_dir`
- `tests/analysis/test_utils.py` — unit tests for data loading and cleaning helpers
- `tests/integration/test_report_generation.py` — integration test for `analysis/06_generate_report.py` that runs with a small sample dataset

Files referenced in this section (examples):
- `requirements.txt` (contains `pytest`, `pytest-cov`)
- `README.md` (testing guidance)
- `AGENTS.md` (notebook testing / CI guidance)

---

*Testing analysis: 2026-02-02*
