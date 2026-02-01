"""
Data loading with Streamlit caching for the Philadelphia Crime Incidents dashboard.

Implements aggressive caching strategy to handle 3.5M-row Parquet dataset
with sub-5-second load times.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from analysis.config import CRIME_DATA_PATH
from analysis.utils import load_data, validate_coordinates, extract_temporal_features
from dashboard.config import CACHE_CONFIG


@st.cache_data(
    ttl=CACHE_CONFIG["data_ttl"],
    max_entries=CACHE_CONFIG["data_max_entries"],
    show_spinner="Loading crime data (3.5M rows, first load takes ~10s)...",
)
def load_crime_data(include_2026: bool = False) -> pd.DataFrame:
    """
    Load the full crime incidents dataset with caching.

    This function is cached by Streamlit. First call loads Parquet from disk
    (~10 seconds), subsequent calls return cached data instantly.

    Args:
        include_2026: If False, exclude 2026 data (incomplete year).
                      Default False to match analysis standards.

    Returns:
        DataFrame with validated coordinates and temporal features extracted.

    Example:
        >>> df = load_crime_data()
        >>> len(df)
        3490000+
    """
    # Load raw data using existing utility
    df = load_data(clean=False)

    # Exclude 2026 if requested (incomplete year)
    if not include_2026 and "dispatch_date" in df.columns:
        df = df[df["dispatch_date"].dt.year < 2026].copy()

    # Validate coordinates (adds valid_coord flag)
    df = validate_coordinates(df)

    # Extract temporal features (adds year, month, day, hour, etc.)
    df = extract_temporal_features(df)

    # Add crime category classification
    from analysis.utils import classify_crime_category
    df = classify_crime_category(df)

    return df


@st.cache_data(
    ttl=CACHE_CONFIG["filter_ttl"],
    max_entries=CACHE_CONFIG["filter_max_entries"],
    show_spinner="Applying filters...",
)
def apply_filters(
    df: pd.DataFrame,
    start_date: str | None = None,
    end_date: str | None = None,
    districts: list[int] | None = None,
    crime_categories: list[str] | None = None,
    crime_types: list[str] | None = None,
) -> pd.DataFrame:
    """
    Apply filters to the crime dataset with caching.

    Each unique filter combination creates a cache entry. Results are cached
    to avoid recomputing the same filtered view.

    Args:
        df: Full crime dataset (from load_crime_data).
        start_date: Start date filter (YYYY-MM-DD format or None for no filter).
        end_date: End date filter (YYYY-MM-DD format or None for no filter).
        districts: List of police districts to include (None for all).
        crime_categories: List of crime categories to include (None for all).
        crime_types: List of specific crime types to include (None for all).

    Returns:
        Filtered DataFrame.

    Example:
        >>> df = load_crime_data()
        >>> filtered = apply_filters(df, start_date="2020-01-01", districts=[1, 2, 3])
        >>> len(filtered)
        # Returns count for districts 1-3 from 2020 onwards
    """
    result = df.copy()

    # Date range filter - handle categorical date columns
    if "dispatch_date" in result.columns:
        # Convert to datetime for comparison (handles categorical columns)
        result["_dispatch_date_dt"] = pd.to_datetime(result["dispatch_date"], errors="coerce")

        if start_date is not None:
            start_dt = pd.to_datetime(start_date)
            result = result[result["_dispatch_date_dt"] >= start_dt].copy()

        if end_date is not None:
            end_dt = pd.to_datetime(end_date)
            result = result[result["_dispatch_date_dt"] <= end_dt].copy()

        # Drop temporary column
        result = result.drop(columns=["_dispatch_date_dt"])

    # District filter
    if districts is not None and "dc_dist" in result.columns:
        # Handle district values that may be strings or floats
        result = result[result["dc_dist"].isin(districts)].copy()

    # Crime category filter
    if crime_categories is not None and "crime_category" in result.columns:
        result = result[result["crime_category"].isin(crime_categories)].copy()

    # Crime type filter (specific crime types)
    if crime_types is not None and "text_general_code" in result.columns:
        result = result[result["text_general_code"].isin(crime_types)].copy()

    return result


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Generate summary statistics for the dataset.

    Args:
        df: Crime dataset (full or filtered).

    Returns:
        Dict with summary statistics: total_records, date_range, districts,
        crime_types, coord_coverage.
    """
    summary = {
        "total_records": len(df),
    }

    # Date range
    if "dispatch_date" in df.columns:
        # Handle categorical date columns (known gotcha)
        dates = pd.to_datetime(df["dispatch_date"], errors="coerce")
        summary["date_range"] = (
            dates.min().strftime("%Y-%m-%d"),
            dates.max().strftime("%Y-%m-%d"),
        )
        summary["years"] = dates.dt.year.nunique()

    # Districts
    if "dc_dist" in df.columns:
        summary["districts"] = df["dc_dist"].nunique()

    # Crime categories
    if "crime_category" in df.columns:
        summary["crime_categories"] = df["crime_category"].value_counts().to_dict()

    # Coordinate coverage
    if "valid_coord" in df.columns:
        coord_valid = df["valid_coord"].sum()
        coord_pct = (coord_valid / len(df) * 100) if len(df) > 0 else 0
        summary["coord_coverage"] = {
            "valid": int(coord_valid),
            "total": len(df),
            "percentage": round(coord_pct, 2),
        }

    return summary


@st.cache_data(show_spinner="Loading pre-computed reports...")
def load_cached_report(report_path: str) -> str | None:
    """
    Load a pre-generated markdown report for embedding.

    Used to embed existing analysis reports without re-running expensive
    computations.

    Args:
        report_path: Path to the markdown report file.

    Returns:
        Report content as string, or None if file not found.
    """
    path = Path(report_path)
    if not path.exists():
        return None

    return path.read_text()
