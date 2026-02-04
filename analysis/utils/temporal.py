"""Temporal feature extraction utilities.

This module provides functions for extracting temporal features from
timestamp data for crime analysis.
"""

from __future__ import annotations

import pandas as pd


def extract_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract temporal features from dispatch timestamps.

    This function extracts year, month, day, and day_of_week features
    from a datetime column. If ``dispatch_datetime`` column exists,
    it is used directly. If only ``dispatch_date`` exists, it is
    converted to datetime. If neither exists, the DataFrame is returned
    unchanged.

    Args:
        df: Dataset containing a dispatch timestamp column
            (``dispatch_datetime`` or ``dispatch_date``).

    Returns:
        DataFrame with ``year``, ``month``, ``day``, and ``day_of_week``
        columns added. The ``day_of_week`` column uses pandas convention
        where Monday=0 and Sunday=6.

    Notes:
        - If ``dispatch_datetime`` does not exist but ``dispatch_date`` does,
          the function creates ``dispatch_datetime`` from ``dispatch_date``.
        - If neither column exists, the DataFrame is returned unchanged.
        - All extractions use pandas ``dt`` accessor for datetime properties.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "dispatch_date": ["2023-01-15", "2023-02-20", "2023-03-25"]
        ... })
        >>> result = extract_temporal_features(df)
        >>> result[["year", "month", "day", "day_of_week"]].values.tolist()
        [[2023, 1, 15, 6], [2023, 2, 20, 0], [2023, 3, 25, 5]]
    """
    df = df.copy()

    if "dispatch_datetime" not in df.columns:
        if "dispatch_date" in df.columns:
            df["dispatch_datetime"] = pd.to_datetime(df["dispatch_date"], errors="coerce")
        else:
            return df

    dt = df["dispatch_datetime"].dt
    df["year"] = dt.year
    df["month"] = dt.month
    df["day"] = dt.day
    df["day_of_week"] = dt.dayofweek

    return df
