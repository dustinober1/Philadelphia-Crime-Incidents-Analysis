"""Spatial utility functions for geographic analysis.

This module provides functions for:
- Coordinate cleaning and validation
- Loading boundary files
- Spatial joins between crime points and geographic boundaries
- Severity score calculation
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from analysis.config import (
    PHILLY_LAT_MAX,
    PHILLY_LAT_MIN,
    PHILLY_LON_MAX,
    PHILLY_LON_MIN,
    SEVERITY_WEIGHTS,
)


def get_repo_root() -> Path:
    """Get the repository root directory.

    Returns:
        Path to the repository root directory.
    """
    return Path(__file__).resolve().parent.parent.parent


def clean_coordinates(
    df: pd.DataFrame,
    x_col: str = "point_x",
    y_col: str = "point_y",
) -> pd.DataFrame:
    """Filter DataFrame to valid WGS84 coordinates for Philadelphia.

    Args:
        df: DataFrame with coordinate columns.
        x_col: Column name for longitude (x coordinate). Default is "point_x".
        y_col: Column name for latitude (y coordinate). Default is "point_y".

    Returns:
        DataFrame filtered to valid Philadelphia coordinates.

    Raises:
        ValueError: If coordinate columns are not found in DataFrame.

    Notes:
        Philadelphia bounds (approximate):
        - Longitude: -75.30 to -74.95
        - Latitude: 39.85 to 40.15

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"point_x": [-75.2, -75.5], "point_y": [40.0, 40.0]})
        >>> result = clean_coordinates(df)
        >>> len(result)
        1
    """
    # Ensure columns exist
    if x_col not in df.columns or y_col not in df.columns:
        raise ValueError(f"Columns {x_col} and/or {y_col} not found in DataFrame")

    # Create mask for valid coordinates
    mask = (
        df[x_col].notna()
        & df[y_col].notna()
        & (df[x_col] >= PHILLY_LON_MIN)
        & (df[x_col] <= PHILLY_LON_MAX)
        & (df[y_col] >= PHILLY_LAT_MIN)
        & (df[y_col] <= PHILLY_LAT_MAX)
    )

    return df[mask].copy()


def load_boundaries(name: str) -> gpd.GeoDataFrame:
    """Load cached boundary file by name.

    Args:
        name: Boundary type: "police_districts" or "census_tracts".

    Returns:
        Loaded boundary data with geometry.

    Raises:
        ValueError: If name is not recognized.
        FileNotFoundError: If boundary file does not exist.

    Examples:
        >>> districts = load_boundaries("police_districts")
        >>> isinstance(districts, gpd.GeoDataFrame)
        True
    """
    repo_root = get_repo_root()

    if name == "police_districts":
        file_path = repo_root / "data" / "boundaries" / "police_districts.geojson"
    elif name in ("census_tracts", "census_tracts_pop"):
        file_path = repo_root / "data" / "boundaries" / "census_tracts_pop.geojson"
    else:
        raise ValueError(
            f"Unknown boundary name: {name}. "
            "Expected 'police_districts' or 'census_tracts'."
        )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {file_path}. "
            "Run scripts/download_boundaries.py first."
        )

    return gpd.read_file(file_path)


def df_to_geodataframe(
    df: pd.DataFrame,
    x_col: str = "point_x",
    y_col: str = "point_y",
    crs: str = "EPSG:4326",
) -> gpd.GeoDataFrame:
    """Convert DataFrame with coordinates to GeoDataFrame.

    Args:
        df: DataFrame with coordinate columns.
        x_col: Column name for longitude. Default is "point_x".
        y_col: Column name for latitude. Default is "point_y".
        crs: Coordinate reference system. Default is "EPSG:4326" (WGS84).

    Returns:
        GeoDataFrame with Point geometry.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"point_x": [-75.2], "point_y": [40.0]})
        >>> gdf = df_to_geodataframe(df)
        >>> isinstance(gdf, gpd.GeoDataFrame)
        True
    """
    geometry = [
        Point(xy) if pd.notna(xy[0]) and pd.notna(xy[1]) else None
        for xy in zip(df[x_col], df[y_col])
    ]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=crs)
    return gdf


def spatial_join_districts(
    df: pd.DataFrame,
    district_gdf: gpd.GeoDataFrame | None = None,
    x_col: str = "point_x",
    y_col: str = "point_y",
) -> pd.DataFrame:
    """Join crime points to police district polygons.

    Args:
        df: Crime data with coordinate columns.
        district_gdf: Police district boundaries. If None, loads from cache.
        x_col: Column name for longitude. Default is "point_x".
        y_col: Column name for latitude. Default is "point_y".

    Returns:
        DataFrame with district information joined (adds 'joined_dist_num' column).

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"point_x": [-75.2], "point_y": [40.0]})
        >>> result = spatial_join_districts(df)
        >>> "joined_dist_num" in result.columns
        True
    """
    if district_gdf is None:
        district_gdf = load_boundaries("police_districts")

    # Clean coordinates first
    df_clean = clean_coordinates(df, x_col, y_col)

    # Convert to GeoDataFrame
    crime_gdf = df_to_geodataframe(df_clean, x_col, y_col)

    # Ensure both have same CRS
    if district_gdf.crs != crime_gdf.crs:
        district_gdf = district_gdf.to_crs(crime_gdf.crs)

    # Spatial join
    joined = gpd.sjoin(
        crime_gdf,
        district_gdf[["dist_num", "geometry"]],
        how="left",
        predicate="within",
    )

    # Rename to avoid confusion with original dc_dist column
    if "dist_num" in joined.columns:
        joined = joined.rename(columns={"dist_num": "joined_dist_num"})

    # Drop index_right if present
    if "index_right" in joined.columns:
        joined = joined.drop(columns=["index_right"])

    return pd.DataFrame(joined.drop(columns=["geometry"]))


def spatial_join_tracts(
    df: pd.DataFrame,
    tract_gdf: gpd.GeoDataFrame | None = None,
    x_col: str = "point_x",
    y_col: str = "point_y",
) -> pd.DataFrame:
    """Join crime points to census tract polygons.

    Args:
        df: Crime data with coordinate columns.
        tract_gdf: Census tract boundaries. If None, loads from cache.
        x_col: Column name for longitude. Default is "point_x".
        y_col: Column name for latitude. Default is "point_y".

    Returns:
        DataFrame with census tract GEOID and population joined.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"point_x": [-75.2], "point_y": [40.0]})
        >>> result = spatial_join_tracts(df)
        >>> "GEOID" in result.columns or "total_pop" in result.columns
        True
    """
    if tract_gdf is None:
        tract_gdf = load_boundaries("census_tracts")

    # Clean coordinates first
    df_clean = clean_coordinates(df, x_col, y_col)

    # Convert to GeoDataFrame
    crime_gdf = df_to_geodataframe(df_clean, x_col, y_col)

    # Ensure both have same CRS
    if tract_gdf.crs != crime_gdf.crs:
        tract_gdf = tract_gdf.to_crs(crime_gdf.crs)

    # Select columns to join
    tract_cols = ["GEOID", "total_pop", "geometry"]
    available_cols = [c for c in tract_cols if c in tract_gdf.columns]

    # Spatial join
    joined = gpd.sjoin(
        crime_gdf,
        tract_gdf[available_cols],
        how="left",
        predicate="within",
    )

    # Drop index_right if present
    if "index_right" in joined.columns:
        joined = joined.drop(columns=["index_right"])

    return pd.DataFrame(joined.drop(columns=["geometry"]))


def calculate_severity_score(
    df: pd.DataFrame,
    weights: dict[int, float] | None = None,
    ucr_col: str = "ucr_general",
) -> pd.Series:
    """Calculate weighted severity score per record.

    Args:
        df: Crime data with UCR code column.
        weights: UCR hundred-band to severity weight mapping.
            If None, uses default weights from config.
        ucr_col: Column name for UCR general code. Default is "ucr_general".

    Returns:
        Severity score for each record.

    Raises:
        ValueError: If ucr_col column is not found in DataFrame.

    Notes:
        Severity weights are based on FBI UCR hierarchy:
        - Homicide (100): 10.0
        - Rape (200): 8.0
        - Robbery (300): 6.0
        - Aggravated Assault (400): 5.0
        - Burglary (500): 3.0
        - Theft (600): 1.0
        - Vehicle Theft (700): 2.0
        - Arson (800): 4.0
        - Other (900): 0.5

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"ucr_general": [100, 600, 999]})
        >>> scores = calculate_severity_score(df)
        >>> scores.tolist()
        [10.0, 1.0, 0.5]
    """
    if weights is None:
        weights = SEVERITY_WEIGHTS

    if ucr_col not in df.columns:
        raise ValueError(f"Column {ucr_col} not found in DataFrame")

    # Convert UCR code to hundred-band
    ucr_numeric = pd.to_numeric(df[ucr_col], errors="coerce")
    ucr_band = (ucr_numeric // 100) * 100

    # Map to severity weights, default to 0.5 for unknown codes
    severity = ucr_band.map(weights).fillna(0.5)

    return severity


def get_coordinate_stats(
    df: pd.DataFrame,
    x_col: str = "point_x",
    y_col: str = "point_y",
) -> dict[str, float | None]:
    """Get statistics about coordinate coverage.

    Args:
        df: DataFrame with coordinate columns.
        x_col: Column name for longitude. Default is "point_x".
        y_col: Column name for latitude. Default is "point_y".

    Returns:
        Dictionary with statistics including coverage rate and bounds.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"point_x": [-75.2, None], "point_y": [40.0, None]})
        >>> stats = get_coordinate_stats(df)
        >>> stats["has_coordinates"]
        1
    """
    total = len(df)
    has_coords = df[x_col].notna() & df[y_col].notna()
    valid_count = has_coords.sum()

    df_clean = clean_coordinates(df, x_col, y_col)
    in_bounds = len(df_clean)

    return {
        "total_records": total,
        "has_coordinates": valid_count,
        "in_philadelphia_bounds": in_bounds,
        "coverage_rate": valid_count / total if total > 0 else 0,
        "in_bounds_rate": in_bounds / total if total > 0 else 0,
        "lon_min": df[x_col].min() if valid_count > 0 else None,
        "lon_max": df[x_col].max() if valid_count > 0 else None,
        "lat_min": df[y_col].min() if valid_count > 0 else None,
        "lat_max": df[y_col].max() if valid_count > 0 else None,
    }
