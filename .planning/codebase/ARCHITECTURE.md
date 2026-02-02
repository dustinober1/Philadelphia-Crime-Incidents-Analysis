# Architecture

**Analysis Date:** 2026-02-02

## Pattern Overview

Overall: Data-analysis / reproducible-notebook project

Key Characteristics:
- Primary deliverables are Jupyter notebooks which contain orchestration, analysis and visualizations.
- Data is stored as committed artifacts under `data/` (Parquet and local cache files).
- Reproducibility and environment isolation are enforced via `environment.yml` and `requirements.txt`.

## Layers

Notebooks (Presentation & Orchestration):
- Purpose: interactively run data loading, transformation, analysis and produce figures/reports.
- Location: `notebooks/`
- Contains: Jupyter notebooks (examples: `notebooks/philadelphia_safety_trend_analysis.ipynb`, `notebooks/covid_lockdown_crime_landscape.ipynb`)
- Depends on: local data files in `data/`, Python environment in `environment.yml`/`requirements.txt`
- Used by: reviewers and CI workflow (CI executes notebooks headless via `.github/workflows/run-notebooks.yml` referenced in `AGENTS.md`)

Data (Raw & Processed Artifacts):
- Purpose: store data used by analysis and cached intermediate artifacts
- Location: `data/` and subfolders (examples: `data/crime_incidents_combined.parquet`, `data/external/weather_philly_2006_2026.parquet`, `data/external/.cache/weather_cache.sqlite`)
- Contains: Parquet datasets, sqlite cache, other raw files
- Depends on: ETL or data retrieval code invoked from notebooks

Reports / Outputs:
- Purpose: final figures and exported assets for consumption
- Location: `reports/` (example: `reports/covid_lockdown_burglary_trends.png`)

Docs & Governance:
- Purpose: contribution rules, notebook standards, delivery notes
- Location: `docs/` (examples: `docs/NOTEBOOK_COMPLETION_REPORT.md`, `docs/NOTEBOOK_QUICK_REFERENCE.md`, `docs/DELIVERY_SUMMARY.md`)

Environment & Config:
- Purpose: pin environment and declare dependencies
- Location: repo root files: `environment.yml`, `requirements.txt`, `.env.example`

Project Metadata & Entry README:
- Location: `README.md`, `AGENTS.md`

## Data Flow

Typical data flow for an analysis notebook:
1. Notebook loads environment and imports (first cells).
2. Notebook reads committed data artifacts from `data/` (e.g. `data/crime_incidents_combined.parquet`).
3. Notebook applies transformations in-cell or calls helper modules (helper modules are not present as top-level Python packages in the repository today; functionality lives inside notebooks).
4. Notebook writes outputs to `reports/` and may write intermediate artifacts back to `data/`.
5. Final notebooks and reports are committed; CI executes notebooks headless for verification.

State Management:
- There is no application-level state store or service. State is files on disk under `data/`.

## Key Abstractions

Notebooks as first-class components:
- Purpose: each notebook is a self-contained entry point for a particular analysis or question.
- Examples: `notebooks/summer_crime_spike_analysis.ipynb`, `notebooks/data_quality_audit_notebook.ipynb`

Data artifacts:
- Purpose: immutable or versioned data snapshots used for reproducibility.
- Examples: `data/crime_incidents_combined.parquet`, `data/external/weather_philly_2006_2026.parquet`

Environment abstraction (conda/pinned requirements):
- Purpose: reproducible execution environment; files: `environment.yml`, `requirements.txt`

## Entry Points

Primary entry points (for users):
- Interactive: open any notebook under `notebooks/` (e.g. `notebooks/philadelphia_safety_trend_analysis.ipynb`).
- Documentation/Guidance: `AGENTS.md` and `README.md` describe workflows and rules.

CI entry points (automation):
- The CI workflow referenced in `AGENTS.md` (`.github/workflows/run-notebooks.yml`) is the automation entrypoint for headless execution. (File referenced in `AGENTS.md` but not present in repository root; CI guidance exists in docs.)

## Error Handling

Strategy: notebooks handle errors ad-hoc inside cells. There is no centralized error-handling library or structured try/catch across notebooks.

Patterns:
- Notebook-level assertions and validations (data quality checks) are present in analysis notebooks — see `notebooks/data_quality_audit_notebook.ipynb` for an example of validation-focused code cells.

## Cross-Cutting Concerns

Logging: ephemeral and ad-hoc via notebook outputs and saved plots; no centralized logging or telemetry.

Validation: validation is implemented inside notebooks (data quality audit notebook).

Authentication: not applicable — this repository does not contain external service integrations that require runtime secrets in code. `.env.example` exists to document expected env variables.

---

*Architecture analysis: 2026-02-02*
