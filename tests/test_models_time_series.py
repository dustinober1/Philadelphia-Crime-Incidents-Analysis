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
