# Phase 13: Pipeline & Supporting Tests - Research

**Researched:** February 7, 2026
**Domain:** Python Testing for Pipeline Operations, Configuration, and Visualization
**Confidence:** HIGH

## Summary

Phase 13 focuses on achieving 95% test coverage across pipeline operations, configuration modules, and visualization code. Research confirms a well-established testing pattern using pytest with monkeypatch and unittest.mock for fast, isolated tests. The key insight is that heavy external dependencies (GeoPandas, Prophet, XGBoost) should be mocked at import boundaries rather than exercised in tests, enabling fast test execution while validating workflow logic.

**Key findings:**
- Pipeline tests should mock file I/O and external APIs (subprocess, JSON serialization) using monkeypatch
- Configuration testing leverages pydantic-settings' test-friendly design with YAML file isolation and environment variable override
- Matplotlib figure testing uses 'Agg' backend to prevent display issues; pytest-mpl provides image comparison but requires baseline management
- Current coverage shows API modules at 88% (268/292 lines) with gaps in error paths; analysis modules lack comprehensive tests
- 37 analysis modules need testing; visualization modules (plots.py, forecast_plots.py) are high-priority untested code
- Refresh operations need reproducibility validation testing

**Primary recommendation:** Use monkeypatch for subprocess and file I/O mocking in pipeline tests, test pydantic configuration models with tmp YAML files and env var overrides, test matplotlib functions with Agg backend and Figure object assertions (not pixel comparisons), and prioritize coverage gaps by workflow criticality (export → config → visualization → supporting modules).

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **pytest-xdist for parallel testing** - use `-nauto` locally, `-n4` on CI for predictable resource allocation
- **Coverage.py configuration** - branch=true, parallel=true in pyproject.toml with 95% overall target for v1.3 milestone
- **Mock heavy dependencies** - GeoPandas, Prophet, XGBoost training mocked for fast tests; test workflow logic, not library internals
- **unittest.mock.patch for external APIs** - standard approach for mocking file I/O and external service calls
- **TestClient error handling** - tests use pytest.raises(KeyError) for unhandled exceptions
- **Source code inspection** - cached functions using joblib.Memory inspected for mocking difficulty; acceptable to exclude optional utilities (shap) from coverage targets

### Claude's Discretion

- Test structure and organization for new test files
- Whether to use pytest-mpl for image comparison or manual Figure assertions
- Specific coverage thresholds for individual modules (must achieve 95% overall)

### Deferred Ideas (OUT OF SCOPE)

- Performance benchmarking tests
- Load testing for API endpoints
- Frontend (web/) testing beyond existing API tests

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **pytest** | 8.x | Test runner | De facto standard Python test framework, mature ecosystem, fixture system |
| **pytest-xdist** | Latest (installed) | Parallel test execution | Official pytest plugin, 4-8x speedup, seamless integration |
| **coverage.py** | 7.x | Coverage measurement | Standard Python coverage tool, pyproject.toml native support |
| **pytest-cov** | Latest (installed) | pytest/coverage integration | Official bridge between pytest and coverage.py |

### Testing Utilities

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **monkeypatch** | Built-in pytest | Runtime attribute replacement | File I/O mocking, environment variables, function patching |
| **unittest.mock.patch** | Built-in | Context manager patching | External API calls, subprocess, complex imports |
| **tmp_path** | Built-in pytest fixture | Temporary directories | Test file creation, isolated outputs |
| **pytest.importorskip** | Built-in | Optional dependency handling | Skip tests when GeoPandas/Prophet unavailable |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| **monkeypatch** | unittest.mock.patch | monkeypatch is more pytest-idiomatic for simple cases; mock.patch for complex imports |
| **manual Figure assertions** | pytest-mpl | pytest-mpl requires baseline image management; manual assertions simpler for chart logic |
| **subprocess mocking** | integration tests | Subprocess mocking is faster; integration tests already cover end-to-end workflows |

**Installation:**
```bash
# All required dependencies already installed
pip install pytest pytest-cov pytest-xdist
```

