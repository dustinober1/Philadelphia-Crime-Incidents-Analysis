# Architecture Research: Analysis Pipeline & Notebook Organization

## Research Objective
Investigate how to structure analysis pipeline, notebook organization patterns, and data flow for academic crime analysis.

## Analysis Pipeline Architecture

### High-Level Data Flow
```
Raw Data
    ↓
Data Loading & Validation
    ↓ (Detect schema, missing values, outliers)
Cleaned/Validated Dataset
    ├→ Exploratory Analysis (univariate, distributions)
    ├→ Temporal Analysis (trends, seasonality, hour/day effects)
    ├→ Geographic Analysis (hotspots, districts, spatial clustering)
    ├→ Offense Analysis (UCR breakdown, severity)
    └→ Interactive Analysis (correlations, disparities)
    ↓
Analysis Results Cache (Preprocessed dataframes, aggregations)
    ├→ Static Report Generation (matplotlib/seaborn figures)
    ├→ Interactive Dashboard (Plotly/Folium)
    └→ Report Document (Markdown → PDF)
    ↓
Academic Report (PDF + Markdown + Interactive Dashboard)
```

### Data Formats & Stages

| Stage | Format | Size | Location | Purpose |
|-------|--------|------|----------|---------|
| **Input** | Parquet | ~500MB | `data/crime_incidents_combined.parquet` | Raw data from CartoDB |
| **Loaded** | Pandas DF | ~5-8GB in-memory | Notebook memory | Analysis operations |
| **Validated** | Parquet | ~450MB | `data/crime_incidents_cleaned.parquet` | Checkpoint; reproducibility |
| **Aggregated** | CSV / Parquet | ~10-50MB | `data/processed/` | Pre-computed summaries |
| **Dashboards** | JSON / HTML | ~50-200MB | `dashboards/` | Plotly/Folium outputs |
| **Reports** | PDF / Markdown | ~20-50MB | `reports/` | Final deliverable |

### Processing Considerations
- **In-Memory Strategy**: 3.5M rows × 15-20 columns = ~8-12 GB
  - Typical laptop: 16GB RAM (squeeze in, monitor memory)
  - Server: 32GB+ (comfortable)
  - Option: Use polars for better memory efficiency, or chunk processing

- **Intermediate Checkpoints**: Save validated data and key aggregations
  - Allows notebooks to restart without re-processing
  - Enables parallel dashboard/report work
  - Improves reproducibility

- **Aggregation Strategy**: Pre-compute common summaries
  - Crime by district, month, hour
  - Crime by UCR type, district
  - Repeat location tallies
  - Saves re-computation across notebooks

---

## Notebook Architecture Patterns

### Pattern 1: Linear Sequential (Simplest)
```
01_load.ipynb
  ↓
02_explore.ipynb
  ↓
03_analyze.ipynb
  ↓
04_report.ipynb
```

**Pros:**
- Simple mental model
- Easy to follow for readers
- Dependencies clear

**Cons:**
- Can't parallelize
- Monolithic notebooks get unwieldy (1000+ cells)
- Hard to reuse analyses

**Best For:** Small projects, teaching, single-author

---

### Pattern 2: Modular with Shared Data (Recommended)
```
data/
├── crime_incidents_combined.parquet (raw)
├── crime_incidents_cleaned.parquet (validated)
└── processed/
    ├── crime_by_district_month.csv
    ├── crime_by_ucr_hour.csv
    ├── hotspot_locations.csv
    └── ...

notebooks/
├── 01_data_loading_validation.ipynb
│   └── Outputs: crime_incidents_cleaned.parquet
├── 02_exploratory_analysis.ipynb
│   ├── Inputs: cleaned data
│   └── Outputs: processed/* aggregations
├── 03_temporal_analysis.ipynb
│   ├── Inputs: cleaned data, aggregations
│   └── Outputs: temporal_figures/, temporal_stats.json
├── 04_geographic_analysis.ipynb
│   ├── Inputs: cleaned data, aggregations
│   └── Outputs: geographic_figures/, geographic_stats.json
├── 05_offense_breakdown.ipynb
│   ├── Inputs: cleaned data, aggregations
│   └── Outputs: offense_figures/, offense_stats.json
├── 06_cross_factor_analysis.ipynb
│   ├── Inputs: cleaned data + all stats from 3-5
│   └── Outputs: interaction_figures/, correlations.json
├── 07_dashboard.ipynb
│   ├── Inputs: processed/* data
│   └── Outputs: dashboards/main_dashboard.html
└── 08_report_generation.ipynb
    ├── Inputs: all figures, stats, aggregations
    └── Outputs: report.pdf, report.md

scripts/
├── config.py (shared parameters, paths)
├── utils.py (shared functions: aggregation, visualization)
├── data_loader.py (data loading utilities)
└── validators.py (data validation functions)
```

