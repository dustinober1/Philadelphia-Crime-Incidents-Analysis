"""Shared analysis utilities for Phase 1 notebooks."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

from analysis.config import CRIME_DATA_PATH

CRIME_CATEGORY_MAP: Dict[str, set[int]] = {
    "Violent": {100, 200},
    "Property": {300, 400, 500},
}


def load_data(clean: bool = True) -> pd.DataFrame:
    """Load the crime incidents dataset.

    Parameters
    ----------
    clean : bool, default True
        Whether to drop rows missing dispatch_date after parsing.

    Returns
    -------
    pandas.DataFrame
        Crime incidents with dispatch_date parsed as datetime.
    """
    if not CRIME_DATA_PATH.exists():
        raise FileNotFoundError(f"Crime data not found: {CRIME_DATA_PATH}")

    df = pd.read_parquet(Path(CRIME_DATA_PATH))

    if "dispatch_date" in df.columns:
        if df["dispatch_date"].dtype.name == "category":
            df["dispatch_date"] = pd.to_datetime(
                df["dispatch_date"].astype(str), errors="coerce"
            )
        elif not pd.api.types.is_datetime64_any_dtype(df["dispatch_date"]):
            df["dispatch_date"] = pd.to_datetime(df["dispatch_date"], errors="coerce")

    if clean and "dispatch_date" in df.columns:
        df = df.dropna(subset=["dispatch_date"])

    return df


def classify_crime_category(df: pd.DataFrame) -> pd.DataFrame:
    """Classify crimes into Violent, Property, or Other.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset containing a ``ucr_general`` column.

    Returns
    -------
    pandas.DataFrame
        DataFrame with a ``crime_category`` column added.
    """
    if "ucr_general" not in df.columns:
        raise ValueError("Expected 'ucr_general' column for classification")

    df = df.copy()
    ucr_series = pd.to_numeric(df["ucr_general"], errors="coerce")
    ucr_group = (ucr_series // 100).astype("Int64")

    df["crime_category"] = "Other"
    for category, groups in CRIME_CATEGORY_MAP.items():
        df.loc[ucr_group.isin(groups), "crime_category"] = category

    return df


def extract_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract temporal features from dispatch timestamps.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset containing a dispatch timestamp.

    Returns
    -------
    pandas.DataFrame
        DataFrame with year, month, day, and day_of_week columns added.
    """
    df = df.copy()

    if "dispatch_datetime" not in df.columns:
        if "dispatch_date" in df.columns:
            df["dispatch_datetime"] = pd.to_datetime(
                df["dispatch_date"], errors="coerce"
            )
        else:
            return df

    dt = df["dispatch_datetime"].dt
    df["year"] = dt.year
    df["month"] = dt.month
    df["day"] = dt.day
    df["day_of_week"] = dt.dayofweek

    return df