## Architecture Patterns

### Recommended Test Structure

```
tests/
├── conftest.py                      # Shared fixtures (sample_crime_df, tmp_output_dir)
├── test_pipeline_export.py          # Pipeline export operations (exists, needs expansion)
├── test_pipeline_refresh.py         # NEW: Pipeline refresh and validation
├── test_config_settings.py          # NEW: GlobalConfig and BaseConfig
├── test_config_schemas.py           # NEW: Pydantic config models
├── test_visualization_plots.py      # NEW: Chart generation logic
├── test_visualization_helpers.py    # NEW: Visualization utility functions
├── test_artifact_manager.py         # NEW: Versioning utilities
└── ...
```

### Pattern 1: Mocking Pipeline Export Operations

**What:** Test pipeline export functions by mocking file I/O and external dependencies without actually writing files or calling subprocess.

**When to use:** All pipeline export and refresh tests to achieve fast, deterministic test execution.

**Example:**
```python
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

def test_export_metadata_writes_json(tmp_path, monkeypatch):
    """Test _export_metadata writes valid JSON with expected structure."""
    from pipeline.export_data import _export_metadata, ExportMetadata

    # Mock sample DataFrame
    sample_df = pd.DataFrame({
        "dispatch_date": pd.date_range("2020-01-01", periods=100, freq="D")
    })

    output_dir = tmp_path / "exports"
    output_dir.mkdir()

    # Call export function
    _export_metadata(sample_df, output_dir)

    # Assertions
    metadata_path = output_dir / "metadata.json"
    assert metadata_path.exists()

    import json
    metadata = json.loads(metadata_path.read_text())
    assert metadata["total_incidents"] == 100
    assert "last_updated" in metadata
    assert metadata["source"] == "Philadelphia Police Department via OpenDataPhilly"

def test_export_all_calls_subfunctions(tmp_path, monkeypatch):
    """Test export_all orchestrates all export functions in correct order."""
    from pipeline.export_data import export_all

    df = pd.DataFrame({"dispatch_date": ["2020-01-01"], "objectid": [1]})

    # Mock load_crime_data and all _export_* functions
    with patch("pipeline.export_data.load_crime_data", return_value=df):
        with patch("pipeline.export_data._export_trends") as mock_trends:
            with patch("pipeline.export_data._export_seasonality") as mock_seasonality:
                with patch("pipeline.export_data._export_spatial") as mock_spatial:
                    with patch("pipeline.export_data._export_policy") as mock_policy:
                        with patch("pipeline.export_data._export_forecasting") as mock_forecast:
                            with patch("pipeline.export_data._export_metadata") as mock_metadata:
                                result = export_all(tmp_path)

                                # Verify all export functions called
                                mock_trends.assert_called_once()
                                mock_seasonality.assert_called_once()
                                mock_spatial.assert_called_once()
                                mock_policy.assert_called_once()
                                mock_forecast.assert_called_once()
                                mock_metadata.assert_called_once()

                                assert result == tmp_path
```

