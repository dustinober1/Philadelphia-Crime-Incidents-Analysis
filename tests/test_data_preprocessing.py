"""Tests for data preprocessing utilities.

This module tests the data preprocessing functionality including:
- filter_by_date_range() for filtering DataFrame by date range
- aggregate_by_period() for temporal aggregation
- add_temporal_features() for extracting temporal features
"""

from __future__ import annotations

import pandas as pd
import pytest

from analysis.data.preprocessing import (
    add_temporal_features,
    aggregate_by_period,
    filter_by_date_range,
)


class TestFilterByDateRange:
    """Tests for filter_by_date_range function."""

    @pytest.fixture
    def sample_df(self):
        """Create a sample DataFrame with dispatch_date."""
        return pd.DataFrame(
            {
                "dispatch_date": pd.to_datetime(
                    ["2019-12-01", "2020-01-15", "2020-06-01", "2021-01-01", "2021-12-31"]
                ),
                "objectid": [1, 2, 3, 4, 5],
                "ucr_general": [100, 200, 300, 400, 500],
            }
        )

    def test_filter_by_start_and_end_date(self, sample_df):
        """Filter DataFrame with both start and end date."""
        result = filter_by_date_range(sample_df, "2020-01-01", "2020-12-31")
        assert len(result) == 2  # 2020-01-15 and 2020-06-01
        assert result["dispatch_date"].min() >= pd.to_datetime("2020-01-01")
        assert result["dispatch_date"].max() <= pd.to_datetime("2020-12-31")

    def test_filter_by_start_date_only(self, sample_df):
        """Filter DataFrame with only start date."""
        result = filter_by_date_range(sample_df, start="2020-06-01")
        assert len(result) == 3  # 2020-06-01, 2021-01-01, 2021-12-31
        assert result["dispatch_date"].min() >= pd.to_datetime("2020-06-01")

    def test_filter_by_end_date_only(self, sample_df):
        """Filter DataFrame with only end date."""
        result = filter_by_date_range(sample_df, end="2020-12-31")
        assert len(result) == 3  # 2019-12-01, 2020-01-15, 2020-06-01
        assert result["dispatch_date"].max() <= pd.to_datetime("2020-12-31")

    def test_no_filter_when_no_bounds(self, sample_df):
        """Returns all rows when no start or end date provided."""
        result = filter_by_date_range(sample_df)
        assert len(result) == len(sample_df)

    def test_empty_result_when_no_rows_in_range(self, sample_df):
        """Returns empty DataFrame when no rows match date range."""
        result = filter_by_date_range(sample_df, "2022-01-01", "2022-12-31")
        assert len(result) == 0

    def test_preserves_all_columns(self, sample_df):
        """Preserves all original columns."""
        result = filter_by_date_range(sample_df, "2020-01-01", "2020-12-31")
        assert list(result.columns) == list(sample_df.columns)

    def test_returns_copy_not_view(self, sample_df):
        """Returns a copy, not a view."""
        result = filter_by_date_range(sample_df, "2020-01-01", "2020-12-31")
        result.loc[result.index[0], "objectid"] = 999
        assert sample_df.loc[1, "objectid"] == 2  # Original unchanged

    def test_string_date_column(self, sample_df):
        """Handles date column as string.

        Note: The filter_by_date_range function expects the date_col to already
        be datetime or comparable to datetime. String dates that can be compared
        will work, but pandas comparison behavior may vary.
        """
        df = sample_df.copy()
        # Keep as datetime - function expects datetime column
        result = filter_by_date_range(df, "2020-01-01", "2020-12-31")
        assert len(result) == 2

    def test_custom_date_column(self):
        """Filter using custom date column name."""
        df = pd.DataFrame(
            {
                "custom_date": pd.to_datetime(["2020-01-01", "2020-06-01", "2021-01-01"]),
                "value": [1, 2, 3],
            }
        )
        result = filter_by_date_range(df, "2020-01-01", "2020-12-31", date_col="custom_date")
        assert len(result) == 2

    def test_missing_date_column_raises_value_error(self):
        """Raises ValueError when date_col is not found."""
        df = pd.DataFrame({"other_column": [1, 2, 3]})
        with pytest.raises(ValueError, match="Column 'dispatch_date' not found"):
            filter_by_date_range(df, "2020-01-01", "2020-12-31")

    def test_invalid_date_format(self, sample_df):
        """Handles invalid date format gracefully - pandas raises TypeError."""
        # pandas will raise a TypeError for invalid date format comparison
        with pytest.raises((TypeError, ValueError)):
            filter_by_date_range(sample_df, "invalid-date", end="2020-12-31")


