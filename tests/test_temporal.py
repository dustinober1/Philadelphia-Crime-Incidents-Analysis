"""Tests for temporal feature extraction utilities."""

import pandas as pd
import pytest

from analysis.utils.temporal import extract_temporal_features


class TestExtractTemporalFeatures:
    """Tests for extract_temporal_features function."""

    def test_with_dispatch_datetime_column(self):
        """Extracts features when dispatch_datetime column exists."""
        df = pd.DataFrame(
            {
                "dispatch_datetime": pd.to_datetime(
                    [
                        "2023-01-15 10:30:00",
                        "2023-02-20 14:45:00",
                        "2023-03-25 08:15:00",
                    ]
                )
            }
        )
        result = extract_temporal_features(df)
        assert "year" in result.columns
        assert "month" in result.columns
        assert "day" in result.columns
        assert "day_of_week" in result.columns
        assert result["year"].tolist() == [2023, 2023, 2023]
        assert result["month"].tolist() == [1, 2, 3]
        assert result["day"].tolist() == [15, 20, 25]

    def test_with_dispatch_date_column(self):
        """Extracts features when dispatch_date column exists (creates dispatch_datetime)."""
        df = pd.DataFrame({"dispatch_date": ["2023-01-15", "2023-02-20", "2023-03-25"]})
        result = extract_temporal_features(df)
        assert "dispatch_datetime" in result.columns
        assert "year" in result.columns
        assert "month" in result.columns
        assert "day" in result.columns
        assert "day_of_week" in result.columns
        # Sunday=6, Monday=0, Saturday=5
        assert result["day_of_week"].tolist() == [6, 0, 5]

    def test_year_is_integer(self):
        """Year column contains integer values."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-05-10"])})
        result = extract_temporal_features(df)
        assert result["year"].dtype == "int64" or result["year"].dtype == "int32"

    def test_month_is_integer(self):
        """Month column contains integer values."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-05-10"])})
        result = extract_temporal_features(df)
        assert result["month"].dtype == "int64" or result["month"].dtype == "int32"
        assert result["month"].iloc[0] == 5

    def test_day_is_integer(self):
        """Day column contains integer values."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-05-10"])})
        result = extract_temporal_features(df)
        assert result["day"].dtype == "int64" or result["day"].dtype == "int32"
        assert result["day"].iloc[0] == 10

    def test_day_of_week_is_integer(self):
        """Day_of_week column contains integer values (Monday=0, Sunday=6)."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-01-02"])})  # Monday
        result = extract_temporal_features(df)
        assert result["day_of_week"].dtype == "int64" or result["day_of_week"].dtype == "int32"
        assert result["day_of_week"].iloc[0] == 0  # Monday

    def test_day_of_week_monday(self):
        """Monday has day_of_week=0."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-01-02"])})
        result = extract_temporal_features(df)
        assert result["day_of_week"].iloc[0] == 0

    def test_day_of_week_tuesday(self):
        """Tuesday has day_of_week=1."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-01-03"])})
        result = extract_temporal_features(df)
        assert result["day_of_week"].iloc[0] == 1

    def test_day_of_week_wednesday(self):
        """Wednesday has day_of_week=2."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-01-04"])})
        result = extract_temporal_features(df)
        assert result["day_of_week"].iloc[0] == 2

    def test_day_of_week_thursday(self):
        """Thursday has day_of_week=3."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-01-05"])})
        result = extract_temporal_features(df)
        assert result["day_of_week"].iloc[0] == 3

    def test_day_of_week_friday(self):
        """Friday has day_of_week=4."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-01-06"])})
        result = extract_temporal_features(df)
        assert result["day_of_week"].iloc[0] == 4

    def test_day_of_week_saturday(self):
        """Saturday has day_of_week=5."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-01-07"])})
        result = extract_temporal_features(df)
        assert result["day_of_week"].iloc[0] == 5

    def test_day_of_week_sunday(self):
        """Sunday has day_of_week=6."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-01-01"])})
        result = extract_temporal_features(df)
        assert result["day_of_week"].iloc[0] == 6

    def test_leap_year_date(self):
        """Handles leap year date (February 29)."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2024-02-29"])})
        result = extract_temporal_features(df)
        assert result["month"].iloc[0] == 2
        assert result["day"].iloc[0] == 29

    def test_year_boundary_end_of_year(self):
        """Handles year boundary (December 31)."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-12-31"])})
        result = extract_temporal_features(df)
        assert result["year"].iloc[0] == 2023
        assert result["month"].iloc[0] == 12
        assert result["day"].iloc[0] == 31

    def test_year_boundary_start_of_year(self):
        """Handles year boundary (January 1)."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2024-01-01"])})
        result = extract_temporal_features(df)
        assert result["year"].iloc[0] == 2024
        assert result["month"].iloc[0] == 1
        assert result["day"].iloc[0] == 1

    def test_midnight_timestamp(self):
        """Handles midnight timestamp (00:00:00)."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-05-10 00:00:00"])})
        result = extract_temporal_features(df)
        assert result["year"].iloc[0] == 2023
        assert result["month"].iloc[0] == 5
        assert result["day"].iloc[0] == 10

    def test_end_of_day_timestamp(self):
        """Handles end of day timestamp (23:59:59)."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-05-10 23:59:59"])})
        result = extract_temporal_features(df)
        assert result["year"].iloc[0] == 2023
        assert result["month"].iloc[0] == 5
        assert result["day"].iloc[0] == 10

    def test_no_datetime_columns_returns_unchanged(self):
        """Returns DataFrame unchanged when no datetime columns exist."""
        df = pd.DataFrame({"other_column": [1, 2, 3]})
        result = extract_temporal_features(df)
        assert "year" not in result.columns
        assert "month" not in result.columns
        assert "day" not in result.columns
        assert "day_of_week" not in result.columns
        assert result.equals(df)

    def test_nan_datetime_handling(self):
        """Handles NaN in datetime column."""
        df = pd.DataFrame(
            {
                "dispatch_datetime": pd.to_datetime(
                    [
                        "2023-01-15",
                        None,
                        "2023-03-25",
                    ]
                )
            }
        )
        result = extract_temporal_features(df)
        assert "year" in result.columns
        assert pd.isna(result["year"].iloc[1])
        assert result["year"].iloc[0] == 2023
        assert result["year"].iloc[2] == 2023

    def test_returns_dataframe(self):
        """Returns a DataFrame."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-01-15"])})
        result = extract_temporal_features(df)
        assert isinstance(result, pd.DataFrame)

    def test_returns_copy(self):
        """Returns a copy, not a view."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-01-15"])})
        result = extract_temporal_features(df)
        result.loc[result.index[0], "year"] = 9999
        assert "year" not in df.columns

    def test_preserves_original_columns(self):
        """Preserves all original columns."""
        df = pd.DataFrame(
            {
                "dispatch_datetime": pd.to_datetime(["2023-01-15", "2023-02-20"]),
                "incident_id": ["ABC", "DEF"],
            }
        )
        result = extract_temporal_features(df)
        assert "incident_id" in result.columns
        assert result["incident_id"].tolist() == ["ABC", "DEF"]

    def test_empty_dataframe(self):
        """Handles empty DataFrame."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime([])})
        result = extract_temporal_features(df)
        assert len(result) == 0
        assert "year" in result.columns
        assert "month" in result.columns
        assert "day" in result.columns
        assert "day_of_week" in result.columns

    def test_single_row(self):
        """Handles single row DataFrame."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-05-10"])})
        result = extract_temporal_features(df)
        assert len(result) == 1
        assert result["year"].iloc[0] == 2023
        assert result["month"].iloc[0] == 5
        assert result["day"].iloc[0] == 10

    def test_multiple_dates(self):
        """Handles multiple dates correctly."""
        df = pd.DataFrame(
            {
                "dispatch_datetime": pd.to_datetime(
                    [
                        "2023-01-15",
                        "2023-02-20",
                        "2023-03-25",
                    ]
                )
            }
        )
        result = extract_temporal_features(df)
        expected = [[2023, 1, 15, 6], [2023, 2, 20, 0], [2023, 3, 25, 5]]
        assert result[["year", "month", "day", "day_of_week"]].values.tolist() == expected

    def test_dispatch_datetime_column_has_priority(self):
        """dispatch_datetime column is used if both dispatch_datetime and dispatch_date exist."""
        df = pd.DataFrame(
            {
                "dispatch_datetime": pd.to_datetime(["2023-01-15"]),
                "dispatch_date": ["2022-01-01"],  # Different date, should be ignored
            }
        )
        result = extract_temporal_features(df)
        assert result["year"].iloc[0] == 2023  # From dispatch_datetime
        assert result["month"].iloc[0] == 1
        assert result["day"].iloc[0] == 15

    @pytest.mark.parametrize(
        "date_str,expected_year,expected_month,expected_day,expected_dow",
        [
            ("2023-01-01", 2023, 1, 1, 6),  # Sunday
            ("2023-02-14", 2023, 2, 14, 1),  # Tuesday
            ("2023-07-04", 2023, 7, 4, 1),  # Tuesday
            ("2023-12-25", 2023, 12, 25, 0),  # Monday
        ],
    )
    def test_various_dates(
        self, date_str, expected_year, expected_month, expected_day, expected_dow
    ):
        """Parametrized test for various dates."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime([date_str])})
        result = extract_temporal_features(df)
        assert result["year"].iloc[0] == expected_year
        assert result["month"].iloc[0] == expected_month
        assert result["day"].iloc[0] == expected_day
        assert result["day_of_week"].iloc[0] == expected_dow

    def test_preserves_dispatch_datetime_column(self):
        """Preserves dispatch_datetime column in result."""
        df = pd.DataFrame({"dispatch_datetime": pd.to_datetime(["2023-05-10"])})
        result = extract_temporal_features(df)
        assert "dispatch_datetime" in result.columns
