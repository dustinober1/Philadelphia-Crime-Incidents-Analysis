# Architecture Research

**Domain:** Exploratory Data Analysis (EDA) with correlation analysis and interactive dashboards
**Researched:** 2025-01-30
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
+-----------------------------------------------------------------------+
│                         PRESENTATION LAYER                            |
+-----------------------------------------------------------------------+
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ Report          │  │  Dashboard      │  │  Publication        │  │
│  │ Generators      │  │  (Streamlit)    │  │  Outputs            │  │
│  │  (analysis/*_   │  │                 │  │  (figures/tables)   │  │
│  │   report.py)    │  │                 │  │                     │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────────┘  │
+-----------┴--------------------┴---------------------┴----------------+
            │                    │                        │
            ▼                    ▼                        ▼
+-----------------------------------------------------------------------+
│                         ANALYSIS LAYER                                |
+-----------------------------------------------------------------------+
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ Existing        │  │  Correlation    │  │  Statistical        │  │
│  │ Analysis        │  │  Analysis       │  │  Analysis           │  │
│  │ Modules         │  │  (NEW)          │  │  (publication)      │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────────┘  │
+-----------┴--------------------┴---------------------┴----------------+
            │                    │                        │
            ▼                    ▼                        ▼
+-----------------------------------------------------------------------+
│                          DATA LAYER                                   |
+-----------------------------------------------------------------------+
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ Core Data       │  │  External Data  │  │  Derived/Cached     │  │
│  │ Loader          │  │  Ingestion      │  │  Data               │  │
│  │ (utils.load_    │  │  (NEW)          │  │  (processed/)       │  │
│  │  data)          │  │                 │  │                     │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────────┘  │
+-----------┴--------------------┴---------------------┴----------------+
            │                    │                        │
            ▼                    ▼                        ▼
+-----------------------------------------------------------------------+
│                        STORAGE LAYER                                  |
+-----------------------------------------------------------------------+
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ Crime Data      │  │  Weather Data   │  │  Economic Data      │  │
│  │ (parquet)       │  │  (CSV/API)      │  │  (CSV/API)          │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘  │
+-----------------------------------------------------------------------+
```

### Component Responsibilities

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| **Core Data Loader** (utils.py) | Load main parquet dataset, validate coordinates, extract temporal features | All analysis modules |
| **External Data Ingestion** (NEW) | Fetch weather, economic, policing data from APIs/files; merge with crime data on date/location | Correlation analysis, dashboard |
| **Analysis Modules** (analysis/*.py) | Perform statistical analysis; return results dicts with base64 plots | Report generators, dashboard |
| **Correlation Analysis** (NEW) | Compute correlations between crime and external factors; statistical tests | Report generators, dashboard |
| **Statistical Analysis** (NEW) | Significance tests, confidence intervals, effect sizes for publication | Publication outputs |
| **Report Generators** (*_report.py) | Orchestrate analysis modules; format markdown with embedded visualizations | All analysis modules |
| **Dashboard** (app.py) | Interactive UI with filters; cached data loading; real-time visualization | All analysis modules, external data |
| **Publication Outputs** (NEW) | Generate high-DPI figures, LaTeX tables, academic-formatted summaries | Analysis modules, statistical analysis |

## Recommended Project Structure

```
crime-incidents-philadelphia/
├── analysis/
│   ├── __init__.py
│   ├── config.py                 # Central configuration
│   ├── utils.py                  # Data loading, validation, helpers
│   ├── data_quality.py           # [existing] Data quality assessment
│   ├── temporal_analysis.py      # [existing] Temporal patterns
│   ├── categorical_analysis.py   # [existing] Crime types, districts
│   ├── spatial_analysis.py       # [existing] Geographic distribution
│   ├── cross_analysis.py         # [existing] Cross-dimensional analysis
│   ├── safety_trend.py           # [existing] Violent vs property trends
│   ├── summer_spike.py           # [existing] Summer surge patterns
│   ├── red_zones.py              # [existing] DBSCAN hotspots
│   ├── covid_lockdown.py         # [existing] COVID impact
│   ├── robbery_timing.py         # [existing] Robbery time patterns
│   ├── weighted_severity_analysis.py  # [existing] Severity scoring
│   │
│   ├── # === NEW MODULES ===
│   ├── external_ingestion.py     # Weather, economic, policing data
│   ├── correlation_analysis.py   # Crime vs external factors
│   ├── statistical_tests.py      # Significance, confidence intervals
│   │
│   ├── # === REPORT GENERATORS ===
│   ├── 06_generate_report.py     # [existing] Comprehensive EDA report
│   ├── 07_report_safety_trend.py # [existing] Safety trend report
│   ├── 08_report_summer_spike.py # [existing] Summer spike report
│   ├── 09_report_red_zones.py    # [existing] Red zones report
│   ├── 10_report_covid_lockdown.py # [existing] COVID impact report
│   ├── 11_report_robbery_timing.py  # [existing] Robbery timing report
│   ├── 12_report_correlation.py  # [NEW] Correlation analysis report
│   │
│   └── # === DASHBOARD SUPPORT ===
│   └── dashboard_utils.py        # Shared functions for Streamlit app
│
├── dashboard/
│   ├── app.py                    # Main Streamlit application
│   ├── pages/
│   │   ├── 1_overview.py         # Homepage: key metrics
│   │   ├── 2_temporal.py         # Time-based explorations
│   │   ├── 3_spatial.py          # Geographic exploration
│   │   ├── 4_correlation.py      # External factor correlations
│   │   └── 5_export.py           # Export data/figures
│   └── components/
│       ├── filters.py            # Shared filter widgets
│       ├── charts.py             # Reusable chart functions
│       └── tables.py             # Reusable table functions
│
├── data/
│   ├── crime_incidents_combined.parquet  # [existing] Main dataset
│   ├── external/                # [NEW] External datasets
│   │   ├── weather/
│   │   │   ├── philadelphia_weather_*.csv
│   │   │   └── README.md
│   │   ├── economic/
│   │   │   ├── philadelphia_unemployment_*.csv
│   │   │   └── README.md
│   │   └── policing/
│   │       ├── philadelphia_policing_*.csv
│   │       └── README.md
│   └── processed/               # Cached/merged datasets
│
├── publication/
│   └── figures/                 # [NEW] High-DPI figures for papers
│       ├── temporal/
│       ├── spatial/
│       └── correlation/
│
├── reports/                     # [existing] Markdown reports
│
├── .streamlit/                  # Streamlit configuration
│   └── config.toml
│
├── requirements.txt
├── CLAUDE.md
└── README.md
```

### Structure Rationale

- **`analysis/`**: Core analytical logic, organized by domain (temporal, spatial, categorical). Analysis modules return results dicts; report generators consume them.
- **`dashboard/`**: Separated from analysis to avoid coupling UI with logic. Uses multipage pattern for navigation.
- **`data/external/`**: External datasets have their own namespace with READMEs documenting source and update cadence.
- **`data/processed/`**: Derived/merged datasets cached for performance. Avoids re-running expensive joins.
- **`publication/`**: High-resolution outputs separate from interactive assets. Publication figures use different DPI and styling.

## Architectural Patterns

### Pattern 1: Analysis Module Function Signature

**What:** Analysis modules follow a consistent `analyze_*() -> dict` pattern returning results with base64-encoded plots.

**When to use:** All new analysis modules (correlation, statistical tests) should follow this pattern.

**Trade-offs:**
- Pro: Predictable interface, easy to test, works with report generators AND dashboard
- Pro: Decouples analysis logic from presentation
- Con: Requires base64 encoding overhead for large figures

**Example:**
```python
# analysis/correlation_analysis.py
def analyze_weather_correlation() -> dict:
    """Run correlation analysis between crime and weather factors.

    Returns:
        Dictionary with:
        - 'stats': correlation coefficients, p-values
        - 'plot': base64-encoded heatmap
        - 'summary': text summary of findings
    """
    df = load_data(clean=False)
    df = extract_temporal_features(df)
    weather_df = load_weather_data()  # NEW

    # Merge on date
    merged = merge_weather_crime(df, weather_df)

    # Compute correlations
    corr_matrix = merged[['temp', 'precipitation', 'crime_count']].corr()

    # Create visualization
    fig = create_correlation_heatmap(corr_matrix)
    plot_tag = create_image_tag(image_to_base64(fig))

    return {
        'correlation_matrix': corr_matrix,
        'plot': plot_tag,
        'summary': generate_summary(corr_matrix),
    }
```

### Pattern 2: External Data Ingestion with Caching

**What:** External data sources are fetched once and cached locally; ingest modules handle API rate limits, missing data, and temporal alignment.

**When to use:** All external data ingestion (weather, economic, policing).

**Trade-offs:**
- Pro: Avoids API rate limits, enables reproducibility
- Pro: Can run analyses offline after initial fetch
- Con: Requires staleness checks and update scripts

**Example:**
```python
# analysis/external_ingestion.py
from pathlib import Path
import requests
import pandas as pd

WEATHER_CACHE_PATH = Path("data/external/weather/philadelphia_weather.parquet")

@st.cache_data(ttl=3600)  # For dashboard: cache 1 hour
def load_weather_data(force_refresh: bool = False) -> pd.DataFrame:
    """Load Philadelphia weather data.

    Fetches from API if cache missing or force_refresh=True.
    Otherwise loads from local cache.
    """
    if WEATHER_CACHE_PATH.exists() and not force_refresh:
        return pd.read_parquet(WEATHER_CACHE_PATH)

    # Fetch from API
    df = fetch_weather_from_api()
    df.to_parquet(WEATHER_CACHE_PATH)
    return df
```

### Pattern 3: Dashboard as Analysis Orchestrator

**What:** Streamlit dashboard calls analysis modules directly, reusing the same `analyze_*()` functions as report generators.

**When to use:** Interactive dashboard building on existing analysis modules.

**Trade-offs:**
- Pro: Single source of truth for analysis logic
- Pro: Report and dashboard always consistent
- Con: Dashboard must handle blocking analysis calls (use @st.cache_data)

**Example:**
```python
# dashboard/app.py
import streamlit as st
from analysis.correlation_analysis import analyze_weather_correlation

st.set_page_config(page_title="Philadelphia Crime EDA")

@st.cache_data
def get_correlation_results():
    """Cache correlation analysis results."""
    return analyze_weather_correlation()

st.title("Crime Correlation Analysis")
results = get_correlation_results()

st.markdown(results['summary'])
st.image(results['plot'])  # Base64 string works directly
```

### Pattern 4: Publication Output Generation

**What:** Separate publication-quality figure generation that uses matplotlib's publication-ready styling (higher DPI, LaTeX fonts, specific sizes).

**When to use:** Generating figures/tables for academic papers or presentations.

**Trade-offs:**
- Pro: Publication-ready figures without manual editing
- Pro: Consistent styling across all figures
- Con: Different figure generation path than dashboard/reports

**Example:**
```python
# analysis/publication_outputs.py
import matplotlib.pyplot as plt

PUBLICATION_CONFIG = {
    'dpi': 300,
    'figsize': (6.4, 4.8),  # IEEE column width
    'font_family': 'serif',
    'font_size': 10,
}

def create_publication_figure(plot_type: str, data, output_path: str):
    """Create publication-ready figure.

    Args:
        plot_type: 'line', 'bar', 'heatmap', 'scatter'
        data: Data to plot
        output_path: Where to save the figure
    """
    plt.rcParams.update({
        'figure.dpi': PUBLICATION_CONFIG['dpi'],
        'font.family': PUBLICATION_CONFIG['font_family'],
        'font.size': PUBLICATION_CONFIG['font_size'],
    })

    fig, ax = plt.subplots(figsize=PUBLICATION_CONFIG['figsize'])
    # ... plotting logic ...

    fig.savefig(output_path, dpi=PUBLICATION_CONFIG['dpi'],
                bbox_inches='tight', format='pdf')
    plt.close(fig)
```

## Data Flow

### External Data Integration Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL DATA INGESTION                         │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Weather API  │    │ Economic API  │    │ Policing API  │
│  (NOAA/etc)   │    │  (Census/BLS) │    │  (OpenData)   │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  external_ingestion.py: fetch_weather(), fetch_economic(), etc.     │
│  - Handle pagination, rate limits                                   │
│  - Standardize date columns                                         │
│  - Save to data/external/*.parquet                                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Correlation/Statistical Analysis: merge external data with crime   │
│  - Temporal merge: on dispatch_date = weather_date                  │
│  - Geographic merge: on police_district (for economic/policing)     │
│  - Handle misalignment: forward-fill, aggregation                   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Results Dict: correlation_matrix, p_values, effect_sizes           │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   Report      │    │  Dashboard    │    │ Publication   │
│  Generator    │    │  (Streamlit)  │    │   Figures     │
└───────────────┘    └───────────────┘    └───────────────┘
```

### Dashboard Data Flow with Caching

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Interaction                             │
│                    (selects filters in Streamlit)                   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  @st.cache_data Decorated Functions                                 │
│  - load_data(date_range, districts)                                 │
│  - load_weather_data(date_range)                                    │
│  - analyze_temporal(date_range)                                     │
│  - compute_correlation(date_range)                                  │
│                                                                      │
│  Cache key: function args + source code hash                         │
│  TTL: Configurable per function (e.g., 1 hour for weather)          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Analysis Module Calls (same as report generators)                  │
│  - analyze_temporal_patterns()                                      │
│  - analyze_weather_correlation()                                    │
│  - analyze_district_patterns()                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Results Dict with Base64 Plots                                     │
│  - Displayed via st.markdown() or st.image()                        │
│  - Downloadable via st.download_button()                            │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Data Flows

1. **Crime Data Loading:** `parquet file` -> `load_data()` -> `validate_coordinates()` -> `extract_temporal_features()` -> analysis modules
2. **External Data Integration:** `API/file` -> `fetch_*()` -> `cache` -> `merge with crime` -> correlation analysis
3. **Report Generation:** analysis modules -> `results dict` -> `generate_markdown_report()` -> markdown file with base64 images
4. **Dashboard Interaction:** user filters -> `@st.cache_data` functions -> analysis modules -> results dict -> Streamlit UI
5. **Publication Output:** analysis modules -> `create_publication_figure()` -> high-DPI PDF/PNG files

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| **Current: 3.5M records, local 16GB RAM** | Sample for visualizations (existing pattern). Use parquet for fast columnar access. Cache merged external data. |
| **10M+ records** | Consider DuckDB or SQLite for querying. Pre-aggregate daily/monthly statistics. Streamlit lazy loading. |
| **100M+ records** | Move to database backend. Use dask for out-of-core computation. Dashboard pagination and virtual scrolling. |

### Scaling Priorities

1. **First bottleneck:** Dashboard interactivity with 3.5M records
   - Fix: Use `@st.cache_data` aggressively. Pre-compute aggregations. Sample for visualizations.

2. **Second bottleneck:** External data merge operations
   - Fix: Cache merged datasets. Use efficient join keys (date integers, not datetime strings).

## Anti-Patterns

### Anti-Pattern 1: Dashboard-Side Data Processing

**What people do:** Put data loading, filtering, and analysis logic directly in Streamlit app files.

**Why it's wrong:**
- Report generators can't reuse the logic
- Testing becomes difficult (need to run Streamlit)
- Logic couples with UI framework

**Do this instead:** Keep analysis logic in `analysis/` modules. Dashboard only handles filters and display.

### Anti-Pattern 2: Re-fetching External Data on Every Run

**What people do:** Call external APIs directly in analysis functions without caching.

**Why it's wrong:**
- Hits rate limits
- Slow execution
- Analyses become non-reproducible (API changes over time)

**Do this instead:** Fetch once, cache to `data/external/`. Check staleness on load.

### Anti-Pattern 3: Mixing Interactive and Publication Figure Styles

**What people do:** Use the same plot function for both dashboard and publication figures.

**Why it's wrong:**
- Dashboard plots are low resolution (web-optimized)
- Publication requires specific DPI, fonts, sizes
- Trade-offs make neither optimal

**Do this instead:** Separate `create_figure()` (dashboard) from `create_publication_figure()` (publication).

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| NOAA Weather API | `requests.get()` -> cache -> parquet | Daily fetch, historical data available |
| Census Bureau API | `census` library -> cache -> parquet | Economic indicators by district |
| Philadelphia OpenData | Socrata API or bulk download | Policing data, 311 calls |
| NIBRS / FBI Crime Data | Bulk CSV download | For comparison/validation |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| **analysis <-> dashboard** | Function calls with @st.cache_data | Dashboard imports analysis modules directly |
| **analysis <-> report** | Function calls, results dict pattern | Reports orchestrate multiple analysis modules |
| **external_ingestion <-> analysis** | Data merge on date/district keys | External ingest provides standardized DataFrames |
| **publication <-> analysis** | Function calls, high-DPI config | Publication outputs reuse analysis results |

## Build Order Dependencies

```
Phase 1: External Data Ingestion (must be first)
├── Set up data/external/ structure
├── Implement fetch_weather_data()
├── Implement fetch_economic_data()
├── Implement fetch_policing_data()
└── Create caching mechanism

Phase 2: Correlation Analysis (depends on Phase 1)
├── Merge external data with crime data
├── Implement analyze_weather_correlation()
├── Implement analyze_economic_correlation()
└── Create correlation report generator

Phase 3: Statistical Testing (depends on Phase 2)
├── Add significance tests to correlations
├── Implement confidence intervals
└── Create statistical utilities

Phase 4: Dashboard Foundation (can run in parallel)
├── Set up Streamlit project structure
├── Implement basic app.py with existing analysis
├── Create dashboard_utils.py
└── Add filter components

Phase 5: Dashboard Correlation Pages (depends on Phase 2, 4)
├── Add correlation pages to dashboard
├── Integrate external data filters
└── Add interactive correlation visualizations

Phase 6: Publication Outputs (depends on Phase 3)
├── Create publication_outputs.py
├── Generate high-DPI figures
├── Create LaTeX table export
└── Document publication pipeline
```

### Dependency Rationale

1. **External data first:** Correlation analysis cannot proceed without external data sources.
2. **Correlation before dashboard:** Dashboard correlation pages need working analysis functions.
3. **Statistical testing after correlation:** Build basic correlations first, add rigor second.
4. **Dashboard foundation in parallel:** Basic dashboard can show existing analyses immediately.
5. **Publication outputs last:** Need stable analysis results before generating publication figures.

## Sources

### HIGH Confidence (Official Documentation)
- [Streamlit Documentation - Multipage Apps](https://docs.streamlit.io/develop/concepts/multipage-apps) (verified 2025-01-30)
- [Streamlit Documentation - Caching with @st.cache_data](https://docs.streamlit.io/develop/api-reference/caching-and-state) (verified 2025-01-30)
- [Streamlit Documentation - Session State](https://docs.streamlit.io/get-started/fundamentals/advanced-concepts) (verified 2025-01-30)

### MEDIUM Confidence (WebSearch verified with official sources)
- [Building Python Dashboards: Streamlit vs Plotly Dash - Dasroot](https://dasroot.net/posts/2025/12/building-python-dashboards-streamlit-vs/) (December 2025)
- [How to Structure and Organise a Streamlit App - Towards Data Science](https://towardsdatascience.com/how-to-structure-and-organise-a-streamlit-app-e66b65ece369) (February 2024)
- [Streamlit Project Folder Structure Discussion - Streamlit Community](https://discuss.streamlit.io/t/streamlit-project-folder-structure-for-medium-sized-apps/5272)

### MEDIUM Confidence (Academic Research)
- [A Weather and Crime Alert Integrated Application - Iowa State University](https://dr.lib.iastate.edu/bitstreams/b38bb66b-7eaf-4763-baa2-22cb7b89ee73/download) (2025)
- [Spatiotemporal Crime Analysis using Community Topology - MDPI](https://www.mdpi.com/2504-2289/9/7/179) (2025)
- [Data in Policing: An Integrative Review - Taylor & Francis](https://www.tandfonline.com/doi/full/10.1080/01900692.2024.2360586) (2025)

### Existing Codebase Analysis
- `/Users/dustinober/Projects/Crime Incidents Philadelphia/analysis/config.py`
- `/Users/dustinober/Projects/Crime Incidents Philadelphia/analysis/utils.py`
- `/Users/dustinober/Projects/Crime Incidents Philadelphia/analysis/temporal_analysis.py`

---
*Architecture research for: Philadelphia Crime EDA with correlation analysis and dashboards*
*Researched: 2025-01-30*
