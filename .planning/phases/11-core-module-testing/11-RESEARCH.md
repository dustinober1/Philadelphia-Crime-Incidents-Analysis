# Phase 11: Core Module Testing - Research

**Researched:** February 7, 2026
**Domain:** Python ML/Data Testing with pytest
**Confidence:** HIGH

## Summary

Phase 11 focuses on writing comprehensive unit tests for core analysis modules (models/, data/, utils/). Research confirms established patterns for testing ML/statistical code, pandas data operations, and coordinate validation using pytest. The existing test suite provides excellent fixtures and patterns to extend. Key challenges include testing time-aware ML models without slow training, mocking external file I/O for data loading, and handling spatial joins with GeoPandas.

**Key findings:**
- **ML model testing**: Test preprocessing pipelines and evaluation metrics, not model training outcomes. Use mock estimators with predictable behavior.
- **Data validation testing**: Parametrize edge cases (boundary values, NaN handling, type coercion). Pydantic validators require testing both valid and invalid inputs.
- **Pandas testing**: Use `pd.testing.assert_frame_equal` for DataFrame comparisons, `np.testing.assert_array_equal` for numpy arrays.
- **Spatial testing**: Mock GeoPandas spatial joins with predetermined point-in-polygon results. Test coordinate filtering, not geometric operations.
- **Time series testing**: Use small, deterministic time series for Prophet model testing. Test metric calculations with synthetic data.
- **Version compatibility**: Python 3.13.9 installed vs. 3.14 required in pyproject.toml - must use 3.13 compatible code patterns.
- **Existing fixtures**: `sample_crime_df` (100 rows), `tmp_output_dir` provide foundation for fast unit tests.

**Primary recommendation:** Structure tests by module with clear separation of concerns: (1) input validation edge cases, (2) deterministic transformations, (3) metric calculations with synthetic data, (4) mocked external dependencies. Avoid testing ML model accuracy - test data flow, preprocessing, and evaluation logic. Use parametrization for comprehensive edge case coverage.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **pytest** | 8.0+ | Test runner | Already configured, de facto standard, fixture system |
| **pandas.testing** | Built into pandas 2.0+ | DataFrame assertions | Official pandas testing utilities, handles NaN equality |
| **numpy.testing** | Built into numpy | Array assertions | Standard numpy testing, handles floating point comparison |
| **unittest.mock** | Built into Python 3.13 | Mocking external deps | Standard library mock, no dependencies |
| **pytest-mock** | Latest (install) | Cleaner mock syntax | Convenience wrapper around unittest.mock, optional |

### Testing ML/Statistical Code

| Library | Purpose | When to Use |
|---------|---------|-------------|
| **sklearn.utils.estimator_checks** | Validate estimator interfaces | For custom sklearn-compatible estimators (not used here) |
| **pytest approx** | Floating point comparison | For metric calculations with tolerance (MAE, RMSE, etc.) |
| **frozen data** | Pre-trained model outputs | Test model integration without retraining |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| **unittest.mock** | pytest-mock | Same functionality, pytest-mock has cleaner syntax via `mocker` fixture |
| **pandas.testing** | assert df.equals | pandas.testing provides detailed error messages on mismatch |
| **Synthetic test data** | Real data subsets | Real data requires I/O and versioning, synthetic is deterministic and fast |

**Installation:**
```bash
# Already installed (from pyproject.toml dev dependencies)
# pytest, pytest-cov, pytest-xdist

# Optional: for cleaner mock syntax
pip install pytest-mock
```

## Architecture Patterns

### Recommended Test Structure

```
tests/
├── conftest.py                    # Shared fixtures (ALREADY EXISTS)
├── test_classification.py         # utils/classification.py (EXISTS, 30 tests)
├── test_temporal.py               # utils/temporal.py (EXISTS, 30 tests)
├── test_data_validation.py        # data/validation.py (EXISTS, 44 tests)
├── test_data_loading.py           # data/loading.py (EXISTS, 31 tests)
├── test_data_preprocessing.py     # data/preprocessing.py (EXISTS, 36 tests)
├── test_models_classification.py  # models/classification.py (NEW)
├── test_models_time_series.py     # models/time_series.py (NEW)
├── test_models_validation.py      # models/validation.py (NEW)
└── test_utils_spatial.py          # utils/spatial.py (NEW)
```

### Pattern 1: Testing ML Model Workflows Without Training

**What:** Test data preprocessing, feature extraction, and metric calculations using mock models or frozen model outputs.

**When to use:** For all ML model testing. Never test model accuracy (random seed issues, slow execution).

**Example:**
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from analysis.models.classification import train_random_forest, extract_feature_importance

def test_train_random_forest_returns_model_and_scaler():
    """Train Random Forest returns fitted model and scaler."""
    np.random.seed(42)
    X_train = pd.DataFrame({
        "feature1": np.random.randn(100),
        "feature2": np.random.randn(100),
    })
    y_train = pd.Series(np.random.randint(0, 2, 100))

    model, scaler = train_random_forest(X_train, y_train, scale_features=True)

    # Test: model is fitted
    assert hasattr(model, "feature_importances_")
    # Test: scaler is fitted
    assert scaler is not None
    assert scaler.n_features_in_ == 2

def test_train_random_forest_without_scaling():
    """Train Random Forest without scaling returns None scaler."""
    X_train = pd.DataFrame({"feature1": [1, 2, 3]})
    y_train = pd.Series([0, 1, 0])

    model, scaler = train_random_forest(X_train, y_train, scale_features=False)

    assert scaler is None
    assert model is not None

def test_extract_feature_importance_returns_sorted_dataframe():
    """Extract feature importance returns DataFrame sorted by importance."""
    from sklearn.ensemble import RandomForestClassifier

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    X = pd.DataFrame({"f1": [1, 2], "f2": [3, 4], "f3": [5, 6]})
    y = pd.Series([0, 1])
    model.fit(X, y)

    importance_df = extract_feature_importance(model, ["f1", "f2", "f3"])

    # Test: returns DataFrame
    assert isinstance(importance_df, pd.DataFrame)
    # Test: has correct columns
    assert list(importance_df.columns) == ["feature", "importance"]
    # Test: sorted descending
    assert importance_df["importance"].is_monotonic_decreasing

def test_extract_feature_importance_top_n():
    """Extract feature importance with top_n parameter."""
    from sklearn.ensemble import RandomForestClassifier

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    X = pd.DataFrame({"f1": [1, 2], "f2": [3, 4], "f3": [5, 6]})
    y = pd.Series([0, 1])
    model.fit(X, y)

    importance_df = extract_feature_importance(model, ["f1", "f2", "f3"], top_n=2)

    assert len(importance_df) == 2
```

**Source:** Pattern from existing test_classification.py and test_data_validation.py

**Key insight:** Test model workflow (inputs → outputs), not model accuracy. Mock models provide deterministic outputs for fast tests.

### Pattern 2: Testing Pandas Transformations with Edge Cases

**What:** Test data transformation functions with comprehensive edge cases using parametrization.

**When to use:** For all data preprocessing, feature extraction, and filtering functions.

**Example:**
```python
import pandas as pd
import pytest
from analysis.models.time_series import prepare_prophet_data, create_train_test_split

