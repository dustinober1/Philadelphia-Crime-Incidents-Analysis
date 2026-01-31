# Phase 2: External Data Integration - Research

**Researched:** 2026-01-31
**Domain:** External data ingestion, caching, and correlation analysis for Philadelphia crime EDA
**Confidence:** HIGH

## Summary

This phase requires integrating three types of external data with the existing Philadelphia crime dataset (3.5M records, 2006-2026): weather data (daily temperature, precipitation), economic indicators (unemployment, poverty, income), and policing data (staffing, arrest rates). The primary technical challenge is aligning different temporal resolutions (daily weather vs monthly economic vs daily crime) and applying detrending to avoid spurious correlations.

**Key findings:**
1. **Weather data**: Meteostat Python library provides daily historical weather via API or direct library access. Requires location coordinates and has a 10-year per-request limit.
2. **Economic data**: Two complementary sources - US Census API for district-level socioeconomic data (via `census` library) and FRED API for county-level unemployment time series (via `fredapi` library, series ID `PAPHIL5URN` for Philadelphia County).
3. **Policing data**: Limited availability - no programmatic API. Must use static reports from Philadelphia Controller's Office and OpenDataPhilly. Arrest rates available from DAO Data Dashboard but not via API.
4. **Geographic alignment**: OpenDataPhilly provides official crosswalk files for 2020 Census block groups to Philadelphia Police District boundaries, addressing MAUP concerns.
5. **Caching**: Use `requests-cache` library with `expire_after` parameter to avoid API rate limits. FRED returns 429 status when rate limited.
6. **Detrending**: Use `statsmodels.tsa.tsatools.detrend` for linear detrending before correlation analysis. The existing `stats_utils.py` provides correlation testing infrastructure.

**Primary recommendation:** Implement a modular data ingestion pipeline with separate modules for each external data type (`weather_data.py`, `economic_data.py`, `policing_data.py`) that inherit patterns from existing analysis modules. Use `requests-cache` for all HTTP requests and store cached data in `data/external/` as parquet files. Apply detrending using `statsmodels.tsa.tsatools.detrend` before any correlation analysis to address spurious correlation risk.

## Standard Stack

### Core Libraries

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `meteostat` | 1.6+ | Historical daily weather data | Official Python library with Pandas integration, no API key required for basic usage |
| `census` | 0.8+ | US Census API wrapper | Most popular Python wrapper for US Census ACS data |
| `fredapi` | 0.5+ | FRED Economic Data API | Standard Python wrapper for FRED, returns pandas DataFrames |
| `statsmodels` | 0.14+ | Detrending and econometric analysis | Required for `tsatools.detrend` and correlation analysis |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `requests-cache` | 1.2+ | HTTP response caching | All external API calls to avoid rate limits |
| `python-dotenv` | 1.0+ | API key management | Load API keys from `.env` file |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `meteostat` | Direct Meteostat API (RapidAPI) | API requires key, has rate limits; library is simpler |
| `census` | `cenpy` or `censusdis` | `cenpy` less maintained; `censusdis` newer but smaller community |
| `fredapi` | `pyfredapi` | `pyfredapi` has more features but `fredapi` is more established |
| `requests-cache` | Manual caching with SQLite/parquet | More control but reinventing the wheel |

**Installation:**
```bash
# Core external data libraries
pip install meteostat census fredapi statsmodels

# Caching and configuration
pip install requests-cache python-dotenv

# Already installed (Phase 1)
# pip install pandas numpy scipy pymannkendall
```

## Architecture Patterns

### Recommended Project Structure

