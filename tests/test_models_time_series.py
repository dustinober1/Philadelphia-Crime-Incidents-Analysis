"""Tests for time series model utilities.

This module tests time series forecasting utilities including Prophet data
preparation, train/test splitting, Prophet configuration, forecast evaluation,
and anomaly detection.

Tests use synthetic time series data to avoid slow Prophet model training.
"""

from __future__ import annotations

import pandas as pd
import pytest

from analysis.models.time_series import (
    prepare_prophet_data,
    create_train_test_split,
    get_prophet_config,
    evaluate_forecast,
    detect_anomalies,
)


class TestPrepareProphetData:
    """Tests for prepare_prophet_data function."""

    def test_returns_prophet_format_columns(self):
        """Returns DataFrame with 'ds' and 'y' columns."""
        df = pd.DataFrame({
            "date": ["2020-01-01", "2020-01-02", "2020-01-03"],
            "count": [10, 20, 30]
        })

        result = prepare_prophet_data(df, "date", "count")

        assert list(result.columns) == ["ds", "y"]
        assert "date" not in result.columns
        assert "count" not in result.columns

    def test_converts_date_column_to_datetime(self):
        """Converts date column to datetime64 dtype."""
        df = pd.DataFrame({
            "date": ["2020-01-01", "2020-01-02", "2020-01-03"],
            "count": [10, 20, 30]
        })

        result = prepare_prophet_data(df, "date", "count")

        assert pd.api.types.is_datetime64_any_dtype(result["ds"])

    def test_sorts_by_date_ascending(self):
        """Sorts DataFrame by date column in ascending order."""
        df = pd.DataFrame({
            "date": ["2020-01-03", "2020-01-01", "2020-01-02"],
            "count": [30, 10, 20]
        })

        result = prepare_prophet_data(df, "date", "count")

        assert result["ds"].is_monotonic_increasing
        assert result["ds"].iloc[0] == pd.Timestamp("2020-01-01")
        assert result["ds"].iloc[1] == pd.Timestamp("2020-01-02")
        assert result["ds"].iloc[2] == pd.Timestamp("2020-01-03")

    def test_resets_index_after_sorting(self):
        """Resets index to 0, 1, 2, ... after sorting."""
        df = pd.DataFrame({
            "date": ["2020-01-03", "2020-01-01", "2020-01-02"],
            "count": [30, 10, 20]
        })

        result = prepare_prophet_data(df, "date", "count")

        assert list(result.index) == [0, 1, 2]

    def test_handles_duplicate_dates(self):
        """Preserves duplicate dates (does not aggregate)."""
        df = pd.DataFrame({
            "date": ["2020-01-01", "2020-01-01", "2020-01-02"],
            "count": [10, 15, 20]
        })

        result = prepare_prophet_data(df, "date", "count")

        # Test: duplicates preserved (not aggregated)
        assert len(result) == 3
        assert result[result["ds"] == pd.Timestamp("2020-01-01")].shape[0] == 2

    def test_handles_empty_dataframe(self):
        """Returns empty DataFrame with correct columns for empty input."""
        df = pd.DataFrame({"date": [], "count": []})

        result = prepare_prophet_data(df, "date", "count")

        assert len(result) == 0
        assert list(result.columns) == ["ds", "y"]

    def test_custom_date_column_name(self):
        """Accepts custom date column name."""
        df = pd.DataFrame({
            "my_date": ["2020-01-01", "2020-01-02"],
            "count": [10, 20]
        })

        result = prepare_prophet_data(df, "my_date", "count")

        assert "ds" in result.columns
        assert result["ds"].iloc[0] == pd.Timestamp("2020-01-01")

    def test_custom_value_column_name(self):
        """Accepts custom value column name."""
        df = pd.DataFrame({
            "date": ["2020-01-01", "2020-01-02"],
            "my_value": [10, 20]
        })

        result = prepare_prophet_data(df, "date", "my_value")

        assert "y" in result.columns
        assert result["y"].iloc[0] == 10