class TestPrepareProphetData:
    """Tests for prepare_prophet_data function."""

    def test_returns_prophet_format_columns(self):
        """Returns DataFrame with 'ds' and 'y' columns."""
        df = pd.DataFrame({
            "date": ["2020-01-01", "2020-01-02"],
            "count": [10, 20]
        })

        result = prepare_prophet_data(df, "date", "count")

        assert list(result.columns) == ["ds", "y"]
        assert result["ds"].dtype.name == "datetime64[ns]"

    def test_sorts_by_date(self):
        """Sorts DataFrame by date column."""
        df = pd.DataFrame({
            "date": ["2020-01-03", "2020-01-01", "2020-01-02"],
            "count": [30, 10, 20]
        })

        result = prepare_prophet_data(df, "date", "count")

        assert result["ds"].is_monotonic_increasing

    @pytest.mark.parametrize(
        "date_str,expected_year,expected_month",
        [
            ("2020-01-15", 2020, 1),
            ("2023-12-31", 2023, 12),
            ("2024-02-29", 2024, 2),  # Leap year
        ]
    )
    def test_various_dates(self, date_str, expected_year, expected_month):
        """Parametrized test for various date formats."""
        df = pd.DataFrame({"date": [date_str], "count": [10]})
        result = prepare_prophet_data(df, "date", "count")

        assert result["ds"].iloc[0].year == expected_year
        assert result["ds"].iloc[0].month == expected_month

    def test_empty_dataframe(self):
        """Handles empty DataFrame."""
        df = pd.DataFrame({"date": [], "count": []})
        result = prepare_prophet_data(df, "date", "count")

        assert len(result) == 0
        assert list(result.columns) == ["ds", "y"]

class TestCreateTrainTestSplit:
    """Tests for create_train_test_split function."""

    def test_requires_ds_column(self):
        """Raises ValueError if 'ds' column missing."""
        df = pd.DataFrame({"date": ["2020-01-01"], "count": [10]})

        with pytest.raises(ValueError, match="must have 'ds' column"):
            create_train_test_split(df, test_days=30)

    def test_splits_by_date_cutoff(self):
        """Splits data based on date cutoff."""
        df = pd.DataFrame({
            "ds": pd.date_range("2020-01-01", periods=100),
            "y": range(100)
        })

        train, test = create_train_test_split(df, test_days=30)

        # Test: no overlap
        assert train["ds"].max() < test["ds"].min()
        # Test: test has 30 days
        assert len(test) == 30
        # Test: train has remaining
        assert len(train) == 70

    def test_custom_test_days(self):
        """Respects custom test_days parameter."""
        df = pd.DataFrame({
            "ds": pd.date_range("2020-01-01", periods=100),
            "y": range(100)
        })

        train, test = create_train_test_split(df, test_days=10)

        assert len(test) == 10
        assert len(train) == 90
```

**Source:** Pattern from existing test_temporal.py and test_data_preprocessing.py

**Key insight:** Parametrize edge cases (empty DataFrames, leap years, boundary values) for comprehensive coverage without repetitive tests.

### Pattern 3: Testing Evaluation Metrics with Synthetic Data

**What:** Test metric calculations (MAE, RMSE, MAPE, R²) with known synthetic inputs.

**When to use:** For all metric calculation functions in models/validation.py and models/time_series.py.

**Example:**
```python
import pandas as pd
import numpy as np
import pytest
from analysis.models.time_series import evaluate_forecast
from analysis.models.validation import compute_regression_metrics

class TestEvaluateForecast:
    """Tests for evaluate_forecast function."""

    def test_perfect_forecast_metrics(self):
        """Perfect forecast (predicted == actual) returns ideal metrics."""
        actual = pd.Series([100.0, 200.0, 300.0])
        predicted = pd.Series([100.0, 200.0, 300.0])

        metrics = evaluate_forecast(actual, predicted)

        # Test: MAE is 0 for perfect prediction
        assert metrics["mae"] == pytest.approx(0.0)
        # Test: RMSE is 0 for perfect prediction
        assert metrics["rmse"] == pytest.approx(0.0)
        # Test: R² is 1.0 for perfect prediction
        assert metrics["r2"] == pytest.approx(1.0)
        # Test: MAPE is 0% for perfect prediction
        assert metrics["mape"] == pytest.approx(0.0)

    def test_constant_forecast_bias(self):
        """Constant forecast bias is captured in bias metric."""
        actual = pd.Series([100.0, 200.0, 300.0])
        predicted = pd.Series([110.0, 210.0, 310.0])  # Always +10

        metrics = evaluate_forecast(actual, predicted)

        # Test: positive bias (over-prediction)
        assert metrics["bias"] == pytest.approx(10.0)

    def test_nan_handling_in_metrics(self):
        """Handles NaN values in actual or predicted."""
        actual = pd.Series([100.0, np.nan, 300.0])
        predicted = pd.Series([110.0, 210.0, 310.0])

        metrics = evaluate_forecast(actual, predicted)

        # Test: filters NaN pairs
        # Metrics computed on (100, 110) and (300, 310) only
        assert "mae" in metrics
        assert not np.isnan(metrics["mae"])

    def test_prediction_interval_coverage(self):
        """Computes coverage when prediction intervals provided."""
        actual = pd.Series([100.0, 200.0, 300.0])
        predicted = pd.Series([150.0, 200.0, 250.0])
        lower = pd.Series([90.0, 190.0, 240.0])
        upper = pd.Series([110.0, 210.0, 260.0])

        metrics = evaluate_forecast(actual, predicted, lower, upper)

        # Test: coverage metric exists
        assert "coverage" in metrics
        # Test: coverage is between 0 and 1
        assert 0.0 <= metrics["coverage"] <= 1.0

class TestComputeRegressionMetrics:
    """Tests for compute_regression_metrics function."""

    def test_metric_names_with_prefix(self):
        """Prefix is added to all metric names."""
        y_true = pd.Series([1, 2, 3])
        y_pred = pd.Series([1.1, 2.1, 3.1])

        metrics = compute_regression_metrics(y_true, y_pred, prefix="test_")

        # Test: all metrics have prefix
        assert all(key.startswith("test_") for key in metrics.keys())
        assert "test_mae" in metrics
        assert "test_rmse" in metrics
        assert "test_r2" in metrics

    def test_empty_prefix_no_prefix(self):
        """Empty prefix adds no prefix to metric names."""
        y_true = pd.Series([1, 2, 3])
        y_pred = pd.Series([1.1, 2.1, 3.1])

        metrics = compute_regression_metrics(y_true, y_pred, prefix="")

        # Test: no prefix
        assert "mae" in metrics
        assert "rmse" in metrics
        assert "_mae" not in metrics  # Not prefixed with underscore

    def test_mape_calculation(self):
        """MAPE is calculated as mean absolute percentage error."""
        y_true = pd.Series([100.0, 200.0, 300.0])
        y_pred = pd.Series([90.0, 210.0, 330.0])  # -10%, +5%, +10%

        metrics = compute_regression_metrics(y_true, y_pred)

        # Test: MAPE is mean of absolute percentage errors
        # |(90-100)/100| = 0.10, |(210-200)/200| = 0.05, |(330-300)/300| = 0.10
        # Mean = (0.10 + 0.05 + 0.10) / 3 * 100 = 8.33%
        assert metrics["mape"] == pytest.approx(8.33, abs=0.01)

    def test_bias_calculation(self):
        """Bias is mean of (predicted - actual)."""
        y_true = pd.Series([100.0, 200.0, 300.0])
        y_pred = pd.Series([110.0, 210.0, 310.0])  # Always +10

        metrics = compute_regression_metrics(y_true, y_pred)

        # Test: bias is positive for over-prediction
        assert metrics["bias"] == pytest.approx(10.0)
