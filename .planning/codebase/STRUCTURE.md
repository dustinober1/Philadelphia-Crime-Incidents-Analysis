# Codebase Structure

**Analysis Date:** 2026-02-02

## Directory Layout

```
[project-root]/
├── notebooks/             # Primary analysis notebooks (entry points)
├── data/                  # Committed data artifacts (Parquet, caches)
│   ├── external/          # External data snapshots and cache
│   └── crime_incidents_combined.parquet
├── reports/               # Generated figures and exported assets
├── docs/                  # Governance and notebook standards
├── .planning/             # Generated codebase maps (this directory)
├── environment.yml        # Conda environment for reproducibility
├── requirements.txt       # Optional pip requirements
├── .env.example           # Example environment variables
└── README.md              # Project overview
```

## Directory Purposes

**notebooks/**:
- Purpose: contain narrative analysis and executable notebooks. Each notebook is a self-contained pipeline for a question/figure.
- Contains: `.ipynb` files. Key files: `notebooks/philadelphia_safety_trend_analysis.ipynb`, `notebooks/covid_lockdown_crime_landscape.ipynb`, `notebooks/summer_crime_spike_analysis.ipynb`, `notebooks/data_quality_audit_notebook.ipynb`.

**data/**:
- Purpose: store source data and intermediate artifacts used by notebooks.
- Contains: Parquet files and caches. Key files: `data/crime_incidents_combined.parquet`, `data/external/weather_philly_2006_2026.parquet`, `data/external/.cache/weather_cache.sqlite`.

**reports/**:
- Purpose: store generated figures (PNG/HTML) and other exported assets. Example: `reports/covid_lockdown_burglary_trends.png`.

**docs/**:
- Purpose: standards, delivery summaries, notebook guidance. Key files: `docs/NOTEBOOK_COMPLETION_REPORT.md`, `docs/NOTEBOOK_QUICK_REFERENCE.md`, `docs/DELIVERY_SUMMARY.md`.

**.planning/**:
- Purpose: machine-generated mapping files and planning artifacts. Location created by this mapping: `.planning/codebase/ARCHITECTURE.md` and `.planning/codebase/STRUCTURE.md`.

## Key File Locations

Entry Points:
- `notebooks/philadelphia_safety_trend_analysis.ipynb`: primary analytical entry for safety trends.

Configuration:
- `environment.yml`: conda environment specification for reproducible runs.
- `requirements.txt`: pip fallback requirements.
- `.env.example`: template for environment variables.

Core Data:
- `data/crime_incidents_combined.parquet`: main combined incidents dataset.
- `data/external/weather_philly_2006_2026.parquet`: weather dataset supporting analyses.

Reports & Outputs:
- `reports/`: visualizations and exported assets.

## Naming Conventions

Files:
- Notebooks use descriptive snake_case filenames: `philadelphia_safety_trend_analysis.ipynb`.
- Data artifacts use snake_case with file-type suffix: `crime_incidents_combined.parquet`.

Directories:
- Short, lowercase names (e.g., `notebooks`, `data`, `reports`, `docs`).

## Where to Add New Code

New Notebook / Analysis:
- Primary code: `notebooks/<descriptive_name>.ipynb`.
- Outputs: `reports/<descriptive_name>.*`.

New Data Assets:
- Add under `data/` or `data/external/`. Commit Parquet or CSV snapshots used for reproducibility.

Utilities / Shared Python modules:
- Not present in repository. If adding reusable modules, create a top-level package directory `analysis/` with an `__init__.py` and place helper modules there (e.g., `analysis/io.py`, `analysis/validation.py`). Add the package to `environment.yml`/`requirements.txt` and update README with usage.

Tests:
- Not present. If adding tests, create `tests/` and use pytest; keep tests co-located with helpers (e.g., `tests/test_io.py`).

## Special Directories

data/external/.cache:
- Purpose: local cache for downloaded external datasets (sqlite cache file present: `data/external/.cache/weather_cache.sqlite`).
- Generated: Yes
- Committed: Yes (cache sqlite is currently committed)

notebooks/:
- Purpose: narrative-first deliverables; committed with outputs preserved (project rule in `AGENTS.md`).

---

*Structure analysis: 2026-02-02*
