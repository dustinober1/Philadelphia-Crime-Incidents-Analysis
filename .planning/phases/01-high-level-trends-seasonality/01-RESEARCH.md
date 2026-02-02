# Phase 1: High-Level Trends & Seasonality - Research

**Researched:** 2026-02-02
**Domain:** Jupyter notebook data analysis, crime data visualization, reproducible reporting
**Confidence:** HIGH

## Summary

This research investigates the technical requirements for implementing Phase 1, which produces audited, reproducible answers to three questions: Is Philadelphia getting safer? Is there a summer spike? How did COVID change the landscape?

**Key Finding:** All three target notebooks already exist and contain working analysis code with outputs. However, **the `analysis/` module that notebooks import does not exist** - this is a CRITICAL gap. The notebooks currently cannot run headless because their import statements will fail.

**Primary recommendation:** Create the missing `analysis/` module first (config, utils), then refactor notebooks to use external configuration and standardized report format per CONTEXT.md decisions.

---

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.3.3 | Data manipulation | Industry standard for tabular data |
| matplotlib | 3.10.8 | Static visualizations | Publication-quality figures |
| seaborn | 0.13.2 | Statistical visualizations | Built on matplotlib, better defaults |
| scipy | 1.16.3 | Statistical tests | t-tests, linear regression |
| jupyter | (installed) | Notebook execution | nbconvert for headless runs |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| papermill | (to add) | Parameterized notebooks | Inject config into notebooks |
| ruamel.yaml | (installed) | YAML config parsing | External configuration files |
| jinja2 | 3.1.6 | Template rendering | Markdown report generation |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| YAML config | JSON config | YAML more readable for humans, JSON simpler |
| papermill | nbconvert only | papermill enables parameter injection |
| matplotlib | plotly | matplotlib better for static publication PNGs |

**Installation:**
```bash
pip install papermill
# OR
conda install -c conda-forge papermill
```

---

## Architecture Patterns

### Recommended Project Structure
```
Crime Incidents Philadelphia/
|-- analysis/                    # NEW: Create this module
|   |-- __init__.py
|   |-- config.py               # Data paths, color palettes
|   |-- utils.py                # load_data, classify_crime_category, etc.
|   |-- report_utils.py         # Data quality summary, report generation
|   +-- orchestrate_phase1.py   # Headless execution orchestrator
|
|-- config/                     # NEW: External configuration
|   |-- phase1_config.yaml      # Parameters for all Phase 1 notebooks
|   +-- report_template.md.j2   # Jinja2 template for markdown reports
|
|-- notebooks/                  # EXISTS: Needs refactoring
|   |-- philadelphia_safety_trend_analysis.ipynb   # CHIEF-01
|   |-- summer_crime_spike_analysis.ipynb          # CHIEF-02
|   +-- covid_lockdown_crime_landscape.ipynb       # CHIEF-03
|
|-- reports/                    # EXISTS: Output artifacts
|   |-- annual_trend_v1.png
|   |-- annual_trend_v1.md
|   +-- manifest.json           # NEW: Version tracking
|
+-- data/
    |-- crime_incidents_combined.parquet
    +-- external/weather_philly_2006_2026.parquet
```

### Pattern 1: External Configuration Loading
**What:** Load all parameters from YAML config at notebook start
**When to use:** Every Phase 1 notebook
**Example:**
```python
# Cell 1: Load configuration
import yaml
from pathlib import Path

config_path = Path.cwd().parent / 'config' / 'phase1_config.yaml'
with open(config_path) as f:
    config = yaml.safe_load(f)

# Access parameters
START_YEAR = config['annual_trend']['params']['start_year']
END_YEAR = config['annual_trend']['params']['end_year']
OUTPUT_DIR = Path(config['environment']['output_dir'])
VERSION = config['version']
```

### Pattern 2: Standardized Data Loading
**What:** Centralized data loading with consistent date handling
**When to use:** All notebooks requiring crime data
**Example:**
```python
# analysis/utils.py
import pandas as pd
from pathlib import Path
from .config import CRIME_DATA_PATH

def load_data(clean: bool = True) -> pd.DataFrame:
    """Load crime incidents dataset with consistent date handling."""
    df = pd.read_parquet(CRIME_DATA_PATH)
    
    # Convert categorical dispatch_date to datetime
    if df['dispatch_date'].dtype.name == 'category':
        df['dispatch_date'] = pd.to_datetime(
            df['dispatch_date'].astype(str), 
            errors='coerce'
        )
    elif not pd.api.types.is_datetime64_any_dtype(df['dispatch_date']):
        df['dispatch_date'] = pd.to_datetime(df['dispatch_date'], errors='coerce')
    
    if clean:
        df = df.dropna(subset=['dispatch_date'])
    
    return df
```