```
analysis/
├── external_data/
│   ├── __init__.py           # Module exports
│   ├── base.py               # Base classes for external data ingestion
│   ├── weather_data.py       # Meteostat integration
│   ├── economic_data.py      # Census + FRED integration
│   ├── policing_data.py      # Static data loaders
│   └── correlation_analysis.py  # Detrended correlation analysis
├── stats_utils.py            # Existing: statistical testing (20+ functions)
├── utils.py                  # Existing: data loading, validation
├── config.py                 # Existing: STAT_CONFIG, paths
└── reproducibility.py        # Existing: DataVersion, seed setting

data/
├── crime_incidents_combined.parquet  # Existing: main dataset
└── external/
    ├── weather_daily_2006_2025.parquet
    ├── census_acs_2020_5year.parquet
    ├── fred_unemployment_philadelphia.parquet
    └── police_district_crosswalk.parquet

.env                        # API keys (gitignored)
```

### Pattern 1: External Data Ingestion Module

All external data modules follow this structure for consistency:

```python
"""
External weather data ingestion for Philadelphia crime analysis.

Uses Meteostat library to fetch daily historical weather data
for Philadelphia coordinates. Data cached locally to avoid API limits.
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np
from datetime import date
import requests_cache
from pathlib import Path

# Local imports following project patterns
from analysis.config import STAT_CONFIG, DATA_DIR
from analysis.reproducibility import set_global_seed, get_analysis_metadata

# Philadelphia coordinates
PHILLY_LAT = 39.9526
PHILLY_LON = -75.1652

# Cache configuration
EXTERNAL_DATA_DIR = DATA_DIR.parent / "data" / "external"
EXTERNAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Staleness settings (days)
WEATHER_CACHE_STALENESS = 7    # Weather doesn't change
CENSUS_CACHE_STALENESS = 365   # Annual data
FRED_CACHE_STALENESS = 30      # Monthly updates


def fetch_weather_data(
    start_date: date,
    end_date: date,
    use_cache: bool = True,
    force_refresh: bool = False
) -> pd.DataFrame:
    """
    Fetch daily weather data for Philadelphia.

    Args:
        start_date: Start of date range
        end_date: End of date range
        use_cache: If True, use cached data if available
        force_refresh: If True, fetch fresh data even if cached exists

    Returns:
        DataFrame with columns: date, tavg, tmin, tmax, prcp, snow
    """
    cache_path = EXTERNAL_DATA_DIR / "weather_daily_2006_2025.parquet"

    # Check cache
    if use_cache and not force_refresh and cache_path.exists():
        cached = pd.read_parquet(cache_path)
        # Check staleness
        # ... staleness check logic ...
        return cached

    # Fetch from Meteostat
    import meteostat as ms

    point = ms.Point(PHILLY_LAT, PHILLY_LON)
    data = ms.daily(point, start_date, end_date)
    df = data.fetch()

    # Save to cache
    df.to_parquet(cache_path)
    return df


def align_weather_with_crime(
    crime_df: pd.DataFrame,
    weather_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge daily weather data with daily crime counts.

    Handles temporal alignment by aggregating crime to daily level
    and joining on date column.
    """
    # Aggregate crime to daily
    daily_crime = crime_df.groupby('dispatch_date').size().reset_index(name='crime_count')

    # Merge with weather
    merged = daily_crime.merge(weather_df, left_on='dispatch_date', right_index=True, how='left')
    return merged
```

### Pattern 2: Detrended Correlation Analysis

**Critical:** Always detrend time series before correlation to avoid spurious correlations.

