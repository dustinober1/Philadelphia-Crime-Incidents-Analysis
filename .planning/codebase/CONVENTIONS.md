# Coding Conventions

**Analysis Date:** 2026-02-02

This document records the coding and notebook conventions that are present in the repository and the prescriptive, actionable conventions to follow when adding code or tests. All referenced files are present in the repository and are shown with exact paths.

## Sources of conventions (observed)
- `AGENTS.md` (root) — explicit, project-wide notebook and style rules. See `AGENTS.md` for the full ruleset. Key references in this document: `AGENTS.md` (root).
- `README.md` (root) — high-level project layout and development guidance (mentions `black`, `flake8`/`ruff`). See `README.md` for quickstart and layout references.
- `requirements.txt` (root) and `environment.yml` (root) — contain formatting and lint dependencies such as `black`, `isort`, `ruff`, and `flake8`.

## High-level style

- Language: Python 3 (recommended 3.9+ in `README.md`; `environment.yml` pins Python to `3.14` in this environment). Files: any Python modules should be `.py` files.
- Style guide: PEP 8 is the canonical style referenced in `AGENTS.md` and `README.md`.
- Formatting tools detected: `black` is included in `requirements.txt` and `environment.yml` (`black` package). Linting tools detected: `flake8` and `ruff` are present in `requirements.txt` and `environment.yml`.
- Import sorting: `isort` is present in `requirements.txt` and `environment.yml`.

Prescriptive rule (follow these when adding code):
- Run `black` on changed Python files before committing.
- Use `isort` to keep import groups stable.
- Run `ruff` or `flake8` as a pre-commit check (project does not include pre-commit hooks in repo; add if desired).

Relevant files/paths:
- `README.md` (root) — `README.md` lines referencing `black` and linting tools.
- `requirements.txt` (root) — contains `black`, `ruff`, `flake8`, and `isort` entries.
- `environment.yml` (root) — contains formatting/linting tools and Python version.

## File & naming conventions

- Python modules: snake_case for file names (example expected paths referenced in `README.md`): `analysis/utils.py`, `analysis/config.py`, `analysis/06_generate_report.py`, `dashboard/app.py`.
- Notebooks: use descriptive, kebab-like or underscore-separated names in `notebooks/`, e.g. `notebooks/data_quality_audit_notebook.ipynb` (observed).
- Packages / directories: use lowercase, short names (observed layout in `README.md` — `analysis/`, `dashboard/`, `notebooks/`, `reports/`, `data/`).
- Tests: when added, tests should be placed in a top-level `tests/` directory using `test_*.py` filenames (see Testing section). `tests/` is not present in the repository currently.

Prescriptive patterns (strict):
- Module filenames: `^[a-z0-9_]+\.py$` (snake_case). Example: `analysis/utils.py`.
- Class names: CapWords (PascalCase). Example: `class DataLoader`.
- Function and variable names: snake_case. Example: `def load_data(path: str) -> pd.DataFrame`.
- Constant names: UPPER_SNAKE_CASE. Example: `DATA_DIR = "data/"`.

Files/paths referenced in guidance:
- `analysis/` (expected directory per `README.md`)
- `dashboard/app.py` (entrypoint referenced in `README.md`)
- `notebooks/` (observed; notebooks present)
- `reports/` (observed)
- `data/raw/`, `data/external/`, `data/processed/` (observed and listed in `.gitignore` and `README.md`)

## Code organization patterns (observed + prescriptive)

Observed organization (from `README.md` and `AGENTS.md`):
- `analysis/` should contain reusable Python modules for heavy processing and helpers. Files mentioned: `analysis/utils.py`, `analysis/config.py`, `analysis/06_generate_report.py`.
- Notebooks should orchestrate analysis and call `analysis/` helpers (explicit instruction in `AGENTS.md`). Notebooks are kept in `notebooks/` and exported artifacts are in `reports/`.

Prescriptive module layout (use when adding code):
- Put reusable functions in `analysis/` modules. Examples: `analysis/utils.py`, `analysis/io.py`, `analysis/transform.py`.
- Keep the notebook logic orchestrating analysis, not implementing large helper functions. When a function is used by multiple notebooks, put it into `analysis/<module>.py` and import it from notebooks (e.g., in `notebooks/philadelphia_safety_trend_analysis.ipynb` import `analysis.utils`).

Key file paths to use when adding code:
- Primary analyses/helpers: `analysis/` (create `analysis/__init__.py` when needed)
- Notebook orchestration: `notebooks/` (co-locate notebooks)
- Exports and figures: `reports/`
- Dashboard code: `dashboard/` (example: `dashboard/app.py`)

## Docstrings and comments

- The repository guidance (`AGENTS.md`) requires short docstrings for helper functions and descriptive variable names. There are no code files in `analysis/` to inspect, so this is a repository policy rather than an enforced pattern in code.

