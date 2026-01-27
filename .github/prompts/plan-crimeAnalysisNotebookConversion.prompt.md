# Plan: Convert Crime Analysis Project to Jupyter Notebooks

Transform the Crime Incidents Philadelphia project from a script-based architecture to a notebook-driven analysis pipeline. Notebooks will handle all exploratory analysis, reporting, and visualization, while helper scripts remain for data ingestion and ETL. This improves interactivity, enables iterative analysis, and maintains code modularity through the existing `src/` library.

## Current State Assessment

### Project Structure Overview
- **Purpose**: Analyze temporal and spatial patterns of crime in Philadelphia (2006-present) from OpenDataPhilly dataset
- **Current Architecture**: Script-based pipeline with reusable modules in `src/`
- **Data Pipeline**: Scrape → Consolidate to Parquet → Profile → Analyze → Visualize
- **Reusable Modules**:
  - `src.data.loader` — Data loading from Parquet
  - `src.analysis.profiler` — Statistical profiling, temporal analysis, categorical breakdowns
  - `src.geospatial.analyzer` — GeoDataFrame conversion, hotspot detection, interactive maps
  - `src.utils.config` — Configuration management

### Current Scripts
| Script | Purpose |
|--------|---------|
| `scripts/helper/scrape.py` | Downloads monthly CSVs from Carto API |
| `scripts/helper/csv_to_parquet.py` | Consolidates CSVs, optimizes types, saves Parquet |
| `scripts/analysis/calculate_statistics.py` | Statistical summaries and trends |
| `scripts/data_exploration/run_exploration.py` | Data profiling (types, missing values, outliers) |
| `scripts/geospatial/run_geographic_analysis.py` | Spatial analysis, hotspot detection, map generation |

### External Dependencies
Key packages: pandas, geopandas, folium, plotly, scikit-learn, requests, pyarrow, contextily

### Existing Plan Reference
`docs/project_plan.md` contains a proposed notebook structure with 5 phases + summary notebook.

---

## Transformation Strategy

### Phase 1: Directory Restructuring
Create new `notebooks/` folder with organized structure:
```
notebooks/
├── 00_start_here.ipynb              # Master index & workflow overview
├── phase_01_data_ingestion/
│   └── 01_scrape_and_consolidate.ipynb
├── phase_02_exploration/
│   ├── 01_data_overview.ipynb
│   └── 02_data_quality_assessment.ipynb
├── phase_03_processing/
│   ├── 01_data_cleaning.ipynb
│   └── 02_feature_engineering.ipynb
├── phase_04_analysis/
│   ├── 01_temporal_analysis.ipynb
│   ├── 02_categorical_analysis.ipynb
│   └── 03_statistical_summaries.ipynb
├── phase_05_visualization/
│   ├── 01_crime_maps_and_hotspots.ipynb
│   └── 02_trend_analysis_dashboards.ipynb
└── phase_06_modeling/
    ├── 01_forecasting_exploration.ipynb
    └── 02_classification_models.ipynb
```

### Phase 2: Refactor Helper Scripts
**Actions:**
- Keep `scripts/helper/scrape.py` and `scripts/helper/csv_to_parquet.py` unchanged
- These will be called from notebooks via `subprocess.run()` or direct Python imports
- Consider adding a `scripts/helper/refresh_data.py` wrapper for batch refreshes

### Phase 3: Create Notebook Suite

#### `00_start_here.ipynb` (Master Index)
- Project overview, goals, and data sources
- Workflow documentation and phase descriptions
- Quick-start guide for users
- Links to all phase notebooks

#### Phase 1: Data Ingestion
**`01_scrape_and_consolidate.ipynb`**
- Markdown: Overview of data sources (OpenDataPhilly Carto API)
- Code: Import scrape.py, run monthly download with status tracking
- Code: Import csv_to_parquet.py, consolidate and optimize
- Output: Display sample rows, data types, file size

#### Phase 2: Exploration
**`01_data_overview.ipynb`**
- Import `from src.data import loader`
- Load Parquet and display basic info (shape, columns, dtypes, sample)
- Import `from src.analysis import profiler` → use DataProfiler class
- Run: `profile.get_shape()`, `profile.get_dtypes()`, `profile.get_columns()`
- Visualize: Column distributions (matplotlib/seaborn)

**`02_data_quality_assessment.ipynb`**
- Duplicate detection, missing value summary
- Outlier analysis using IQR method
- Geographic coordinate validation
- Data type optimization opportunities
- Identify inconsistencies in categorical fields (crime types, districts)

#### Phase 3: Processing
**`01_data_cleaning.ipynb`**
- Handle missing values (deletion vs. imputation strategy)
- Remove or flag duplicates
- Parse and standardize date/time formats
- Geographic coordinate fixes (out-of-bounds values)
- Categorical standardization (crime types, district codes)

**`02_feature_engineering.ipynb`**
- Create temporal features (month, day of week, season, is_weekend)
- Create spatial features (zone classification, distance to city center)
- Aggregate by district/crime type for lookup tables
- Time-based resampling (daily/weekly/monthly aggregations)

#### Phase 4: Analysis
**`01_temporal_analysis.ipynb`**
- Import ProfilerExtension → use `profile.resample_by_time()`
- Time-series plots: Crime incidents over years, months, days
- Seasonality detection (annual, monthly patterns)
- Trend decomposition (STL or similar)

**`02_categorical_analysis.ipynb`**
- Top crime types (value_counts)
- Top districts
- Cross-tabulations: Crime type × District
- Using ProfilerExtension → `profile.get_cross_tabulation()`

