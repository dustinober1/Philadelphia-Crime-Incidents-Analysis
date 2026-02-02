# Architecture

**Analysis Date:** 2026-02-02

## Pattern Overview

Overall: Repository is an analysis-first project organized around reproducible notebooks and data artifacts. There is no running web service or packaged library in the current tree; analysis is performed in Jupyter notebooks which act as the primary executable units.

Key Characteristics:
- Notebook-driven analysis (single-purpose notebooks are the functional units).
- Data-artifact centric: large datasets and preprocessed Parquet files under `data/` are primary inputs/outputs.
- Report generation is file-based: outputs are written to `reports/` as images and Markdown/HTML assets.

## Layers

Data Layer:
- Purpose: store source and processed datasets used by analyses.
- Location: `data/` and `data/external/`.
- Contains: `data/crime_incidents_combined.parquet`, `data/external/weather_philly_2006_2026.parquet`, `data/external/.cache/weather_cache.sqlite`.
- Depends on: none (static files on disk).
- Used by: notebooks in `notebooks/` that read Parquet/CSV with pandas/geopandas.

Analysis Layer (Working/Computation):
- Purpose: perform data cleaning, transformations, visualization and reporting.
- Location: `notebooks/`.
- Contains: `notebooks/philadelphia_safety_trend_analysis.ipynb`, `notebooks/summer_crime_spike_analysis.ipynb`, `notebooks/covid_lockdown_crime_landscape.ipynb`, `notebooks/data_quality_audit_notebook.ipynb`.
- Depends on: `data/` artifacts and environment defined in `environment.yml` / `requirements.txt`.
- Used by: human operators, CI notebook-runner (if configured).

Reporting Layer:
- Purpose: hold human-consumable outputs produced by analyses.
- Location: `reports/`.
- Contains: images and exported figures, e.g. `reports/covid_lockdown_burglary_trends.png`.
- Depends on: outputs produced by notebooks.

Documentation & Governance:
- Purpose: standards, rules and repository guidance.
- Location: `docs/`, `AGENTS.md`, `README.md`.
- Contains: notebook standards (`AGENTS.md`), quick references (`docs/NOTEBOOK_QUICK_REFERENCE.md`), completion checklist guidance.

Configuration & Environment:
- Purpose: define reproducible execution environment and secrets placeholders.
- Files: `environment.yml`, `requirements.txt`, `.env.example`.

Version control / Metadata:
- Purpose: project history and repository metadata.
- Location: `.git/` (present in repository root).

## Data Flow

1. Source datasets are present under `data/` (example: `data/crime_incidents_combined.parquet`).
2. Notebooks in `notebooks/` load these files (pandas/geopandas) and perform cleaning/transformations in-memory.
3. Notebooks generate visualizations and export artifacts into `reports/` (images/Markdown/HTML).
4. Documentation and guidance in `docs/` and `AGENTS.md` describe standards for notebooks and CI execution.

State Management:
- Transient and memory-first: notebooks manage state in-memory during execution. There is no centralized state store or database in the current repository.

## Key Abstractions

Dataset (parquet artifact):
- Purpose: compact, columnar snapshot of cleaned/merged crime data.
- Examples: `data/crime_incidents_combined.parquet`.
- Pattern: consumed directly by notebooks via `pandas.read_parquet` / `geopandas.read_file`.

Notebook (analysis unit):
- Purpose: hold an end-to-end analysis or validation workflow (data load → transform → visualize → export).
- Examples: `notebooks/data_quality_audit_notebook.ipynb`.
- Pattern: self-contained scripts with a reproducibility cell as required by `AGENTS.md`.

Report (artifact):
- Purpose: final outputs for publication or presentation.
- Examples: `reports/covid_lockdown_burglary_trends.png`.

## Entry Points

There are no Python script entrypoints (no `analysis/` or `dashboard/` packages present). The practical entry points are the notebooks themselves:
- `notebooks/philadelphia_safety_trend_analysis.ipynb`
- `notebooks/summer_crime_spike_analysis.ipynb`
- `notebooks/covid_lockdown_crime_landscape.ipynb`
- `notebooks/data_quality_audit_notebook.ipynb`

CI Entry Point (if configured):
- The repository documents an automated notebook-runner in `AGENTS.md` and expects a workflow such as `.github/workflows/run-notebooks.yml` to execute notebooks via `jupyter nbconvert --execute`. The workflow file is not present in the current tree; if CI is present, it would invoke the notebooks listed above.

## Error Handling

Strategy: ad-hoc, per-notebook error checks and validation. Notebooks include data-validation steps (per `AGENTS.md`) but there is no shared exception-handling framework or central logging service configured in the codebase.

Patterns:
- Validate inputs early in each notebook (missingness, schema checks).
- Fail-fast: notebooks should abort on critical data errors and report via raised exceptions or captured traceback in CI.

## Cross-Cutting Concerns

Logging: there is no centralized logging library in the repository. Notebooks typically rely on standard Python stdout/stderr and notebook outputs.

Validation: per-notebook validation responsibilities are documented in `AGENTS.md` and implemented inside notebooks.

Authentication: Not applicable — there are no external services requiring runtime auth in the current repository. A placeholder `.env.example` exists for secret configuration.

---

*Architecture analysis: 2026-02-02*
