"""Spatial utility functions for Phase 2 analysis.

This module provides functions for:
- Coordinate cleaning and validation
- Loading boundary files
- Spatial joins between crime points and geographic boundaries
- Severity score calculation
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from analysis.phase2_config_loader import Phase2Config, load_phase2_config


def get_repo_root() -> Path:
    """Get the repository root directory."""
    return Path(__file__).resolve().parent.parent


def clean_coordinates(
    df: pd.DataFrame,
    x_col: str = "point_x",
    y_col: str = "point_y",
    config: Phase2Config | None = None,
) -> pd.DataFrame:
    """Filter DataFrame to valid WGS84 coordinates for Philadelphia.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with coordinate columns.
    x_col : str, default "point_x"
        Column name for longitude (x coordinate).
    y_col : str, default "point_y"
        Column name for latitude (y coordinate).
    config : Phase2Config, optional
        Configuration with coordinate bounds. If None, loads default.

    Returns
    -------
    pd.DataFrame
        DataFrame filtered to valid Philadelphia coordinates.

    Notes
    -----
    Philadelphia bounds (approximate):
    - Longitude: -75.30 to -74.95
    - Latitude: 39.85 to 40.15
    """
    if config is None:
        config = load_phase2_config()

    bounds = config.coordinate_bounds

    # Ensure columns exist
    if x_col not in df.columns or y_col not in df.columns:
        raise ValueError(f"Columns {x_col} and/or {y_col} not found in DataFrame")

    # Create mask for valid coordinates
    mask = (
        df[x_col].notna()
        & df[y_col].notna()
        & (df[x_col] >= bounds.min_lon)
        & (df[x_col] <= bounds.max_lon)
        & (df[y_col] >= bounds.min_lat)
        & (df[y_col] <= bounds.max_lat)
    )

    return df[mask].copy()


def load_boundaries(name: str) -> gpd.GeoDataFrame:
    """Load cached boundary file by name.

    Parameters
    ----------
    name : str
        Boundary type: "police_districts" or "census_tracts".

    Returns
    -------
    gpd.GeoDataFrame
        Loaded boundary data with geometry.

    Raises
    ------
    ValueError
        If name is not recognized.
    FileNotFoundError
        If boundary file does not exist.
    """
    config = load_phase2_config()
    repo_root = get_repo_root()

    if name == "police_districts":
        file_path = repo_root / config.boundaries.police_districts_file
    elif name in ("census_tracts", "census_tracts_pop"):
        file_path = repo_root / config.boundaries.census_tracts_file
    else:
        raise ValueError(
            f"Unknown boundary name: {name}. " "Expected 'police_districts' or 'census_tracts'."
        )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {file_path}. " "Run scripts/download_boundaries.py first."
        )

    return gpd.read_file(file_path)


def df_to_geodataframe(
    df: pd.DataFrame,
    x_col: str = "point_x",
    y_col: str = "point_y",
    crs: str = "EPSG:4326",
) -> gpd.GeoDataFrame:
    """Convert DataFrame with coordinates to GeoDataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with coordinate columns.
    x_col : str, default "point_x"
        Column name for longitude.
    y_col : str, default "point_y"
        Column name for latitude.
    crs : str, default "EPSG:4326"
        Coordinate reference system.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with Point geometry.
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

    Parameters
    ----------
    df : pd.DataFrame
        Crime data with coordinate columns.
    district_gdf : gpd.GeoDataFrame, optional
        Police district boundaries. If None, loads from cache.
    x_col : str, default "point_x"
        Column name for longitude.
    y_col : str, default "point_y"
        Column name for latitude.

    Returns
    -------
    pd.DataFrame
        DataFrame with district information joined (adds 'joined_dist_num' column).
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

    Parameters
    ----------
    df : pd.DataFrame
        Crime data with coordinate columns.
    tract_gdf : gpd.GeoDataFrame, optional
        Census tract boundaries. If None, loads from cache.
    x_col : str, default "point_x"
        Column name for longitude.
    y_col : str, default "point_y"
        Column name for latitude.

    Returns
    -------
    pd.DataFrame
        DataFrame with census tract GEOID and population joined.
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

    Parameters
    ----------
    df : pd.DataFrame
        Crime data with UCR code column.
    weights : dict, optional
        UCR hundred-band to severity weight mapping.
        If None, loads from Phase 2 config.
    ucr_col : str, default "ucr_general"
        Column name for UCR general code.

    Returns
    -------
    pd.Series
        Severity score for each record.

    Notes
    -----
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
    """
    if weights is None:
        config = load_phase2_config()
        weights = config.severity_weights

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
) -> dict[str, float]:
    """Get statistics about coordinate coverage.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with coordinate columns.
    x_col : str, default "point_x"
        Column name for longitude.
    y_col : str, default "point_y"
        Column name for latitude.

    Returns
    -------
    dict
        Statistics including coverage rate and bounds.
    """
    total = len(df)
    has_coords = df[x_col].notna() & df[y_col].notna()
    valid_count = has_coords.sum()

    config = load_phase2_config()
    df_clean = clean_coordinates(df, x_col, y_col, config)
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