**Pros:**
- Modular and reusable
- Parallelizable (notebooks 3-6 can run independently)
- Scalable to larger projects
- Shared utilities in scripts/ reduce duplication
- Easier for multiple people to contribute

**Cons:**
- More setup (need scripts/, file structure)
- Requires coordination (shared data formats)

**Best For:** Academic projects, teams, large datasets

---

### Pattern 3: Literate Programming (Quarto / Sphinx)
```
source/
├── 01_methods.qmd          (Methodology chapter)
├── 02_data_quality.qmd     (Data quality assessment)
├── 03_results.qmd          (All results with live code)
└── _quarto.yml             (Config: PDF, HTML output)

_quarto.yml → Renders → report.pdf + report.html
```

**Pros:**
- Single source of truth (code + narrative together)
- Automatic report generation (no manual copy-paste)
- Live code in deliverable; reproducible

**Cons:**
- Learning curve (Quarto/R Markdown syntax)
- Slower to render (re-runs all code)
- Harder to iterate (full re-render needed)

**Best For:** Academic papers, formal reports, reproducible research

---

## Recommended Architecture for This Project

**Pattern 2 (Modular) with Quarto Report Generation**

### Directory Structure
```
Crime_Incidents_Philadelphia/
├── data/
│   ├── crime_incidents_combined.parquet (raw)
│   ├── crime_incidents_cleaned.parquet (validated)
│   ├── philadelphia_districts.geojson (spatial)
│   └── processed/
│       ├── crime_by_district_month.parquet
│       ├── crime_by_ucr_hour.parquet
│       ├── hotspot_locations.csv
│       ├── disparity_metrics.csv
│       └── ...
├── notebooks/
│   ├── 00_environment_setup.ipynb (one-time: install packages, validate paths)
│   ├── 01_data_loading_validation.ipynb
│   ├── 02_exploratory_analysis.ipynb
│   ├── 03_temporal_analysis.ipynb
│   ├── 04_geographic_analysis.ipynb
│   ├── 05_offense_breakdown.ipynb
│   ├── 06_disparity_analysis.ipynb
│   ├── 07_cross_factor_analysis.ipynb
│   ├── 08_dashboard.ipynb
│   └── README.md (execution order, dependencies)
├── scripts/
│   ├── __init__.py
│   ├── config.py (paths, constants, color palettes)
│   ├── data_loader.py (load/validate utilities)
│   ├── aggregations.py (pre-computed summaries)
│   ├── visualizations.py (plotting utilities)
│   ├── statistics.py (hypothesis testing utilities)
│   └── report_utils.py (figure compilation for report)
├── output/
│   ├── figures/ (all static plots)
│   ├── tables/ (statistical results tables)
│   ├── dashboards/ (HTML interactive dashboards)
│   └── report/ (PDF + markdown outputs)
├── reports/
│   ├── 01_methodology.qmd
│   ├── 02_data_quality.qmd
│   ├── 03_temporal_findings.qmd
│   ├── 04_geographic_findings.qmd
│   ├── 05_offense_findings.qmd
│   ├── 06_disparity_findings.qmd
│   ├── 07_cross_factor_findings.qmd
│   ├── 08_discussion.qmd
│   ├── 09_conclusion.qmd
│   ├── _quarto.yml
│   └── references.bib (citations)
├── environment.yml (conda environment specification)
├── requirements.txt (pip packages with pinned versions)
└── README.md (project overview)
```

### Execution Workflow
```
1. Setup
   └─ notebooks/00_environment_setup.ipynb
      └─ Creates output/, processes/ directories
      └─ Validates data file presence
      └─ Checks package versions

2. Data Processing (Sequential)
   └─ notebooks/01_data_loading_validation.ipynb
      └─ Validates schema, missing values
      └─ Outputs: crime_incidents_cleaned.parquet
      └─ Outputs: data_quality_report.csv

3. Core Analysis (Parallelizable)
   ├─ notebooks/02_exploratory_analysis.ipynb (univariate)
   ├─ notebooks/03_temporal_analysis.ipynb
   ├─ notebooks/04_geographic_analysis.ipynb
   ├─ notebooks/05_offense_breakdown.ipynb
   ├─ notebooks/06_disparity_analysis.ipynb
   └─ notebooks/07_cross_factor_analysis.ipynb
      └─ All save outputs to output/

4. Aggregation & Dashboard
   ├─ notebooks/02_exploratory_analysis.ipynb pre-computes into data/processed/
   └─ notebooks/08_dashboard.ipynb reads from data/processed/
      └─ Outputs: dashboards/main_dashboard.html

5. Report Generation (Sequential)
   └─ reports/
      └─ quarto render _quarto.yml
      └─ Reads from output/figures, output/tables
      └─ Outputs: output/report/final_report.pdf
```