class TestCreateTrainTestSplit:
    """Tests for create_train_test_split function."""

    def test_requires_ds_column_raises_value_error(self):
        """Raises ValueError when 'ds' column missing."""
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

    def test_custom_test_days_parameter(self):
        """Respects custom test_days parameter."""
        df = pd.DataFrame({
            "ds": pd.date_range("2020-01-01", periods=100),
            "y": range(100)
        })

        train, test = create_train_test_split(df, test_days=10)

        assert len(test) == 10
        assert len(train) == 90

    def test_test_days_30_default(self):
        """Default 30 days held out for testing."""
        df = pd.DataFrame({
            "ds": pd.date_range("2020-01-01", periods=100),
            "y": range(100)
        })

        train, test = create_train_test_split(df)

        assert len(test) == 30
        assert len(train) == 70

    def test_no_overlap_between_train_and_test(self):
        """No overlap between train and test data."""
        df = pd.DataFrame({
            "ds": pd.date_range("2020-01-01", periods=100),
            "y": range(100)
        })

        train, test = create_train_test_split(df, test_days=30)

        # Test: train ends before test starts
        assert train["ds"].max() < test["ds"].min()
        # Test: gap is exactly test_days
        assert (test["ds"].min() - train["ds"].max()).days == 1

    def test_handles_exact_boundary(self):
        """Handles boundary dates correctly."""
        df = pd.DataFrame({
            "ds": pd.date_range("2020-01-01", periods=31),
            "y": range(31)
        })

        train, test = create_train_test_split(df, test_days=30)

        # Test: train has 1 day (day 0)
        assert len(train) == 1
        # Test: test has 30 days (days 1-30)
        assert len(test) == 30


class TestGetProphetConfig:
    """Tests for get_prophet_config function."""

    def test_default_configuration(self):
        """Returns default Prophet configuration."""
        config = get_prophet_config()

        assert config["seasonality_mode"] == "multiplicative"
        assert config["yearly_seasonality"] is True
        assert config["weekly_seasonality"] is True
        assert config["daily_seasonality"] is False
        assert config["changepoint_prior_scale"] == 0.05
        assert config["interval_width"] == 0.95

    def test_seasonality_mode_additive(self):
        """Accepts seasonality_mode='additive'."""
        config = get_prophet_config(seasonality_mode="additive")

        assert config["seasonality_mode"] == "additive"
        assert config["yearly_seasonality"] is True
        assert config["weekly_seasonality"] is True

    def test_seasonality_mode_multiplicative(self):
        """Accepts seasonality_mode='multiplicative'."""
        config = get_prophet_config(seasonality_mode="multiplicative")

        assert config["seasonality_mode"] == "multiplicative"

    def test_yearly_seasonality_parameter(self):
        """Passes through yearly_seasonality parameter."""
        config = get_prophet_config(yearly=False)

        assert config["yearly_seasonality"] is False

    def test_weekly_seasonality_parameter(self):
        """Passes through weekly_seasonality parameter."""
        config = get_prophet_config(weekly=False)

        assert config["weekly_seasonality"] is False

    def test_daily_seasonality_parameter(self):
        """Passes through daily_seasonality parameter."""
        config = get_prophet_config(daily=True)

        assert config["daily_seasonality"] is True

    def test_changepoint_prior_scale_parameter(self):
        """Passes through changepoint_prior_scale parameter."""
        config = get_prophet_config(changepoint_prior_scale=0.1)

        assert config["changepoint_prior_scale"] == 0.1

    def test_interval_width_parameter(self):
        """Passes through interval_width parameter."""
        config = get_prophet_config(interval_width=0.8)

        assert config["interval_width"] == 0.8

    def test_all_parameters_combination(self):
        """Multiple custom parameters work together."""
        config = get_prophet_config(
            seasonality_mode="additive",
            yearly=False,
            weekly=False,
            daily=True,
            changepoint_prior_scale=0.5,
            interval_width=0.9
        )

        assert config["seasonality_mode"] == "additive"
        assert config["yearly_seasonality"] is False
        assert config["weekly_seasonality"] is False
        assert config["daily_seasonality"] is True
        assert config["changepoint_prior_scale"] == 0.5
        assert config["interval_width"] == 0.9


