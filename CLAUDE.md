# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Philadelphia Crime Incidents Analysis - exploratory data analysis of 3.5M crime records spanning 2006-2026. The dataset contains 32 crime types across 26 police districts with geographic coordinates.

## Environment Setup

```bash
# Activate virtual environment (Python 3.14)
source .venv/bin/activate

# Install dependencies (if needed)
pip install pandas pyarrow matplotlib seaborn scipy pillow
```

## Running Analysis

### Generate Full EDA Report

```bash
python analysis/06_generate_report.py
```

This orchestrates all 5 analysis phases and produces a self-contained markdown report at `reports/eda_report.md` with 40+ embedded base64 visualizations. Runtime: ~15 seconds.

### Run Individual Analysis Modules

Each module can be run independently and generates its own report:

```bash
python analysis/data_quality.py        # Missing data, coordinates, duplicates
python analysis/temporal_analysis.py   # Time trends, seasonality
python analysis/categorical_analysis.py # Crime types, districts, UCR codes
python analysis/spatial_analysis.py    # Geographic distribution, density
python analysis/cross_analysis.py      # Multi-dimensional patterns
```

## Architecture

### Module Structure

```
analysis/
├── config.py                 # Centralized configuration (paths, colors, figure sizes)
├── utils.py                  # Data loading, coordinate validation, temporal features, image helpers
├── data_quality.py           # Phase 1: Data quality assessment
├── temporal_analysis.py      # Phase 2: Temporal patterns
├── categorical_analysis.py   # Phase 3: Crime types and districts
├── spatial_analysis.py       # Phase 4: Geographic analysis
├── cross_analysis.py         # Phase 5: Multi-dimensional analysis
└── 06_generate_report.py     # Orchestrator - runs all phases, compiles report
```

### Data Flow

1. **utils.py** provides `load_data()` - loads parquet file, parses dates, returns DataFrame
2. **utils.py** provides `validate_coordinates()` - adds `valid_coord` flag and `coord_issue` categorization
3. **utils.py** provides `extract_temporal_features()` - adds year, month, day_of_week, hour, time_period, season columns
4. Each analysis module imports utilities, processes data, returns dict with statistics and base64-encoded plots
5. `06_generate_report.py` orchestrates all modules, compiles markdown with embedded visualizations

### Key Configuration (analysis/config.py)

- `CRIME_DATA_PATH`: Path to main parquet file
- `PHILADELPHIA_BBOX`: Coordinate bounds for validation
- `FIGURE_SIZES`: Predefined figure dimensions for consistent plotting
- `COLORS`: Color scheme constants for visualizations

### Dataset Columns

Key columns in `crime_incidents_combined.parquet`:
- `dispatch_date`: Date of incident (parsed to datetime)
- `point_x`, `point_y`: Longitude, latitude coordinates
- `text_general_code`: Crime type/category (32 values)
- `dc_dist`: Police district (1-26)
- `ucr_general`: UCR code
- `psa`: Police Service Area
- `hour`: Hour of day (0-23, has 2.92% missing)
- `location_block`: Street/block location

### Coordinate Validation

Invalid coordinates are common (~1.6% missing). The `PHILADELPHIA_BBOX` defines valid ranges:
- Longitude: -75.28 to -74.95
- Latitude: 39.86 to 40.14

Always filter using the `valid_coord` flag from `validate_coordinates()` for spatial analysis.

### Report Generation Pattern

Each analysis module follows this pattern:
1. `analyze_*()` function - runs analysis, returns dict with results and base64 plots
2. `generate_markdown_report()` function - converts results dict to markdown
3. Plots converted via `image_to_base64(fig)` → HTML `<img>` tag with data URI

## Data Location

- **Raw data**: `data/crime_incidents_combined.parquet` (~184 MB, 3.5M rows)
- **Reports**: `reports/eda_report.md`
- **Processed**: `data/processed/` (reserved for cleaned data)

## Known Issues

- **2026 data incomplete**: Only includes records through January 20, 2026
- **Hour column**: 2.92% missing values
- **Coordinates**: ~1.6% missing or invalid (some have positive longitude incorrectly)
- **PSA values**: May contain non-numeric values (e.g., "A"), handle with try/except when converting to int
