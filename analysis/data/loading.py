"""Data loading functions with joblib caching.

This module provides functions to load crime data, boundary data, and
external data sources. All loading functions use joblib caching for
performance - the first load reads from disk, subsequent loads return
cached results.

Example:
    >>> from analysis.data import load_crime_data
    >>> df = load_crime_data()  # First load: reads from parquet
    >>> df = load_crime_data()  # Second load: returns cached result
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, cast

import pandas as pd

from analysis.config import CRIME_DATA_PATH
from .cache import memory

# Optional geopandas import for spatial data
try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
    if TYPE_CHECKING:
        import geopandas as gpd


@memory.cache
def _load_crime_data_parquet(clean: bool = True) -> pd.DataFrame:
    """Load crime data from parquet with caching (internal function).

    This function is cached using joblib.Memory. The cache key includes
    the 'clean' parameter, so different clean values are cached separately.

    Args:
        clean: Whether to drop rows with missing dispatch_date.

    Returns:
        DataFrame with parsed dispatch_date column.

    Raises:
        FileNotFoundError: If crime data file doesn't exist.
    """
    if not CRIME_DATA_PATH.exists():
        raise FileNotFoundError(f"Crime data not found: {CRIME_DATA_PATH}")

    df = pd.read_parquet(CRIME_DATA_PATH)

    # Parse dispatch_date (handle category dtype from parquet)
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


def load_crime_data(clean: bool = True) -> pd.DataFrame:
    """Load crime incidents data from parquet.

    This function loads the combined crime incidents dataset and parses
    the dispatch_date column. Results are cached using joblib for
    performance on subsequent calls.

    Args:
        clean: Whether to drop rows with missing dispatch_date. Default True.

    Returns:
        DataFrame with crime incident data. dispatch_date is parsed as datetime.

    Raises:
        FileNotFoundError: If the crime data parquet file doesn't exist.

    Example:
        >>> from analysis.data import load_crime_data
        >>> df = load_crime_data()
        >>> print(f"Loaded {len(df)} incidents")
        Loaded 1500000 incidents
    """
    return cast(pd.DataFrame, _load_crime_data_parquet(clean=clean))


@memory.cache
def _load_boundaries_geojson(name: Literal["police_districts", "census_tracts"]) -> bytes:
    """Load boundary GeoJSON data with caching (internal function).

    Args:
        name: Name of the boundary dataset to load.

    Returns:
        Raw GeoJSON data as bytes.

    Raises:
        FileNotFoundError: If the boundary file doesn't exist.
        ValueError: If name is not a valid boundary dataset.
    """
    repo_root = Path(__file__).resolve().parent.parent.parent
    boundaries_dir = repo_root / "data" / "boundaries"

    boundary_files = {
        "police_districts": "Police_Districts.geojson",
        "census_tracts": "Census_Tracts_2020.geojson",
    }

    if name not in boundary_files:
        raise ValueError(
            f"Unknown boundary: {name}. "
            f"Valid options: {list(boundary_files.keys())}"
        )

    file_path = boundaries_dir / boundary_files[name]

    if not file_path.exists():
        raise FileNotFoundError(f"Boundary data not found: {file_path}")

    return file_path.read_bytes()


def load_boundaries(
    name: Literal["police_districts", "census_tracts"],
) -> "gpd.GeoDataFrame":
    """Load boundary data as a GeoDataFrame.

    This function loads geographic boundary data for police districts
    or census tracts. Results are cached using joblib.

    Args:
        name: Type of boundary to load - "police_districts" or "census_tracts".

    Returns:
        GeoDataFrame with boundary geometries.

    Raises:
        FileNotFoundError: If the boundary file doesn't exist.
        ValueError: If name is not a valid boundary dataset.
        ImportError: If geopandas is not installed.

    Example:
        >>> from analysis.data import load_boundaries
        >>> districts = load_boundaries("police_districts")
        >>> print(f"Loaded {len(districts)} districts")
    """
    if not HAS_GEOPANDAS:
        raise ImportError(
            "geopandas is required to load boundary data. "
            "Install it with: conda install -c conda-forge geopandas"
        )

    geojson_bytes = _load_boundaries_geojson(name)
    return gpd.GeoDataFrame.from_features(
        gpd.GeoDataFrame.from_file(geojson_bytes).__geo_interface__["features"]
    )


@memory.cache
def _load_external_data_csv(name: str) -> bytes:
    """Load external data CSV with caching (internal function).

    Args:
        name: Name of the external dataset (without .csv extension).

    Returns:
        Raw CSV data as bytes.

    Raises:
        FileNotFoundError: If the external data file doesn't exist.
    """
    repo_root = Path(__file__).resolve().parent.parent.parent
    external_dir = repo_root / "data" / "external"
    file_path = external_dir / f"{name}.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"External data not found: {file_path}")

    return file_path.read_bytes()


def load_external_data(name: str) -> pd.DataFrame:
    """Load external data (weather, economic indicators, etc.).

    This function loads external datasets stored in data/external/.
    Common datasets include weather data and economic indicators.

    Args:
        name: Name of the external dataset (without .csv extension).

    Returns:
        DataFrame with external data.

    Raises:
        FileNotFoundError: If the external data file doesn't exist.

    Example:
        >>> from analysis.data import load_external_data
        >>> weather = load_external_data("weather_daily")
        >>> print(weather.head())
    """
    from io import StringIO

    csv_bytes = _load_external_data_csv(name)
    return pd.read_csv(StringIO(csv_bytes.decode("utf-8")))


__all__ = [
    "load_crime_data",
    "load_boundaries",
    "load_external_data",
]