### Pattern 3: Crime Category Classification
**What:** Map UCR codes to Violent/Property/Other categories
**When to use:** Any analysis comparing crime types
**Example:**
```python
# analysis/utils.py
def classify_crime_category(df: pd.DataFrame) -> pd.DataFrame:
    """Classify crimes into Violent, Property, or Other categories."""
    df = df.copy()
    
    # Violent: Homicide (100), Rape (200), Robbery (300), Aggravated Assault (400)
    violent_codes = [100, 200, 300, 400]
    # Property: Burglary (500), Theft (600), Motor Vehicle Theft (700)
    property_codes = [500, 600, 700]
    
    def categorize(ucr_code):
        if ucr_code in violent_codes:
            return 'Violent'
        elif ucr_code in property_codes:
            return 'Property'
        else:
            return 'Other'
    
    df['crime_category'] = df['ucr_general'].apply(categorize)
    return df
```

### Anti-Patterns to Avoid
- **Hardcoded paths:** Use `Path` objects and config files, not string literals
- **Inline utility functions:** Extract to `analysis/utils.py` for reuse
- **Missing reproducibility cells:** Every notebook needs version/timestamp info
- **Interactive-only code:** All code must work in headless `nbconvert --execute`

---

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Parameterized notebooks | Custom injection | papermill | Handles parameter cells, kernel management |
| Colorblind-safe palettes | Custom colors | seaborn's `colorblind` palette or Tol's scheme | Validated for accessibility |
| Markdown report generation | String concatenation | Jinja2 templates | Handles escaping, structure, reuse |
| Notebook execution | subprocess + manual parsing | nbconvert | Built-in timeout, error handling |
| YAML config | configparser | ruamel.yaml | Preserves comments, handles complex structures |

**Key insight:** The notebooks already contain ~80% of the analysis code. Focus on refactoring infrastructure, not rewriting analysis logic.

---

## Common Pitfalls

### Pitfall 1: Missing analysis/ Module
**What goes wrong:** Notebooks fail on first cell with `ModuleNotFoundError`
**Why it happens:** Notebooks import from `analysis.config` and `analysis.utils` but directory doesn't exist
**How to avoid:** Create `analysis/__init__.py`, `analysis/config.py`, `analysis/utils.py` FIRST
**Warning signs:** Import errors when running `jupyter nbconvert --execute`

### Pitfall 2: Categorical datetime columns
**What goes wrong:** Date operations fail with "unhashable type: 'Categorical'" or comparison errors
**Why it happens:** Parquet file stores `dispatch_date` as category dtype, not datetime64
**How to avoid:** Always convert with `pd.to_datetime(df['dispatch_date'].astype(str))`
**Warning signs:** `TypeError` or `AttributeError` when calling `.dt` accessor

### Pitfall 3: Incomplete year data
**What goes wrong:** 2026 averages appear artificially low (only 20 days of data)
**Why it happens:** Current date is 2026-02-02, so 2026 has only 7,543 records vs ~160,000 expected
**How to avoid:** Filter to complete years only: `df = df[df['year'] <= 2025]`
**Warning signs:** Sudden drop in final year of time series

### Pitfall 4: Headless execution timeouts
**What goes wrong:** `jupyter nbconvert` hangs or times out
**Why it happens:** Default timeout is 30 seconds; complex visualizations take longer
**How to avoid:** Set `--ExecutePreprocessor.timeout=600` (10 minutes)
**Warning signs:** Process appears frozen during large data operations

### Pitfall 5: Hardcoded absolute paths
**What goes wrong:** Notebooks work on one machine, fail on CI or teammate's machine
**Why it happens:** Paths like `/Users/dustinober/Projects/...` are machine-specific
**How to avoid:** Use `Path.cwd().parent / 'data'` or config-based paths
**Warning signs:** `FileNotFoundError` on different systems

---

## Code Examples

Verified patterns from existing notebooks and official sources:

### Data Loading and Preparation
```python
# From covid_lockdown_crime_landscape.ipynb (verified working)
from pathlib import Path
import pandas as pd

DATA_PATH = Path.cwd().parent / 'data' / 'crime_incidents_combined.parquet'
df = pd.read_parquet(DATA_PATH)

# Handle categorical dispatch_date
if df['dispatch_date'].dtype.name == 'category':
    df['dispatch_date'] = df['dispatch_date'].astype(str)
df['dispatch_date'] = pd.to_datetime(df['dispatch_date'], errors='coerce')

# Extract temporal features
df['year'] = df['dispatch_date'].dt.year
df['month'] = df['dispatch_date'].dt.to_period('M').dt.to_timestamp()
```

