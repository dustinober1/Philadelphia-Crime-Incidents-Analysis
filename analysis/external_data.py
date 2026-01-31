"""
External data fetching module for Philadelphia Crime Incidents EDA.

Provides functions to fetch and cache external data sources:
- Weather data from Meteostat (historical daily weather)
- Economic data from FRED (unemployment rates)
- Census data from U.S. Census Bureau (income, poverty rates)

All functions implement local caching to avoid API rate limits.

Temporal alignment functions handle misalignment between data sources:
- Crime: Daily (2006-2026)
- Weather: Daily (2006-2026)
- FRED: Monthly (1990-present)
- Census ACS: Annual 5-year estimates (2010-present)
"""

from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import requests_cache

from analysis.config import (
    CACHE_CONFIG,
    EXTERNAL_CACHE_DIR,
    EXTERNAL_DATA_DIR,
    PHILADELPHIA_CENTER,
    get_cache_staleness,
)


# =============================================================================
# CACHING INFRASTRUCTURE
# =============================================================================


def _ensure_cache_dir() -> Path:
    """Ensure cache directory exists."""
    EXTERNAL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return EXTERNAL_CACHE_DIR


def get_cached_session(source: str = "weather"):
    """
    Get a requests session with caching enabled.

    Uses requests-cache to cache API responses locally with per-source
    staleness settings. Avoids rate limits and speeds up repeated requests.

    Args:
        source: Data source name for staleness settings ('weather', 'fred', 'census').

    Returns:
        requests_cache.CachedSession configured for the data source.

    Example:
        >>> session = get_cached_session('weather')
        >>> response = session.get('https://example.com/api')
    """
    if not CACHE_CONFIG.get("cache_enabled", True):
        # Return uncached session if caching disabled
        import requests

        return requests.Session()

    _ensure_cache_dir()

    cache_path = EXTERNAL_CACHE_DIR / f"{source}_cache"
    staleness = get_cache_staleness(source)

    # Create cached session with SQLite backend
    session = requests_cache.CachedSession(
        cache_name=str(cache_path),
        expire_after=staleness,
        backend=CACHE_CONFIG.get("cache_backend", "sqlite"),
    )

    return session


def clear_cache(source: str = None) -> None:
    """
    Clear cached API responses.

    Args:
        source: Specific source to clear ('weather', 'fred', 'census').
                If None, clears all caches.

    Example:
        >>> clear_cache('weather')  # Clear only weather cache
        >>> clear_cache()  # Clear all caches
    """
    _ensure_cache_dir()

    if source:
        # Clear specific source cache
        cache_pattern = EXTERNAL_CACHE_DIR / f"{source}_cache.*"
        for cache_file in EXTERNAL_CACHE_DIR.glob(f"{source}_cache.*"):
            cache_file.unlink()
    else:
        # Clear all caches
        for cache_file in EXTERNAL_CACHE_DIR.glob("*_cache.*"):
            cache_file.unlink()


def get_cache_info() -> dict:
    """
    Get information about cached data.

    Returns:
        Dict with cache file sizes and counts for each data source.

    Example:
        >>> info = get_cache_info()
        >>> print(info['weather']['size_mb'])
    """
    _ensure_cache_dir()

    sources = ['weather', 'fred', 'census']
    info = {}

    for source in sources:
        cache_files = list(EXTERNAL_CACHE_DIR.glob(f"{source}_cache.*"))

        if cache_files:
            total_size = sum(f.stat().st_size for f in cache_files)
            info[source] = {
                'exists': True,
                'file_count': len(cache_files),
                'size_bytes': total_size,
                'size_mb': round(total_size / (1024 * 1024), 2),
                'files': [str(f.name) for f in cache_files],
            }
        else:
            info[source] = {'exists': False}

    # Also check parquet cache files in parent directory
    parquet_files = list(EXTERNAL_DATA_DIR.glob("*.parquet"))
    info['parquet'] = {
        'count': len(parquet_files),
        'files': [str(f.name) for f in parquet_files],
    }

    return info

# =============================================================================
# WEATHER DATA (Meteostat v2)
# =============================================================================

