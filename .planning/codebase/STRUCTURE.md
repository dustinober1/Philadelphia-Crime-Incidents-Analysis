# Codebase Structure

**Analysis Date:** 2026-02-02

## Directory Layout

```
[project-root]/
├── .git/                 # Git metadata
├── .env.example          # Environment variable template
├── README.md             # Project overview and quickstart
├── environment.yml       # Conda environment spec
├── requirements.txt      # Python pip requirements (present)
├── data/                 # Data artifacts (raw, processed, external)
│   ├── crime_incidents_combined.parquet
│   └── external/
│       ├── weather_philly_2006_2026.parquet
│       └── .cache/weather_cache.sqlite
├── notebooks/            # Jupyter notebooks (analysis units)
│   ├── philadelphia_safety_trend_analysis.ipynb
│   ├── summer_crime_spike_analysis.ipynb
│   ├── covid_lockdown_crime_landscape.ipynb
│   └── data_quality_audit_notebook.ipynb
├── reports/              # Generated report artifacts (images, html)
│   └── covid_lockdown_burglary_trends.png
├── docs/                 # Documentation and notebook standards
│   ├── NOTEBOOK_QUICK_REFERENCE.md
│   └── NOTEBOOK_COMPLETION_REPORT.md
├── AGENTS.md             # Agent and contributor guidance (notebook rules)
└── .planning/            # Generated planning artifacts
    └── codebase/         # (this output)
```

## Directory Purposes

**data/**:
- Purpose: store datasets consumed by notebooks and analyses.
- Contains: Parquet datasets and caching DBs.
- Key files: `data/crime_incidents_combined.parquet`, `data/external/weather_philly_2006_2026.parquet`.

**notebooks/**:
- Purpose: primary place for analyses. Each notebook is an executable analysis pipeline (load → transform → visualize → export).
- Contains: domain-focused notebooks named by analysis purpose.
- Key files: all `.ipynb` files in `notebooks/`.

**reports/**:
- Purpose: generated artifacts for presentation and review.
- Contains: PNGs, HTML exports, and other report assets.

**docs/** and `AGENTS.md`:
- Purpose: governance, reproducibility rules, and contributor guidance. Notebooks must follow these rules.

**Root config files** (`environment.yml`, `requirements.txt`, `.env.example`):
- Purpose: define runtime environment, Python dependencies, and required environment variables.

## Key File Locations

Entry Points:
- `notebooks/*.ipynb` — primary executable content. Run via Jupyter or headless `jupyter nbconvert --execute`.

Configuration:
- `environment.yml` — conda environment specification
- `requirements.txt` — pip fallback
- `.env.example` — environment variable placeholders

Core Data:
- `data/crime_incidents_combined.parquet` — canonical combined dataset
- `data/external/weather_philly_2006_2026.parquet` — external reference dataset

Documentation:
- `README.md`, `AGENTS.md`, `docs/NOTEBOOK_QUICK_REFERENCE.md`

## Naming Conventions

Files:
- Notebooks: use descriptive, snake_case names ending with `_analysis` or context (e.g., `summer_crime_spike_analysis.ipynb`).
- Data artifacts: descriptive, lower_snake_case, include timeframe when appropriate (e.g., `weather_philly_2006_2026.parquet`).

Directories:
- Top-level functional directories: `data/`, `notebooks/`, `reports/`, `docs/`.

## Where to Add New Code

New Analysis Feature (notebook-first):
- Primary code: create a new notebook under `notebooks/` named `YYYY_mm_dd_<short_description>.ipynb` or `<feature>_analysis.ipynb`.
- Tests: add data validation cells inside the notebook; create a matching `docs/notebook_summaries/` entry if producing published output.

New Utility Module (reusable code):
- Implementation: add a new `analysis/` package at project root (create `analysis/__init__.py`) and place helpers under `analysis/utils.py` or `analysis/io.py`.
- Tests: add `tests/` directory and `pytest` test modules (not present yet).

Utilities & Shared Helpers:
- Shared code should live under `analysis/` (notebooks should import from `analysis` rather than duplicating logic inside notebooks).

## Special Directories

`.planning/`: contains generated planning artifacts and maps (this folder). Generated files committed here are for orchestrator use.

`data/external/.cache/`: contains caching artifacts (SQLite cache) — committed in this repo but should be considered for `.gitignore` if environment-specific.

---

*Structure analysis: 2026-02-02*