### Publication-Quality Visualization with Annotations
```python
# From philadelphia_safety_trend_analysis.ipynb (verified working)
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(14, 8))

# Main plot
ax.plot(annual_totals['year'], annual_totals['total_crimes'], 
        marker='o', linewidth=3, markersize=10, color='#2E86AB')

# Peak annotation
max_row = annual_totals.loc[annual_totals['total_crimes'].idxmax()]
ax.annotate(
    f"Peak: {int(max_row['total_crimes']):,}",
    xy=(max_row['year'], max_row['total_crimes']),
    xytext=(10, 20), textcoords='offset points',
    fontsize=10, fontweight='bold', color='red',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='red', alpha=0.8),
    arrowprops=dict(arrowstyle='->', color='red', lw=1.5)
)

# Save with publication settings
plt.savefig('reports/trend_v1.png', dpi=300, bbox_inches='tight')
```

### Lockdown Annotation (COVID Analysis)
```python
# From covid_lockdown_crime_landscape.ipynb (verified working)
import pandas as pd

lockdown_date = pd.Timestamp('2020-03-01')
ax.axvline(lockdown_date, color='red', linestyle='--', linewidth=2)
ax.annotate(
    'Lockdown (Mar 2020)',
    xy=(lockdown_date, y_max * 0.9),
    xytext=(lockdown_date, y_max * 0.85),
    arrowprops=dict(arrowstyle='->', color='red'),
    color='red', fontsize=12, ha='left'
)
```

### Statistical Testing
```python
# From summer_crime_spike_analysis.ipynb (verified working)
from scipy import stats

summer_data = df[df['month'].isin([6, 7, 8])]['crime_count'].values
winter_data = df[df['month'].isin([1, 2, 3])]['crime_count'].values

t_stat, p_value = stats.ttest_ind(summer_data, winter_data)
print(f"T-statistic: {t_stat:.4f}, P-value: {p_value:.6f}")
if p_value < 0.05:
    print("STATISTICALLY SIGNIFICANT")
```

---

## Data Schema Summary

### Crime Incidents Dataset
**Location:** `data/crime_incidents_combined.parquet`
**Records:** 3,496,353
**Date Range:** 2006-01-01 to 2026-01-20

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| dispatch_date_time | datetime64[ns, UTC] | Full timestamp | Primary datetime |
| dispatch_date | category | Date only | Convert to datetime! |
| dispatch_time | category | Time only | |
| hour | float64 | Hour of dispatch | |
| ucr_general | int64 | UCR crime code | 100-2600 range |
| text_general_code | category | Crime description | 32 categories |
| dc_dist | int64 | Police district | |
| point_x | float64 | Longitude | Some missing |
| point_y | float64 | Latitude | Some missing |

### UCR Code to Category Mapping
| UCR Code | text_general_code | Category |
|----------|-------------------|----------|
| 100 | Homicide - Criminal | Violent |
| 200 | Rape | Violent |
| 300 | Robbery (Firearm/No Firearm) | Violent |
| 400 | Aggravated Assault (Firearm/No Firearm) | Violent |
| 500 | Burglary (Residential/Non-Residential) | Property |
| 600 | Thefts / Theft from Vehicle | Property |
| 700 | Motor Vehicle Theft | Property |
| 800+ | Other Assaults, Fraud, Drugs, etc. | Other |

### Crime Category Distribution
| Category | Records | Percentage |
|----------|---------|------------|
| Violent | 333,298 | 9.53% |
| Property | 1,098,225 | 31.41% |
| Other | 2,064,830 | 59.06% |

### Temporal Coverage (Complete Years)
| Period | Years | Notes |
|--------|-------|-------|
| Full dataset | 2006-2025 | 20 complete years |
| Phase 1 focus | 2015-2024 | Last 10 years for CHIEF-01 |
| COVID analysis | 2018-2025 | Before/During/After periods |
| INCOMPLETE | 2026 | Only 7,543 records (20 days) |

---

## Existing Notebook Inventory

### Notebook 1: philadelphia_safety_trend_analysis.ipynb
**Purpose:** CHIEF-01 - Annual aggregation, Violent vs Property trends
**Lines:** ~1,000
**Status:** Functional with outputs

**What it does:**
- Loads and prepares data for 2015-2024
- Classifies crimes into Violent/Property/Other
- Creates annual aggregation with YoY changes
- Statistical significance testing (linear regression)
- Generates 3 publication-quality PNGs

**Gaps vs CONTEXT.md:**
- No external config (hardcoded parameters)
- Missing formal Methods/Assumptions/Limitations sections
- No data quality summary table
- No version numbers in artifact names

### Notebook 2: summer_crime_spike_analysis.ipynb
**Purpose:** CHIEF-02 - Monthly seasonality, summer spike quantification
**Lines:** ~1,100
**Status:** Functional with outputs