```python
"""
Detrended correlation analysis between crime and external variables.

Addresses the critical pitfall of spurious correlations in long-term
trending data (20-year drift will correlate regardless of true relationship).
"""

from typing import Dict, Tuple
import pandas as pd
import numpy as np
from statsmodels.tsa.tsatools import detrend
from scipy import stats

from analysis.stats_utils import (
    correlation_test,
    mann_kendall_test,
    apply_fdr_correction
)


def detrend_series(series: pd.Series, order: int = 1) -> pd.Series:
    """
    Remove linear trend from time series.

    Uses statsmodels.tsa.tsatools.detrend which fits a polynomial
    of specified order and returns residuals.

    Args:
        series: Time series data (must be numeric)
        order: Order of polynomial to fit (1=linear, 2=quadratic)

    Returns:
        Detrended series as pandas Series with original index
    """
    detrended = detrend(series.values, order=order)
    return pd.Series(detrended, index=series.index)


def analyze_crime_weather_correlation(
    crime_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    alpha: float = 0.01  # Matching STAT_CONFIG["alpha"]
) -> Dict:
    """
    Analyze correlation between crime rates and weather variables.

    **IMPORTANT:** Applies detrending to both series to address
    spurious correlation risk from shared 20-year drift.

    Process:
    1. Align data temporally (daily aggregation)
    2. Test for trends in both series (Mann-Kendall)
    3. Detrend if significant trend present
    4. Compute correlation on detrended residuals
    5. Report effect size with 99% CI

    Args:
        crime_df: Crime incidents with dispatch_date column
        weather_df: Daily weather with date index
        alpha: Significance level (default 0.01 for 99% CI)

    Returns:
        Dict with correlation results, trend tests, detrending info
    """
    # Step 1: Aggregate crime to daily
    daily_crime = crime_df.groupby('dispatch_date').size()
    daily_crime.name = 'crime_count'

    # Step 2: Align dates
    aligned = pd.DataFrame({
        'crime': daily_crime,
        'temperature': weather_df['tavg'],
        'precipitation': weather_df['prcp']
    }).dropna()

    # Step 3: Test for trends (Mann-Kendall)
    crime_trend = mann_kendall_test(aligned['crime'].values, alpha=alpha)
    temp_trend = mann_kendall_test(aligned['temperature'].values, alpha=alpha)

    # Step 4: Detrend if needed
    crime_detrended = detrend_series(aligned['crime']) if crime_trend['is_significant'] else aligned['crime']
    temp_detrended = detrend_series(aligned['temperature']) if temp_trend['is_significant'] else aligned['temperature']

    # Step 5: Correlation on detrended data
    corr_result = correlation_test(
        crime_detrended.values,
        temp_detrended.values,
        method='auto',
        alpha=alpha
    )

    return {
        'correlation': corr_result,
        'crime_trend': crime_trend,
        'temperature_trend': temp_trend,
        'n_obs': len(aligned),
        'detrending_applied': crime_trend['is_significant'] or temp_trend['is_significant']
    }
```

### Anti-Patterns to Avoid

- **Anti-pattern: Correlating raw trending data**
  - Why: 20-year trends will correlate due to shared drift, not causal relationship
  - Instead: Always apply `detrend()` from `statsmodels.tsa.tsatools` before correlation

- **Anti-pattern: Ignoring MAUP (Modifiable Areal Unit Problem)**
  - Why: Results change with boundary choices (census tract vs block group vs district)
  - Instead: Use official crosswalk files and analyze at multiple scales

- **Anti-pattern: Treating 2026 data as complete**
  - Why: 2026 data is incomplete (only through January 20, 2026)
  - Instead: Exclude 2026 from trend analysis

- **Anti-pattern: Making API calls without caching**
  - Why: Rate limits will block analysis, FRED returns 429 status
  - Instead: Use `requests-cache` with appropriate `expire_after` for each data source

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTP caching | Custom SQLite/JSON cache | `requests-cache` | Handles staleness, expiration, backends properly |
| Weather data fetching | Scraping weather websites | `meteostat` | Provides clean Pandas integration, multiple data sources |
| Census API queries | Manual requests with URL construction | `census` library | Handles variable names, geography codes, API authentication |
| Detrending | Manual linear regression | `statsmodels.tsa.tsatools.detrend` | Battle-tested, handles edge cases, multiple polynomial orders |
| API rate limiting | Custom `time.sleep()` | `requests-cache` with `expire_after` | Preventative caching beats reactive throttling |

**Key insight:** External data integration has many edge cases (rate limits, staleness, network errors, API changes). Established libraries have already solved these problems.

## Common Pitfalls

### Pitfall 1: Spurious Correlations from Trend Drift