```

**Source:** Pattern from existing test_data_validation.py (edge case parametrization)

**Key insight:** Test metric calculations with synthetic data where expected values are computable by hand. Use `pytest.approx` for floating point comparison with tolerance.

### Pattern 4: Mocking External Dependencies

**What:** Mock file I/O, database connections, and external APIs to test logic without dependencies.

**When to use:** For data loading functions, external API calls, file system operations.

**Example:**
```python
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd
import pytest

# Test file not found error
def test_load_crime_data_file_not_found():
    """Raises FileNotFoundError when parquet file doesn't exist."""
    with patch("analysis.data.loading.CRIME_DATA_PATH", Path("/nonexistent/file.parquet")):
        with pytest.raises(FileNotFoundError, match="Crime data not found"):
            from analysis.data.loading import load_crime_data
            load_crime_data()

# Test parquet parsing with mock
def test_load_crime_data_parses_dispatch_date():
    """Parses dispatch_date column from parquet category dtype."""
    mock_df = pd.DataFrame({
        "objectid": [1, 2, 3],
        "dispatch_date": pd.Categorical(["2020-01-01", "2020-01-02", "2020-01-03"]),
        "ucr_general": [100, 200, 300]
    })

    with patch("analysis.data.loading.CRIME_DATA_PATH", Path("/mock/file.parquet")):
        with patch("pandas.read_parquet", return_value=mock_df):
            from analysis.data.loading import load_crime_data
            result = load_crime_data(clean=False)

            # Test: dispatch_date is datetime
            assert pd.api.types.is_datetime64_any_dtype(result["dispatch_date"])
            # Test: dates parsed correctly
            assert result["dispatch_date"].iloc[0].year == 2020

# Test GeoPandas spatial join with mock
def test_spatial_join_districts_mock_geodataframe():
    """Spatial join uses GeoPandas sjoin internally."""
    from analysis.utils.spatial import spatial_join_districts

    # Mock crime data
    crime_df = pd.DataFrame({
        "point_x": [-75.16],
        "point_y": [39.95],
        "incident_id": ["123"]
    })

    # Mock district boundaries
    mock_district_gdf = MagicMock()
    mock_district_gdf.crs = "EPSG:4326"
    mock_district_gdf.columns = ["dist_num", "geometry"]

    # Mock sjoin result
    mock_joined = pd.DataFrame({
        "point_x": [-75.16],
        "point_y": [39.95],
        "incident_id": ["123"],
        "dist_num": [1],
        "index_right": [0]
    })

    with patch("geopandas.sjoin", return_value=mock_joined):
        result = spatial_join_districts(crime_df, mock_district_gdf)

        # Test: district number joined
        assert "joined_dist_num" in result.columns
        assert result["joined_dist_num"].iloc[0] == 1
        # Test: index_right cleaned up
        assert "index_right" not in result.columns

# Test Prophet model training with mock
def test_time_series_cv_score_with_mock_model():
    """Time series CV uses cross_val_score internally."""
    from analysis.models.validation import time_series_cv_score
    from sklearn.ensemble import RandomForestRegressor

    # Mock model (avoid actual training)
    mock_model = MagicMock(spec=RandomForestRegressor())
    mock_model.fit = MagicMock()
    mock_model.predict = MagicMock(return_value=np.array([1, 2, 3]))

    X = pd.DataFrame({"feature": [1, 2, 3, 4, 5]})
    y = pd.Series([1, 2, 3, 4, 5])

    with patch("sklearn.model_selection.cross_val_score", return_value=np.array([0.8, 0.9, 0.85])):
        results = time_series_cv_score(mock_model, X, y, n_splits=3)

        # Test: returns scores dict
        assert "mean" in results
        assert "std" in results
        assert "scores" in results
        # Test: mean computed correctly
        assert results["mean"] == pytest.approx(0.85)