Prescriptive rule (enforceable):
- Use Google-style or NumPy-style docstrings for non-trivial functions and classes. Example:

```python
def load_data(path: str) -> pd.DataFrame:
    """Load raw data from path and apply minimal validation.

    Parameters
    ----------
    path : str
        Path to the parquet/csv file

    Returns
    -------
    pandas.DataFrame
    """
    ...
```

Place docstrings at the function/class level and keep inline comments only for non-obvious decisions.

## Import organization

- Observed guidance: `isort` and `black` are available and should be used to keep imports consistent. `README.md` recommends `black`.

Prescriptive import groups:
1. Standard library (sorted)
2. Third-party packages (sorted)
3. Local application imports (sorted)

Always use absolute imports within the project (example):
`from analysis.utils import load_data` rather than relative imports from notebooks.

## Error handling

Observed state: There are no production Python modules to inspect for error-handling patterns. The notebooks contain analysis code but are not a reliable source of code-level error strategy.

Prescriptive rules (consistent with project style and data-processing requirements):
- Validate inputs early. For example, functions that accept a file path should check existence and expected format and raise `ValueError` with an explanatory message on invalid input.
- Use specific exceptions rather than bare `except:` blocks. Example:

```python
try:
    df = pd.read_parquet(path)
except (FileNotFoundError, OSError) as e:
    raise FileNotFoundError(f"Missing data file: {path}") from e
```

- For long-running processing steps, raise informative exceptions and include `logging` calls (see Logging below).

## Logging

Observed: The repo does not include a centralized logging configuration file. `AGENTS.md` and `README.md` do not prescribe a logging framework explicitly.

Prescriptive guidance:
- Use the standard `logging` module for analysis and dashboard code. Provide a small helper at `analysis/logging.py` or `analysis/config.py` that configures a logger used across modules. Example usage:

```python
import logging

logger = logging.getLogger("crime")
logger.setLevel(logging.INFO)

logger.info("Loaded dataset with %d rows", len(df))
```

Place logging configuration in `analysis/config.py` and avoid printing to stdout for non-interactive scripts. Notebooks may use `print` for exploratory output but prefer `logger` in scripts.

## Notebooks (strong, repository-level conventions)

The repository defines detailed notebook rules in `AGENTS.md` and summary items in `README.md`. These are enforced as project policy.

Observed, enforceable rules and file paths:
- Notebooks live in `notebooks/`. Observed files: `notebooks/data_quality_audit_notebook.ipynb`, `notebooks/summer_crime_spike_analysis.ipynb`, etc.
- Reproducibility cell must be the first code cell and record Python version, environment name, and key packages (`AGENTS.md`).
- Notebooks must include a fast/sampled dev path for long-running steps and be runnable headless in CI via `jupyter nbconvert --execute` (see `AGENTS.md`).
- Notebook outputs guidance conflict: `AGENTS.md` requests that completed notebooks be committed with outputs preserved, while `README.md` (line 69) instructs to "Commit notebooks with outputs cleared". Both files exist in the repository — this is the current state and should be resolved by maintainers. Paths: `AGENTS.md`, `README.md`.

Prescriptive, reconciled guidance (recommended to adopt consistently):
- Keep a repository policy and follow only one rule. Prefer committing executed notebooks with outputs preserved for reproducibility and also maintain a CI step that runs a cleared execution for validation. Document the chosen policy in `README.md` and `AGENTS.md`.

## Type hints and static typing

Observed: `mypy` is present in `requirements.txt` and `environment.yml` (the environment includes `mypy`) but the repo does not contain `.py` modules to inspect for type usage.

Prescriptive guidance:
- Use type hints on public functions and return types for analysis modules (e.g., `def load_data(path: str) -> pd.DataFrame`).
- Consider adding `mypy.ini`/`pyproject.toml` and a CI step running `mypy` for non-notebook code.

## Security & secrets

Observed security conventions:
- `.env` is ignored via `.gitignore` (path: `.gitignore`). An example `.env.example` is present at project root.

Prescriptive rule:
- Do not commit secrets. Use `python-dotenv` (present in `requirements.txt`) for local development and ensure `.env` is in `.gitignore` (observed).

## Summary / Next actions for contributors

- Follow PEP 8; use `black` + `isort` + `ruff` as part of local development workflow. Files: `requirements.txt`, `environment.yml`.
- Place reusable code in `analysis/` and keep notebooks in `notebooks/` as orchestrators. Reference: `README.md` and `AGENTS.md`.
- Add tests under `tests/` (see `TESTING.md`) and include `pytest`/`pytest-cov` entries (already present in `requirements.txt`).
- Resolve the notebook outputs instruction conflict between `AGENTS.md` and `README.md`.

---

*Convention analysis: 2026-02-02*