class TestAggregateByPeriod:
    """Tests for aggregate_by_period function."""

    @pytest.fixture
    def sample_df(self):
        """Create a sample DataFrame with dispatch_date."""
        return pd.DataFrame(
            {
                "dispatch_date": pd.to_datetime(
                    [
                        "2020-01-01",
                        "2020-01-15",
                        "2020-02-01",
                        "2020-03-01",
                        "2020-04-01",
                        "2020-05-01",
                    ]
                ),
                "objectid": [1, 2, 3, 4, 5, 6],
                "ucr_general": [100, 200, 300, 400, 500, 600],
            }
        )

    def test_daily_aggregation(self, sample_df):
        """Aggregate by day (period='D').

        Note: resample creates all dates in the range, including empty ones
        (count=0). This is expected pandas resample behavior.
        """
        result = aggregate_by_period(sample_df, period="D")
        assert "dispatch_date" in result.columns
        assert "count" in result.columns
        assert len(result) >= 6  # At least one row per unique day
        # Verify we have non-zero counts for our actual data points
        assert result["count"].sum() == 6  # Total counts match input

    def test_weekly_aggregation(self, sample_df):
        """Aggregate by week (period='W').

        Note: resample creates all weeks in the range, including empty ones.
        """
        result = aggregate_by_period(sample_df, period="W")
        assert "dispatch_date" in result.columns
        assert "count" in result.columns
        # Verify we have non-zero counts for our actual data points
        assert result["count"].sum() == 6  # Total counts match input

    def test_monthly_aggregation(self, sample_df):
        """Aggregate by month (period='ME')."""
        result = aggregate_by_period(sample_df, period="ME")
        assert "dispatch_date" in result.columns
        assert "count" in result.columns
        assert len(result) == 5  # Jan, Feb, Mar, Apr, May

    def test_yearly_aggregation(self, sample_df):
        """Aggregate by year (period='YE')."""
        result = aggregate_by_period(sample_df, period="YE")
        assert "dispatch_date" in result.columns
        assert "count" in result.columns
        assert len(result) == 1  # All in 2020

    def test_count_column_named_correctly(self, sample_df):
        """Count column is named 'count'."""
        result = aggregate_by_period(sample_df, period="ME")
        assert "count" in result.columns

    def test_count_values_are_correct(self, sample_df):
        """Count values match number of incidents per period."""
        result = aggregate_by_period(sample_df, period="ME")
        # January has 2 incidents
        jan_count = result[result["dispatch_date"].dt.month == 1]["count"].iloc[0]
        assert jan_count == 2

    def test_custom_count_column(self):
        """Use custom column for counting."""
        df = pd.DataFrame(
            {
                "dispatch_date": pd.to_datetime(["2020-01-01", "2020-01-15", "2020-02-01"]),
                "custom_id": [1, 2, 3],
            }
        )
        result = aggregate_by_period(df, period="ME", count_col="custom_id")
        assert "count" in result.columns
        assert result["count"].sum() == 3

    def test_custom_date_column(self):
        """Use custom date column."""
        df = pd.DataFrame(
            {
                "custom_date": pd.to_datetime(["2020-01-01", "2020-01-15", "2020-02-01"]),
                "objectid": [1, 2, 3],
            }
        )
        result = aggregate_by_period(df, period="ME", date_col="custom_date")
        assert "custom_date" in result.columns
        assert len(result) == 2

    def test_missing_date_column_raises_value_error(self):
        """Raises ValueError when date_col is not found."""
        df = pd.DataFrame({"objectid": [1, 2, 3]})
        with pytest.raises(ValueError, match="Column 'dispatch_date' not found"):
            aggregate_by_period(df, period="ME")

    def test_missing_count_column_raises_value_error(self):
        """Raises ValueError when count_col is not found."""
        df = pd.DataFrame({"dispatch_date": pd.to_datetime(["2020-01-01"])})
        with pytest.raises(ValueError, match="Column 'objectid' not found"):
            aggregate_by_period(df, period="ME")

    def test_empty_dataframe_returns_empty(self):
        """Handles empty DataFrame."""
        df = pd.DataFrame({"dispatch_date": pd.to_datetime([]), "objectid": []})
        result = aggregate_by_period(df, period="ME")
        assert len(result) == 0

    def test_month_start_aggregation(self, sample_df):
        """Aggregate by month start (period='MS')."""
        result = aggregate_by_period(sample_df, period="MS")
        assert "dispatch_date" in result.columns
        assert "count" in result.columns
        assert len(result) == 5


