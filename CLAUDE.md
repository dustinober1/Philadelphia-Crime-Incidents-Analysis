# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based exploratory data analysis (EDA) project for Philadelphia crime incidents spanning 2006-2026, with over 3.4 million records. The project analyzes spatial patterns, temporal trends, crime severity, and generates focused reports answering specific questions about crime in Philadelphia.

**Dataset**: `data/crime_incidents_combined.parquet` (~3.5M records, 2006-2026)

## Development Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# External data API keys (optional - see .env.example for signup)
# FRED API: https://fred.stlouisfed.org/docs/api/api_key.html (free, instant)
# Census API: https://api.census.gov/data/key_signup.html (free, email approval)

# Install dependencies (requirements.txt not managed - install manually)
pip install pandas numpy matplotlib seaborn folium scikit-learn scipy pyarrow
# External data libraries (Phase 2)
pip install meteostat fredapi census python-dotenv requests-cache statsmodels

# Statistical rigor (Phase 1)
pip install pymannkendall  # Mann-Kendall trend test for temporal data

# Advanced temporal analysis (Phase 3)
pip install workalendar  # US federal holiday detection (15+ holidays)

# Dashboard libraries (Streamlit chosen over Dash)
pip install streamlit plotly kaleido  # Dashboard framework, interactive plots, high-DPI export

# Run individual analysis modules
python analysis/data_quality.py
python analysis/temporal_analysis.py
python analysis/categorical_analysis.py
python analysis/spatial_analysis.py
python analysis/cross_analysis.py

# Run focused report generators
python analysis/07_report_safety_trend.py     # "Is Philadelphia getting safer?"
python analysis/08_report_summer_spike.py    # Summer crime patterns
python analysis/09_report_red_zones.py       # Hotspot detection for patrol deployment
python analysis/10_report_covid_lockdown.py  # COVID-19 impact analysis
python analysis/11_report_robbery_timing.py  # Robbery time patterns

# Generate comprehensive EDA report (all phases)
python analysis/06_generate_report.py

# Run weighted severity analysis
python analysis/weighted_severity_analysis.py

