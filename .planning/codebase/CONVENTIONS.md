# Coding Conventions

**Analysis Date:** 2026-02-02

## Overview

This repository is primarily an analysis / notebook project. Conventions are focused on reproducible Python data-analysis, notebook hygiene, and a small dashboard. Key policy and convention sources in the repo:

- Project guidance: `AGENTS.md`
- High-level README: `README.md`
- Environment / deps: `environment.yml`, `requirements.txt`
- Notebooks: `notebooks/` (examples: `notebooks/data_quality_audit_notebook.ipynb`, `notebooks/summer_crime_spike_analysis.ipynb`)

Where code is referenced but not present, the README documents the expected conventions (for contributors and CI).

## Naming Patterns

Files
- Notebook files: live in `notebooks/` and use descriptive, snake_case names, e.g. `notebooks/data_quality_audit_notebook.ipynb`.
- Analysis scripts (expected): `analysis/` scripts are referenced in `README.md` (examples: `analysis/06_generate_report.py`, `analysis/temporal_analysis.py`). If added, use snake_case and a numeric prefix for ordered steps (e.g. `01_fetch_data.py`, `06_generate_report.py`).

Functions and Variables
- Use snake_case for functions and variables (PEP 8). This is the stated style in `README.md` and `AGENTS.md`.
- Avoid `from module import *`. Prefer explicit imports: `from analysis.utils import load_data` or `import analysis.utils as utils`.

Classes and Types
- Use PascalCase for classes (PEP 8). No class-heavy code detected in repo, but follow Pydantic/typing conventions for models (the environment contains `pydantic`).

Modules / Packages
- Module file names are snake_case. When creating packages, include an explicit `__init__.py`.

## Code Style

Formatting
- The project recommends `black` for formatting (`requirements.txt` lists `black`) and `isort` is present in `requirements.txt`.
- Enforce formatting before commit locally or via CI (no CI is present; add if needed).

Linting
- The README recommends `flake8` or `ruff` for linting; both appear in `requirements.txt`.
- Add a top-level config when enabling linting (examples: `.flake8`, `pyproject.toml` for `ruff/black`). No lint config files were detected.

Type Checking
- `mypy` and `pydantic` packages are present in `requirements.txt`. No `mypy.ini` or explicit type-checking workflow detected. When adding typed modules, include `mypy` config and add to CI.

Notebook Conventions (prescribed and enforced in `AGENTS.md`)
- Notebooks must include a reproducibility metadata cell as the first code cell that records: Python version, conda env (`crime`), and key package versions (pandas, numpy, matplotlib, plotly, etc.). See `AGENTS.md` for the exact checklist.
- Notebooks live in `notebooks/` and publication-ready exports go to `reports/` (illustrated by `reports/` and the README).
- Notebooks should keep heavy processing in helper modules under `analysis/` and keep notebooks as orchestration/visualization layers. The README explicitly says "Keep heavy processing in `analysis/` helper modules".
- Notebooks must be runnable headless with `jupyter nbconvert --execute` for CI. The repo includes example notebooks in `notebooks/`.

Import Organization
- Prefer absolute imports for project modules (e.g. `import analysis.utils as utils`). No path aliasing / advanced import setup detected.

Error Handling

- Strategy: No centralized application-level error handling exists (this is an analysis repo). For scripts and small modules follow these rules:
  - Validate input files early and raise informative exceptions with context (use ValueError/RuntimeError with clear messages).
  - Use try/except sparingly in analysis scripts — prefer failing fast so notebooks/CI surface errors.
  - For dashboard entrypoint `dashboard/app.py` (referenced in `README.md`), handle configuration errors (missing env vars declared in `.env.example`) and exit with non-zero status.

Logging
- Use the Python `logging` module for scripts and the dashboard (no logging config detected in repo). Example pattern for script-level logging:

  import logging
  logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

Documentation & Docstrings
- Short docstrings for public functions and modules are recommended (AGENTS.md requests docstrings in notebooks and helper functions). Follow Google or NumPy style docstrings consistently.

Security & Secrets
- `.env.example` is present. Keep real secrets out of source control. Scripts should read configuration from environment variables (use `python-dotenv` if needed). The README calls out `dashboard/config.py` for env var references (file not present in repository).

Where to Put New Code
- Analysis helpers: `analysis/` (create if missing). Key helper files referenced in README: `analysis/utils.py`, `analysis/config.py`, `analysis/06_generate_report.py`.
- Dashboard code: `dashboard/` — entry point referenced as `dashboard/app.py` in `README.md`.

Prescriptive Rules (for contributors and automated agents)
- Use `black` + `isort` on all Python code before committing.
- Run `flake8` or `ruff` and fix reported issues before opening a PR.
- Keep notebooks small: move reusable code into `analysis/` helpers and import them from notebooks.
- Add tests for any non-trivial function in `analysis/` (see `TESTING.md`).

Files referenced in this section (examples):
- `README.md`
- `AGENTS.md`
- `requirements.txt`
- `environment.yml`
- `notebooks/data_quality_audit_notebook.ipynb`
- `notebooks/summer_crime_spike_analysis.ipynb`

---

*Convention analysis: 2026-02-02*
