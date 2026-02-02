# Testing Patterns

**Analysis Date:** 2026-02-02

This document summarizes the current testing-related state in the repository and prescribes patterns to use when adding tests. All file paths are included where relevant.

## Test framework and runner

- Framework: The repository includes `pytest` and `pytest-cov` in `requirements.txt` (path: `requirements.txt`, lines referencing `pytest` and `pytest-cov`). The README (path: `README.md`) recommends adding `pytest` and a `tests/` folder when you want CI.
- No `pytest.ini`/`tox.ini`/`pyproject.toml` is present that configures test discovery. Not detected: `pytest.ini`, `tox.ini`, `pyproject.toml`.

Prescriptive guidance (setup):
- Add a `pytest.ini` at project root with basic configuration:

  - `pytest.ini` example contents (recommended path: `pytest.ini`):

    [pytest]
    minversion = 7.0
    addopts = --strict-markers -q
    testpaths = tests

- Use `pytest` and `pytest-cov` for running tests and coverage reporting. Commands:

```bash
pytest                # run all tests
pytest -q             # quiet output
pytest --maxfail=1    # fail fast
pytest --cov=analysis --cov-report=term-missing  # coverage for analysis modules
```

## Test file organization and naming

Observed: There is no `tests/` directory currently. The README (path: `README.md`) suggests creating `tests/` for unit tests.

Prescriptive organization (strict):
- Create a top-level `tests/` directory.
- Use `test_*.py` filenames for test modules and `test_<name>` for functions.
- Co-locate tests with modules when appropriate (for modules inside `analysis/`, place tests in `tests/analysis/test_<module>.py`).

Example structure to add:

```
[project-root]/
├── analysis/                 # reusable code
├── notebooks/                # notebooks (not executed during unit tests)
├── tests/
│   ├── analysis/
│   │   └── test_utils.py
│   └── test_integration_reports.py
```

## Test structure and patterns

Recommended test layout for analysis modules (example):

```python
# tests/analysis/test_utils.py
import pandas as pd
from analysis.utils import load_data

def test_load_data_valid(tmp_path):
    path = tmp_path / "data.parquet"
    # create small sample parquet
    df_in = pd.DataFrame({"a": [1, 2]})
    df_in.to_parquet(path)

    df = load_data(str(path))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2

def test_load_data_missing_file():
    import pytest
    from analysis.utils import load_data

    with pytest.raises(FileNotFoundError):
        load_data("nonexistent.parquet")
```

Patterns to follow:
- Use `tmp_path` or `tmpdir` fixtures to create temporary files for IO tests.
- Keep unit tests small and focused; prefer pure-Python tests for fast execution.
- Use parametrized tests (`@pytest.mark.parametrize`) for input matrix coverage.

## Fixtures and test utilities

Recommendation: Add a `tests/conftest.py` for shared fixtures.

Common fixtures to include (path: `tests/conftest.py`):
- `sample_df` — small pandas DataFrame used by multiple tests.
- `tmp_path` — built-in pytest fixture for temporary files.

Example `conftest.py`:

```python
import pytest
import pandas as pd

@pytest.fixture
def sample_df():
    return pd.DataFrame({"lat": [39.95], "lon": [-75.16], "offense": ["burglary"]})
```

## Mocking and isolation

Observed: There are no existing tests or mocking patterns to inspect.

Recommendations and patterns:
- Use `monkeypatch` (pytest fixture) for temporary environment or function patching. Example: `monkeypatch.setenv("API_KEY", "fake")`.
- For external service calls (S3, web APIs), replace network calls with recorded fixtures or use `responses` or `requests-mock` packages.
- Prefer dependency injection where possible: write functions that accept a `session` or file-like object to make them easy to test without network.

Mocking example (monkeypatching `requests.get`):

```python
def test_fetch_remote(monkeypatch):
    import requests

    class DummyResp:
        status_code = 200
        text = 'ok'

    monkeypatch.setattr(requests, 'get', lambda *a, **k: DummyResp())
    from analysis.external import fetch_url

    assert fetch_url('http://example') == 'ok'
```

## Integration and E2E tests

Observed: The repository contains notebooks that orchestrate large processing and report generation (`analysis/06_generate_report.py` referenced in `README.md`). Integration tests should validate these orchestration scripts in a fast mode.

Recommendations:
- Provide a `--fast` or `--sample` flag to scripts like `analysis/06_generate_report.py` to allow CI to run a smoke integration test using sample data (place sample data under `data/sample/`).
- Create an `tests/integration/test_generate_report.py` that runs the script in sample mode and asserts output files are created in a temporary `reports/` directory.

Example integration test snippet:

```python
def test_generate_report_sample(tmp_path, monkeypatch):
    out = tmp_path / 'reports'
    monkeypatch.setenv('REPORTS_DIR', str(out))
    # call CLI entrypoint or module function with sample mode
    from analysis import generate_report

    generate_report(sample=True, outdir=str(out))
    assert (out / 'summary.md').exists()
```

## Coverage

Observed: `pytest-cov` is present in `requirements.txt` (path: `requirements.txt`). There is no configured minimum coverage in CI config (CI not detected in repo).

Recommendation:
- Use `pytest --cov=analysis --cov-report=term-missing` locally and set up a CI job to require a coverage threshold (e.g., 80%).
- Add a `coverage.ini` or configure `pytest-cov` in `pytest.ini`.

## Running tests (commands)

Suggested commands to document in `README.md` or `CONTRIBUTING.md`:

```bash
# run tests
pytest

# run tests with coverage
pytest --cov=analysis --cov-report=term-missing

# run a single test file
pytest tests/analysis/test_utils.py -q
```

## Notebooks and testing

Observed: Notebooks are required to be runnable headless in CI (`AGENTS.md`). There are no existing automated notebook tests.

Recommendations:
- Use `nbconvert` to execute notebooks in CI in a cleared/execution mode: `jupyter nbconvert --execute --to notebook --inplace notebooks/<notebook>.ipynb`.
- For faster CI runs, create sample-mode notebooks or run a stripped-down version that imports analysis modules and runs small smoke checks.

## Linting and static checks (test-adjacent)

Observed linters/formatters: `black`, `isort`, `ruff`, `flake8`, `mypy` present in `requirements.txt` and `environment.yml`.

Recommendation:
- Add a CI job that runs `black --check`, `isort --check-only`, `ruff check`, and `mypy` for non-notebook code before running tests.

## Gaps & Next steps

- No `tests/` directory or test files exist; add a baseline set of unit tests for `analysis/` helper functions.
- Add `pytest.ini` and `tests/conftest.py` to standardize fixtures and test discovery.
- Add sample datasets under `data/sample/` for integration and notebook CI runs.

---

*Testing analysis: 2026-02-02*