**What goes wrong:** Long-term trends (20 years) in both crime and external variables create artificial correlation. Temperature increases over 20 years, crime patterns shift over 20 years - they correlate but not causally.

**Why it happens:** Pearson/Spearman correlation captures any monotonic relationship, including shared secular trends. In 20-year datasets, many variables trend upward due to population growth, urbanization, climate change.

**How to avoid:**
1. **Always test for trend first** using Mann-Kendall test (already in `stats_utils.py`)
2. **Apply detrending** using `statsmodels.tsa.tsatools.detrend(order=1)` for linear trends
3. **Correlate residuals**, not raw data
4. **Document detrending** in all reports

**Warning signs:** Correlation coefficient > 0.7 on raw data without obvious causal mechanism.

### Pitfall 2: Temporal Misalignment

**What goes wrong:** Daily weather data aggregated to monthly for comparison with monthly economic data loses information and creates misaligned timestamps.

**Why it happens:** Different sources have different native resolutions:
- Weather: Daily
- Crime: Daily (incident level)
- Economic: Monthly or annual (ACS 5-year estimates)
- Policing: Annual reports

**How to avoid:**
1. **Aggregate to lowest common resolution** (usually daily for crime-weather, monthly for crime-economic)
2. **Use proper date joins** (not integer indexes)
3. **Document alignment decisions** in reports
4. **For economic data:** Use time lagged models (e.g., Q1 economic data vs Q2 crime)

**Warning signs:** DataFrame length mismatch after merge, warnings about multi-index issues.

### Pitfall 3: MAUP (Modifiable Areal Unit Problem)

**What goes wrong:** Analysis results change depending on geographic boundaries used (census tract vs block group vs police district).

**Why it happens:** Census data uses tracts/block groups, police data uses districts. These boundaries don't align perfectly. A district may contain parts of 10 different tracts.

**How to avoid:**
1. **Use official crosswalk files** from OpenDataPhilly: `2020-census-police-district-crosswalk`
2. **Analyze at multiple scales** (tract, block group, district) and compare
3. **Weight census data by overlap** when aggregating to districts
4. **Document boundary choices** in all spatial analyses

**Warning signs:** District-level economic indicators don't match district characteristics; sudden jumps at boundaries.

### Pitfall 4: API Rate Limits

**What goes wrong:** Analysis script fails mid-run with HTTP 429 errors. Progress lost, partial results saved.

**Why it happens:**
- FRED API: Unknown exact limit, returns 429 when exceeded
- Census API: 500 requests per day per key (undocumented)
- Meteostat: No key required but RapidAPI endpoint has limits

**How to avoid:**
1. **Use `requests-cache`** with appropriate expiration:
   ```python
   requests_cache.install_cache(
       'api_cache',
       expire_after=timedelta(days=1),
       allowable_methods=['GET']
   )
   ```
2. **Check cache before fetching:**
   ```python
   cache_path = EXTERNAL_DATA_DIR / "weather.parquet"
   if cache_path.exists() and not force_refresh:
       return pd.read_parquet(cache_path)
   ```
3. **Store intermediate results** as parquet files
4. **Use exponential backoff** for retries

**Warning signs:** HTTP 429 responses, `ConnectionError` exceptions, script hangs.

### Pitfall 5: Missing Police Data

**What goes wrong:** Planning policing correlation analysis, then discovering no programmatic API exists.

**Why it happens:** Philadelphia Police Department does not publish staffing levels or arrest rates via API. Only static PDF reports and manual dashboards exist.

**How to avoid:**
1. **Document data limitations** upfront (this research note)
2. **Use available sources:**
   - Philadelphia Controller's Office PPD Review reports (2022, 2024)
   - OpenDataPhilly crosswalk files
   - DAO Data Dashboard for arrest rates (manual download only)
3. **Consider proxy variables:** Crime clearance rates, response times (if available)
4. **State limitations clearly** in reports

**Warning signs:** No official API documentation found, only PDF reports.

## Code Examples

### Example 1: Meteostat Weather Data Fetching

