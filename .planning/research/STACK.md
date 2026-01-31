# Stack Research

**Domain:** Python-based exploratory data analysis with correlation analysis and interactive dashboards
**Researched:** 2025-01-30
**Confidence:** HIGH

## Recommended Stack

### Core Dashboard Framework

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Streamlit** | 1.40+ | Interactive dashboard framework | Fastest time-to-prototype for data science dashboards; pure Python (no HTML/CSS/JS required); excellent for single-use research dashboards; reactive UI with session state management; extensive documentation and active ecosystem |
| **Plotly** | 6.0+ | Interactive visualization library | Native integration with both Streamlit and Dash; 40+ chart types including geographic maps, time series, statistical plots; WebGL-accelerated rendering for large datasets (`scattergl`, `scattermapbox`); publication-quality static export via Kaleido |

### Statistical Analysis

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| **statsmodels** | 0.14.6+ | Econometric and time series analysis | Academic-standard statistical modeling; hypothesis tests, correlation analysis, time series decomposition; comprehensive API for regression, ANOVA, unit root tests; outputs include p-values, confidence intervals, effect sizes |
| **SciPy** | 1.16+ | Scientific computing and statistical tests | Pearson, Spearman, Kendall correlation functions; chi-squared tests, Fisher's exact; linear regression; extensive hypothesis testing library |
| **seaborn** | 0.13.2+ | Statistical visualization | Publication-quality statistical plots (heatmaps, violin plots, pair plots); minimal code for attractive defaults; built on matplotlib with higher-level interface; widely cited in academic publications |

### Geographic Visualization

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| **folium** | 0.20.0+ | Interactive Leaflet maps | Choropleth maps for district-level crime visualization; interactive markers with popups; GeoJSON support for Philadelphia police district boundaries; pure Python interface |
| **Plotly Express** | 6.0+ | Geographic scatter and density maps | `scatter_mapbox` for point-level crime data; choropleth maps for aggregated statistics; built-in map tiles (Carto, OpenStreetMap); integrates with dashboard framework |

### External Data Sources

| Source | Type | Access | Why Recommended |
|--------|------|--------|-----------------|
| **Meteostat** | Weather (historical) | Python library or API | Free access to historical weather data; hourly and daily aggregations; includes temperature (tavg, tmin, tmax), precipitation (prcp), wind; data aggregated from multiple governmental sources; Python SDK available via pip |
| **NOAA CDO API** | Weather (historical) | REST API | Official U.S. climate data source; free access with token; comprehensive historical weather records; station-based or point-based queries |
| **U.S. Census API** | Economic/demographic | REST API | American Community Survey (ACS) 5-year estimates; poverty rates, median income, unemployment data; free with API key; geographically granular (tract, county, city level) |
| **FRED API** | Economic time series | REST API | Philadelphia-specific unemployment rate series (PAPHIL5URN); Federal Reserve Economic Data; free with API key; long historical time series (1990-present) |
| **OpenDataPhilly** | Crime/policing | Web portal + API | Official Philadelphia open data repository; crime incidents dataset (already in use); additional datasets for arrests, policing resources; API access for programmatic queries |
| **PhilaDAO Dashboard** | Arrest statistics | Web interface | District Attorney Office arrest data; offense type breakdowns; complementary to PPD crime data |

### Data Processing

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| **pandas** | 2.2+ | Data manipulation | Already in use; core DataFrame operations; time series handling; merge/join operations for combining crime data with external sources |
| **polars** | 1.0+ | High-performance dataframe (optional) | For datasets exceeding memory; faster than pandas for large aggregations; compatible with Plotly via `.to_pandas()` conversion |

### HTTP/API Access

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| **requests** | 2.32+ | HTTP client | Industry-standard Python HTTP library; simple API for REST calls; session management for API rate limits; built-in JSON handling |

### Static Image Export

| Tool | Version | Purpose | Why Recommended |
|------|---------|---------|-----------------|
| **Kaleido** | 1.0+ | Static image export from Plotly | Export to PNG, JPEG, SVG, PDF formats; publication-quality resolution with scale parameter; cross-platform; simple pip install; replaces deprecated Orca |

## Installation

```bash
# Core dashboard framework
pip install streamlit>=1.40 plotly>=6.0

# Statistical analysis
pip install statsmodels>=0.14.6 scipy>=1.16 seaborn>=0.13.2

# Geographic visualization
pip install folium>=0.20.0

# External data access
pip install meteostat requests>=2.32

# Image export
pip install kaleido>=1.0

# Optional: high-performance data processing
pip install polars>=1.0
```

## Alternatives Considered

