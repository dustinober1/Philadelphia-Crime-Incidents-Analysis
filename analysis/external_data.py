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

Detrending utilities prevent spurious correlations from long-term trend drift
when analyzing relationships between crime and external variables.
"""

from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import requests_cache

# Import statsmodels for detrending
try:
    from statsmodels.tsa.tsatools import detrend as sm_detrend
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = None

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
# DETRENDING UTILITIES
# =============================================================================


def detrend_series(series: pd.Series, method: str = "linear") -> pd.Series:
    """
    Remove trend from a time series to avoid spurious correlations.

    Spurious correlation occurs when two series with long-term trends
    show high correlation even if no real relationship exists. Detrending
    removes the trend component before correlation analysis.

    Args:
        series: Time series (pandas Series with datetime or numeric index).
        method: Detrending method ('linear' or 'mean').
                - 'linear': Remove best-fit line trend (statsmodels.detrend)
                - 'mean': Subtract mean (simple centering)

    Returns:
        Detrended series with same index as input.

    Note:
        Crime and weather both show trends over 20 years. Correlating raw
        data will produce significant results even if unrelated. Always
        detrend before correlation analysis.

    Example:
        >>> crime_detrended = detrend_series(crime_series, 'linear')
        >>> temp_detrended = detrend_series(temp_series, 'linear')
        >>> correlation = crime_detrended.corr(temp_detrended)
    """
    if method == "linear":
        if STATSMODELS_AVAILABLE is None:
            raise ImportError(
                "statsmodels is required for linear detrending. "
                "Install with: pip install statsmodels"
            )
        # Use statsmodels to remove linear trend
        detrended = sm_detrend(series.values, order=1)
        return pd.Series(detrended, index=series.index, name=series.name)

    elif method == "mean":
        # Simple mean centering
        return series - series.mean()

    else:
        raise ValueError(f"Unknown detrending method: {method}. Use 'linear' or 'mean'.")


def first_difference(series: pd.Series) -> pd.Series:
    """
    Apply first-differencing to remove trend (alternative to detrending).

    First-differencing computes the change between consecutive periods:
        diff[t] = series[t] - series[t-1]

    This removes any linear trend and makes the series stationary.

    Args:
        series: Time series (pandas Series).

    Returns:
        Differenced series (length = len(series) - 1).

    Example:
        >>> crime_diff = first_difference(crime_series)
        >>> temp_diff = first_difference(temp_series)
        >>> correlation = crime_diff.corr(temp_diff)
    """
    return series.diff().dropna()


def cross_correlation(
    series1: pd.Series,
    series2: pd.Series,
    max_lag: int = 7,
) -> pd.DataFrame:
    """
    Compute cross-correlation between two series at multiple lags.

    Tests whether series2 leads series1 (positive lags) or vice versa.

    Args:
        series1: First time series (e.g., crime count).
        series2: Second time series (e.g., temperature).
        max_lag: Maximum lag to test (in periods, same as series frequency).

    Returns:
        DataFrame with columns:
            - lag: Lag period (negative = series2 leads, positive = series1 leads)
            - correlation: Spearman correlation at each lag
            - p_value: Statistical significance of correlation
            - n: Sample size for each lag

    Example:
        >>> # Test if temperature today predicts crime tomorrow
        >>> cc = cross_correlation(crime_series, temp_series, max_lag=7)
        >>> print(cc[cc['lag'] == 1])  # Temp today -> Crime tomorrow
    """
    from scipy.stats import spearmanr

    lags = range(-max_lag, max_lag + 1)
    results = []

    for lag in lags:
        if lag < 0:
            # series2 leads (shift series2 left)
            s1 = series1.iloc[abs(lag):]
            s2 = series2.iloc[:lag]
        elif lag > 0:
            # series1 leads (shift series1 left)
            s1 = series1.iloc[:-lag]
            s2 = series2.iloc[lag:]
        else:
            # No lag (contemporaneous)
            s1 = series1
            s2 = series2

        # Align and compute correlation
        min_len = min(len(s1), len(s2))
        s1 = s1.iloc[:min_len]
        s2 = s2.iloc[:min_len]

        if min_len > 10:  # Need sufficient data
            corr, p_value = spearmanr(s1, s2)
            results.append({
                'lag': lag,
                'correlation': corr,
                'p_value': p_value,
                'n': min_len,
            })

    return pd.DataFrame(results)


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


# =============================================================================
# POLICING DATA AVAILABILITY ASSESSMENT
# =============================================================================


def assess_policing_data_availability() -> dict:
    """
    Assess availability of Philadelphia policing data for correlation analysis.

    CORR-03 requires correlation analysis between crime outcomes and policing
    data (resource allocation, arrest rates). This function documents the
    availability of such data.

    Returns:
        Dictionary with:
            - available: Boolean, whether policing data is accessible
            - sources: Dict of known data sources with URLs and limitations
            - variables: List of policing variables of interest
            - recommendation: How to proceed given data limitations
            - manual_options: Potential manual data collection approaches

    Note:
        Philadelphia policing data exists but lacks programmatic access:
            - Controller's Office: Static PDF reports (2022, 2024)
            - DAO Dashboard: Interactive web visualization
            - OpenDataPhilly: May have historical datasets (requires search)

        For automated correlation analysis, consider:
            1. Manual data entry from PDF reports (small dataset, feasible)
            2. Web scraping (fragile, may violate ToS)
            3. Contact data owners directly for CSV access

    Example:
        >>> assessment = assess_policing_data_availability()
        >>> print(assessment['available'])  # False
        >>> print(assessment['recommendation'])
    """
    from analysis.config import POLICING_DATA_CONFIG

    sources = POLICING_DATA_CONFIG['sources']

    # Detailed assessment for each source
    detailed_assessment = {}

    for source_key, source_info in sources.items():
        detailed_assessment[source_key] = {
            'name': source_info['name'],
            'url': source_info['url'],
            'format': source_info['format'],
            'has_api': source_info['api'],
            'notes': source_info['notes'],
            'feasibility_for_automation': _assess_automation_feasibility(source_info),
        }

    # Manual data collection options
    manual_options = {
        "pdf_data_entry": {
            "effort": "Medium (2-4 hours)",
            "feasibility": "High",
            "description": "Manually extract data from Controller's Office PDF reports",
            "variables_possible": [
                "police_officer_count_by_district",
                "arrest_counts_by_district",
                "budget_by_district",
            ],
            "years_covered": [2022, 2024],
        },
        "web_scraping": {
            "effort": "High (8-16 hours)",
            "feasibility": "Low to Medium",
            "description": "Scrape DAO dashboard or Controller's Office website",
            "risks": [
                "Fragile (breaks if website changes)",
                "May violate Terms of Service",
                "Requires maintenance",
            ],
        },
        "direct_request": {
            "effort": "Low (1-2 hours)",
            "feasibility": "Uncertain",
            "description": "Contact agencies directly for CSV/data access",
            "contacts": [
                "Philadelphia Controller's Office: data@controller.phila.gov",
                "OpenDataPhilly: opendata@phila.gov",
            ],
        },
    }

    return {
        'available': POLICING_DATA_CONFIG['available_for_correlation'],
        'sources': detailed_assessment,
        'variables_of_interest': POLICING_DATA_CONFIG['variables_of_interest'],
        'recommendation': POLICING_DATA_CONFIG['recommendation'],
        'manual_options': manual_options,
        'correlation_implications': {
            'status': 'CORR-03 partially addressable',
            'note': 'Automated correlation analysis not possible without API access. '
                    'Manual data entry from PDF reports could enable limited analysis '
                    'for 2022 and 2024 data points only.',
            'alternative': 'Consider district-level crime trend analysis without '
                          'policing data as a control variable.',
        },
    }


def _assess_automation_feasibility(source_info: dict) -> str:
    """
    Assess whether a data source is feasible for automated retrieval.

    Args:
        source_info: Source information dict from POLICING_DATA_CONFIG.

    Returns:
        Feasibility assessment: 'High', 'Medium', 'Low', or 'Not Feasible'.
    """
    if source_info.get('api') is True:
        return 'High'
    elif source_info.get('format') == 'PDF reports':
        return 'Low (requires OCR or manual entry)'
    elif source_info.get('format') == 'Interactive web dashboard':
        return 'Low (requires web scraping)'
    elif 'CSV' in source_info.get('format', ''):
        return 'Medium'
    else:
        return 'Not Feasible'


def generate_policing_data_report() -> str:
    """
    Generate a markdown report on policing data availability.

    Returns:
        Markdown string documenting policing data sources, limitations,
        and recommendations for addressing CORR-03.

    Example:
        >>> report = generate_policing_data_report()
        >>> print(report)
    """
    assessment = assess_policing_data_availability()

    md_lines = [
        "# Philadelphia Policing Data Availability Assessment",
        "",
        "## Summary",
        "",
        f"**Automated correlation analysis (CORR-03):** {'Possible' if assessment['available'] else 'Not Currently Possible'}",
        "",
        f"**Limitation:** {assessment['recommendation']}",
        "",
        "## Known Data Sources",
        "",
    ]

    for source_key, source in assessment['sources'].items():
        md_lines.extend([
            f"### {source['name']}",
            "",
            f"- **URL:** {source['url']}",
            f"- **Format:** {source['format']}",
            f"- **API Access:** {'Yes' if source['has_api'] else 'No'}",
            f"- **Automation Feasibility:** {source['feasibility_for_automation']}",
            f"- **Notes:** {source['notes']}",
            "",
        ])

    md_lines.extend([
        "## Variables of Interest",
        "",
    ])

    for var in assessment['variables_of_interest']:
        md_lines.append(f"- {var}")

    md_lines.extend([
        "",
        "## Manual Data Collection Options",
        "",
    ])

    for option_key, option in assessment['manual_options'].items():
        md_lines.extend([
            f"### {option_key.replace('_', ' ').title()}",
            "",
            f"- **Effort:** {option['effort']}",
            f"- **Feasibility:** {option['feasibility']}",
            f"- **Description:** {option['description']}",
        ])

        if 'risks' in option:
            md_lines.append(f"- **Risks:** {', '.join(option['risks'])}")

        if 'variables_possible' in option:
            md_lines.append(f"- **Variables:** {', '.join(option['variables_possible'])}")

        md_lines.append("")

    md_lines.extend([
        "## Recommendations",
        "",
    ])

    implications = assessment['correlation_implications']
    md_lines.extend([
        f"**Status:** {implications['status']}",
        "",
        implications['note'],
        "",
        implications['alternative'],
        "",
    ])

    return "\n".join(md_lines)