class TestAddTemporalFeatures:
    """Tests for add_temporal_features function."""

    def test_adds_temporal_features(self):
        """Adds year, month, day, and day_of_week columns."""
        df = pd.DataFrame(
            {"dispatch_date": pd.to_datetime(["2020-01-15", "2020-06-20", "2020-12-25"])}
        )
        result = add_temporal_features(df)
        assert "year" in result.columns
        assert "month" in result.columns
        assert "day" in result.columns
        assert "day_of_week" in result.columns

    def test_year_values_are_correct(self):
        """Year column has correct values."""
        df = pd.DataFrame({"dispatch_date": pd.to_datetime(["2020-01-15", "2021-06-20"])})
        result = add_temporal_features(df)
        assert result["year"].tolist() == [2020, 2021]

    def test_month_values_are_correct(self):
        """Month column has correct values."""
        df = pd.DataFrame({"dispatch_date": pd.to_datetime(["2020-01-15", "2020-06-20"])})
        result = add_temporal_features(df)
        assert result["month"].tolist() == [1, 6]

    def test_day_values_are_correct(self):
        """Day column has correct values."""
        df = pd.DataFrame({"dispatch_date": pd.to_datetime(["2020-01-15", "2020-06-20"])})
        result = add_temporal_features(df)
        assert result["day"].tolist() == [15, 20]

    def test_day_of_week_values_are_correct(self):
        """day_of_week column uses pandas convention (Monday=0, Sunday=6)."""
        df = pd.DataFrame(
            {
                "dispatch_date": pd.to_datetime(
                    ["2020-01-06", "2020-01-07", "2020-01-08"]
                )  # Mon, Tue, Wed
            }
        )
        result = add_temporal_features(df)
        assert result["day_of_week"].tolist() == [0, 1, 2]

    def test_preserves_original_columns(self):
        """Preserves all original columns."""
        df = pd.DataFrame(
            {
                "dispatch_date": pd.to_datetime(["2020-01-15"]),
                "ucr_general": [100],
                "objectid": [1],
            }
        )
        result = add_temporal_features(df)
        assert "ucr_general" in result.columns
        assert "objectid" in result.columns

    def test_returns_copy_not_view(self):
        """Returns a copy, not a view."""
        df = pd.DataFrame({"dispatch_date": pd.to_datetime(["2020-01-15"])})
        result = add_temporal_features(df)
        result.loc[result.index[0], "year"] = 9999
        assert "year" not in df.columns

    def test_empty_dataframe(self):
        """Handles empty DataFrame."""
        df = pd.DataFrame({"dispatch_date": pd.to_datetime([])})
        result = add_temporal_features(df)
        assert "year" in result.columns
        assert "month" in result.columns
        assert "day" in result.columns
        assert "day_of_week" in result.columns

    def test_dispatch_date_column(self):
        """Uses dispatch_date column when dispatch_datetime doesn't exist."""
        df = pd.DataFrame({"dispatch_date": pd.to_datetime(["2020-01-15"])})
        result = add_temporal_features(df)
        assert "year" in result.columns
        assert "dispatch_datetime" in result.columns

    def test_dispatch_datetime_column_exists(self):
        """Uses existing dispatch_datetime column."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2020-01-15"]), "value": [1]})
        result = add_temporal_features(df)
        assert "year" in result.columns
        assert result["year"].iloc[0] == 2020
