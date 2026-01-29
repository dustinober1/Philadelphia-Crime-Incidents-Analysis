"""
Utility functions for Philadelphia Crime Incidents EDA.

Provides data loading, validation, and helper functions for analysis.
"""

import base64
from io import BytesIO
from pathlib import Path

import pandas as pd
import numpy as np

from analysis.config import (
    CRIME_DATA_PATH,
    CLEANED_DATA_PATH,
    LON_MIN,
    LON_MAX,
    LAT_MIN,
    LAT_MAX,
    PHILADELPHIA_BBOX,
    DBSCAN_CONFIG,
)


# =============================================================================
# UCR CODE CLASSIFICATION
# =============================================================================

# FBI UCR (Uniform Crime Reporting) standard classification
VIOLENT_CRIME_UCR = [100, 200, 300, 400]  # Homicide, Rape, Robbery, Aggravated Assault
PROPERTY_CRIME_UCR = [500, 600, 700]      # Burglary, Theft, Motor Vehicle Theft

UCR_CATEGORY_NAMES = {
    100: "Homicide",
    200: "Rape",
    300: "Robbery",
    400: "Aggravated Assault",
    500: "Burglary",
    600: "Theft/Larceny",
    700: "Motor Vehicle Theft",
}


def load_data(clean: bool = False) -> pd.DataFrame:
    """
    Load the crime incidents dataset.

    Args:
        clean: If True, load cleaned data; if False, load raw data.

    Returns:
        DataFrame with crime incidents data.
    """
    path = CLEANED_DATA_PATH if clean else CRIME_DATA_PATH

    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    df = pd.read_parquet(path)

    # Ensure datetime columns are properly parsed
    if "dispatch_date" in df.columns:
        df["dispatch_date"] = pd.to_datetime(df["dispatch_date"], errors="coerce")

    if "dispatch_datetime" not in df.columns and "dispatch_date" in df.columns:
        # Create datetime if not exists
        df["dispatch_datetime"] = df["dispatch_date"]

    return df


def validate_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and flag coordinate data.

    Adds columns indicating whether coordinates are valid.

    Args:
        df: DataFrame with point_x (longitude) and point_y (latitude) columns.

    Returns:
        DataFrame with added coordinate validation columns.
    """
    df = df.copy()

    # Initialize validation flags
    df["valid_coord"] = False
    df["coord_issue"] = None

    # Check for coordinate columns
    has_x = "point_x" in df.columns
    has_y = "point_y" in df.columns

    if has_x and has_y:
        # Valid coordinates: within Philadelphia bbox and no NaN
        valid_mask = (
            df["point_x"].notna()
            & df["point_y"].notna()
            & (df["point_x"] >= LON_MIN)
            & (df["point_x"] <= LON_MAX)
            & (df["point_y"] >= LAT_MIN)
            & (df["point_y"] <= LAT_MAX)
        )
        df.loc[valid_mask, "valid_coord"] = True

        # Categorize issues
        missing_mask = df["point_x"].isna() | df["point_y"].isna()
        df.loc[missing_mask, "coord_issue"] = "missing"

        # Invalid longitude (common issue: positive values)
        invalid_lon = (
            df["point_x"].notna()
            & ((df["point_x"] < LON_MIN) | (df["point_x"] > LON_MAX))
        )
        df.loc[invalid_lon, "coord_issue"] = "invalid_longitude"

        # Invalid latitude
        invalid_lat = (
            df["point_y"].notna()
            & ((df["point_y"] < LAT_MIN) | (df["point_y"] > LAT_MAX))
        )
        df.loc[invalid_lat & ~invalid_lon, "coord_issue"] = "invalid_latitude"

    return df


def classify_crime_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add crime_category column classifying crimes as 'Violent', 'Property', or 'Other'.

    Based on FBI UCR (Uniform Crime Reporting) standard classification:
    - Violent Crimes (UCR 100-499): Homicide, Rape, Robbery, Aggravated Assault
    - Property Crimes (UCR 500-799): Burglary, Theft, Motor Vehicle Theft
    - Other (UCR 800+): All other offenses

    Args:
        df: DataFrame with ucr_general column.

    Returns:
        DataFrame with added crime_category column.
    """
    df = df.copy()
    df["crime_category"] = "Other"
    df.loc[df["ucr_general"].isin(VIOLENT_CRIME_UCR), "crime_category"] = "Violent"
    df.loc[df["ucr_general"].isin(PROPERTY_CRIME_UCR), "crime_category"] = "Property"
    return df


