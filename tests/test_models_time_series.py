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