| Category | Recommended | Alternative | When to Use Alternative |
|----------|-------------|-------------|-------------------------|
| Dashboard | Streamlit | Dash (Plotly) | Use Dash if building production-grade, multi-page applications with complex custom layouts; use Dash if you need fine-grained control over component styling and callbacks; Streamlit is better for rapid prototyping and research-focused dashboards |
| Weather Data | Meteostat | NOAA CDO API | Use NOAA directly if you need station-specific raw data or data not available through Meteostat; Meteostat provides a simpler Python interface for most use cases |
| Statistical Tests | SciPy | pingouin | Use pingouin if you need more specialized effect size calculations or Bayesian tests; SciPy is sufficient for standard correlation and hypothesis testing |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **Tableau, Power BI** | Proprietary, requires licensing, less programmatic control; difficult to reproduce analyses | Streamlit/Dash with Plotly for full Python integration |
| **Paid weather APIs** (Visual Crossing, WeatherAPI) | Unnecessary cost; free alternatives provide adequate historical data | Meteostat or NOAA CDO API (both free) |
| **D3.js** | Requires JavaScript/HTML/CSS knowledge; steeper learning curve for Python-only users | Plotly Express for interactive charts, Folium for maps |
| **Bokeh** | Less mature ecosystem than Plotly; fewer examples and community resources | Plotly for broader integration and documentation |
| **Orca** (legacy) | Deprecated; difficult installation; replaced by Kaleido | Kaleido for static image export |
| **Enterprise BI tools** (Looker, Sisense) | Overkill for research project; expensive; designed for business dashboards not academic analysis | Streamlit for free, customizable research dashboard |

## Data Source Integration Patterns

### Weather Data Integration

```python
# Meteostat for Philadelphia weather
from meteostat import Point, Daily
# Philadelphia coordinates: 39.9526° N, 75.1652° W
philadelphia = Point(39.9526, -75.1652, 12)  # lat, lon, elevation
data = Daily(philadelphia, start, end).fetch()
# Returns: tavg, tmin, tmax, prcp, snow, wspd, pres, tsun
```

### Census Economic Data Integration

```python
# U.S. Census API for ACS 5-year estimates
import requests
BASE_URL = "https://api.census.gov/data/2022/acs/acs5"
# Example: Poverty rate for Philadelphia County
response = requests.get(f"{BASE_URL}?get=NAME,S1701_C01_001E&for=county:101&in=state:42")
```

### FRED Economic Data Integration

```python
# FRED API for Philadelphia unemployment rate
import requests
FRED_API_KEY = "your-key"
series_id = "PAPHIL5URN"  # Philadelphia unemployment rate
response = requests.get(
    f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
)
```

## Stack Patterns by Variant

**If building a quick exploratory dashboard for personal research:**
- Use Streamlit with Plotly Express
- Single-page app with sidebar filters
- Deploy locally or via Streamlit Community Cloud (free)

**If building a production dashboard for broader publication:**
- Use Dash with Dash Bootstrap Components for professional styling
- Multi-page app with persistent state
- Consider deploying via Heroku, AWS, or Streamlit Community Cloud

**If dataset grows beyond 16GB RAM:**
- Use Polars for data loading and aggregation
- Sample data for interactive visualizations
- Use Datashader with Plotly for large-scale geographic visualizations

**If generating publication figures:**
- Use Plotly for interactive exploration
- Export to high-resolution PNG/SVG via Kaleido for papers
- Use seaborn for statistical figures in matplotlib style

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| plotly 6.0+ | streamlit 1.40+, Dash 3+ | Native integration; no version conflicts |
| statsmodels 0.14.6 | scipy 1.16+, numpy 1.23+ | Standard scientific Python stack |
| kaleido 1.0+ | plotly 5.0+ | Required for static image export |
| folium 0.20.0 | No strict dependencies | Standalone Leaflet wrapper |

## Philadelphia-Specific Data Sources

| Source | URL | Variables Available | Geographic Granularity |
|--------|-----|---------------------|------------------------|
| OpenDataPhilly Crime | [opendataphilly.org](https://opendataphilly.org/datasets/crime-incidents/) | Incident type, date, location, district | Point-level (lat/lon) |
| OpenDataPhilly Economy | [opendataphilly.org/economy](https://opendataphilly.org/categories/economy/) | Various economic indicators | City/neighborhood level |
| Census ACS (Philly) | [api.census.gov](https://api.census.gov/data/2022/acs/acs5) | Poverty, income, employment, demographics | Tract, county, place level |
| FRED Philly Unemployment | [fred.stlouisfed.org/series/PAPHIL5URN](https://fred.stlouisfed.org/series/PAPHIL5URN) | Unemployment rate | Philadelphia MSA monthly |
| PhilaDAO Arrests | [data.philadao.com](https://data.philadao.com/Arrest_Report.html) | Arrest counts by offense type | Citywide |
| Meteostat Philadelphia | [dev.meteostat.net](https://dev.meteostat.net) | Temperature, precipitation, wind | Point-based (city center) |

## Sources

- **Streamlit Docs** — Session state patterns, dataframes, Altair integration
- **Dash Documentation** — DataTable with backend paging, filtering, sorting; Datashader integration for large datasets
- **Plotly.py Documentation** — Geographic scatter maps, time series line charts, performance with large datasets, scattergl for WebGL acceleration
- **Meteostat Documentation** — Daily and hourly weather API endpoints, available variables (temperature, precipitation, wind, pressure)
- **SciPy Documentation** — Version 1.16.2; correlation tests (Pearson, Spearman, Kendall), chi-squared tests, Fisher's exact
- **Web Search Verification (2025)** — Streamlit vs Dash comparison articles; weather API options; economic data sources

---

*Stack research for: Python EDA with correlation analysis and interactive dashboards*
*Researched: 2025-01-30*
