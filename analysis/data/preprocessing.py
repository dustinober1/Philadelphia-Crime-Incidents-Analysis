"""Data preprocessing utilities for crime incident analysis.

This module provides common data transformation functions:
- Date range filtering
- Temporal aggregation
- Temporal feature extraction

Example:
    >>> from analysis.data import load_crime_data, filter_by_date_range, aggregate_by_period
    >>> df = load_crime_data()
    >>> df_2020 = filter_by_date_range(df, "2020-01-01", "2020-12-31")
    >>> monthly = aggregate_by_period(df_2020, period="ME")
"""

from __future__ import annotations

from typing import Literal

import pandas as pd

from analysis.utils.temporal import extract_temporal_features


def filter_by_date_range(
    df: pd.DataFrame,
    start: str | None = None,
    end: str | None = None,
    date_col: str = "dispatch_date",
) -> pd.DataFrame:
    """Filter DataFrame by date range.

    This function filters a DataFrame to only include rows within the
    specified date range. Dates are parsed using pandas.to_datetime.

    Args:
        df: Input DataFrame with datetime column.
        start: Start date (ISO format string, e.g., '2020-01-01').
        end: End date (ISO format string, e.g., '2023-12-31').
        date_col: Name of datetime column. Default is "dispatch_date".

    Returns:
        Filtered DataFrame with rows in the specified date range.

    Raises:
        ValueError: If date_col is not found in DataFrame.

    Example:
        >>> from analysis.data import load_crime_data, filter_by_date_range
        >>> df = load_crime_data()
        >>> df_2020 = filter_by_date_range(df, "2020-01-01", "2020-12-31")
        >>> print(f"Filtered to {len(df_2020)} rows in 2020")
    """
    result = df.copy()

    if date_col not in result.columns:
        raise ValueError(f"Column '{date_col}' not found in DataFrame")

    if start is not None:
        result = result[result[date_col] >= pd.to_datetime(start)]

    if end is not None:
        result = result[result[date_col] <= pd.to_datetime(end)]

    return result


def aggregate_by_period(
    df: pd.DataFrame,
    period: Literal["D", "W", "ME", "MS", "QE", "QS", "YE", "YS"] = "ME",
    count_col: str = "objectid",
    date_col: str = "dispatch_date",
) -> pd.DataFrame:
    """Aggregate crime counts by time period.

    This function groups and counts incidents by a time period.
    Valid periods are:
    - 'D': Daily
    - 'W': Weekly
    - 'ME': Month end (default)
    - 'MS': Month start
    - 'QE': Quarter end
    - 'QE': Quarter start
    - 'YE': Year end
    - 'YS': Year start

    Note: Use 'ME' for month end (not 'M' which is deprecated in pandas 2.2+).

    Args:
        df: Input DataFrame with datetime column.
        period: Pandas resample period. Default is "ME" (month end).
        count_col: Column to count (default: objectid).
        date_col: Datetime column to group by. Default is "dispatch_date".

    Returns:
        DataFrame with period index and count column.

    Raises:
        ValueError: If date_col or count_col is not found in DataFrame.

    Example:
        >>> from analysis.data import load_crime_data, aggregate_by_period
        >>> df = load_crime_data()
        >>> monthly = aggregate_by_period(df, "ME")
        >>> print(monthly.head())
           dispatch_date  count
        0    2006-01-31    123
        1    2006-02-28    456
    """
    if date_col not in df.columns:
        raise ValueError(f"Column '{date_col}' not found in DataFrame")
    if count_col not in df.columns:
        raise ValueError(f"Column '{count_col}' not found in DataFrame")

    # Make a copy and set index
    df_copy = df.set_index(date_col)

    # Resample and count
    counts = df_copy.resample(period)[count_col].count().reset_index()
    counts.columns = [date_col, "count"]

    return counts


def add_temporal_features(df: pd.DataFrame, date_col: str = "dispatch_date") -> pd.DataFrame:
    """Extract temporal features from datetime column.

    This is a wrapper around analysis.utils.temporal.extract_temporal_features
    for convenience when using the data layer.

    Args:
        df: Input DataFrame with datetime column.
        date_col: Name of datetime column. Default is "dispatch_date".

    Returns:
        DataFrame with temporal features added (year, month, day, day_of_week).

    Example:
        >>> from analysis.data import load_crime_data, add_temporal_features
        >>> df = load_crime_data()
        >>> df = add_temporal_features(df)
        >>> print(df[["year", "month", "day_of_week"]].head())
    """
    return extract_temporal_features(df)


__all__ = [
    "filter_by_date_range",
    "aggregate_by_period",
    "add_temporal_features",
]
