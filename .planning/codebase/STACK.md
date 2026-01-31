# Technology Stack

**Analysis Date:** 2026-01-30

## Languages

**Primary:**
- **Python 3.14.2** - Core language for all analysis scripts
  - Used for: Data processing, statistical analysis, visualization
  - Version: 3.14.2 (latest stable in venv)

## Runtime

**Execution Environment:**
- **Python Virtual Environment (`.venv`)**
  - Isolated dependencies via venv module
  - Located at project root: `.venv/`
  - Python 3.14.2 runtime
  - Activated via: `source .venv/bin/activate`

**Script Execution:**
- Direct Python script execution: `python analysis/[module].py`
- No application server or runtime container
- Scripts run as standalone processes

## Frameworks

**Data Analysis:**
- **pandas 3.0.0** - Data manipulation and analysis
  - DataFrame operations, data cleaning, aggregations
  - Primary data structure for all analyses
- **numpy 2.4.1** - Numerical computing
  - Array operations, mathematical functions
- **scipy 1.17.0** - Scientific computing
  - Statistical functions (e.g., `scipy.stats` for trend analysis)
- **scikit-learn 1.8.0** - Machine learning utilities
  - DBSCAN clustering for hotspot detection

**Visualization:**
- **matplotlib 3.10.8** - Plotting library
  - All static charts and graphs
  - Agg backend for non-interactive rendering
- **seaborn 0.13.2** - Statistical visualization
  - Enhanced plot styling and heatmaps
- **folium 0.20.0** - Interactive maps
  - Choropleth maps, hotspot visualizations
  - HTML map generation for reports

## Data Storage

**Format:**
- **Parquet** (`pyarrow 23.0.0`)
  - Main dataset: `crime_incidents_combined.parquet`
  - ~3.5 million records spanning 2006-2026
  - Columnar storage for efficient querying

**Location:**
- `data/crime_incidents_combined.parquet` - Primary dataset
- `data/processed/` - Cleaned/transformed data outputs

## Key Dependencies

**Core Analysis:**
| Package | Version | Purpose |
|---------|---------|---------|
| pandas | 3.0.0 | Data manipulation |
| numpy | 2.4.1 | Numerical computing |
| scipy | 1.17.0 | Statistical functions |
| scikit-learn | 1.8.0 | Clustering algorithms |

**Visualization:**
| Package | Version | Purpose |
|---------|---------|---------|
| matplotlib | 3.10.8 | Static plots |
| seaborn | 0.13.2 | Statistical charts |
| folium | 0.20.0 | Interactive maps |
| branca | 0.8.2 | Map color scales |

**Utilities:**
| Package | Version | Purpose |
|---------|---------|---------|
| pyarrow | 23.0.0 | Parquet I/O |
| requests | 2.32.5 | HTTP (future use) |
| Pillow | 12.1.0 | Image encoding |
| joblib | 1.5.3 | Parallel processing |

## Configuration

**Python Version:** 3.14.2

**Environment:**
- Virtual environment: `.venv/`
- No environment variables used for configuration
- Configuration in code: `analysis/config.py`

**Missing:**
- No `requirements.txt` file (noted in CONCERNS.md)
- No `pyproject.toml` or `setup.py`
- Dependencies managed manually via pip

## Development Tools

**Not explicitly configured:**
- Code formatter: None configured (code appears Black-formatted)
- Linter: None configured
- Test runner: None configured
- Type checker: None configured (type hints used but not enforced)

**Version Control:**
- Git repository initialized
- `.gitignore` present (excludes `.venv/`, data files)

## Build and Deployment

**Not applicable:**
- This is an analysis project, not a deployed application
- No build process
- No CI/CD pipeline
- No containerization (Docker, etc.)

---

*Stack analysis: 2026-01-30*