**`03_statistical_summaries.ipynb`**
- Correlation analysis → `profile.get_correlation()`
- Summary statistics by district/crime type
- Distribution analysis (skewness, kurtosis)
- Generate printable report summaries

#### Phase 5: Visualization
**`01_crime_maps_and_hotspots.ipynb`**
- Import `from src.geospatial import analyzer`
- Initialize GeoAnalyzer on DataFrame
- Generate interactive Folium map with crime markers
- Hotspot detection using KDE → `analyzer.detect_hotspots()`
- Save map to `visualizations/crime_incidents_map.html`

**`02_trend_analysis_dashboards.ipynb`**
- Plotly/Seaborn: Crime trends over time
- Multi-faceted plots: Trends by district and crime type
- Heatmaps: Month × Year or Crime × District
- Dashboard-style layout with multiple subplots
- Export as HTML report

#### Phase 6: Modeling (Future)
**`01_forecasting_exploration.ipynb`**
- Time-series decomposition and stationarity testing
- Prophet/SARIMA baseline models
- Model comparison and diagnostics

**`02_classification_models.ipynb`**
- Predict crime type or district from features
- Algorithm comparison (Random Forest, Gradient Boosting, etc.)
- Feature importance analysis

---

## Data Refresh Workflow

### Option A: Notebook-Driven Refresh (Recommended)
- Each notebook assumes data is current
- Provide `refresh_data()` cell at top of Phase 1 notebook
- Users run once per analysis session or on-demand

### Option B: External Scheduled Refresh
- Assume data is refreshed by external scheduler (cron job, GitHub Actions)
- Notebooks always work with current data
- Simpler for users, requires infrastructure setup

### Option C: Manual Refresh Steps
- Document manual steps in `00_start_here.ipynb`
- Users understand when/how to refresh

**Recommendation**: Implement Option A + Option C documentation.

---

## Code Organization & Imports

All notebooks will:
1. Import from `src.data`, `src.analysis`, `src.geospatial`, `src.utils`
2. Use configuration from `src.utils.config`
3. Import helper functions as needed
4. Minimize code duplication (delegate to `src/`)

**Example notebook structure:**
```python
# Cell 1: Imports & Configuration
import pandas as pd
import matplotlib.pyplot as plt
from src.data import loader
from src.analysis import profiler
from src.utils.config import get_project_root, get_processed_data_path

# Cell 2: Load Data
df = loader.load_data()
print(f"Loaded {len(df)} records")

# Cell 3: Analysis
profile = profiler.DataProfiler(df)
profile.missing_values_summary()
# ... etc
```

---

## Implementation Roadmap

### Step 1: Create Notebook Structure
- Create `notebooks/` directory
- Create phase subdirectories
- Create stub notebooks with markdown headers

### Step 2: Implement Phase 1 (Data Ingestion)
- `01_scrape_and_consolidate.ipynb` — integrate scrape.py and csv_to_parquet.py

### Step 3: Implement Phase 2 (Exploration)
- `01_data_overview.ipynb` — load and describe data
- `02_data_quality_assessment.ipynb` — profiling analysis

### Step 4: Implement Phase 3 (Processing)
- `01_data_cleaning.ipynb` — cleaning logic
- `02_feature_engineering.ipynb` — feature creation

### Step 5: Implement Phase 4 (Analysis)
- `01_temporal_analysis.ipynb` — time-series analysis
- `02_categorical_analysis.ipynb` — categorical breakdowns
- `03_statistical_summaries.ipynb` — summary statistics

### Step 6: Implement Phase 5 (Visualization)
- `01_crime_maps_and_hotspots.ipynb` — geospatial visualizations
- `02_trend_analysis_dashboards.ipynb` — trend charts and dashboards

### Step 7: Plan Phase 6 (Modeling)
- Define forecasting and classification requirements
- Create notebook templates

### Step 8: Update Supporting Files
- Update `README.md` with notebook workflow
- Update `requirements.txt` if needed (add Jupyter)
- Archive old analysis scripts (optional)

---

## Key Decisions to Make

1. **Data Refresh**: Choose Option A, B, or C (see Data Refresh Workflow section)
2. **Output Handling**: Should notebooks auto-export HTML, CSV, or just save visualizations?
3. **Modeling Scope**: Implement forecasting/classification in Phase 6, or scope for future?
4. **Script Deprecation**: Archive or delete old scripts in `scripts/analysis/`, `scripts/data_exploration/`, `scripts/geospatial/`?
5. **Documentation**: Should Phase notebooks export HTML reports or just serve as interactive analyses?
6. **Environment**: Add Jupyter/JupyterLab to `requirements.txt`?

---

## Benefits of This Approach

✅ **Interactivity**: Exploratory analysis becomes iterative  
✅ **Documentation**: Markdown + code + outputs tell a complete story  
✅ **Maintainability**: Reusable code stays in `src/`, notebooks stay focused  
✅ **Reproducibility**: Step-by-step workflow is transparent and auditable  
✅ **Scalability**: New analyses can be added as new notebooks without cluttering `scripts/`  
✅ **Sharing**: Notebooks are easy to share with stakeholders  

---

## Potential Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Notebooks become large/slow | Split into smaller notebooks per phase; use lazy loading |
| Data refresh inconsistency | Implement standardized refresh workflow; document clearly |
| Code duplication in notebooks | Keep reusable logic in `src/`; import aggressively |
| Merge conflicts in notebook JSON | Use nbstripout or similar to minimize JSON diffs in git |
| Modeling scope creep | Define Phase 6 requirements upfront; prototype with simple models |