```python
# Source: https://dev.meteostat.net/python
from datetime import date
import meteostat as ms

# Philadelphia coordinates
PHILLY_LAT, PHILLY_LON = 39.9526, -75.1652

# Create Point object
point = ms.Point(PHILLY_LAT, PHILLY_LON)

# Define date range (max 10 years per request)
START = date(2006, 1, 1)
END = date(2015, 12, 31)

# Fetch daily data
data = ms.daily(point, START, END)
df = data.fetch()

# Result columns:
# - tavg: Average temperature (°C)
# - tmin: Minimum temperature (°C)
# - tmax: Maximum temperature (°C)
# - prcp: Precipitation total (mm)
# - snow: Snow depth (mm)
# - wdir: Wind direction (degrees)
# - wspd: Wind speed (km/h)
```

### Example 2: Census API with Authentication

```python
# Source: https://github.com/datamade/census
from census import Census
import pandas as pd

# API key from environment variable or .env file
import os
from dotenv import load_dotenv
load_dotenv()

CENSUS_API_KEY = os.getenv('CENSUS_API_KEY')

# Initialize Census client for ACS 5-year estimates
c = Census(CENSUS_API_KEY, year=2020)

# Philadelphia County FIPS code: 42101
PHILADELPHIA_COUNTY_FIPS = '42101'

# Fetch economic indicators for all tracts in Philadelphia
# Variables: B19013_001E (median income), B17001_002E (poverty count)
economic_data = c.acs5.get((
    'NAME', 'B19013_001E', 'B17001_002E', 'B23025_005E'
), {'for': 'tract:*', 'in': f'state:42+county:101'})

# Convert to DataFrame
df = pd.DataFrame(economic_data)
```

### Example 3: FRED API Unemployment Data

```python
# Source: https://github.com/mortada/fredapi
from fredapi import Fred
import os

# API key from environment
FRED_API_KEY = os.getenv('FRED_API_KEY')
fred = Fred(api_key=FRED_API_KEY)

# Philadelphia County unemployment rate series ID: PAPHIL5URN
unemployment_df = fred.get_series('PAPHIL5URN', observation_start='2006-01-01')

# Returns pandas Series with monthly unemployment rate (percent)
# Frequency: Monthly
# Units: Percent, Not Seasonally Adjusted
```

### Example 4: Detrending with statsmodels

```python
# Source: https://www.statsmodels.org/stable/generated/statsmodels.tsa.tsatools.detrend.html
from statsmodels.tsa.tsatools import detrend
import pandas as pd
import numpy as np

# Example: Detrend crime counts
crime_series = pd.Series([...])  # Daily or monthly crime counts

# Linear detrending (order=1)
crime_detrended = detrend(crime_series.values, order=1)

# Convert back to Series
crime_detrended = pd.Series(crime_detrended, index=crime_series.index)

# For quadratic trends (rare):
# crime_detrended = detrend(crime_series.values, order=2)
```

### Example 5: requests-cache Configuration