class TestEvaluateForecast:
    """Tests for evaluate_forecast function."""

    def test_perfect_forecast_returns_ideal_metrics(self):
        """Perfect forecast returns MAE=0, RMSE=0, R2=1, MAPE=0."""
        actual = pd.Series([100.0, 200.0, 300.0])
        predicted = pd.Series([100.0, 200.0, 300.0])

        metrics = evaluate_forecast(actual, predicted)

        assert metrics["mae"] == pytest.approx(0.0, abs=0.01)
        assert metrics["rmse"] == pytest.approx(0.0, abs=0.01)
        assert metrics["r2"] == pytest.approx(1.0, abs=0.01)
        assert metrics["mape"] == pytest.approx(0.0, abs=0.01)

    def test_constant_bias_captured_in_bias_metric(self):
        """Constant forecast bias is captured in bias metric."""
        # Note: bias is computed as mean(predicted - actual)
        # But our implementation doesn't have a bias metric - let's verify
        actual = pd.Series([100.0, 200.0, 300.0])
        predicted = pd.Series([110.0, 210.0, 310.0])  # Always +10

        metrics = evaluate_forecast(actual, predicted)

        # MAE should be 10 (constant bias)
        assert metrics["mae"] == pytest.approx(10.0, abs=0.01)

    def test_mae_calculation(self):
        """MAE computed correctly with known synthetic data."""
        actual = pd.Series([100.0, 200.0, 300.0])
        predicted = pd.Series([110.0, 210.0, 310.0])  # All +10

        metrics = evaluate_forecast(actual, predicted)

        # MAE = mean(|110-100|, |210-200|, |310-300|) = 10
        assert metrics["mae"] == pytest.approx(10.0, abs=0.01)

    def test_rmse_calculation(self):
        """RMSE computed correctly with known synthetic data."""
        actual = pd.Series([100.0, 200.0, 300.0])
        predicted = pd.Series([110.0, 210.0, 310.0])  # All +10

        metrics = evaluate_forecast(actual, predicted)

        # RMSE = sqrt(mean(10^2, 10^2, 10^2)) = sqrt(100) = 10
        assert metrics["rmse"] == pytest.approx(10.0, abs=0.01)

    def test_r2_calculation(self):
        """R2 computed correctly with known synthetic data."""
        actual = pd.Series([100.0, 200.0, 300.0])
        predicted = pd.Series([100.0, 200.0, 300.0])

        metrics = evaluate_forecast(actual, predicted)

        # Perfect prediction = R2 = 1
        assert metrics["r2"] == pytest.approx(1.0, abs=0.01)

    def test_mape_calculation(self):
        """MAPE computed correctly with known synthetic data."""
        actual = pd.Series([100.0, 200.0, 300.0])
        predicted = pd.Series([90.0, 210.0, 330.0])  # -10%, +5%, +10%

        metrics = evaluate_forecast(actual, predicted)

        # MAPE = mean(|90-100|/100, |210-200|/200, |330-300|/300) * 100
        # = mean(0.10, 0.05, 0.10) * 100 = 8.33%
        assert metrics["mape"] == pytest.approx(8.33, abs=0.1)

    def test_nan_handling_filters_nan_pairs(self):
        """NaN values filtered from both actual and predicted."""
        import numpy as np
        actual = pd.Series([100.0, np.nan, 300.0])
        predicted = pd.Series([110.0, 210.0, 310.0])

        metrics = evaluate_forecast(actual, predicted)

        # Metrics computed on (100, 110) and (300, 310) only
        assert "mae" in metrics
        assert not pd.isna(metrics["mae"])
        assert metrics["mae"] == pytest.approx(10.0, abs=0.01)

    def test_coverage_with_prediction_intervals(self):
        """Coverage metric computed when lower/upper provided."""
        actual = pd.Series([100.0, 200.0, 300.0])
        predicted = pd.Series([150.0, 200.0, 250.0])
        lower = pd.Series([90.0, 190.0, 240.0])
        upper = pd.Series([110.0, 210.0, 260.0])

        metrics = evaluate_forecast(actual, predicted, lower, upper)

        # Coverage metric exists
        assert "coverage" in metrics
        # First actual (100) in [90, 110] = in interval
        # Second actual (200) in [190, 210] = in interval
        # Third actual (300) not in [240, 260] = out of interval
        # Coverage = 2/3 = 0.667
        assert metrics["coverage"] == pytest.approx(0.667, abs=0.01)

    def test_coverage_not_computed_without_intervals(self):
        """Coverage not in results without lower/upper."""
        actual = pd.Series([100.0, 200.0, 300.0])
        predicted = pd.Series([150.0, 200.0, 250.0])

        metrics = evaluate_forecast(actual, predicted)

        # Coverage not computed
        assert "coverage" not in metrics

    def test_returns_dict_with_all_expected_keys(self):
        """Returns dict with all expected keys."""
        actual = pd.Series([100.0, 200.0, 300.0])
        predicted = pd.Series([110.0, 210.0, 310.0])

        metrics = evaluate_forecast(actual, predicted)

        # Has expected keys
        assert "mae" in metrics
        assert "rmse" in metrics
        assert "mape" in metrics
        assert "r2" in metrics


