# Codebase Structure

**Analysis Date:** 2026-01-27

## Directory Layout

```
[project-root]/
├── data/               # Crime incident datasets and processed files
├── notebooks/          # Jupyter notebooks for analysis (assumed)
├── .venv/              # Python virtual environment
├── .planning/          # GSD planning files
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── .gitignore         # Git ignore configuration
```

## Directory Purposes

**data/:**
- Purpose: Store raw and processed crime incident data files
- Contains: Parquet files, CSV exports, geospatial data
- Key files: `crime_incidents_combined.parquet`

**notebooks/:**
- Purpose: Host Jupyter notebooks for data analysis and visualization
- Contains: Interactive analysis scripts, exploratory data analysis
- Key files: `*.ipynb` files organized by analysis phase

**.venv/:**
- Purpose: Python virtual environment with project dependencies
- Contains: Python interpreter and installed packages
- Key files: Python executable and site-packages

**.planning/:**
- Purpose: GSD framework planning and metadata
- Contains: Architecture and codebase analysis documents
- Key files: `codebase/` directory with analysis docs

## Key File Locations

**Entry Points:**
- `notebooks/`: Starting point for analysis (assumed location)

**Configuration:**
- `requirements.txt`: Python dependency management

**Core Logic:**
- `notebooks/*.ipynb`: Data processing and analysis logic

**Data Files:**
- `data/crime_incidents_combined.parquet`: Main dataset

## Naming Conventions

**Files:**
- Notebooks: Descriptive names with numeric prefixes for sequence (e.g., `01_data_loading.ipynb`)
- Data: Descriptive names with format extension (e.g., `crime_incidents_combined.parquet`)

**Directories:**
- Lowercase with underscores: `data_processing/`, `visualizations/`

## Where to Add New Code

**New Analysis:**
- Primary code: `notebooks/[NN_descriptive_name].ipynb`
- Data: `data/` if new datasets are required

**New Component/Module:**
- Implementation: `notebooks/` as new analysis notebooks

**Utilities:**
- Shared helpers: `utils/` directory (if created) or within relevant notebooks

## Special Directories

**.venv/:**
- Purpose: Python virtual environment
- Generated: Yes (using pip/virtualenv)
- Committed: No (in .gitignore)

**data/:**
- Purpose: Data storage
- Generated: May contain generated processed files
- Committed: Selectively (large files typically ignored)

---

*Structure analysis: 2026-01-27*