```

**Source:** WebSearch research on pytest-mock and unittest.mock patterns [MEDIUM confidence]

**Key insight:** Mock external dependencies (file I/O, database, API calls) to test error handling and edge cases. Mock model training to test workflow without slow execution.

### Anti-Patterns to Avoid

- **Testing model accuracy:** Don't assert `accuracy > 0.9`. Model performance varies with random seed. Test workflow, not outcomes.
- **Loading real data files:** Don't load real parquet/CSV files in tests. Use mock data or fixtures. Real data requires I/O and versioning.
- **Testing sklearn internals:** Don't test sklearn model.fit() behavior. Trust sklearn, test your wrapper logic.
- **Ignoring floating point tolerance:** Don't use `assert metrics["mae"] == 0.0`. Use `pytest.approx` for float comparisons.
- **Testing GeoPandas internals:** Don't test spatial join algorithm. Test input/output with mocked GeoPandas.
- **Slow Prophet training:** Don't train Prophet models in tests (slow, non-deterministic). Test preprocessing and metric calculations.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| DataFrame comparison | Custom df.equals() | pd.testing.assert_frame_equal | Detailed error messages showing column/diff |
| Array comparison | Custom np.array_equal() | np.testing.assert_array_equal | Handles NaN and floating point tolerance |
| Mock creation | Manual patch objects | pytest-mock mocker fixture | Cleaner syntax, auto-cleanup |
| Parametrization | Separate test functions | @pytest.mark.parametrize | Less boilerplate, better test reporting |
| Fixture scoping | Manual setup/teardown | @pytest.fixture with scope | Automatic cleanup, reusable across tests |
| Float comparison | assert abs(a - b) < 0.01 | pytest.approx(0.01) | Standard tolerance handling, readable |

**Key insight:** Use pandas.testing and numpy.testing utilities for data assertions. They provide detailed error messages and handle NaN/equality semantics correctly.

## Common Pitfalls

### Pitfall 1: Testing Model Training Outcomes

**What goes wrong:** Tests fail randomly due to random seed variations, slow execution from training models, flaky assertions on accuracy metrics.

**Why it happens:** ML models have non-deterministic training (random initialization, stochastic algorithms). Accuracy depends on data split and hyperparameters.

**How to avoid:**
- Test preprocessing pipelines (feature extraction, scaling) with deterministic inputs
- Test evaluation metrics with known synthetic data
- Test model workflow (fit() called without error) without asserting accuracy
- Mock trained models for integration tests

**Warning signs:** Test file takes >5 seconds to run, tests use `random_state` parameter, assertions on accuracy/precision metrics.

### Pitfall 2: Loading Real Data Files in Tests

**What goes wrong:** Tests require data files to exist, slow I/O operations, tests fail when data changes, can't run tests in isolation.

**Why it happens:** Convenience of using real data for "realistic" tests, lack of fixture setup time investment.

**How to avoid:**
- Create small fixtures with synthetic data (10-100 rows)
- Use `sample_crime_df` fixture from conftest.py as template
- Mock file I/O with unittest.mock.patch for error handling tests
- Test data loading logic with in-memory DataFrames

**Warning signs:** Tests use `pd.read_parquet()`, `pd.read_csv()`, test file requires data/ directory to exist.

### Pitfall 3: Not Handling NaN in Pandas Assertions

**What goes wrong:** Tests fail because `NaN != NaN` in Python, pandas comparison semantics misunderstood.

**Why it happens:** Standard equality (`==`) doesn't work for NaN, but pandas treats NaN as equal in some contexts.

**How to avoid:**
- Use `pd.testing.assert_frame_equal` for DataFrame comparisons (handles NaN)
- Use `np.testing.assert_array_equal` for numpy arrays
- Filter NaN in tests: `df.dropna()` or explicit NaN checks with `pd.isna()`

**Warning signs:** Tests use `assert df1 == df2`, failures mention NaN comparison, tests use `fillna(0)` to work around NaN issues.

### Pitfall 4: Ignoring Floating Point Tolerance

**What goes wrong:** Tests fail due to minor floating point differences (0.999999 vs 1.0), brittle assertions.

**Why it happens:** Direct equality (`==`) doesn't account for floating point precision errors.

**How to avoid:**
- Use `pytest.approx` for float comparisons: `assert value == pytest.approx(expected, abs=0.01)`
- Use `np.testing.assert_allclose` for arrays
- Set appropriate tolerance based on metric (e.g., 0.01 for MAE, 0.001 for R²)

**Warning signs:** Assertions like `assert metric == 0.0`, tests randomly fail on CI, assertions use `round(value, 2)`.

### Pitfall 5: Testing GeoPandas Internal Algorithms

**What goes wrong:** Slow tests (geometric operations are expensive), requires real GeoJSON files, brittle to GeoPandas version changes.

**Why it happens:** Desire to test "real" spatial operations end-to-end.

**How to avoid:**
- Mock GeoPandas `sjoin()` function to return predetermined results
- Test coordinate filtering (bounds checking) without spatial joins
- Test spatial join logic (columns renamed, index_right removed) with mock
- Use small GeoJSON fixtures if real spatial operations needed

**Warning signs:** Tests load GeoJSON files, tests take >1 second, tests use `gpd.sjoin()` without mocking.

### Pitfall 6: Parametrization Overuse or Underuse

**What goes wrong:** Overuse: tests unreadable with 20+ parametrize cases. Underuse: repetitive test code for similar edge cases.

**Why it happens:** Balance between test coverage and readability, unclear when to parametrize.

**How to avoid:**
- Parametrize edge cases with similar test logic (boundary values, invalid inputs)
- Separate test classes for different test scenarios (valid inputs vs invalid inputs)
- Use `@pytest.mark.parametrize` for 3-10 similar cases
- Create separate test functions for conceptually different scenarios

**Warning signs:** Test file has 5 functions testing same logic with different values, or single parametrize with 20+ test cases.

## Code Examples

### Example 1: Testing Time Series Cross-Validation

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from analysis.models.validation import time_series_cv_score

def test_time_series_cv_score_returns_statistics():
    """Time series CV returns mean, std, min, max of scores."""
    np.random.seed(42)

    # Create synthetic time series data
    X = pd.DataFrame({"feature": np.arange(100)})
    y = pd.Series(np.arange(100) + np.random.randn(100) * 0.1)

    model = RandomForestRegressor(n_estimators=10, random_state=42)

    results = time_series_cv_score(model, X, y, n_splits=5)

    # Test: returns dict with expected keys
    assert "scores" in results
    assert "mean" in results
    assert "std" in results
    assert "min" in results
    assert "max" in results

    # Test: scores array has correct length
    assert len(results["scores"]) == 5

    # Test: statistics computed correctly
    assert results["mean"] == pytest.approx(results["scores"].mean())
    assert results["min"] == pytest.approx(results["scores"].min())
    assert results["max"] == pytest.approx(results["scores"].max())

def test_time_series_cv_with_custom_scoring():
    """Time series CV supports custom scoring metrics."""
    X = pd.DataFrame({"feature": [1, 2, 3, 4, 5]})
    y = pd.Series([1, 2, 3, 4, 5])

    model = RandomForestRegressor(n_estimators=5, random_state=42)

    # Test with different scoring metrics
    for scoring in ["neg_mean_absolute_error", "neg_mean_squared_error", "r2"]:
        results = time_series_cv_score(model, X, y, n_splits=3, scoring=scoring)

        assert "mean" in results
        assert len(results["scores"]) == 3
```

### Example 2: Testing Prophet Data Preparation

```python
import pandas as pd
import pytest
from analysis.models.time_series import prepare_prophet_data, get_prophet_config

class TestPrepareProphetData:
    """Tests for Prophet data preparation."""

    def test_converts_column_names_to_ds_y(self):
        """Renames date and value columns to 'ds' and 'y'."""
        df = pd.DataFrame({
            "my_date": ["2020-01-01", "2020-01-02"],
            "my_value": [100, 200]
        })

        result = prepare_prophet_data(df, "my_date", "my_value")

        assert list(result.columns) == ["ds", "y"]
        assert result["ds"].iloc[0] == pd.Timestamp("2020-01-01")
        assert result["y"].iloc[0] == 100

    def test_parses_date_column_to_datetime(self):
        """Converts date column to datetime."""
        df = pd.DataFrame({
            "date": ["2020-01-01", "2020-01-02", "2020-01-03"],
            "count": [10, 20, 30]
        })

        result = prepare_prophet_data(df, "date", "count")

        assert pd.api.types.is_datetime64_any_dtype(result["ds"])

    def test_handles_duplicate_dates(self):
        """Preserves duplicate dates (Prophet handles aggregation)."""
        df = pd.DataFrame({
            "date": ["2020-01-01", "2020-01-01", "2020-01-02"],
            "count": [10, 15, 20]
        })

        result = prepare_prophet_data(df, "date", "count")

        # Test: preserves duplicates (doesn't aggregate)
        assert len(result) == 3

    def test_resets_index_after_sorting(self):
        """Resets index after sorting by date."""
        df = pd.DataFrame({
            "date": ["2020-01-03", "2020-01-01", "2020-01-02"],
            "count": [30, 10, 20]
        })

        result = prepare_prophet_data(df, "date", "count")

        # Test: index is 0, 1, 2 (not original order)
        assert list(result.index) == [0, 1, 2]
        # Test: sorted by date
        assert result["ds"].is_monotonic_increasing

class TestGetProphetConfig:
    """Tests for Prophet configuration."""

    def test_default_config(self):
        """Returns default Prophet configuration."""
        config = get_prophet_config()

        assert config["seasonality_mode"] == "multiplicative"
        assert config["yearly_seasonality"] is True
        assert config["weekly_seasonality"] is True
        assert config["daily_seasonality"] is False
        assert config["changepoint_prior_scale"] == 0.05
        assert config["interval_width"] == 0.95

    @pytest.mark.parametrize(
        "seasonality_mode,yearly,weekly,daily",
        [
            ("additive", True, True, False),
            ("multiplicative", False, True, True),
            ("additive", False, False, True),
        ]
    )
    def test_custom_prophet_config(self, seasonality_mode, yearly, weekly, daily):
        """Accepts custom Prophet configuration parameters."""
        config = get_prophet_config(
            seasonality_mode=seasonality_mode,
            yearly=yearly,
            weekly=weekly,
            daily=daily
        )

        assert config["seasonality_mode"] == seasonality_mode
        assert config["yearly_seasonality"] == yearly
        assert config["weekly_seasonality"] == weekly
        assert config["daily_seasonality"] == daily

    def test_custom_changepoint_prior_scale(self):
        """Accepts custom changepoint_prior_scale."""
        config = get_prophet_config(changepoint_prior_scale=0.1)

        assert config["changepoint_prior_scale"] == 0.1

    def test_custom_interval_width(self):
        """Accepts custom interval width."""
        config = get_prophet_config(interval_width=0.8)

        assert config["interval_width"] == 0.8
```