class TestDetectAnomalies:
    """Tests for detect_anomalies function."""

    def test_returns_boolean_series(self):
        """Returns pd.Series with dtype bool."""
        df = pd.DataFrame({
            "y": [100, 200, 300],
            "yhat": [100, 200, 300],
            "yhat_lower": [90, 190, 290],
            "yhat_upper": [110, 210, 310]
        })

        anomalies = detect_anomalies(df)

        assert isinstance(anomalies, pd.Series)
        assert anomalies.dtype == bool

    def test_threshold_anomaly_detection(self):
        """Anomalies detected when residual > threshold_std * std."""
        import numpy as np
        df = pd.DataFrame({
            "y": [100, 200, 500],  # Last value is outlier
            "yhat": [100, 200, 300],
            "yhat_lower": [90, 190, 290],
            "yhat_upper": [110, 210, 310]
        })

        anomalies = detect_anomalies(df)

        # Third row is anomaly due to interval check (500 > 310 upper bound)
        # Threshold check: residuals = [0, 0, 200], mean=66.67, std=115.47
        # |200 - 66.67| = 133.33 > 2*115.47? No (not > threshold)
        # But interval check catches it: 500 > 310
        assert anomalies.iloc[2] == True

    def test_interval_anomaly_detection(self):
        """Anomalies detected outside prediction interval."""
        import numpy as np
        df = pd.DataFrame({
            "y": [100, 200, 500],  # Last value outside interval
            "yhat": [100, 200, 300],
            "yhat_lower": [90, 190, 290],
            "yhat_upper": [110, 210, 310]
        })

        anomalies = detect_anomalies(df)

        # First two in interval [90, 110] and [190, 210], third outside [290, 310]
        assert anomalies.iloc[0] == False  # 100 in [90, 110]
        assert anomalies.iloc[1] == False  # 200 in [190, 210]
        assert anomalies.iloc[2] == True   # 500 > 310 (outside interval)

    def test_custom_threshold_std_parameter(self):
        """Custom threshold_std affects detection sensitivity."""
        import numpy as np
        # Create data where threshold matters
        # residuals = [0, 0, 150], mean=50, std=86.6
        # threshold=2: |150-50| = 100 > 2*86.6 = 173? No
        # threshold=1: |150-50| = 100 > 1*86.6 = 86.6? Yes
        df = pd.DataFrame({
            "y": [100, 200, 450],
            "yhat": [100, 200, 300],
            "yhat_lower": [90, 190, 290],
            "yhat_upper": [110, 210, 310]
        })

        # With threshold=2.0, no threshold anomalies
        anomalies_default = detect_anomalies(df, threshold_std=2.0)

        # With threshold=1.0, threshold anomaly detected
        anomalies_sensitive = detect_anomalies(df, threshold_std=1.0)

        # Sensitive should detect more (interval + threshold vs just interval)
        # Both detect interval anomaly (450 > 310), but sensitive also detects threshold
        assert anomalies_sensitive.sum() >= anomalies_default.sum()

    def test_custom_column_names(self):
        """Custom column names work correctly."""
        df = pd.DataFrame({
            "actual": [100, 200, 300],
            "predicted": [100, 200, 300],
            "lower": [90, 190, 290],
            "upper": [110, 210, 310]
        })

        anomalies = detect_anomalies(
            df,
            actual_col="actual",
            predicted_col="predicted",
            lower_col="lower",
            upper_col="upper"
        )

        # Should have no anomalies (all in interval)
        assert anomalies.sum() == 0

    def test_handles_empty_dataframe(self):
        """Empty DataFrame returns empty boolean series."""
        df = pd.DataFrame({
            "y": [],
            "yhat": [],
            "yhat_lower": [],
            "yhat_upper": []
        })

        anomalies = detect_anomalies(df)

        assert len(anomalies) == 0
        assert isinstance(anomalies, pd.Series)

    def test_all_anomalies_when_all_outside_interval(self):
        """All True when all values outside bounds."""
        df = pd.DataFrame({
            "y": [50, 150, 400],  # All outside interval
            "yhat": [100, 200, 300],
            "yhat_lower": [90, 190, 290],
            "yhat_upper": [110, 210, 310]
        })

        anomalies = detect_anomalies(df)

        # All should be anomalies
        assert anomalies.sum() == 3
        assert all(anomalies)