```python
# Source: https://requests-cache.readthedocs.io/en/stable/user_guide/expiration.html
import requests_cache
from datetime import timedelta

# Install cache for all requests
requests_cache.install_cache(
    cache_name='api_cache',  # Creates api_cache.sqlite
    expire_after=timedelta(days=1),  # Default expiration
    allowable_methods=['GET', 'POST']  # Cache POST too if needed
)

# Or use a session for specific URLs
session = requests_cache.CachedSession('weather_cache', expire_after=timedelta(hours=6))
response = session.get('https://dev.meteostat.net/...')

# Check cache info
print(response.from_cache)  # True if from cache, False if fresh
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual CSV download | Programmatic API access with caching | ~2020 | Reproducible, automated pipelines |
| Correlation without detrending | Mandatory detrending before correlation | Ongoing | Prevents spurious correlations |
| Single geographic scale | Multi-scale analysis (tract, district, city) | ~2018 | Addresses MAUP concerns |
| Static reports | Automated markdown with embedded plots | ~2021 | Self-documenting analysis |

**Deprecated/outdated:**
- **Direct Meteostat API calls**: Use Python library instead (cleaner interface, no auth needed)
- **Census CSV downloads**: Use `census` library for programmatic access
- **Manual rate limiting with `time.sleep()`**: Use `requests-cache` instead
- **Excel for data cleaning**: Use pandas parquet files

## Open Questions

### Question 1: Policing Data Availability
**What we know:**
- Philadelphia Police Department does not publish staffing levels via API
- Controller's Office has reports (2022, 2024) but not machine-readable
- DAO Data Dashboard has arrest rates but requires manual download

**What's unclear:**
- Whether historical staffing levels by district exist in any format
- Whether clearance rates (solved cases) are available programmatically

**Recommendation:** Document this limitation explicitly. Use available reports for one-time analysis. Consider omitting CORR-03 if data is insufficient for rigorous analysis.

### Question 2: Optimal Economic Variables
**What we know:**
- FRED provides county-level unemployment (PAPHIL5URN) monthly
- Census ACS provides tract-level poverty, income, demographics (5-year estimates)
- Different temporal resolutions (monthly vs annual)

**What's unclear:**
- Which economic variables have strongest theoretical link to crime (literature needed)
- Whether to use leading or lagged economic indicators
- How to handle Census 5-year estimates (data represents 2016-2020 average, not point-in-time)

**Recommendation:** Start with unemployment rate (most common in criminology literature) and poverty rate. Add others as exploratory variables. Use time-lagged models (e.g., annual economic data vs following year crime).

### Question 3: Crosswalk File Format and Usage
**What we know:**
- OpenDataPhilly provides "2020 Census to Police District Crosswalk"
- DVRPC also provides crosswalk files

**What's unclear:**
- Exact file format (shapefile, geojson, csv?)
- Whether crosswalk includes population weighting
- How to handle districts that cross tract boundaries

**Recommendation:** Download and inspect crosswalk file early in phase. Verify format and create helper function for weighting census data by overlap.

## Data Source Catalog

### Weather Data (Meteostat)

| Attribute | Value |
|-----------|-------|
| **Library** | `meteostat` |
| **Python Install** | `pip install meteostat` |
| **API Key Required** | No (for library), Yes (for RapidAPI endpoint) |
| **Temporal Resolution** | Daily |
| **Spatial Resolution** | Point-based (lat/lon) |
| **Date Range** | 1950-present (varies by station) |
| **Variables** | tavg, tmin, tmax, prcp, snow, wdir, wspd |
| **Rate Limit** | None documented for library; RapidAPI has limits |
| **Cache Strategy** | Local parquet, expire_after=7 days |
| **Confidence** | HIGH (official docs) |

### Economic Data - FRED

| Attribute | Value |
|-----------|-------|
| **Library** | `fredapi` |
| **Python Install** | `pip install fredapi` |
| **API Key Required** | Yes (free, 32-char key) |
| **Key Source** | https://fred.stlouisfed.org/docs/api/api_key.html |
| **Philadelphia Unemployment Series** | `PAPHIL5URN` |
| **Temporal Resolution** | Monthly |
| **Spatial Resolution** | County (Philadelphia County/City, PA) |
| **Date Range** | 1990-present |
| **Variables** | Unemployment rate (%) |
| **Rate Limit** | Undocumented, returns 429 when exceeded |
| **Cache Strategy** | Local parquet, expire_after=30 days |
| **Confidence** | HIGH (official docs) |

### Economic Data - US Census ACS

| Attribute | Value |
|-----------|-------|
| **Library** | `census` |
| **Python Install** | `pip install census` |
| **API Key Required** | Yes (free, required) |
| **Key Source** | https://api.census.gov/data/key_signup.html |
| **Dataset** | ACS 5-Year Estimates |
| **Temporal Resolution** | Annual (5-year average) |
| **Spatial Resolution** | Census tract, block group |
| **Relevant Variables** | B19013_001E (median income), B17001_002E (poverty), B23025_005E (unemployment) |
| **Philadelphia County FIPS** | 42101 (state:42, county:101) |
| **Rate Limit** | ~500 requests/day (undocumented) |
| **Cache Strategy** | Local parquet, expire_after=365 days |
| **Confidence** | HIGH (official docs) |

### Geographic Crosswalk

| Attribute | Value |
|-----------|-------|
| **Source** | OpenDataPhilly / DVRPC |
| **File Name** | "2020 Census to Police District Crosswalk" |
| **URL** | https://opendataphilly.org/datasets/2020-census-police-district-crosswalk/ |
| **Format** | Unknown (verify: likely shapefile or geojson) |
| **Purpose** | Maps census geographies to police districts |
| **Cache Strategy** | Static file, download once |
| **Confidence** | MEDIUM (exists but format unverified) |

### Policing Data

| Attribute | Value |
|-----------|-------|
| **Primary Source** | Philadelphia Controller's Office |
| **Report URL** | https://controller.phila.gov/philadelphia-reports/ppd-review/ |
| **Data Available** | District headcounts, staffing levels |
| **Format** | PDF report (not machine-readable) |
| **Arrest Rate Source** | DAO Data Dashboard (data.philadao.com) |
| **API Access** | No - manual download only |
| **Cache Strategy** | N/A (static reports) |
| **Confidence** | HIGH (exists but limited accessibility) |

## Sources

### Primary (HIGH confidence)

- [Meteostat Python Documentation](https://dev.meteostat.net/python) - Daily weather data API
- [Meteostat Point Daily API](https://dev.meteostat.net/api/point/daily) - API endpoint documentation
- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/fred/) - Economic data API
- [FRED Series Observations](https://fred.stlouisfed.org/docs/api/fred/series_observations) - Series data retrieval
- [FRED API Key](https://fred.stlouisfed.org/docs/api/api_key.html) - API key instructions
- [statsmodels detrend function](https://www.statsmodels.org/stable/generated/statsmodels.tsa.tsatools.detrend.html) - Detrending API
- [requests-cache Expiration](https://requests-cache.readthedocs.io/en/stable/user_guide/expiration.html) - Cache configuration
- [US Census Data API](https://www.census.gov/data/developers/data-sets.html) - Available datasets
- [census library GitHub](https://github.com/datamade/census) - Python wrapper for Census API
- [fredapi GitHub](https://github.com/mortada/fredapi) - Python wrapper for FRED API

### Secondary (MEDIUM confidence)

- [Working with ACS data in Python](https://nicolepaul.io/post/python-census/) - Tutorial with examples (verified against official docs)
- [Philadelphia Unemployment FRED Series](https://fred.stlouisfed.org/series/PAPHIL5URN) - Confirmed series ID
- [2020 Census to Police District Crosswalk](https://opendataphilly.org/datasets/2020-census-police-district-crosswalk/) - Geographic alignment file
- [Philadelphia Controller's PPD Review](https://controller.phila.gov/philadelphia-reports/ppd-review/) - Staffing data source

### Tertiary (LOW confidence - marked for validation)

- Various tutorials on Medium, DataCamp, YouTube - Used only for cross-checking official documentation
- Stack Overflow discussions - Verified against official sources where mentioned

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified via official documentation
- Architecture: HIGH - Based on existing project patterns from Phase 1
- Pitfalls: HIGH - Well-documented issues in longitudinal analysis (spurious correlation, MAUP)
- Data sources: MEDIUM - Weather and economic sources verified; policing data availability confirmed but limited

**Research date:** 2026-01-31
**Valid until:** 2026-03-01 (60 days - APIs and libraries stable, but verify before implementation)

**Next steps for planner:**
1. Verify crosswalk file format early in phase
2. Decide whether CORR-03 (policing data) is feasible given API limitations
3. Plan for API key management (.env file pattern)
4. Design correlation analysis module with mandatory detrending step