### Example 3: Testing Data Validation with Pydantic

```python
import pandas as pd
import pytest
from pydantic import ValidationError
from analysis.data.validation import (
    CrimeIncidentValidator,
    validate_crime_data,
    validate_coordinates,
)

class TestValidateCrimeDataSampling:
    """Tests for validate_crime_data sampling behavior."""

    @pytest.fixture
    def large_valid_df(self):
        """Create large DataFrame for sampling tests."""
        return pd.DataFrame({
            "dispatch_date": pd.date_range("2020-01-01", periods=5000),
            "ucr_general": [100] * 5000,
            "point_x": [-75.16] * 5000,
            "point_y": [39.95] * 5000,
        })

    def test_sample_mode_validates_subset(self, large_valid_df):
        """Sample mode validates only subset of rows."""
        # Should validate only 100 rows (default sample_size)
        result = validate_crime_data(large_valid_df, sample_size=100)

        assert result is large_valid_df  # Returns same DataFrame

    def test_strict_mode_validates_all_rows(self, large_valid_df):
        """Strict mode validates all rows (slow for large datasets)."""
        @pytest.mark.slow
        def test_slow():
            result = validate_crime_data(large_valid_df, strict=True)

            assert result is large_valid_df

    def test_sample_smaller_than_dataframe(self, large_valid_df):
        """Sample size smaller than DataFrame validates only sample."""
        result = validate_crime_data(large_valid_df, sample_size=50)

        assert result is large_valid_df

    def test_sample_larger_than_dataframe(self):
        """Sample size larger than DataFrame validates all rows."""
        small_df = pd.DataFrame({
            "dispatch_date": pd.date_range("2020-01-01", periods=10),
            "ucr_general": [100] * 10,
        })

        result = validate_crime_data(small_df, sample_size=1000)

        assert result is small_df

class TestValidateCoordinatesEdgeCases:
    """Tests for validate_coordinates edge cases."""

    def test_all_invalid_coordinates_returns_empty(self):
        """All rows with invalid coordinates returns empty DataFrame."""
        df = pd.DataFrame({
            "point_x": [-100.0, -200.0],  # Outside Philly bounds
            "point_y": [50.0, 60.0],       # Outside Philly bounds
        })

        result = validate_coordinates(df)

        assert len(result) == 0

    def test_partial_invalid_coordinates_filters_correctly(self):
        """Filters only rows with invalid coordinates."""
        df = pd.DataFrame({
            "point_x": [-75.16, -100.0, -75.20],  # Middle one invalid
            "point_y": [39.95, 50.0, 40.0],       # Middle one invalid
            "id": [1, 2, 3]
        })

        result = validate_coordinates(df)

        assert len(result) == 2
        assert result["id"].tolist() == [1, 3]

    def test_nan_coordinates_filtered_out(self):
        """NaN coordinates are filtered out."""
        df = pd.DataFrame({
            "point_x": [-75.16, None, -75.20],
            "point_y": [39.95, 40.0, None],
            "id": [1, 2, 3]
        })

        result = validate_coordinates(df)

        assert len(result) == 1  # Only first row valid

    @pytest.mark.parametrize(
        "lon,lat,should_pass",
        [
            (-75.3, 39.85, True),   # Minimum bounds
            (-74.95, 40.15, True),  # Maximum bounds
            (-75.31, 39.85, False), # Just below min lon
            (-74.94, 40.15, False), # Just above max lon
            (-75.16, 39.84, False), # Just below min lat
            (-75.16, 40.16, False), # Just above max lat
        ]
    )
    def test_boundary_coordinates(self, lon, lat, should_pass):
        """Boundary coordinates at edge of Philly bounds."""
        df = pd.DataFrame({
            "point_x": [lon],
            "point_y": [lat]
        })

        result = validate_coordinates(df)

        assert len(result) == (1 if should_pass else 0)
```

### Example 4: Testing Spatial Utilities