**What it does:**
- Monthly aggregation across all years (2006-2026)
- Boxplot visualization by month
- Summer vs Winter comparison with percentages
- t-test statistical validation (p < 0.001)
- Crime category breakdown

**Key findings already computed:**
- Summer months: +18.3% vs winter
- July vs January: +15.1%
- Peak month: August (319,471 incidents)

**Gaps vs CONTEXT.md:**
- No external config
- Missing formal report structure
- No artifact versioning

### Notebook 3: covid_lockdown_crime_landscape.ipynb
**Purpose:** CHIEF-03 - Pre/During/Post COVID comparison, displacement analysis
**Lines:** ~850
**Status:** Functional with outputs

**What it does:**
- Defines periods: Before (2018-2019), During (2020-2021), After (2023-2025)
- Monthly averages by period
- Residential vs Commercial burglary displacement analysis
- Time series with lockdown annotation
- Already exports to reports/

**Key findings already computed:**
- Commercial burglary: +75% during lockdown vs before
- Residential burglary: -25.5% during lockdown vs before
- Clear displacement effect confirmed

**Gaps vs CONTEXT.md:**
- No external config
- Missing formal limitations section
- No artifact versioning

### Notebook 4: data_quality_audit_notebook.ipynb
**Purpose:** Data quality assessment (reference, not deliverable)
**Status:** Functional, self-contained

**Useful patterns to extract:**
- Utility functions defined inline (can copy to `analysis/utils.py`)
- COLORS palette definition
- `extract_temporal_features()` implementation
- Quality scoring methodology

---

## Gaps to Address in Planning

### Critical (Blocks Execution)
1. **Create `analysis/` module** - Notebooks fail without it
   - `analysis/__init__.py`
   - `analysis/config.py` (CRIME_DATA_PATH, COLORS)
   - `analysis/utils.py` (load_data, classify_crime_category, extract_temporal_features)

### High Priority (Required by CONTEXT.md)
2. **Create external configuration** - `config/phase1_config.yaml`
3. **Refactor notebooks to use config** - Replace all hardcoded parameters
4. **Add report format sections** - Methods, Assumptions, Limitations
5. **Add data quality summary** - Table in each notebook
6. **Implement artifact versioning** - `_v1.png` naming scheme
7. **Build orchestrator script** - `analysis/orchestrate_phase1.py`

### Medium Priority (Enhance Quality)
8. **Colorblind-safe palette** - Verify current colors, update if needed
9. **Heavy annotations** - Ensure all notable points labeled
10. **Markdown report generation** - Optional Jinja2 templates
11. **Version manifest** - JSON tracking all artifacts

---

## Recommendations for Plan Structure

### Sub-phase A: Infrastructure Setup
**Tasks:**
1. Create `analysis/` module with `__init__.py`, `config.py`, `utils.py`
2. Create `config/phase1_config.yaml` with all parameters
3. Install papermill dependency
4. Create orchestrator script skeleton

### Sub-phase B: Annual Trends Notebook (CHIEF-01)
**Tasks:**
1. Refactor to use external config
2. Add Methods/Assumptions/Limitations sections
3. Add data quality summary table
4. Update artifact naming with versions
5. Test headless execution

### Sub-phase C: Seasonality Notebook (CHIEF-02)
**Tasks:**
1. Refactor to use external config
2. Add academic-style sections
3. Add data quality summary
4. Verify boxplot meets requirements
5. Test headless execution

### Sub-phase D: COVID Analysis Notebook (CHIEF-03)
**Tasks:**
1. Refactor to use external config
2. Add academic-style sections
3. Verify displacement analysis complete
4. Ensure lockdown annotation prominent
5. Test headless execution

### Sub-phase E: Integration & Testing
**Tasks:**
1. Complete orchestrator with logging
2. Run full phase headless
3. Verify all artifacts generated
4. Create version manifest
5. Final quality review

---

## Sources

### Primary (HIGH confidence)
- Direct file inspection of project structure
- Reading actual notebook content and outputs
- Python data inspection of parquet files

### Secondary (MEDIUM confidence)
- nbconvert official documentation
- papermill official documentation

### Verification Notes
- **Confirmed:** `analysis/` directory does NOT exist (glob and bash ls)
- **Confirmed:** All 3 target notebooks exist with outputs
- **Confirmed:** Data schema via pandas inspection
- **Confirmed:** 2026 data incomplete (7,543 records)

---

## Metadata

**Confidence breakdown:**
- Data schema: HIGH - Direct parquet inspection
- Notebook inventory: HIGH - Direct file reading
- Missing analysis/ module: HIGH - Verified with ls and glob
- Implementation patterns: HIGH - Extracted from working notebooks
- Configuration approach: MEDIUM - Based on CONTEXT.md decisions + standard practices

**Research date:** 2026-02-02
**Valid until:** 2026-03-02 (30 days - stable brownfield project)