def fetch_weather_data(
    start_date: str = "2006-01-01",
    end_date: str = "2026-01-31",
    cache_path: Path = None,
    force_refresh: bool = False,
    station_id: str = "72408",
) -> pd.DataFrame:
    """
    Fetch daily weather data for Philadelphia using Meteostat API.

    Retrieves temperature (temp, tmin, tmax) and precipitation (prcp) data
    for the specified date range. Uses local cache to avoid repeated API calls.

    Args:
        start_date: Start date in YYYY-MM-DD format. Default is "2006-01-01".
        end_date: End date in YYYY-MM-DD format. Default is "2026-01-31".
        cache_path: Path to cache file. If None, uses EXTERNAL_DATA_DIR.
        force_refresh: If True, bypass cache and fetch from API.
        station_id: Meteostat station ID. Default is "72408" (Philadelphia International Airport).

    Returns:
        DataFrame with columns:
            - time: Date index
            - temp: Average temperature (C)
            - tmin: Minimum temperature (C)
            - tmax: Maximum temperature (C)
            - prcp: Precipitation (mm)
            - snwd: Snow depth (mm)
            - wspd: Wind speed (km/h)
            - wpgt: Wind peak gust (km/h)
            - pres: Sea-level air pressure (hPa)

    Raises:
        ValueError: If dates are invalid or API returns no data.

    Example:
        >>> df = fetch_weather_data("2020-01-01", "2020-12-31")
        >>> print(df[['temp', 'prcp']].head())
    """
    from datetime import datetime

    from meteostat import Point, daily

    if cache_path is None:
        cache_path = EXTERNAL_DATA_DIR / "weather_philly_2006_2026.parquet"

    # Check cache first
    if cache_path.exists() and not force_refresh:
        cached_data = pd.read_parquet(cache_path)
        # Ensure requested range is covered
        cached_data['date'] = pd.to_datetime(cached_data.index)
        cached_start = cached_data['date'].min()
        cached_end = cached_data['date'].max()
        if pd.to_datetime(start_date) >= cached_start and pd.to_datetime(end_date) <= cached_end:
            return cached_data.loc[start_date:end_date]

    # Philadelphia coordinates: lat, lon, elevation (meters)
    philly = Point(
        PHILADELPHIA_CENTER["lat"],
        PHILADELPHIA_CENTER["lon"],
        6  # Approximate elevation in meters
    )

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Fetch daily weather data
    data = daily(station_id, start, end)
    df = data.fetch()

    if df is None or df.empty:
        raise ValueError("No weather data returned from Meteostat API")

    # Ensure cache directory exists
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to cache
    df.to_parquet(cache_path)

    return df.loc[start_date:end_date]


def load_cached_weather(
    cache_path: Path = None,
    start_date: str = None,
    end_date: str = None,
) -> pd.DataFrame:
    """
    Load cached weather data from local parquet file.

    Args:
        cache_path: Path to cache file. If None, uses default.
        start_date: Optional start date filter (YYYY-MM-DD).
        end_date: Optional end date filter (YYYY-MM-DD).

    Returns:
        DataFrame with weather data. Returns None if cache doesn't exist.

    Example:
        >>> df = load_cached_weather()
        >>> if df is not None:
        ...     print(df.describe())
    """
    if cache_path is None:
        cache_path = EXTERNAL_DATA_DIR / "weather_philly_2006_2026.parquet"

    if not cache_path.exists():
        return None

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


# =============================================================================
# TEMPORAL ALIGNMENT UTILITIES
# =============================================================================

def aggregate_crime_by_period(
    crime_df: pd.DataFrame,
    period: str = "D",  # D=daily, W=weekly, M=monthly, Y=yearly
    date_column: str = "dispatch_date",
) -> pd.DataFrame:
    """
    Aggregate crime incidents to a temporal period.

    Args:
        crime_df: DataFrame with crime incidents. Must have date_column.
        period: Pandas resample period code ('D', 'W', 'M', 'Q', 'Y').
        date_column: Name of date column to aggregate by.

    Returns:
        DataFrame with date index and 'crime_count' column.

    Raises:
        ValueError: If date_column not found in DataFrame.

    Note:
        - Daily (D): Full temporal resolution, matches weather data
        - Monthly (M): Matches FRED unemployment data
        - Yearly (Y): Matches Census ACS 5-year estimates

    Example:
        >>> from analysis.utils import load_data
        >>> df = load_data()
        >>> daily = aggregate_crime_by_period(df, 'D')
        >>> monthly = aggregate_crime_by_period(df, 'M')
    """
    if date_column not in crime_df.columns:
        raise ValueError(f"Date column '{date_column}' not found in DataFrame")

    # Ensure date column is datetime
    df = crime_df.copy()
    df[date_column] = pd.to_datetime(df[date_column])

    # Set date as index and count incidents per period
    df = df.set_index(date_column)

    # Resample and count
    aggregated = df.resample(period).size().reset_index(name='crime_count')
    aggregated = aggregated.set_index(date_column)

    return aggregated