```python
import pandas as pd
import numpy as np
import pytest
from analysis.utils.spatial import (
    clean_coordinates,
    calculate_severity_score,
    get_coordinate_stats,
)

class TestCleanCoordinates:
    """Tests for clean_coordinates function."""

    def test_filters_valid_philadelphia_coordinates(self):
        """Filters to valid Philadelphia coordinates only."""
        df = pd.DataFrame({
            "point_x": [-75.16, -100.0, -75.20],  # Middle invalid
            "point_y": [39.95, 40.0, 50.0],       # Middle invalid
            "id": [1, 2, 3]
        })

        result = clean_coordinates(df)

        assert len(result) == 2
        assert result["id"].tolist() == [1, 3]

    def test_custom_column_names(self):
        """Accepts custom column names for coordinates."""
        df = pd.DataFrame({
            "custom_lon": [-75.16],
            "custom_lat": [39.95]
        })

        result = clean_coordinates(df, x_col="custom_lon", y_col="custom_lat")

        assert len(result) == 1

    def test_missing_column_raises_value_error(self):
        """Raises ValueError when coordinate columns missing."""
        df = pd.DataFrame({"other_column": [1, 2, 3]})

        with pytest.raises(ValueError, match="Columns .* not found"):
            clean_coordinates(df)

    def test_returns_copy_not_view(self):
        """Returns a copy, not a view."""
        df = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "id": [1]
        })

        result = clean_coordinates(df)
        result.loc[result.index[0], "id"] = 999

        # Original DataFrame unchanged
        assert df["id"].iloc[0] == 1

class TestCalculateSeverityScore:
    """Tests for calculate_severity_score function."""

    def test_ucr_hundred_band_mapping(self):
        """Maps UCR codes to severity weights by hundred-band."""
        df = pd.DataFrame({
            "ucr_general": [100, 600, 250]  # 100, 600, 200-band
        })

        scores = calculate_severity_score(df)

        # Test: 100-band -> 10.0 severity
        assert scores.iloc[0] == 10.0
        # Test: 600-band -> 1.0 severity
        assert scores.iloc[1] == 1.0
        # Test: 250 -> 200-band -> 8.0 severity
        assert scores.iloc[2] == 8.0

    def test_unknown_ucr_code_defaults_to_0_5(self):
        """Unknown UCR codes default to 0.5 severity."""
        df = pd.DataFrame({
            "ucr_general": [9999]  # Not in severity weights
        })

        scores = calculate_severity_score(df)

        assert scores.iloc[0] == 0.5

    def test_custom_weights_override_defaults(self):
        """Custom weights override default severity weights."""
        custom_weights = {
            100: 5.0,  # Override
            200: 3.0,
            300: 2.0,
        }

        df = pd.DataFrame({"ucr_general": [100, 600]})
        scores = calculate_severity_score(df, weights=custom_weights)

        # Test: custom weight used
        assert scores.iloc[0] == 5.0
        # Test: unknown code defaults to 0.5
        assert scores.iloc[1] == 0.5

    def test_nan_ucr_code_defaults_to_0_5(self):
        """NaN UCR code defaults to 0.5 severity."""
        df = pd.DataFrame({
            "ucr_general": [None, 600]
        })

        scores = calculate_severity_score(df)

        assert pd.isna(scores.iloc[0])
        assert scores.iloc[1] == 1.0

    def test_custom_ucr_column_name(self):
        """Accepts custom UCR column name."""
        df = pd.DataFrame({
            "custom_ucr": [100, 600]
        })

        scores = calculate_severity_score(df, ucr_col="custom_ucr")

        assert scores.iloc[0] == 10.0
        assert scores.iloc[1] == 1.0

class TestGetCoordinateStats:
    """Tests for get_coordinate_stats function."""

    def test_calculates_coverage_rate(self):
        """Calculates coordinate coverage rate."""
        df = pd.DataFrame({
            "point_x": [-75.16, None, -75.20],
            "point_y": [39.95, 40.0, None]
        })

        stats = get_coordinate_stats(df)

        # Test: 2 out of 3 have coordinates
        assert stats["has_coordinates"] == 2
        assert stats["coverage_rate"] == pytest.approx(2/3)

    def test_calculates_in_bounds_rate(self):
        """Calculates in-bounds rate (valid Philly coordinates)."""
        df = pd.DataFrame({
            "point_x": [-75.16, -100.0, -75.20],  # Middle out of bounds
            "point_y": [39.95, 40.0, 50.0]
        })

        stats = get_coordinate_stats(df)

        # Test: only first row in Philly bounds
        assert stats["in_philadelphia_bounds"] == 1
        assert stats["in_bounds_rate"] == pytest.approx(1/3)

    def test_returns_min_max_bounds(self):
        """Returns min/max longitude and latitude."""
        df = pd.DataFrame({
            "point_x": [-75.16, -75.20, -75.10],
            "point_y": [39.95, 40.0, 39.90]
        })

        stats = get_coordinate_stats(df)

        # Test: bounds computed correctly
        assert stats["lon_min"] == pytest.approx(-75.20)
        assert stats["lon_max"] == pytest.approx(-75.10)
        assert stats["lat_min"] == pytest.approx(39.90)
        assert stats["lat_max"] == pytest.approx(40.0)

    def test_empty_dataframe_returns_zero_stats(self):
        """Empty DataFrame returns zero statistics."""
        df = pd.DataFrame({"point_x": [], "point_y": []})

        stats = get_coordinate_stats(df)

        assert stats["total_records"] == 0
        assert stats["has_coordinates"] == 0
        assert stats["coverage_rate"] == 0
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| **assert df1.equals(df2)** | **pd.testing.assert_frame_equal()** | Pandas 1.0+ | Better error messages, handles NaN correctly |
| **Model accuracy tests** | **Workflow + metric tests** | 2020+ | Tests faster, less flaky, focus on logic |
| **Loading real data** | **Synthetic fixtures** | Always | Tests deterministic, fast, no I/O |
| **unittest.TestCase** | **pytest fixtures** | 2018+ | Less boilerplate, better parametrization |
| **Testing sklearn internals** | **Mocking model training** | 2021+ | Faster tests, test your code not library |

**Deprecated/outdated:**
- **Testing model accuracy**: Don't assert `model.score() > 0.9`. Test workflow logic instead.
- **Loading production data**: Don't use `pd.read_parquet("data/crime.parquet")`. Use fixtures.
- **Direct float equality**: Don't use `assert metric == 0.0`. Use `pytest.approx(0.0)`.

## Open Questions

1. **Python version compatibility**
   - What we know: pyproject.toml requires Python 3.14+, but Python 3.13.9 is installed
   - What's unclear: Whether code uses 3.14-only features, or if requirement can be relaxed
   - Recommendation: Use Python 3.13-compatible code patterns (avoid 3.14-only syntax), test on 3.13

2. **Prophet model testing approach**
   - What we know: Prophet is slow to train, non-deterministic results
   - What's unclear: Whether to mock Prophet entirely or use tiny synthetic datasets
   - Recommendation: Test data preparation and metric calculations with synthetic data, mock Prophet.fit() for workflow tests

3. **GeoPandas mocking strategy**
   - What we know: GeoPandas spatial joins are slow, require GeoJSON files
   - What's unclear: Whether to mock sjoin() or use tiny fixture GeoJSON
   - Recommendation: Mock sjoin() for logic tests, use tiny fixture for integration tests

## Sources

### Primary (HIGH confidence)

- **pytest documentation** - Test discovery, fixtures, parametrization, marks
  - https://docs.pytest.org/
- **pandas.testing.assert_frame_equal** - DataFrame comparison with NaN handling
  - https://pandas.pydata.org/docs/reference/api/pandas.testing.assert_frame_equal.html
- **numpy.testing** - Array comparison with tolerance
  - https://numpy.org/doc/stable/reference/routines.testing.html
- **unittest.mock** - Python standard library mocking
  - https://docs.python.org/3/library/unittest.mock.html
- **scikit-learn documentation** - Model validation, time series cross-validation
  - https://scikit-learn.org/stable/modules/cross_validation.html
- **Phase 10 baseline** - Existing test patterns, fixtures, coverage data
  - /Users/dustinober/Projects/Crime Incidents Philadelphia/.planning/phases/10-test-infrastructure-&-baseline/

### Secondary (MEDIUM confidence)

- **Effective Python Testing With pytest** (RealPython, 2025) - pytest fixtures, best practices
  - https://realpython.com/pytest-python-testing/
- **How to Use pytest Fixtures** (OneUptime, Jan 2026) - Fixture patterns, scoping
  - https://oneuptime.com/blog/post/2026-02-02-pytest-fixtures/view
- **Testing Best Practices for Machine Learning Libraries** (Towards Data Science, 2021) - ML testing patterns
  - https://towardsdatascience.com/testing-best-practices-for-machine-learning-libraries-41b7d0362c95/
- **pytest-mock Tutorial** (DataCamp, Dec 2024) - Mocking external dependencies
  - https://www.datacamp.com/tutorial/pytest-mock
- **Pytest Fixtures in Plain English** (The Data Savvy Corner, Apr 2024) - Fixture fundamentals
  - https://thedatasavvycorner.com/blogs/11-fiddly-bits-of-pytest
- **Mastering Pytest: Advanced Fixtures, Parameterization** (Medium, Dec 2024) - Parametrize patterns
  - https://medium.com/@abhayda/mastering-pytest-advanced-fixtures-parameterization-and-mocking-explained-108a6a2ab82d
- **Code coverage vs. test coverage in Python** (Honeybadger, Jan 2026) - Coverage best practices
  - https://www.honeybadger.io/blog/code-test-coverage-python/

### Tertiary (LOW confidence)

- **Automated Testing in Machine Learning Projects** (Neptune.ai) - ML testing strategies
  - https://neptune.ai/blog/automated-testing-machine-learning
- **The Machine Learning Engineer's Checklist** (Machine Learning Mastery, Dec 2025) - ML testing guidelines
  - https://machinelearningmastery.com/the-machine-learning-engineers-checklist-best-practices-for-reliable-models/
- **Testing APIs with PyTest: Mocks** (Codilime, Oct 2024) - API mocking patterns
  - https://codilime.com/blog/testing-apis-with-pytest-mocks-in-python/

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - pytest, pandas.testing, numpy.testing are well-established standards
- Architecture: HIGH - existing test suite provides proven patterns (test_classification.py, test_temporal.py)
- Pitfalls: HIGH - common ML/data testing mistakes well-documented in community
- ML testing patterns: MEDIUM - based on web research and common practices, not official guidelines
- GeoPandas mocking: MEDIUM - based on general mocking patterns, not GeoPandas-specific docs

**Research date:** February 7, 2026
**Valid until:** March 9, 2026 (30 days - Python testing ecosystem is stable)

## Module Inventory

### analysis/models/ (3 modules, 178 statements)

**models/classification.py (70 statements)**
- Functions to test:
  - `create_time_aware_split()` - Time series train/test split
  - `get_time_series_cv()` - TimeSeriesSplit factory
  - `train_random_forest()` - Random Forest training workflow
  - `train_xgboost()` - XGBoost training workflow
  - `extract_feature_importance()` - Feature importance extraction
  - `compute_shap_values()` - SHAP value computation (optional)
  - `evaluate_classifier()` - Classification metrics
  - `handle_class_imbalance()` - Class weight calculation
- Testing strategy:
  - Test split logic (temporal ordering, indices) without training models
  - Test model workflow (returns fitted model, scaler) without asserting accuracy
  - Test feature importance sorting and top_n filtering
  - Test metric calculations with synthetic predictions
  - Mock SHAP computation (slow, optional)

**models/time_series.py (48 statements)**
- Functions to test:
  - `prepare_prophet_data()` - Prophet format conversion
  - `create_train_test_split()` - Time-aware train/test split
  - `get_prophet_config()` - Prophet configuration factory
  - `evaluate_forecast()` - Forecast metrics (MAE, RMSE, MAPE, R²)
  - `detect_anomalies()` - Residual-based anomaly detection
- Testing strategy:
  - Test data preparation (column renaming, sorting, datetime parsing)
  - Test Prophet configuration defaults and custom parameters
  - Test metric calculations with known synthetic data
  - Test anomaly detection logic with predetermined residuals
  - Mock Prophet.fit() for workflow tests (slow)

**models/validation.py (60 statements)**
- Functions to test:
  - `time_series_cv_score()` - Time series cross-validation
  - `walk_forward_validation()` - Walk-forward validation
  - `compute_regression_metrics()` - Regression metrics (MAE, RMSE, R², MAPE)
  - `compute_forecast_accuracy()` - Forecast metrics with MASE
  - `create_model_card()` - Model documentation
  - `check_residual_autocorrelation()` - Ljung-Box test
  - `validate_temporal_split()` - Train/test split validation
- Testing strategy:
  - Test cross-validation returns correct statistics (mean, std, min, max)
  - Test regression metrics with synthetic data
  - Test MASE calculation with naive forecast baseline
  - Test model card structure and fields
  - Mock autocorrelation test (statsmodels dependency)
  - Test temporal split validation logic

### analysis/data/ (4 modules, 159 statements)

**data/loading.py (55 statements)**
- Functions to test:
  - `load_crime_data()` - Load crime parquet with caching
  - `load_boundaries()` - Load GeoJSON boundaries
  - `load_external_data()` - Load CSV data
  - `_load_crime_data_parquet()` - Cached parquet loader (internal)
  - `_load_boundaries_geojson()` - Cached GeoJSON loader (internal)
  - `_load_external_data_csv()` - Cached CSV loader (internal)
- Testing strategy:
  - Test FileNotFoundError handling when files missing
  - Test datetime parsing from parquet category dtype
  - Test clean parameter (NaN dropping)
  - Test boundary name validation
  - Mock file I/O (pd.read_parquet, Path.read_bytes)
  - Test caching behavior (memoization) with joblib

**data/validation.py (64 statements)**
- Already tested: 44 tests in test_data_validation.py
- Coverage: Likely 80-90% (existing tests are comprehensive)
- Testing gaps: Possibly error handling, edge cases not covered
- Strategy: Run coverage report to identify gaps, add targeted tests

**data/preprocessing.py (25 statements)**
- Already tested: 36 tests in test_data_preprocessing.py
- Coverage: Likely 90%+ (existing tests are comprehensive)
- Testing gaps: Minimal, verify with coverage report
- Strategy: Run coverage report, add tests only for missing branches

**data/cache.py (15 statements)**
- Functions to test:
  - `memory` - joblib.Memory instance configuration
- Testing strategy:
  - Test cache directory configuration
  - Test cached function behavior (memoization)
  - Test cache invalidation

### analysis/utils/ (3 modules, 96 statements)

**utils/classification.py (13 statements)**
- Already tested: 30 tests in test_classification.py
- Coverage: Likely 95%+ (very comprehensive test suite)
- Testing gaps: None significant
- Strategy: Verify with coverage report, no additional tests needed

**utils/temporal.py (14 statements)**
- Already tested: 30 tests in test_temporal.py
- Coverage: Likely 95%+ (very comprehensive test suite)
- Testing gaps: None significant
- Strategy: Verify with coverage report, no additional tests needed

**utils/spatial.py (69 statements)**
- Functions to test:
  - `clean_coordinates()` - Filter to valid Philly coordinates
  - `load_boundaries()` - Load boundary GeoJSON
  - `df_to_geodataframe()` - Convert DataFrame to GeoDataFrame
  - `spatial_join_districts()` - Join crime to police districts
  - `spatial_join_tracts()` - Join crime to census tracts
  - `calculate_severity_score()` - Calculate severity from UCR codes
  - `get_coordinate_stats()` - Coordinate coverage statistics
- Testing strategy:
  - Test coordinate filtering bounds checking
  - Test severity score UCR band mapping
  - Test coordinate statistics calculations
  - Mock GeoPandas operations (sjoin, GeoDataFrame conversion)
  - Test spatial join logic (column renaming, cleanup)
  - Test error handling (missing columns, invalid boundary names)

## Testing Recommendations

### Priority 1: High-Impact Modules (Start Here)

1. **utils/spatial.py** - Core spatial operations, high usage
   - Estimated tests: 50-60
   - Estimated effort: 4-6 hours
   - Complexity: Medium (GeoPandas mocking required)

2. **models/classification.py** - ML workflows for classification
   - Estimated tests: 40-50
   - Estimated effort: 3-4 hours
   - Complexity: Medium (model mocking, workflow testing)

3. **models/validation.py** - Time series validation, metrics
   - Estimated tests: 30-40
   - Estimated effort: 2-3 hours
   - Complexity: Low-Medium (metric calculations, mock statsmodels)

4. **models/time_series.py** - Prophet utilities, forecasting
   - Estimated tests: 30-40
   - Estimated effort: 2-3 hours
   - Complexity: Medium (Prophet mocking, time series logic)

### Priority 2: Supporting Modules

5. **data/loading.py** - Data loading with caching
   - Estimated tests: 25-30
   - Estimated effort: 2 hours
   - Complexity: Low (file I/O mocking)

6. **data/cache.py** - Caching configuration
   - Estimated tests: 5-10
   - Estimated effort: 1 hour
   - Complexity: Low

### Priority 3: Already Well-Tested (Verify Only)

7. **data/validation.py** - Verify coverage gaps
   - Estimated additional tests: 0-10
   - Estimated effort: 1 hour
   - Strategy: Run coverage, add tests only for missing branches

8. **data/preprocessing.py** - Verify coverage gaps
   - Estimated additional tests: 0-5
   - Estimated effort: 1 hour
   - Strategy: Run coverage, add tests only for missing branches

9. **utils/classification.py** - Verify coverage gaps
   - Estimated additional tests: 0-5
   - Estimated effort: 0.5 hour
   - Strategy: Run coverage, likely no additional tests needed

10. **utils/temporal.py** - Verify coverage gaps
    - Estimated additional tests: 0-5
    - Estimated effort: 0.5 hour
    - Strategy: Run coverage, likely no additional tests needed

### Total Effort Estimate

- **New tests required:** ~180-230 tests
- **Time estimate:** 15-20 hours
- **Coverage target:** 60-70% for core modules (CORE-04 requirement)
- **Milestone:** Achieve 95% overall coverage by Phase 13

## Test File Organization

### Recommended File Structure

```
tests/
├── conftest.py                           # SHARED FIXTURES (EXISTS)
├── test_classification.py                # utils/classification (EXISTS, 30 tests)
├── test_temporal.py                      # utils/temporal (EXISTS, 30 tests)
├── test_data_validation.py               # data/validation (EXISTS, 44 tests)
├── test_data_loading.py                  # data/loading (EXISTS, 31 tests)
├── test_data_preprocessing.py            # data/preprocessing (EXISTS, 36 tests)
│
├── test_models_classification.py         # NEW: models/classification.py
│   ├── TestCreateTimeAwareSplit
│   ├── TestGetTimeSeriesCV
│   ├── TestTrainRandomForest
│   ├── TestTrainXGBoost
│   ├── TestExtractFeatureImportance
│   ├── TestEvaluateClassifier
│   └── TestHandleClassImbalance
│
├── test_models_time_series.py            # NEW: models/time_series.py
│   ├── TestPrepareProphetData
│   ├── TestCreateTrainTestSplit
│   ├── TestGetProphetConfig
│   ├── TestEvaluateForecast
│   └── TestDetectAnomalies
│
├── test_models_validation.py             # NEW: models/validation.py
│   ├── TestTimeSeriesCVScore
│   ├── TestWalkForwardValidation
│   ├── TestComputeRegressionMetrics
│   ├── TestComputeForecastAccuracy
│   ├── TestCreateModelCard
│   ├── TestCheckResidualAutocorrelation
│   └── TestValidateTemporalSplit
│
└── test_utils_spatial.py                 # NEW: utils/spatial.py
    ├── TestCleanCoordinates
    ├── TestLoadBoundaries
    ├── TestDfToGeodataframe
    ├── TestSpatialJoinDistricts
    ├── TestSpatialJoinTracts
    ├── TestCalculateSeverityScore
    └── TestGetCoordinateStats