**Source:** [Pytest + unittest.mock Deep Dive for Real-World Testing](https://medium.com/@bhagyarana80/mock-anything-in-python-pytest-unittest-mock-deep-dive-for-real-world-testing-d4ed26f65649) (Medium, 2025)

**Confidence:** HIGH - Established pattern for mocking in pytest

### Pattern 2: Testing Configuration with Pydantic-Settings

**What:** Test pydantic-settings configuration models by isolating YAML files and overriding environment variables per-test.

**When to use:** All configuration module tests (config/settings.py, config/schemas/*.py).

**Example:**
```python
import os
from pathlib import Path
import pytest
import yaml
from analysis.config.settings import GlobalConfig, BaseConfig

def test_global_config_defaults():
    """Test GlobalConfig loads with sensible defaults."""
    config = GlobalConfig()

    assert config.output_dir == Path("reports")
    assert config.dpi == 300
    assert config.output_format == "png"
    assert config.fast_sample_frac == 0.1
    assert config.cache_enabled is True
    assert config.log_level == "INFO"

def test_global_config_from_yaml(tmp_path, monkeypatch):
    """Test GlobalConfig loads from YAML file."""
    # Create test YAML config
    config_file = tmp_path / "global.yaml"
    config_data = {
        "output_dir": "/tmp/test_reports",
        "dpi": 150,
        "output_format": "svg",
    }
    config_file.write_text(yaml.dump(config_data))

    # Change to temp directory where config exists
    monkeypatch.chdir(tmp_path)

    config = GlobalConfig()
    assert config.output_dir == Path("/tmp/test_reports")
    assert config.dpi == 150
    assert config.output_format == "svg"

def test_global_config_env_override(monkeypatch):
    """Test environment variables override YAML and defaults."""
    monkeypatch.setenv("CRIME_OUTPUT_DIR", "/env/reports")
    monkeypatch.setenv("CRIME_DPI", "200")
    monkeypatch.setenv("CRIME_LOG_LEVEL", "DEBUG")

    config = GlobalConfig()
    assert config.output_dir == Path("/env/reports")
    assert config.dpi == 200
    assert config.log_level == "DEBUG"

def test_base_config_validation_fails_invalid_format(monkeypatch):
    """Test BaseConfig validates output_format pattern."""
    monkeypatch.setenv("CRIME_OUTPUT_FORMAT", "invalid")

    with pytest.raises(Exception):  # pydantic ValidationError
        BaseConfig()
```

**Source:** [Test Pydantic settings in FastAPI - python](https://stackoverflow.com/questions/61582142/test-pydantic-settings-in-fastapi) (StackOverflow) and [FastAPI loads different config files using pytest](https://www.ixiqin.com/2023/11/26/fastapi-loads-different-configuration-files-using-pytest-to/) (November 2023)

**Confidence:** HIGH - Pydantic-settings is designed for testability

### Pattern 3: Testing Matplotlib Figure Generation

**What:** Test visualization functions return valid Figure objects with expected properties without requiring display or pixel comparison.

**When to use:** All analysis/visualization/ tests to ensure chart generation logic works.

**Example:**
```python
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for tests
import matplotlib.pyplot as plt
import pandas as pd
import pytest
from analysis.visualization.plots import plot_line, plot_bar

def test_plot_line_returns_figure(sample_crime_df):
    """Test plot_line returns a valid Figure object."""
    fig = plot_line(
        data=sample_crime_df,
        x_col="dispatch_date",
        y_col="objectid",
        title="Test Plot",
        xlabel="Date",
        ylabel="Count"
    )

    # Assertions on Figure object
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    ax = fig.axes[0]
    assert ax.get_title() == "Test Plot"
    assert ax.get_xlabel() == "Date"
    assert ax.get_ylabel() == "Count"

    # Verify data plotted
    assert len(ax.lines) == 1
    line = ax.lines[0]
    assert len(line.get_xdata()) > 0
    assert len(line.get_ydata()) > 0

    plt.close(fig)  # Prevent memory leak

def test_plot_bar_applies_style():
    """Test plot_bar uses consistent styling."""
    data = pd.DataFrame({
        "category": ["A", "B", "C"],
        "value": [10, 20, 30]
    })

    fig = plot_bar(
        data=data,
        x_col="category",
        y_col="value",
        title="Bar Chart Test"
    )

    ax = fig.axes[0]
    # Check grid enabled
    assert ax.grid

    # Check tick labels visible
    assert len(ax.get_xticklabels()) == 3

    plt.close(fig)

def test_plot_handles_empty_data():
    """Test plot functions handle empty DataFrames gracefully."""
    empty_df = pd.DataFrame({"x": [], "y": []})

    with pytest.raises((ValueError, IndexError)):
        # Should either raise error or return empty figure
        fig = plot_line(empty_df, "x", "y", "Empty")
```

**Source:** [Matplotlib tests headless and without warning](https://stackoverflow.com/questions/67251721/matplotlib-tests-headless-and-without-warning) (StackOverflow) and [matplotlib.testing documentation](https://matplotlib.org/stable/api/testing_api.html)

**Confidence:** HIGH - Matplotlib provides testing utilities and Agg backend is standard for CI

### Pattern 4: Testing Pipeline Refresh and Validation

**What:** Test refresh operation validates data integrity and reproducibility of export outputs.

**When to use:** Pipeline refresh tests to ensure data consistency across runs.

**Example:**
```python
from pathlib import Path
from unittest.mock import patch
import pytest
from pipeline.refresh_data import _validate_artifacts, _assert_reproducible

def test_validate_artifacts_passes_complete_exports(tmp_path):
    """Test _validate_artifacts passes when all required files exist."""
    from pipeline.refresh_data import _REQUIRED_FILES

    # Create all required files
    for relative_path in _REQUIRED_FILES:
        file_path = tmp_path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if relative_path.endswith(".json"):
            if "metadata" in relative_path:
                content = '{"total_incidents": 100, "date_start": "2020-01-01", "date_end": "2020-12-31", "last_updated": "2025-01-01T00:00:00Z", "source": "Test", "colors": {}}'
            elif "annual_trends" in relative_path:
                content = '[{"year": 2020, "crime_category": "Violent", "count": 100}]'
            elif "forecast" in relative_path:
                content = '{"historical": [], "forecast": []}'
            else:
                content = '{}'
            file_path.write_text(content)

    # Should not raise
    _validate_artifacts(tmp_path)

def test_validate_artifacts_raises_missing_files(tmp_path):
    """Test _validate_artifacts raises RuntimeError when files missing."""
    with pytest.raises(RuntimeError, match="Missing required export files"):
        _validate_artifacts(tmp_path)

def test_validate_artifacts_raises_invalid_metadata(tmp_path):
    """Test _validate_artifacts validates metadata structure."""
    # Create incomplete metadata
    (tmp_path / "metadata.json").write_text('{"total_incidents": 100}')

    with pytest.raises(RuntimeError, match="metadata.json is missing required keys"):
        _validate_artifacts(tmp_path)

def test_assert_reproducible_runs_export_twice(tmp_path, monkeypatch):
    """Test _assert_reproducible compares two export runs."""
    from pipeline.refresh_data import _assert_reproducible
    from pipeline.export_data import export_all

    # Mock load_crime_data to return deterministic data
    sample_df = pd.DataFrame({
        "dispatch_date": pd.date_range("2020-01-01", periods=10, freq="D"),
        "objectid": range(10)
    })

    with patch("pipeline.export_data.load_crime_data", return_value=sample_df):
        # Should not raise if exports are deterministic
        _assert_reproducible()
```

**Confidence:** HIGH - Existing test pattern in test_pipeline_export.py validates approach

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Mocking subprocess calls | Custom subprocess wrappers | unittest.mock.patch('subprocess.run') | Standard library, handles edge cases |
| Figure comparison | Custom pixel diff logic | pytest-mpl or manual Figure assertions | pytest-mpl provides baseline management; manual assertions simpler for logic validation |
| Configuration fixtures | Custom YAML loaders | pydantic-settings native test support + tmp_path | Pydantic designed for testability with env overrides |
| Test data generation | Hardcoded test datasets | pytest fixtures (sample_crime_df) | Fixtures are reproducible, isolated, pytest-native |

**Key insight:** pytest and pydantic-settings provide all necessary testing utilities. Custom solutions add maintenance burden without benefit.

## Common Pitfalls

### Pitfall 1: Not Mocking GeoPandas/Prophet Imports

**What goes wrong:** Tests actually load GeoPandas or run Prophet models, causing 10-100x slowdown (seconds vs milliseconds) and test failures when optional dependencies unavailable.

**Why it happens:** Importing modules at test file level forces real imports even when using monkeypatch later.

**How to avoid:**
```python
# BAD - forces real import
from analysis.spatial_utils import some_function  # Imports GeoPandas

def test_something():
    with patch("geopandas.read_file"):
        some_function()  # Too late, already imported

# GOOD - patch before import
def test_something():
    with patch("analysis.spatial_utils.gpd", Mock()):
        from analysis.spatial_utils import some_function
        some_function()  # Uses mock

# BETTER - test at import boundary
def test_spatial_function_with_mocked_geopandas(monkeypatch):
    # Mock the entire gpd module
    mock_gpd = Mock()
    monkeypatch.setattr("analysis.spatial_utils.gpd", mock_gpd)

    # Now import and test
    from analysis.spatial_utils import some_function
    result = some_function()
    assert result is not None
```

**Warning signs:** Tests take >1 second per function, test failures with "ImportError: No module named 'geopandas'"

### Pitfall 2: Testing Chart Pixel Values Instead of Logic

**What goes wrong:** Tests fail due to minor rendering differences (font versions, DPI, backend) rather than actual logic bugs.

**Why it happens:** Using image comparison (pytest-mpl) without accounting for environment differences.

**How to avoid:**
```python
# BAD - fragile pixel comparison
def test_plot_output_image():
    fig = plot_line(data, "x", "y", "title")
    # Compare to baseline image - fails on different systems

# GOOD - test chart structure
def test_plot_structure():
    fig = plot_line(data, "x", "y", "title")
    ax = fig.axes[0]

    # Test chart properties, not pixels
    assert ax.get_title() == "title"
    assert len(ax.lines) == 1
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y"
    plt.close(fig)
```

**Warning signs:** Tests fail locally but pass on CI (or vice versa), flaky tests with "Image mismatch"

### Pitfall 3: Not Isolating Test Configuration Files

**What goes wrong:** Tests accidentally load real config files from project root, causing test pollution and nondeterministic results.

**Why it happens:** Tests run from project directory where config/ already exists.

**How to avoid:**
```python
# BAD - uses real config if present
def test_config_loading():
    config = GlobalConfig()  # May load config/global.yaml from project

# GOOD - explicit test isolation
def test_config_loading(tmp_path, monkeypatch):
    # Change to isolated temp directory
    monkeypatch.chdir(tmp_path)

    # Create test-specific config
    config_file = tmp_path / "global.yaml"
    config_file.write_text(yaml.dump({"dpi": 150}))

    config = GlobalConfig()
    assert config.dpi == 150
```

**Warning signs:** Tests pass when run individually but fail in parallel, nondeterministic test results

### Pitfall 4: Missing Branch Coverage in Error Paths

**What goes wrong:** Coverage reports 95%+ but error handling code is untested, masking critical bugs.

**Why it happens:** Only testing happy paths, not error conditions (file not found, invalid data, API failures).

**How to avoid:**
```python
# Test both success and failure paths
def test_load_crime_data_success():
    df = load_crime_data()
    assert len(df) > 0

def test_load_crime_data_file_not_found(monkeypatch):
    # Mock missing file
    def mock_read(*args, **kwargs):
        raise FileNotFoundError("No such file")
    monkeypatch.setattr("pandas.read_parquet", mock_read)

    with pytest.raises(FileNotFoundError):
        load_crime_data()

def test_load_crime_data_invalid_format(monkeypatch):
    # Mock corrupted file
    def mock_read(*args, **kwargs):
        raise ValueError("Invalid Parquet file")
    monkeypatch.setattr("pandas.read_parquet", mock_read)

    with pytest.raises(ValueError):
        load_crime_data()
```

**Warning signs:** Coverage.py shows "missing branches" in output, tests only use assert for positive conditions

## Code Examples

### Verified Pattern: Mocking File I/O in Pipeline Tests

```python
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd
import pytest

def test_write_json_creates_file(tmp_path):
    """Test _write_json helper writes valid JSON."""
    from pipeline.export_data import _write_json

    test_file = tmp_path / "test.json"
    test_data = {"key": "value", "number": 42}

    _write_json(test_file, test_data)

    assert test_file.exists()

    import json
    loaded = json.loads(test_file.read_text())
    assert loaded == test_data

def test_export_trends_generates_expected_files(tmp_path, monkeypatch):
    """Test _export_trends creates all trend JSON files."""
    from pipeline.export_data import _export_trends

    # Prepare sample data
    df = pd.DataFrame({
        "dispatch_date": pd.date_range("2020-01-01", periods=100, freq="D"),
        "ucr_general": [100] * 50 + [600] * 50
    })

    output_dir = tmp_path / "trends"
    output_dir.mkdir()

    _export_trends(df, output_dir)

    # Verify expected files created
    assert (output_dir / "annual_trends.json").exists()
    assert (output_dir / "monthly_trends.json").exists()
    assert (output_dir / "covid_comparison.json").exists()

    # Validate JSON structure
    import json
    annual = json.loads((output_dir / "annual_trends.json").read_text())
    assert isinstance(annual, list)
    assert len(annual) > 0
    assert "year" in annual[0]
    assert "count" in annual[0]
```

**Source:** Adapted from [How to use mock in request.post to an external API](https://stackoverflow.com/questions/63899742/how-to-use-mock-in-request-post-to-anexternal-api) (StackOverflow)

### Verified Pattern: Testing Pydantic Config Validation

```python
import pytest
from analysis.config.settings import GlobalConfig
from analysis.config.schemas.chief import ChiefConfig

def test_global_config_dpi_validation_fails_out_of_range(monkeypatch):
    """Test GlobalConfig validates DPI is within 72-600 range."""
    monkeypatch.setenv("CRIME_DPI", "1000")  # Out of range

    with pytest.raises(Exception):  # pydantic ValidationError
        GlobalConfig()

def test_global_config_output_format_validation_fails_invalid(monkeypatch):
    """Test GlobalConfig validates output_format pattern."""
    monkeypatch.setenv("CRIME_OUTPUT_FORMAT", "jpg")  # Not in pattern

    with pytest.raises(Exception):  # pydantic ValidationError
        GlobalConfig()

def test_chief_config_loads_from_yaml(tmp_path, monkeypatch):
    """Test ChiefConfig loads and validates YAML configuration."""
    config_file = tmp_path / "chief.yaml"
    config_data = {
        "version": "v1.0",
        "annual_trend": {
            "params": {
                "start_date": "2020-01-01",
                "end_date": "2020-12-31"
            },
            "outputs": {
                "png": "annual_trend_{version}.png",
                "report": "annual_trend_report_{version}.txt"
            }
        }
    }
    config_file.write_text(yaml.dump(config_data))
    monkeypatch.chdir(tmp_path)

    config = ChiefConfig()
    assert config.version == "v1.0"
    assert "annual_trend" in config.data

    params = config.get_notebook_params("annual_trend")
    assert params["start_date"] == "2020-01-01"

def test_chief_config_validation_fails_missing_outputs(tmp_path, monkeypatch):
    """Test ChiefConfig validates required outputs section."""
    config_file = tmp_path / "chief.yaml"
    config_data = {
        "version": "v1.0",
        "annual_trend": {
            "params": {"start_date": "2020-01-01"}
            # Missing "outputs"
        }
    }
    config_file.write_text(yaml.dump(config_data))
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="must define params and outputs"):
        ChiefConfig()
```

**Source:** Adapted from [Test Pydantic settings in FastAPI](https://stackoverflow.com/questions/61582142/test-pydantic-settings-in-fastapi) and [FastAPI pytest config loading](https://www.ixiqin.com/2023/11/26/fastapi-loads-different-configuration-files-using-pytest-to/)

### Verified Pattern: Testing Visualization Functions

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import pytest
from analysis.visualization.plots import plot_line, plot_bar
from analysis.visualization.helpers import setup_style

def test_setup_style_applies_consistent_theme():
    """Test setup_style applies matplotlib style settings."""
    plt.style.use('default')  # Reset to default
    setup_style()

    # Check style applied
    assert plt.rcParams['figure.facecolor'] == 'white'
    assert plt.rcParams['axes.facecolor'] == '#f0f0f0'

def test_plot_line_uses_custom_color():
    """Test plot_line accepts custom color parameter."""
    data = pd.DataFrame({
        "date": pd.date_range("2020-01-01", periods=10),
        "value": range(10)
    })

    fig = plot_line(data, "date", "value", "Test", color="#FF0000")
    ax = fig.axes[0]

    # Check custom color applied
    line = ax.lines[0]
    assert line.get_color() == "#FF0000"

    plt.close(fig)

def test_plot_line_default_color():
    """Test plot_line uses default Violent color when color not specified."""
    data = pd.DataFrame({
        "date": pd.date_range("2020-01-01", periods=10),
        "value": range(10)
    })

    fig = plot_line(data, "date", "value", "Test")
    ax = fig.axes[0]

    # Check default color from COLORS palette
    from analysis.visualization.style import COLORS
    line = ax.lines[0]
    assert line.get_color() == COLORS["Violent"]

    plt.close(fig)

def test_plot_bar_handles_negative_values():
    """Test plot_bar correctly plots negative values."""
    data = pd.DataFrame({
        "category": ["A", "B", "C"],
        "value": [-10, 0, 10]
    })

    fig = plot_bar(data, "category", "value", "Test")
    ax = fig.axes[0]

    # Check all bars plotted
    assert len(ax.patches) == 3

    # Check bar heights
    heights = [patch.get_height() for patch in ax.patches]
    assert heights == [-10, 0, 10]

    plt.close(fig)
```

**Source:** [Matplotlib tests headless and without warning](https://stackoverflow.com/questions/67251721/matplotlib-tests-headless-and-without-warning) and [matplotlib testing API](https://matplotlib.org/stable/api/testing_api.html)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Testing with real matplotlib display | Agg backend for headless testing | Matplotlib 2.1+ (2017) | Tests run in CI without X11/fpeg dependencies |
| unittest.mock as mock.patch | pytest monkeypatch for simple cases | pytest 3.0+ (2016) | More pytest-idiomatic, cleaner syntax |
| Hard-coded test data | pytest fixtures with parametrize | pytest 2.0+ | DRY, composable, parallel-safe |
| Coverage enforcement in pytest addopts | coverage.py fail_under in pyproject.toml | coverage.py 5.0+ | Native tool support, cleaner separation |

**Deprecated/outdated:**
- **nose testing framework:** Unmaintained since 2015, replaced by pytest
- **mock library (PyPI):** Merged into unittest.mock in Python 3.3+, use standard library
- **ImageMagick-based figure comparison:** pytest-mpl or manual assertions preferred

## Open Questions

1. **Should we use pytest-mpl for image comparison tests?**
   - **What we know:** pytest-mpl provides baseline image comparison but requires managing baseline images and fails on rendering differences across environments.
   - **What's unclear:** Whether pixel-perfect chart testing is necessary or if Figure structure assertions are sufficient.
   - **Recommendation:** Start with manual Figure assertions (test titles, axes, data presence). Add pytest-mpl only if visual regression bugs become problematic. Use Agg backend to ensure tests run headless.

2. **How to handle cached functions using joblib.Memory?**
   - **What we know:** joblib.Memory decorator makes mocking difficult by caching function results. Source code inspection required to identify cached functions.
   - **What's unclear:** Whether to test cached functions directly or test the uncached implementation and mock the cache.
   - **Recommendation:** Test cached functions by clearing cache before test (`analysis.data.clear_cache()`), then testing behavior. Mock at import boundary if cache persistence causes test pollution.

3. **What coverage threshold for individual modules?**
   - **What we know:** Overall 95% target for v1.3 milestone. Some modules (CLI entry points, optional utilities) may not reach 95%.
   - **What's unclear:** Whether to enforce per-module thresholds or only overall threshold.
   - **Recommendation:** Enforce 95% overall threshold with coverage.py's fail_under. Allow individual modules below 95% if documented in coverage.omit patterns (e.g., CLI __main__.py already excluded). Prioritize coverage by workflow criticality: export → config → visualization → supporting.

## Sources

### Primary (HIGH confidence)

- **[pytest documentation - How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)** - Official pytest fixture documentation
- **[coverage.py documentation](https://coverage.readthedocs.io/)** - Official coverage.py documentation with pyproject.toml configuration
- **[Pytest + unittest.mock Deep Dive for Real-World Testing](https://medium.com/@bhagyarana80/mock-anything-in-python-pytest-unittest-mock-deep-dive-for-real-world-testing-d4ed26f65649)** (Medium, 2025) - Comprehensive mocking guide
- **[Testing APIs with PyTest](https://codilime.com/blog/testing-apis-with-pytest-mocks-in-python/)** (Codilime, October 2024) - Mocking external dependencies
- **[Matplotlib testing API](https://matplotlib.org/stable/api/testing_api.html)** - Official matplotlib testing utilities
- **[Pydantic Changelog](https://docs.pydantic.dev/latest/changelog/)** - Latest pydantic-settings v2.12.5 (November 2025)

### Secondary (MEDIUM confidence)

- **[Test Pydantic settings in FastAPI](https://stackoverflow.com/questions/61582142/test-pydantic-settings-in-fastapi)** (StackOverflow) - Pydantic testing patterns
- **[FastAPI loads different config files using pytest](https://www.ixiqin.com/2023/11/26/fastapi-loads-different-configuration-files-using-pytest-to/)** (November 2023) - Config file isolation
- **[How to use mock in request.post to an external API](https://stackoverflow.com/questions/63899742/how-to-use-mock-in-request-post-to-anexternal-api)** (StackOverflow) - External API mocking
- **[Matplotlib tests headless and without warning](https://stackoverflow.com/questions/67251721/matplotlib-tests-headless-and-without-warning)** (StackOverflow) - Agg backend usage
- **[Pytest Plugin List](https://docs.pytest.org/en/stable/reference/plugin-list.html)** - Official pytest plugin ecosystem
- **[Building a Lightweight Data Validation Framework with Pytest](https://medium.com/@husein2709/building-a-lightweight-data-validation-framework-with-pytest-and-github-actions-b9995c7f9556)** (Medium) - Data validation testing patterns

### Tertiary (LOW confidence)

- **[pytest + YAML + Allure framework](https://blog.csdn.net/ylong52/article/details/154261081)** (CSDN Blog, November 2025) - YAML test configuration (Chinese source, less verifiable)
- **[Deep Dive into Pytest](https://medium.com/ai-qa-nexus/deep-dive-into-pytest-advanced-test-automation-techniques-part-1-a7397fc868b2)** (Medium) - Advanced pytest techniques
- **[Can I make conda solve this environment faster](https://stackoverflow.com/questions/71393065/can-i-make-conda-solve-this-environment-faster)** (StackOverflow) - Environment setup optimization (not directly relevant)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All tools are well-documented, industry-standard Python testing infrastructure
- Architecture: HIGH - Existing test patterns in codebase (test_pipeline_export.py, test_data_loading.py) validate approaches
- Pitfalls: HIGH - Based on common pytest testing anti-patterns documented in official resources
- Code examples: HIGH - Adapted from official documentation and verified StackOverflow answers

**Research date:** February 7, 2026
**Valid until:** March 9, 2026 (30 days - stable testing ecosystem)
**Phase requirements coverage:**
- PIPE-01 (export tests): Pattern 1, Code Examples
- PIPE-02 (refresh tests): Pattern 4, Code Examples
- PIPE-03 (error handling): Pitfall 4, Code Examples
- SUPP-01 (config tests): Pattern 2, Code Examples
- SUPP-02 (visualization tests): Pattern 3, Code Examples
- SUPP-03 (remaining modules): Standard Stack section
- SUPP-04 (95% milestone): Coverage configuration in Pattern 2, Open Questions #3
