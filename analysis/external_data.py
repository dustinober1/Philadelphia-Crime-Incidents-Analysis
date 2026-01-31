"""
External data fetching module for Philadelphia Crime Incidents EDA.

Provides functions to fetch and cache external data sources:
- Weather data from Meteostat (historical weather)
- Economic data from FRED (unemployment rates)
- Census data from U.S. Census Bureau (income, poverty rates)

All functions implement local caching to avoid API rate limits.
"""

from pathlib import Path

import pandas as pd

from analysis.config import PROJECT_ROOT

# =============================================================================
# PATHS
# =============================================================================

EXTERNAL_DATA_DIR = PROJECT_ROOT / "data" / "external"


# =============================================================================
# WEATHER DATA (Met eostat)
# =============================================================================

def fetch_weather_data(
    station_id: str = "724060-93740",
    start_date: str = "2006-01-01",
    end_date: str = "2026-01-31",
    cache_path: Path = None,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    Fetch historical weather data from Meteostat.

    Args:
        station_id: Meteostat station ID. Default is Philadelphia International Airport.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        cache_path: Path to cache file. If None, uses default.
        force_refresh: If True, bypass cache and fetch from API.

    Returns:
        DataFrame with hourly weather data including temperature,
        precipitation, wind speed, etc.

    Example:
        >>> df = fetch_weather_data("2006-01-01", "2006-12-31")
        >>> print(df.head())
    """
    if cache_path is None:
        cache_path = EXTERNAL_DATA_DIR / f"weather_{station_id}_{start_date}_{end_date}.parquet"

    # Check cache first
    if cache_path.exists() and not force_refresh:
        return pd.read_parquet(cache_path)

    from datetime import datetime

    from meteostat import Hourly, Point

    # Philadelphia coordinates
    philly = Point(39.9526, -75.1652, 12)

    # Fetch data
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    data = Hourly(philly, start, end)
    df = data.fetch()

    # Ensure cache directory exists
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to cache
    df.to_parquet(cache_path)

    return df


def load_cached_weather(
    station_id: str = "724060-93740",
    start_date: str = None,
    end_date: str = None,
) -> pd.DataFrame:
    """
    Load cached weather data from local parquet file.

    Args:
        station_id: Meteostat station ID.
        start_date: Optional start date filter.
        end_date: Optional end date filter.

    Returns:
        DataFrame with weather data. Returns None if cache doesn't exist.
    """
    cache_path = EXTERNAL_DATA_DIR / f"weather_{station_id}_*.parquet"

    # Find matching cache file (wildcard for date range)
    matching_files = list(cache_path.parent.glob(f"weather_{station_id}_*.parquet"))

    if not matching_files:
        return None

    # Use the most recent matching file
    cache_path = sorted(matching_files)[-1]
    df = pd.read_parquet(cache_path)

    if start_date:
        df = df.loc[start_date:]
    if end_date:
        df = df.loc[:end_date]

    return df


# =============================================================================
# ECONOMIC DATA (FRED API)
# =============================================================================

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def fetch_fred_data(
    series_id: str = "PAPHIL5URN",  # Philadelphia County unemployment rate
    start_date: str = "2006-01-01",
    end_date: str = "2026-01-31",
    cache_path: Path = None,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    Fetch economic data from FRED (Federal Reserve Economic Data).

    Requires FRED_API_KEY environment variable. Get free key at:
    https://fred.stlouisfed.org/docs/api/api_key.html

    Args:
        series_id: FRED series ID. Default is PAPHIL5URN (Philadelphia County unemployment).
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        cache_path: Path to cache file. If None, uses default.
        force_refresh: If True, bypass cache and fetch from API.

    Returns:
        DataFrame with date index and value column containing the economic indicator.

    Raises:
        ValueError: If FRED_API_KEY not set or API returns no data.

    Example:
        >>> df = fetch_fred_data("PAPHIL5URN", "2020-01-01", "2020-12-31")
        >>> print(df.describe())
    """
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise ValueError(
            "FRED_API_KEY environment variable not set. "
            "Get free API key at: https://fred.stlouisfed.org/docs/api/api_key.html"
        )

    if cache_path is None:
        cache_path = EXTERNAL_DATA_DIR / f"fred_{series_id}_{start_date}_{end_date}.parquet"

    # Check cache first
    if cache_path.exists() and not force_refresh:
        return pd.read_parquet(cache_path)

    # Import here to avoid API key requirement on module load
    from fredapi import Fred

    fred = Fred(api_key=api_key)
    try:
        data = fred.get_series(series_id, start=start_date, end=end_date)
    except Exception as e:
        raise ValueError(f"FRED API error: {e}")

    if data.empty:
        raise ValueError(f"No data returned from FRED for series {series_id}")

    df = pd.DataFrame(data, columns=['value'])
    df.index.name = 'date'

    # Ensure cache directory exists
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to cache
    df.to_parquet(cache_path)

    return df


def load_cached_fred(
    series_id: str = "PAPHIL5URN",
    start_date: str = None,
    end_date: str = None,
) -> pd.DataFrame:
    """
    Load cached FRED data from local parquet file.

    Args:
        series_id: FRED series ID.
        start_date: Optional start date filter.
        end_date: Optional end date filter.

    Returns:
        DataFrame with FRED data. Returns None if cache doesn't exist.
    """
    cache_path = EXTERNAL_DATA_DIR / f"fred_{series_id}_*.parquet"

    # Find matching cache file (wildcard for date range)
    matching_files = list(cache_path.parent.glob(f"fred_{series_id}_*.parquet"))

    if not matching_files:
        return None

    # Use the most recent matching file
    cache_path = sorted(matching_files)[-1]
    df = pd.read_parquet(cache_path)

    if start_date:
        df = df.loc[start_date:]
    if end_date:
        df = df.loc[:end_date]

    return df


# =============================================================================
# CENSUS DATA (U.S. Census Bureau ACS)
# =============================================================================

def fetch_census_data(
    variables: tuple = ("B19013_001E", "B17001_002E", "B17001_001E"),
    year: int = 2019,  # Most recent pre-COVID 5-year estimates
    state_fips: str = "42",  # Pennsylvania
    place: str = None,  # Optional: restrict to Philadelphia city
    cache_path: Path = None,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    Fetch American Community Survey (ACS) data from U.S. Census Bureau.

    Requires CENSUS_API_KEY environment variable. Get free key at:
    https://api.census.gov/data/key_signup.html

    Default variables:
        - B19013_001E: Median household income (dollars)
        - B17001_002E: Population below poverty line
        - B17001_001E: Population for whom poverty status determined

    Args:
        variables: Tuple of ACS variable IDs to fetch.
        year: Year of ACS 5-year estimates (available 2010-present).
        state_fips: State FIPS code (42 = Pennsylvania).
        place: Optional place FIPS code for city-level filtering.
        cache_path: Path to cache file. If None, uses default.
        force_refresh: If True, bypass cache and fetch from API.

    Returns:
        DataFrame with tract-level data including state, county, tract,
        and requested variables.

    Raises:
        ValueError: If CENSUS_API_KEY not set or API returns no data.

    Example:
        >>> df = fetch_census_data(year=2019)
        >>> print(df.head())
    """
    api_key = os.environ.get("CENSUS_API_KEY")
    if not api_key:
        raise ValueError(
            "CENSUS_API_KEY environment variable not set. "
            "Get free API key at: https://api.census.gov/data/key_signup.html"
        )

    if cache_path is None:
        var_str = "_".join(variables)
        cache_path = EXTERNAL_DATA_DIR / f"census_acs5_{var_str}_{year}.parquet"

    # Check cache first
    if cache_path.exists() and not force_refresh:
        return pd.read_parquet(cache_path)

    # Import here to avoid API key requirement on module load
    from census import Census

    c = Census(api_key)

    # Build query parameters
    params = {'for': 'tract:*', 'in': f'state:{state_fips}'}

    # Add county filter if place specified (Philadelphia County = 101)
    if place == "Philadelphia":
        params['in'] = f'state:{state_fips} county:101'

    try:
        # Fetch data for each variable and merge
        results = []
        for var in variables:
            data = c.acs5.get((var,), params, year=year)
            df_var = pd.DataFrame(data)
            results.append(df_var)

        # Merge all variables
        df = results[0]
        for df_var in results[1:]:
            df = df.merge(df_var, on=['state', 'county', 'tract'], how='outer')

    except Exception as e:
        raise ValueError(f"Census API error: {e}")

    if df.empty:
        raise ValueError(f"No data returned from Census API for year {year}")

    # Create a geographic identifier
    df['geo_id'] = df['state'] + df['county'] + df['tract']

    # Calculate poverty rate if both numerator and denominator present
    if "B17001_002E" in variables and "B17001_001E" in variables:
        df['poverty_rate'] = (
            pd.to_numeric(df['B17001_002E'], errors='coerce') /
            pd.to_numeric(df['B17001_001E'], errors='coerce') * 100
        )

    # Ensure cache directory exists
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to cache
    df.to_parquet(cache_path)

    return df


def load_cached_census(
    variables: tuple = ("B19013_001E", "B17001_002E", "B17001_001E"),
    year: int = 2019,
) -> pd.DataFrame:
    """
    Load cached Census ACS data from local parquet file.

    Args:
        variables: Tuple of ACS variable IDs.
        year: Year of ACS data.

    Returns:
        DataFrame with Census data. Returns None if cache doesn't exist.
    """
    var_str = "_".join(variables)
    cache_path = EXTERNAL_DATA_DIR / f"census_acs5_{var_str}_{year}.parquet"

    if not cache_path.exists():
        return None

    return pd.read_parquet(cache_path)