```

## Coverage Milestones

### Phase 11 Target: 60-70% Overall Coverage

**Starting point (Phase 10):**
- Overall coverage: 0%
- Total statements: 2528

**Phase 11 goal (CORE-04):**
- Target coverage: 60-70% overall
- Statements to cover: ~1515-1770 statements
- Coverage gap: ~60-70 percentage points

**Per-module targets:**

| Module | Current | Phase 11 Target | Statements | Tests Needed |
|--------|---------|-----------------|------------|--------------|
| models/classification.py | 0% | 80% | 70 | ~50-60 tests |
| models/time_series.py | 0% | 80% | 48 | ~30-40 tests |
| models/validation.py | 0% | 80% | 60 | ~30-40 tests |
| utils/spatial.py | 0% | 80% | 69 | ~50-60 tests |
| data/loading.py | 0% | 80% | 55 | ~25-30 tests |
| data/validation.py | ~60%* | 80% | 64 | ~5-10 tests |
| data/preprocessing.py | ~80%* | 90% | 25 | ~0-5 tests |
| utils/classification.py | ~95%* | 95% | 13 | ~0-3 tests |
| utils/temporal.py | ~95%* | 95% | 14 | ~0-3 tests |

*Estimated based on existing test counts

**Progress tracking:**
```bash
# After Phase 11
pytest --cov=analysis --cov=api --cov=pipeline --cov-report=term-missing
coverage report > .planning/phases/11-core-module-testing/coverage-phase11.txt
```

## Python Version Compatibility Issue

**Current situation:**
- pyproject.toml requires: `requires-python = ">=3.14"`
- Installed Python: 3.13.9
- Issue: Tests must run on 3.13.9 (development environment)

**Resolution:**
1. Test on Python 3.13.9 (current installation)
2. Avoid Python 3.14-only features:
   - No new syntax patterns from 3.14
   - Use type hints compatible with 3.13
   - Avoid deprecated APIs removed in 3.14
3. Update pyproject.toml after testing: `requires-python = ">=3.13"`
4. Verify tests pass on both 3.13 and 3.14 (CI can test 3.14)

**Code patterns to avoid:**
- No 3.14-specific syntax (if any added)
- No type checking changes specific to 3.14
- Use `from __future__ import annotations` for forward compatibility

**Testing approach:**
- Run tests on 3.13.9 (local development)
- CI will test on 3.14 (when configured)
- Ensure compatibility with both versions
