# Codebase Structure

**Analysis Date:** 2026-01-27

## Directory Layout

```
/
├── config.ini                  # Global configuration
├── data/                       # Data storage (ignored in git)
│   ├── raw/                    # Raw CSV downloads
│   └── processed/              # Optimized Parquet files
├── docs/                       # Project documentation
├── scripts/                    # Executable scripts
│   ├── helper/                 # Active ETL scripts
│   ├── data_exploration/       # Placeholder for EDA
│   ├── data_processing/        # Placeholder for transformation
│   ├── modeling/               # Placeholder for ML models
│   └── visualization/          # Placeholder for plotting
├── src/                        # Shared library code (currently empty/minimal)
│   ├── features/               # Feature engineering modules
│   ├── models/                 # Model definitions
│   └── utils/                  # Shared utilities
└── visualizations/             # Output directory for plots
```

## Directory Purposes

**`scripts/helper/`:**
- Purpose: Contains the core maintenance scripts for fetching and preparing data.
- Contains: Python scripts (`.py`).
- Key files: `scripts/helper/scrape.py`, `scripts/helper/csv_to_parquet.py`

**`src/`:**
- Purpose: Intended for reusable application logic, separate from execution scripts.
- Contains: Python modules (currently largely empty).

**`data/`:**
- Purpose: Local storage for the data pipeline.
- Contains: Subdirectories for `raw`, `processed`, and `external` data.

## Key File Locations

**Entry Points:**
- `scripts/helper/scrape.py`: Data downloader.
- `scripts/helper/csv_to_parquet.py`: Data processor.

**Configuration:**
- `config.ini`: Project-wide settings.

**Core Logic:**
- `scripts/helper/`: Currently holds the primary business logic for data handling.

## Naming Conventions

**Files:**
- `snake_case.py`: e.g., `csv_to_parquet.py`, `daily_update.py`

**Directories:**
- `snake_case`: e.g., `data_processing`, `data_exploration`

## Where to Add New Code

**New ETL Step:**
- Create a new script in `scripts/helper/` or `scripts/data_processing/`.

**New Analysis/EDA:**
- Create a script or notebook in `scripts/data_exploration/`.

**Reusable Logic:**
- Add functions to `src/utils/` or create new modules in `src/`.

**Visualization:**
- Add generation scripts to `scripts/visualization/`.

## Special Directories

**`data/`:**
- Purpose: Stores large datasets.
- Generated: Yes (by scripts).
- Committed: No (typically `.gitignore`'d).

**`models/`:**
- Purpose: Binary model artifacts.
- Generated: Yes.

---

*Structure analysis: 2026-01-27*