def align_temporal_data(
    crime_df: pd.DataFrame,
    weather_df: pd.DataFrame = None,
    unemployment_df: pd.DataFrame = None,
    census_df: pd.DataFrame = None,
    resolution: str = "monthly",
) -> pd.DataFrame:
    """
    Align crime data with external data sources for correlation analysis.

    Handles temporal misalignment between sources:
        - Crime: Daily (2006-2026)
        - Weather: Daily (2006-2026)
        - FRED: Monthly (1990-present)
        - Census ACS: Annual 5-year estimates (2010-present)

    Args:
        crime_df: Crime incident DataFrame. Must have 'dispatch_date' column.
        weather_df: Weather DataFrame with date index. Optional.
        unemployment_df: FRED unemployment DataFrame with date index. Optional.
        census_df: Census DataFrame with year column. Optional.
        resolution: Temporal resolution ('daily', 'monthly', 'annual').

    Returns:
        DataFrame with aligned data. Columns depend on resolution and
        available external data:
            - daily: date, crime_count, temp, prcp
            - monthly: date, crime_count, temp, prcp, unemployment_rate
            - annual: year, crime_count, unemployment_rate, poverty_rate

        Resolution trade-offs:
            - Daily: Weather only (no economic data due to monthly/annual frequency)
            - Monthly: Weather + unemployment (no Census due to annual frequency)
            - Annual: Weather + unemployment + Census (full alignment but fewer points)

    Raises:
        ValueError: If resolution not recognized or crime_df is empty.

    Example:
        >>> # Monthly alignment with weather and unemployment
        >>> df = align_temporal_data(crime_df, weather_df, unemployment_df, resolution='monthly')
        >>> print(df.columns)
    """
    if resolution not in ("daily", "monthly", "annual"):
        raise ValueError(f"Unknown resolution: {resolution}. Use 'daily', 'monthly', or 'annual'.")

    # Get analysis range from config
    from analysis.config import get_analysis_range
    start_date, end_date = get_analysis_range(resolution)

    # Aggregate crime to specified period
    if resolution == "daily":
        period = "D"
    elif resolution == "monthly":
        period = "M"
    else:  # annual
        period = "Y"

    crime_agg = aggregate_crime_by_period(crime_df, period=period)

    # Filter to analysis range
    crime_agg = crime_agg.loc[start_date:end_date]

    # Initialize result DataFrame with crime counts
    result = crime_agg.rename(columns={'crime_count': 'crime_count'})

    # Align and merge weather data (if provided)
    if weather_df is not None:
        weather_df = weather_df.copy()
        weather_df.index = pd.to_datetime(weather_df.index)

        # Resample weather to match period
        weather_agg = weather_df[['temp', 'prcp']].resample(period).mean()
        weather_agg = weather_agg.loc[start_date:end_date]

        # Merge
        result = result.join(weather_agg, how='left')

    # Align and merge unemployment data (if provided and not daily)
    if unemployment_df is not None and resolution != "daily":
        unemployment_df = unemployment_df.copy()
        unemployment_df.index = pd.to_datetime(unemployment_df.index)

        # Unemployment is already monthly, just resample if annual
        if resolution == "annual":
            unemployment_agg = unemployment_df.resample("Y").mean()
        else:
            unemployment_agg = unemployment_df

        unemployment_agg = unemployment_agg.loc[start_date:end_date]
        unemployment_agg.columns = ['unemployment_rate']

        # Merge
        result = result.join(unemployment_agg, how='left')

    # Align and merge Census data (if provided and annual only)
    if census_df is not None and resolution == "annual":
        # Census data is at tract level, need to aggregate to city-wide
        # For now, skip as we need district crosswalk (separate plan)
        pass

    # Remove rows with all-NaN external data
    result = result.dropna(how='all', subset=[c for c in result.columns if c != 'crime_count'])

    return result


def create_lagged_features(
    df: pd.DataFrame,
    columns: list = None,
    lags: list = [1, 7, 30],  # 1 day, 1 week, 1 month
) -> pd.DataFrame:
    """
    Create lagged features for cross-correlation analysis.

    Tests whether weather today predicts crime tomorrow, etc.

    Args:
        df: DataFrame with datetime index.
        columns: Columns to create lags for. If None, uses all numeric columns.
        lags: List of lag periods (same units as DataFrame index frequency).

    Returns:
        DataFrame with added {column}_lag{lag} columns.

    Example:
        >>> df = create_lagged_features(weather_df, columns=['temp'], lags=[1, 7])
        >>> print(df.columns)  # temp, temp_lag1, temp_lag7
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    result = df.copy()

    for col in columns:
        for lag in lags:
            result[f'{col}_lag{lag}'] = result[col].shift(lag)

    return result