def extract_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract temporal features from datetime column.

    Adds year, month, day of week, hour, etc.

    Args:
        df: DataFrame with dispatch_datetime column.

    Returns:
        DataFrame with added temporal features.
    """
    df = df.copy()

    if "dispatch_datetime" not in df.columns:
        if "dispatch_date" in df.columns:
            df["dispatch_datetime"] = pd.to_datetime(df["dispatch_date"])
        else:
            return df

    dt = df["dispatch_datetime"].dt

    # Basic temporal features
    df["year"] = dt.year
    df["month"] = dt.month
    df["day"] = dt.day
    df["day_of_week"] = dt.dayofweek  # 0=Monday, 6=Sunday
    df["day_name"] = dt.day_name()
    df["hour"] = dt.hour
    df["month_name"] = dt.month_name()

    # Derived features
    df["is_weekend"] = df["day_of_week"].isin([5, 6])

    # Time of day categories
    df["time_period"] = pd.cut(
        df["hour"],
        bins=[-1, 6, 12, 18, 24],
        labels=["Overnight (12am-6am)", "Morning (6am-12pm)", "Afternoon (12pm-6pm)", "Evening (6pm-12am)"]
    )

    # Season
    df["season"] = pd.cut(
        df["month"],
        bins=[0, 3, 6, 9, 12],
        labels=["Winter", "Spring", "Summer", "Fall"]
    )

    # Year-month for trend analysis
    df["year_month"] = df["dispatch_datetime"].dt.to_period("M")

    return df


def get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a summary of missing data.

    Args:
        df: DataFrame to analyze.

    Returns:
        DataFrame with missing count and percentage for each column.
    """
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)

    summary = pd.DataFrame({
        "column": df.columns,
        "missing_count": missing.values,
        "missing_percentage": missing_pct.values,
        "dtype": df.dtypes.values,
    })

    summary = summary[summary["missing_count"] > 0].sort_values("missing_count", ascending=False)

    return summary


def image_to_base64(fig) -> str:
    """
    Convert a matplotlib figure to base64 encoded string.

    Args:
        fig: matplotlib figure object.

    Returns:
        Base64 encoded string of the figure image.
    """
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    return img_str


def create_image_tag(base64_str: str, alt: str = "", width: int = 800) -> str:
    """
    Create an HTML img tag with base64 encoded image.

    Args:
        base64_str: Base64 encoded image string.
        alt: Alt text for the image.
        width: Display width in pixels.

    Returns:
        HTML img tag as string.
    """
    return f'<img src="data:image/png;base64,{base64_str}" alt="{alt}" width="{width}">'


def format_number(num: int | float) -> str:
    """
    Format a number with thousands separators.

    Args:
        num: Number to format.

    Returns:
        Formatted number string.
    """
    if isinstance(num, float):
        return f"{num:,.2f}"
    return f"{num:,}"


def get_top_n(df: pd.DataFrame, column: str, n: int = 10) -> pd.DataFrame:
    """
    Get top N values by count for a column.

    Args:
        df: DataFrame to analyze.
        column: Column name to count.
        n: Number of top values to return.

    Returns:
        DataFrame with top N values and counts.
    """
    top = df[column].value_counts().head(n)
    result = pd.DataFrame({
        column: top.index,
        "count": top.values,
        "percentage": (top.values / len(df) * 100).round(2)
    })
    return result


def create_comparison_df(before: pd.DataFrame, after: pd.DataFrame, label_before: str = "Before", label_after: str = "After") -> pd.DataFrame:
    """
    Create a comparison DataFrame for before/after analysis.

    Args:
        before: DataFrame before changes.
        after: DataFrame after changes.
        label_before: Label for before column.
        label_after: Label for after column.

    Returns:
        Comparison DataFrame.
    """
    comparison = pd.DataFrame({
        "Metric": ["Total Records", "Columns", "Missing Coordinates (%)"],
        label_before: [
            len(before),
            len(before.columns),
            (before["point_x"].isna().sum() / len(before) * 100).round(2) if "point_x" in before.columns else 0
        ],
        label_after: [
            len(after),
            len(after.columns),
            (after["point_x"].isna().sum() / len(after) * 100).round(2) if "point_x" in after.columns else 0
        ],
    })
    return comparison


# =============================================================================
# CLUSTERING UTILITIES (for Red Zones Analysis)
# =============================================================================

def haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.

    Args:
        lon1, lat1: Longitude and latitude of first point (decimal degrees).
        lon2, lat2: Longitude and latitude of second point (decimal degrees).

    Returns:
        Distance in meters.
    """
    from math import radians, cos, sin, asin, sqrt

    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))

    # Radius of Earth in meters
    r = 6371000
    return c * r


def dbscan_clustering(
    df: pd.DataFrame,
    eps_meters: int | None = None,
    min_samples: int | None = None,
    sample_size: int | None = None,
) -> tuple[pd.DataFrame, np.ndarray]:
    """
    Perform DBSCAN clustering on geographic coordinates using Haversine distance.

    Args:
        df: DataFrame with point_x (longitude) and point_y (latitude) columns.
        eps_meters: Maximum distance between points in same cluster (meters).
                   Defaults to DBSCAN_CONFIG["eps_meters"].
        min_samples: Minimum samples for a core point.
                     Defaults to DBSCAN_CONFIG["min_samples"].
        sample_size: Maximum number of points to cluster (for performance).
                     If None, uses all data. If specified, randomly samples.

    Returns:
        Tuple of (clustered_df, cluster_labels):
        - clustered_df: DataFrame with cluster labels added
        - cluster_labels: Array of cluster labels (-1 = noise)
    """
    from sklearn.cluster import DBSCAN

    # Use config defaults if not specified
    if eps_meters is None:
        eps_meters = DBSCAN_CONFIG["eps_meters"]
    if min_samples is None:
        min_samples = DBSCAN_CONFIG["min_samples"]

    # Filter to valid coordinates
    df = df[df["valid_coord"]].copy()

    # Sample if needed for performance
    if sample_size and len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=42)

    # Convert coordinates to radians for Haversine distance
    coords = df[["point_x", "point_y"]].values
    coords_rad = np.radians(coords)

    # Convert eps to radians (Earth radius ~6371km)
    eps_rad = eps_meters / 6371000

    # Run DBSCAN with Haversine metric
    db = DBSCAN(eps=eps_rad, min_samples=min_samples, metric="haversine", n_jobs=-1)
    cluster_labels = db.fit_predict(coords_rad)

    # Add labels to dataframe
    df = df.copy()
    df["cluster"] = cluster_labels

    return df, cluster_labels


def calculate_cluster_centroids(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate centroid coordinates and statistics for each cluster.

    Args:
        df: DataFrame with cluster, point_x, point_y columns.

    Returns:
        DataFrame with cluster_id, centroid_lon, centroid_lat, count.
    """
    # Exclude noise points (cluster = -1)
    clustered = df[df["cluster"] >= 0].copy()

    if len(clustered) == 0:
        return pd.DataFrame(columns=["cluster_id", "centroid_lon", "centroid_lat", "count"])

    # Calculate centroids (mean coordinates)
    centroids = clustered.groupby("cluster").agg({
        "point_x": "mean",
        "point_y": "mean",
        "cluster": "count"
    }).rename(columns={"point_x": "centroid_lon", "point_y": "centroid_lat", "cluster": "count"})

    centroids = centroids.reset_index().rename(columns={"cluster": "cluster_id"})
    centroids = centroids.sort_values("count", ascending=False)

    return centroids


def calculate_cluster_stats(
    df: pd.DataFrame,
    centroids: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate detailed statistics for each cluster.

    Args:
        df: DataFrame with cluster, point_x, point_y, text_general_code, dc_dist, hour columns.
        centroids: DataFrame from calculate_cluster_centroids().

    Returns:
        DataFrame with cluster_id, centroid_lon, centroid_lat, count, top_crime_type,
        top_district, peak_hour, radius_meters.
    """
    results = []

    for _, row in centroids.iterrows():
        cluster_id = row["cluster_id"]
        cluster_data = df[df["cluster"] == cluster_id]

        # Top crime type
        top_crime = cluster_data["text_general_code"].value_counts().idxmax()
        top_crime_count = cluster_data["text_general_code"].value_counts().max()
        top_crime_pct = (top_crime_count / len(cluster_data) * 100)

        # Top district
        if "dc_dist" in cluster_data.columns:
            top_district = cluster_data["dc_dist"].value_counts().idxmax()
        else:
            top_district = None

        # Peak hour (if available)
        if "hour" in cluster_data.columns:
            peak_hour = cluster_data["hour"].value_counts().idxmax()
        else:
            peak_hour = None

        # Calculate approximate radius (distance from centroid to farthest point)
        centroid_lon = row["centroid_lon"]
        centroid_lat = row["centroid_lat"]
        max_dist = cluster_data.apply(
            lambda r: haversine_distance(centroid_lon, centroid_lat, r["point_x"], r["point_y"]),
            axis=1
        ).max()

        results.append({
            "cluster_id": cluster_id,
            "centroid_lon": centroid_lon,
            "centroid_lat": centroid_lat,
            "count": row["count"],
            "top_crime_type": top_crime,
            "top_crime_pct": top_crime_pct,
            "top_district": top_district,
            "peak_hour": peak_hour,
            "radius_meters": max_dist,
        })

    return pd.DataFrame(results)
