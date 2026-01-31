# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based exploratory data analysis (EDA) project for Philadelphia crime incidents spanning 2006-2026, with over 3.4 million records. The project analyzes spatial patterns, temporal trends, crime severity, and generates focused reports answering specific questions about crime in Philadelphia.

**Dataset**: `data/crime_incidents_combined.parquet` (~3.5M records, 2006-2026)

## Development Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt  # or: pip install pandas numpy matplotlib seaborn folium scikit-learn

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
```

## Architecture

The project follows a modular analysis pipeline pattern with two types of scripts:

### Analysis Modules (`analysis/*.py`)

Core analysis scripts that perform computations and return results dictionaries:

| Module | Purpose |
|--------|---------|
| `config.py` | Centralized constants (paths, plot settings, DBSCAN params, crime severity weights) |
| `utils.py` | Data loading, coordinate validation, temporal feature extraction, UCR classification, clustering helpers |
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

### Report Generators (`analysis/*_report.py`)

Scripts that orchestrate analysis modules and generate markdown reports:
- `06_generate_report.py` - Comprehensive report (all phases)
- `07_report_safety_trend.py` - Safety trend focused report
- `08_report_summer_spike.py` - Summer spike focused report
- `09_report_red_zones.py` - Red zones focused report
- `10_report_covid_lockdown.py` - COVID impact focused report
- `11_report_robbery_timing.py` - Robbery timing focused report

## Key Patterns

### Analysis Module Structure
```python
def analyze_*() -> dict:
    """Run analysis and return results dict with base64-encoded plots."""
    df = load_data()
    df = validate_coordinates(df)
    df = extract_temporal_features(df)
    # ... analysis code ...
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

## Configuration

Edit `analysis/config.py` for:
- Plot figure sizes (`FIGURE_SIZES`)
- Color schemes (`COLORS`)
- Philadelphia bounding box (`PHILADELPHIA_BBOX`)
- DBSCAN parameters (`DBSCAN_CONFIG`)
- Crime severity weights (`CRIME_SEVERITY_WEIGHTS` in `weighted_severity_analysis.py`)

## Report Output

Reports are saved to `reports/` as markdown files with:
- Embedded base64-encoded plots
- HTML tables
- Statistical summaries

## Common Gotchas

1. **Missing coordinates**: ~25% of records lack valid coordinates. Always filter with `valid_coord` flag.
2. **2026 data**: Incomplete year (only through January 20, 2026) - exclude from trend analysis.
3. **Large dataset**: Use sampling (`df.sample()`) for visualizations to avoid memory issues.
4. **Matplotlib backend**: Set `os.environ["MPLBACKEND"] = "Agg"` for non-interactive plotting.
5. **District values**: May be strings or floats; convert with `int(float(value))` before use.
6. **UCR codes**: Stored as floats in source; convert to int for lookups.