---

## Shared Scripts & Utilities

### config.py
```python
# Paths
DATA_DIR = "data"
NOTEBOOKS_DIR = "notebooks"
OUTPUT_DIR = "output"
FIGURES_DIR = f"{OUTPUT_DIR}/figures"
TABLES_DIR = f"{OUTPUT_DIR}/tables"
DASHBOARDS_DIR = f"{OUTPUT_DIR}/dashboards"

CLEANED_DATA = f"{DATA_DIR}/crime_incidents_cleaned.parquet"
RAW_DATA = f"{DATA_DIR}/crime_incidents_combined.parquet"

# Analysis parameters
CONFIDENCE_LEVEL = 0.95
ALPHA = 0.05  # Significance level
COLORBLIND_PALETTE = "husl"  # For matplotlib/seaborn
UCR_CATEGORIES = [...] # Major crime categories

# Districts (hard-coded or loaded from data)
DISTRICTS = ['01D', '02D', '03D', ...]
```

### utils.py
```python
def load_crime_data(path):
    """Load and validate crime data"""
    
def aggregate_by_district_month(df):
    """Pre-compute district × month summary"""
    
def plot_trend(df, title, ax):
    """Standardized trend plotting"""
    
def calculate_confidence_interval(data, ci=0.95):
    """Calculate CI for rate estimates"""
    
def hotspot_kde(lons, lats, bandwidth=0.01):
    """Kernel density estimation for hotspots"""
```

### data_loader.py
```python
def validate_schema(df):
    """Check expected columns present"""
    
def detect_missing_values(df):
    """Profile missing data patterns"""
    
def clean_coordinates(df):
    """Validate/fix latitude/longitude"""
    
def standardize_datetime(df):
    """Ensure dispatch_date_time is parsed correctly"""
```

---

## Reproducibility Checklist

- [ ] `environment.yml` and `requirements.txt` specify exact versions
- [ ] `notebooks/README.md` documents execution order and dependencies
- [ ] `scripts/config.py` centralizes all parameters (no magic numbers)
- [ ] Random seeds set: `np.random.seed(42)`, `random.seed(42)`
- [ ] Notebook cells are idempotent (can restart kernel and re-run in order)
- [ ] Intermediate data saved at checkpoints (don't re-compute if possible)
- [ ] Data provenance documented (source, date downloaded, version)
- [ ] Processing decisions logged (why this filter? why that threshold?)
- [ ] Outputs timestamped (allows versioning)
- [ ] README includes "how to run" instructions

---

## Performance Considerations

### For 3.5M Crime Records

| Operation | Time | Strategy |
|-----------|------|----------|
| Load parquet | ~5-10s | Acceptable |
| Group by district, month | ~1-2s | Fast |
| Kernel density (whole city) | ~30-60s | Parallelize by district |
| Geographic join (district polygons) | ~5-15s | Depends on precision |
| Generate all figures | ~2-5 min | Cache intermediate results |
| Full pipeline run | ~30-45 min | Parallelizable steps can cut to 15-20 min |

### Optimization Tips
1. Pre-compute summaries → CSV/Parquet for re-use
2. Use polars instead of pandas if memory tight
3. Parallelize independent notebooks (concurrent execution)
4. Cache Plotly/Folium outputs (don't re-render)
5. Lazy evaluation for large aggregations (dask if needed)

---

## Key Insights

1. **Modular > Monolithic**: Start with single notebook, but refactor into modules by phase 2
2. **Shared utilities save time**: Centralize plotting, stats, data loading → consistency + reusability
3. **Intermediate checkpoints are essential**: Save cleaned data, aggregations; saves re-computation
4. **Reproducibility from day 1**: Set seeds, document versions, explain decisions early
5. **Consider report generation pipeline**: Quarto / nbconvert for moving from notebooks to final PDF
6. **Memory management matters**: With 3.5M rows, monitor RAM; plan for 16GB minimum

---

*Prepared: 2026-01-27 | Evidence Level: Data science best practices + large project patterns*
