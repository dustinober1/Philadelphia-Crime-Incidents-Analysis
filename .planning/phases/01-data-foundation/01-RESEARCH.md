# Phase 01: Data Foundation - Research

**Researched:** 2026-01-27
**Domain:** Data Engineering & Exploratory Data Analysis (EDA)
**Confidence:** HIGH

## Summary

Phase 1 establishes the trust layer for all subsequent analysis. The goal is not just "loading data" but "characterizing truth." Research confirms that for crime data, the critical challenges are **reporting lag**, **geospatial noise**, and **seasonality**.

The standard stack for this in 2026 relies on **Polars** or **Pandas 2.x** for processing (we will stick to Pandas for ecosystem compatibility with geospatial tools) and **Pandera** for rigorous schema validation. **Statsmodels STL** is the industry standard for robust seasonal decomposition, preferred over simple moving averages because it handles outliers (common in crime data) effectively.

**Primary recommendation:** Use `pandera` for executable data dictionaries and `statsmodels.STL` for robust seasonality extraction.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **pandas** | 2.2+ | Data Manipulation | Ecosystem foundation; critical for GeoPandas. |
| **geopandas** | 0.14+ | Geospatial | Adds spatial indexing and joins to pandas. |
| **pandera** | 0.20+ | Data Validation | "Executable documentation" - validates schema at runtime. |
| **statsmodels** | 0.14+ | Statistical Analysis | robust `STL` decomposition implementation. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **seaborn** | 0.13+ | Visualization | Statistical plots (histograms, boxplots) for quality audit. |
| **pyarrow** | 14.0+ | I/O | Fast Parquet read/write support. |

**Installation:**
```bash
pip install pandas geopandas pandera statsmodels seaborn pyarrow
```

## Architecture Patterns

### Recommended Project Structure
```
data/
├── raw/             # Immutable input (CSV/GeoJSON)
├── interim/         # Parquet (fast I/O), partially cleaned
└── processed/       # Final analysis-ready datasets
notebooks/
├── 00_environment_setup.ipynb   # Path/Library checks
└── 01_data_loading.ipynb        # Load -> Validate -> Save
src/
└── data/
    ├── validation.py    # Pandera schemas
    └── cleaning.py      # Cleaning functions
```

### Pattern 1: The "Executable Data Dictionary"
**What:** Define schemas in code (Pandera) rather than just a Markdown table.
**When to use:** ALWAYS for the primary dataset.
**Example:**
```python
# Source: https://pandera.readthedocs.io/en/stable/
import pandera as pa
from pandera.typing import Series

class CrimeSchema(pa.DataFrameModel):
    dc_key: Series[str] = pa.Field(unique=True, description="District Control Number")
    dispatch_date: Series[pa.DateTime] = pa.Field(description="Date of dispatch")
    lat: Series[float] = pa.Field(ge=-90, le=90, nullable=True)
    lng: Series[float] = pa.Field(ge=-180, le=180, nullable=True)
    
    class Config:
        strict = True # Error on unknown columns
```

### Pattern 2: Robust Seasonal Decomposition (STL)
**What:** Using LOESS (Locally Estimated Scatterplot Smoothing) to separate Trend, Seasonality, and Residue.
**Why:** Simple moving averages fail when crime spikes (outliers) occur. STL is robust to these.
**Example:**
```python
from statsmodels.tsa.seasonal import STL
# Resample to weekly counts first
res = STL(weekly_counts, seasonal=13).fit()
res.plot()
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| **Schema Validation** | `if df['col'].isnull().any(): ...` | `pandera` | Handling all edge cases (types, ranges, nulls) produces spaghetti code. |
| **Seasonality** | Rolling means / Pivot tables | `statsmodels.STL` | Mathematical rigor; handles edge effects and outliers correctly. |
| **Coordinate Clean** | Manual bounding box checks | `geopandas.clip` | Spatial indexing is much faster and more accurate for "in city" checks. |

## Common Pitfalls

### Pitfall 1: The "Null Island" Trap
**What goes wrong:** Geocoding failures often default to (0,0) or the exact city center coordinate.
**Why it happens:** Upstream geocoders return default values on failure.
**How to avoid:** Filter `(lat, lng) == (0,0)` AND verify point-in-polygon against the City boundary shapefile.
**Warning signs:** A spike of crimes exactly at City Hall.

### Pitfall 2: Reporting Lag Bias
**What goes wrong:** Trends look like they are "dropping" in the most recent weeks.
**Why it happens:** Police reports take time to enter the system (Data Entry Lag).
**How to avoid:** Calculate `lag = entry_date - dispatch_date` (if available) or simply cut off the last 4-6 weeks of data as decided.

### Pitfall 3: Duplicate Records
**What goes wrong:** The same incident appears multiple times with different status (e.g., "Founded" vs "Arrest").
**How to avoid:** Deduplicate by `dc_key` (District Control Number), keeping the most recent `update_date` (if available).

## Code Examples

### Geocoding Validation
```python
import geopandas as gpd

def validate_boundaries(df, city_shapefile_path):
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.lng, df.lat), crs="EPSG:4326"
    )
    city_boundary = gpd.read_file(city_shapefile_path).to_crs("EPSG:4326")
    
    # Spatial join to find points inside city
    valid_points = gpd.sjoin(gdf, city_boundary, predicate="within")
    return valid_points
```

### Missing Value Audit
```python
import pandas as pd
import seaborn as sns

def plot_missing_matrix(df):
    # Visual audit of missingness patterns
    plt.figure(figsize=(10, 6))
    sns.heatmap(df.isnull(), cbar=False, yticklabels=False, cmap="viridis")
    plt.title("Missing Value Matrix")
```

## Sources

### Primary (HIGH confidence)
- **Pandera Docs** (v0.25.0) - Schema definition and validation patterns.
- **Statsmodels Docs** (v0.14.6) - `STL` decomposition usage.

### Secondary (MEDIUM confidence)
- **General Crime Analysis Best Practices** - Common knowledge regarding "Null Island" and reporting lags.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Pandas/Pandera/Statsmodels is the gold standard.
- Architecture: HIGH - Notebooks + src/ layout is robust.
- Pitfalls: HIGH - "Null Island" and Lag are well-documented phenomena in open data.

**Research date:** 2026-01-27
**Valid until:** 2026-06-01 (Pandas ecosystem moves fast, but these basics are stable)