# Run advanced temporal analysis modules (Phase 3)
python analysis/03-01-holiday_effects.py      # Holiday effects on crime patterns
python analysis/03-02-crime_type_profiles.py  # Individual crime type analysis
python analysis/03-03-shift_analysis.py       # Shift-by-shift temporal analysis
python analysis/03-04-advanced_temporal_report.py  # Unified report generator
```

## Architecture

The project follows a modular analysis pipeline pattern with two types of scripts:

### Analysis Modules (`analysis/*.py`)

Core analysis scripts that perform computations and return results dictionaries:

| Module | Purpose |
|--------|---------|
| `config.py` | Centralized constants (paths, plot settings, STAT_CONFIG, DBSCAN params, crime severity weights) |
| `utils.py` | Data loading, coordinate validation, temporal feature extraction, UCR classification, clustering helpers |
| `stats_utils.py` | Statistical testing (20+ functions): normality, comparisons, bootstrap CI, FDR, Mann-Kendall, chi-square, correlation, effect sizes |
| `reproducibility.py` | DataVersion (SHA256 tracking), set_global_seed(), analysis metadata documentation |
| `data_quality.py` | Missing data, coordinate validation, duplicate detection |
| `temporal_analysis.py` | Long-term trends, seasonal patterns, day/hour heatmaps |
| `categorical_analysis.py` | Crime types, police districts, UCR categories |
| `spatial_analysis.py` | Geographic distribution, density maps, coordinate analysis |
| `cross_analysis.py` | Crime × Time, Crime × Location, District × Time patterns |
| `safety_trend.py` | Violent vs property crime trends (2016-2025) |
| `summer_spike.py` | July-August crime spike analysis |
| `red_zones.py` | DBSCAN clustering for hotspot detection |
| `covid_lockdown.py` | Pre/lockdown/post-COVID period comparison |
| `robbery_timing.py` | Robbery patterns by time of day |
| `weighted_severity_analysis.py` | District-level severity scoring distinguishing high-volume/low-risk vs low-volume/high-risk areas |
| `external_data.py` | External data fetching (Meteostat weather, FRED/Census APIs) with caching and temporal alignment |
| `correlation_analysis.py` | Crime-weather and crime-economic correlation analysis with detrending and statistical testing |
| `03-01-holiday_effects.py` | Holiday effects analysis (15+ US federal holidays, 3-day pre/post windows) with FDR correction |
| `03-02-crime_type_profiles.py` | Individual crime type analysis (homicide, burglary, theft, vehicle theft, aggravated assault) |
| `03-03-shift_analysis.py` | Shift-by-shift temporal analysis (4 shifts: Morning/Afternoon/Evening/Late Night) |
| `03-04-advanced_temporal_report.py` | Unified report generator orchestrating all Phase 3 analyses |

### Report Generators (`analysis/*_report.py`)

Scripts that orchestrate analysis modules and generate markdown reports:
- `06_generate_report.py` - Comprehensive report (all phases)
- `07_report_safety_trend.py` - Safety trend focused report
- `08_report_summer_spike.py` - Summer spike focused report
- `09_report_red_zones.py` - Red zones focused report
- `10_report_covid_lockdown.py` - COVID impact focused report
- `11_report_robbery_timing.py` - Robbery timing focused report
- `03-04-advanced_temporal_report.py` - Unified Phase 3 report (holiday effects, crime types, shift patterns)

## Key Patterns

### Analysis Module Structure
```python
def analyze_*() -> dict:
    """Run analysis and return results dict with base64-encoded plots."""
    # Imports for statistical rigor (Phase 1)
    from analysis.stats_utils import mann_kendall_test, bootstrap_ci, compare_two_samples
    from analysis.reproducibility import set_global_seed, get_analysis_metadata, format_metadata_markdown
    from analysis.config import STAT_CONFIG

    # Set seed for reproducibility
    set_global_seed(STAT_CONFIG["random_seed"])

    df = load_data()
    df = validate_coordinates(df)
    df = extract_temporal_features(df)
    # ... analysis code with statistical tests ...
    results = {"stats": ..., "plot": create_image_tag(image_to_base64(fig))}
    return results

def generate_markdown_report(results: dict) -> str:
    """Convert results dict to markdown with embedded base64 images."""
    # ... markdown generation ...
    return md_string
```

### Data Loading Gotchas
- **Always call `validate_coordinates(df)`** after loading to filter valid Philadelphia coordinates
- **Use `extract_temporal_features(df)`** to add year/month/day/hour/season columns
- **Coordinate columns**: `point_x` (longitude), `point_y` (latitude)
- **Date columns**: `dispatch_date`, `dispatch_time` → combined as `dispatch_datetime`

### Column Name Variations
The dataset may have varying column names. Use patterns like:
```python
district_col = None
for col in ['police_districts', 'dc_dist', 'district']:
    if col in df.columns:
        district_col = col
        break
```

### UCR Crime Classification
FBI UCR codes are used for crime categorization:
- **Violent Crimes** (UCR 100-499): Homicide, Rape, Robbery, Aggravated Assault
- **Property Crimes** (UCR 500-799): Burglary, Theft, Motor Vehicle Theft
- **Other** (UCR 800+): All other offenses

Use `classify_crime_category()` from `utils.py` to add `crime_category` column.

### DBSCAN Clustering (Red Zones)
Uses Haversine distance for geographic clustering:
- `eps_meters=150` (500ft radius)
- `min_samples=50` (minimum incidents for hotspot)
- `CLUSTERING_SAMPLE_SIZE=500_000` (samples full dataset for performance)

Functions: `dbscan_clustering()`, `calculate_cluster_centroids()`, `calculate_cluster_stats()`

### Shift Definitions (Phase 3)

**4 shifts used for temporal analysis:**
- Morning: 6AM-12PM (hours 6-11)
- Afternoon: 12PM-6PM (hours 12-17)
- Evening: 6PM-12AM (hours 18-23)
- Late Night: 12AM-6AM (hours 0-5)

**Weekend handling**: Same as weekdays (patterns emerge from data, not forced separation)

**Hour preservation**: `extract_temporal_features()` overwrites hour with 0; preserve original hour column BEFORE calling if needed for shift classification.

### Holiday Effects Analysis (Phase 3)

**Window**: 3 days before + holiday + 3 days after (7-day holiday week)

**Holidays**: 15+ US federal observances via `workalendar.UnitedStates()`

**Moving holidays**: Thanksgiving (4th Thursday), Memorial Day (last Monday May), etc. - use `workalendar`, never hard-code

**Statistical approach**: FDR correction required for 15+ holiday comparisons

### Small Sample Handling (Phase 3 Crime Type Analysis)

**Adaptive methods:**
- n < 30: Use exact tests (`fisher_exact()` from stats_utils)
- n >= 30: Use asymptotic tests (chi-square, t-tests)
- Document limitations in report for rare crimes (e.g., homicide)

**Chi-square validity**: Filter categories to minimum 5 * num_groups observations for valid expected frequencies.

## Configuration

Edit `analysis/config.py` for:
- Plot figure sizes (`FIGURE_SIZES`)
- Color schemes (`COLORS`)
- Philadelphia bounding box (`PHILADELPHIA_BBOX`)
- DBSCAN parameters (`DBSCAN_CONFIG`)
- Crime severity weights (`CRIME_SEVERITY_WEIGHTS` in `weighted_severity_analysis.py`)

## GSD Workflow

This project uses GSD (Get Shit Done) workflow for project management:
- `.planning/PROJECT.md` - Project context, requirements, constraints, decisions
- `.planning/REQUIREMENTS.md` - v1/v2 requirements with traceability to phases
- `.planning/ROADMAP.md` - Phase structure with goals, requirements, success criteria
- `.planning/STATE.md` - Project state and current phase
- `.planning/config.json` - Workflow settings (mode: yolo, depth: comprehensive, model_profile: quality)
- `.planning/research/` - Domain research (STACK, FEATURES, ARCHITECTURE, PITFALLS, SUMMARY)
- `.planning/codebase/` - Codebase documentation (7 files: STACK, ARCHITECTURE, STRUCTURE, CONVENTIONS, TESTING, INTEGRATIONS, CONCERNS)
- `.planning/phases/XX-name/` - Phase-specific CONTEXT.md, RESEARCH.md, PLAN.md files
- Use `/gsd:new-project` to initialize a new project phase
- Use `/gsd:map-codebase` to refresh codebase documentation
- Use `/gsd:plan-phase N` to create execution plans for a phase
- Use `/gsd:execute-phase N` to run all plans in a phase

**GSD agent model profiles** (from config.json model_profile):
- quality/balanced/budget settings determine which model each agent uses
- quality → gsd-phase-researcher: opus, gsd-planner: opus, gsd-plan-checker: sonnet
- balanced → gsd-phase-researcher: sonnet, gsd-planner: opus, gsd-plan-checker: sonnet
- budget → gsd-phase-researcher: haiku, gsd-planner: sonnet, gsd-plan-checker: haiku

## Research Roadmap (6 Phases)

1. **Statistical Rigor Layer** - Add significance testing (p-values), confidence intervals (99% CI), effect sizes (Cohen's d), FDR correction
2. **External Data Integration** - Weather (Meteostat), Economic (Census/FRED APIs), Policing data correlation
   - API keys required: FRED (free signup), Census (free signup)
   - Use `.env` file with `python-dotenv` for key management
3. **Advanced Temporal Analysis** - Holiday effects, individual crime types (homicide, burglary, theft, assault), shift patterns
4. **Dashboard Foundation** - Streamlit app with time/geographic/crime-type filters
5. **Dashboard Cross-Filtering** - Linked views with cross-filtering interactions
6. **Publication Outputs** - High-DPI export (PNG/SVG/PDF 300+ DPI), LaTeX table export

## Dashboard Framework

**Chosen: Streamlit** (over Dash) - pure Python, faster prototyping, excellent for single-use research dashboards
- Performance: Must use aggressive caching for 3.5M records (target: <5s load, <3s updates)
- State persistence: URL encoding for shareable filtered views

## Statistical Rigor Requirements

This is an **academic/research** project - methodological rigor is paramount:
- **Significance testing**: All trends, comparisons, correlations must report p-values
- **Confidence intervals**: 99% CI on all point estimates in visualizations
- **Effect sizes**: Cohen's d, Cliff's delta, odds ratios, Cramer's V, or standardized coefficients
- **Multiple testing correction**: FDR (Benjamini-Hochberg) for omnibus comparisons
- **Reproducibility**: Random seeds, version tracking, parameter documentation

**Implementation**: Use `analysis.stats_utils` for all statistical functions (20+ available). SciPy 1.17+ required (uses `false_discovery_control`, `tukey_hsd`). `pymannkendall` for temporal trends. STAT_CONFIG in `config.py` centralizes all parameters (confidence_level=0.99, alpha=0.01, effect_size benchmarks).

**Phase 1 Complete**: All 11 analysis modules updated with statistical rigor. Data quality audit at `reports/01_data_quality_audit.md` (97.83/100 score).

## Critical Pitfalls

1. **Spurious correlations**: 20-year trends will correlate due to shared drift - **detrend first**
2. **MAUP** (Modifiable Areal Unit Problem): Results change with boundary choices - use **multi-scale analysis**
3. **Missing coordinate bias**: ~25% missing data is **non-random** - profile missingness before spatial analysis
4. **Dashboard performance**: 3.5M records will kill Streamlit without **aggressive caching from the start**
5. **Causal claims**: EDA shows correlation - state "associated with" not "causes"

## Report Output

Reports are saved to `reports/` as markdown files with:
- Embedded base64-encoded plots
- HTML tables
- Statistical summaries

## Common Gotchas

1. **Missing coordinates**: ~25% of records lack valid coordinates. Always filter with `valid_coord` flag.
2. **Meteostat v2 API**: Uses `daily(station_id, start, end)` function, not `Hourly` class. Returns `temp` not `tavg`. Station ID for Philadelphia: 72408 (PHL International Airport).
3. **Date dtype handling**: Date columns in crime data may be categorical dtype - convert to datetime before temporal operations: `df[date_col] = pd.to_datetime(df[date_col])`
4. **External API keys**: Functions in `external_data.py` raise ValueError with helpful signup instructions when keys missing. Not required for module import.
5. **2026 data**: Incomplete year (only through January 20, 2026) - exclude from trend analysis.
6. **Python version**: Uses Python 3.14.2 in `.venv/` - ensure compatibility when adding new dependencies.
7. **Large dataset**: Use sampling (`df.sample()`) for visualizations to avoid memory issues.
   **Memory overflow**: Full-dataset analysis (3.5M records) causes exit 137; use 20% sampling for memory-intensive operations like holiday effects.
8. **Matplotlib backend**: Set `os.environ["MPLBACKEND"] = "Agg"` for non-interactive plotting.
9. **District values**: May be strings or floats; convert with `int(float(value))` before use.
10. **UCR codes**: Stored as floats in source; convert to int for lookups.
11. **No requirements.txt**: Dependencies are in `.venv/` but not pinned to a requirements file.
12. **Moving holidays**: Thanksgiving (4th Thursday), Memorial Day, Labor Day change dates each year - use `workalendar.UnitedStates()` to calculate correctly.
    **workalendar v17+ API**: Use `workalendar.usa.UnitedStates` (not `america`); returns list of tuples not dict.
    **Numeric module filenames**: Phase 3 modules (03-01-*, 03-02-*, etc.) require `importlib.import_module()` due to leading digits.
13. **Zsh glob patterns**: Wildcard patterns like `/*-PLAN.md` fail in zsh; use `ls ... | grep PATTERN` or Glob tool instead.

## Dashboard Package Structure (Phase 4)

**Created:** `dashboard/` package with 5 page renderers, 3 filter modules, cache component, and main app

**Run dashboard:** `streamlit run dashboard/app.py` (launches at http://localhost:8501)

**Package structure:**
- `dashboard/__init__.py` - Package initialization
- `dashboard/app.py` - Main entry point with st.set_page_config, st.tabs for 5 views
- `dashboard/config.py` - Dashboard constants (PAGE_NAMES, FILTER_DEFAULTS, CACHE_CONFIG, DISPLAY_CONFIG)
- `dashboard/components/cache.py` - Data loading with @st.cache_data decorators
- `dashboard/filters/` - Filter modules (time_filters.py, geo_filters.py, crime_filters.py)
- `dashboard/pages/` - Page renderers (overview.py, temporal.py, spatial.py, correlations.py, advanced.py)

### Streamlit Caching Pattern (Large Datasets)

**Pattern:** Multi-layer @st.cache_data decorators for sub-5s load times

```python
@st.cache_data(ttl=3600, max_entries=10, show_spinner="Loading...")
def load_data() -> pd.DataFrame:
    # First load ~10s, subsequent loads instant
    # Cache key derived from function arguments automatically
    return df
```

**Layers:** Data loading (ttl=3600), filter results (ttl=1800), reports (ttl=300)
**Key:** Each unique filter combination creates its own cache entry - no manual cache key management

### Streamlit URL State Sync Pattern

**Pattern:** Bidirectional st.query_params for shareable filtered views

```python
# Read from URL
params = st.query_params
start = params.get("start_date", "2006-01-01")

# Write to URL
st.query_params["start_date"] = start_date.isoformat()
```

**Clean URL trick:** When "select all" is active, omit the parameter entirely (cleaner: `?start=2020` vs `?districts=1,2,3,...,23`)

### Streamlit Filter State with NamedTuple

**Pattern:** Use NamedTuple for immutable filter state containers

```python
class TimeFilterState(NamedTuple):
    start_date: date
    end_date: date
    preset: str | None

    @property
    def years(self) -> list[int]:
        return list(range(self.start_date.year, self.end_date.year + 1))
```

**Benefits:** Type safety, IDE autocomplete, hashable for cache keys, derived properties encapsulated

### Cascading Filter Architecture

**Pattern:** Downstream filters receive progressively filtered data

```python
# Time filter (no dependencies)
time_state = render_time_filters()
df_filtered = apply_filters(df, start=start, end=end)

# Geo filter (limited to time range)
geo_state = render_geo_filters(df_filtered)  # Pass filtered data
selected_districts = get_filter_districts(geo_state)

# Crime filter (limited to time + geo)
df_tg_filtered = apply_filters(df, start=start, end=end, districts=districts)
crime_state = render_crime_filters(df_tg_filtered)  # Pass filtered data
```

**Why:** Prevents showing options that would return zero results (e.g., districts with no data in selected time period)

## Phase 5 Cross-Filtering Architecture

**Hybrid state management:** Sidebar filters require explicit apply button (deliberate filtering), view-to-view cross-filters are instant (exploratory interaction)
**URL encoding:** Unified namespace for sidebar + view params (e.g., `?districts=22&active_view=spatial&active_district=22`)
**Visual feedback:** Per-filter indicators (dots/icons) for pending changes, 30% opacity dimming for filtered-out data
**State persistence:** Sidebar in session state + URL, views in URL (shareable), apply button enables/disables based on pending changes

## GSD Context Gathering Workflow

**/gsd:discuss-phase N** - Extract implementation decisions before planning
- Generates phase-specific gray areas (not generic UI/UX categories)
- Asks 4 questions per area, then checks: "More questions or next area?"
- Scope guardrail: new capabilities → "That's its own phase. I'll note it for later."
- CONTEXT.md feeds researcher (WHAT to investigate) and planner (WHAT choices are locked)

**Phase directory creation pattern:**
```bash
PADDED_PHASE=$(printf "%02d" 5)
PHASE_NAME=$(grep "Phase 5:" .planning/ROADMAP.md | sed 's/.*Phase [0-9]*: //' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
mkdir -p ".planning/phases/${PADDED_PHASE}-${PHASE_NAME}"
```

**Planning docs commit pattern:**
```bash
COMMIT_PLANNING_DOCS=$(cat .planning/config.json 2>/dev/null | grep -o '"commit_docs"[[:space:]]*:[[:space:]]*[^,}]*' | grep -o 'true\|false' || echo "true")
git check-ignore -q .planning 2>/dev/null && COMMIT_PLANNING_DOCS=false
```
