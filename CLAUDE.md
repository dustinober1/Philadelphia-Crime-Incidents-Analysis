# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Python-first, CLI-driven data science repository** that answers public-safety questions about crime in Philadelphia. The project produces reproducible analyses and static report artifacts (charts, maps, Markdown) for operational decision-making.

**Core value:** Provide clear, reproducible, evidence-based answers to policy and operations questions about crime in Philadelphia.

## Environment

**Conda environment:** `crime` (defined in `environment.yml`)

Prefer `conda install` when adding packages; use `pip` only if a package is unavailable via conda.

Python version: 3.14+

## Common Commands

### v1.1 CLI System (Primary)

```bash
# Run any analysis via CLI
python -m analysis.cli chief trends --fast
python -m analysis.cli patrol hotspots --fast
python -m analysis.cli policy retail-theft --fast
python -m analysis.cli forecasting time-series --fast

# Show all available commands
python -m analysis.cli --help

# Environment variable override (CRIME_* prefix)
CRIME_OUTPUT_FORMAT=svg python -m analysis.cli chief trends
```

### Manual CLI Execution

All analyses are available as CLI commands:

```bash
# Chief-level analyses
python -m analysis.cli chief trends
python -m analysis.cli chief seasonality
python -m analysis.cli chief covid

# Patrol analyses
python -m analysis.cli patrol hotspots
python -m analysis.cli patrol robbery-heatmap
python -m analysis.cli patrol district-severity
python -m analysis.cli patrol census-rates

# Policy analyses
python -m analysis.cli policy retail-theft
python -m analysis.cli policy vehicle-crimes
python -m analysis.cli policy composition
python -m analysis.cli policy events

# Forecasting
python -m analysis.cli forecasting time-series
python -m analysis.cli forecasting classification
```

For command-specific help:
```bash
python -m analysis.cli chief trends --help
```

### Development & Quality Tools (v1.1)

```bash
# Install dev dependencies (pytest, black, ruff, mypy, pre-commit)
pip install -r requirements-dev.txt

# Run tests with coverage
pytest tests/ --cov=analysis --cov-report=term-missing

# Type checking
mypy analysis/

# Code formatting
black analysis/
ruff check analysis/

# Install pre-commit hooks
pre-commit install
```

**Note:** Dev dependencies are not auto-installed. Run `pip install -r requirements-dev.txt` before running quality tools.
**Coverage target:** 90% minimum (configured in pyproject.toml --cov-fail-under=90)
**mypy strict mode:** Enabled in pyproject.toml; fix errors before committing

### GSD Workflow Commands

```bash
# Plan a phase with gap closure (after verification finds gaps)
/gsd:plan-phase <NN> --gaps

# Execute only gap closure plans
/gsd:execute-phase <NN> --gaps-only

# Check phase progress and status
/gsd:progress
```

**Gap Closure Pattern:** Executors run in parallel to discover gaps, verifier documents them in VERIFICATION.md, orchestrator closes gaps with direct commits, re-verification confirms success.

### Running Tests

```bash
pytest tests/
```



## Architecture

### Phase-Based Organization

The project is organized into phases corresponding to stakeholder questions:

- **v1.1 CLI System** (Primary): `python -m analysis.cli <command>` — 13 commands across 4 groups
- **Chief:** High-level trends & seasonality — `python -m analysis.cli chief <command>`
- **Patrol:** Spatial analysis, hotspots, district severity — `python -m analysis.cli patrol <command>`
- **Policy:** Policy analysis (retail theft, vehicle crimes, events) — `python -m analysis.cli policy <command>`
- **Forecasting:** Time series forecasting, violence classification — `python -m analysis.cli forecasting <command>`

### CLI Pattern

Analyses are executed via CLI commands in `analysis/cli/`:

1. CLI loads configuration from YAML (`config/*.yaml`) with CLI argument overrides
2. Data is loaded via `analysis.data.loading.load_crime_data()` with caching
3. Analysis produces figures and reports saved to `reports/{version}/{group}/`
4. Artifacts (PNGs, SVGs, PDFs, Markdown reports) are versioned

### Key Modules

| Module | Purpose |
|--------|---------|
| `analysis/utils.py` | Legacy: Data loading, crime classification, temporal features |
| `analysis/utils/__init__.py` | v1.1: Modular utils package (classification, temporal, spatial) |
| `analysis/utils/classification.py` | v1.1: `classify_crime_category()`, `CRIME_CATEGORY_MAP` |
| `analysis/utils/temporal.py` | v1.1: `extract_temporal_features()` |
| `analysis/utils/spatial.py` | v1.1: Coordinate cleaning, spatial joins, severity scoring |
| `analysis/data/__init__.py` | v1.1: Data layer with loading, validation, preprocessing, caching |
| `analysis/data/loading.py` | v1.1: `load_crime_data()` with joblib caching |
| `analysis/data/validation.py` | v1.1: Pydantic validation (`CrimeIncidentValidator`) |
| `analysis/data/preprocessing.py` | v1.1: `filter_by_date_range()`, `aggregate_by_period()` |
| `analysis/config/` | v1.1: Pydantic-settings config package with BaseConfig, GlobalConfig |
| `analysis/config/schemas/` | v1.1: Analysis-specific configs (chief, patrol, policy, forecasting) |
| `analysis/cli/` | v1.1: CLI entry points with typer (13 commands across 4 groups) |
| `analysis/config.py` | Constants: `CRIME_DATA_PATH`, `REPORTS_DIR`, `COLORS` palette |
| `analysis/models/classification.py` | Violence classification models |
| `analysis/models/time_series.py` | Time-aware train/test splits |
| `analysis/artifact_manager.py` | Versioning, manifests, artifact tracking |
| `analysis/report_utils.py` | Report normalization, JSON schema handling |

### Configuration System

Phase parameters are stored in YAML files under `config/`:
- `phase1_config.yaml` — Annual trends, seasonality, COVID dates
- `phase2_config.yaml` — Spatial analysis, clustering, severity weights, census config
- `phase3_config.yaml` — Forecasting parameters

Configuration is loaded via Pydantic-based loaders (e.g., `analysis/config_loader.py`, `analysis/phase2_config_loader.py`).

### Data Layer

**Primary dataset:** `data/crime_incidents_combined.parquet` (192MB)

**Boundaries:** `data/boundaries/` — GeoJSON files for police districts, census tracts

**External data:** `data/external/` — Weather, economic indicators

### Data Schema Gotchas

**UCR codes:** Data uses expanded format (100-9999), not standard UCR hundred-bands (100-999)
**PSA values:** Are letter codes (A, E, D, etc.), not integers
**Count column:** Use `'objectid'` for incident counting, not `'incident_id'`
**Date aggregation:** Use `'ME'`/`'YE'` for month/year-end (pandas 2.2+), not `'M'`/`'Y'` (deprecated)
**geopandas imports:** Wrap in try/except for environments without spatial packages
**Coordinate columns:** Crime data uses `point_x`/`point_y`, not `lng`/`lat`
**load_crime_data():** Only accepts `clean` parameter; cache is always enabled
**filter_by_date_range():** Uses `start`/`end` args, not `start_date`/`end_date`
**aggregate_by_period():** Returns DataFrame with 3 columns when aggregating counts

### Output Artifacts

All outputs are saved to `reports/` with versioned filenames:
- PNG visualizations (300 DPI publication quality)
- Markdown reports
- JSON manifests (with hashes, params, runtime)
- Executed notebooks
- CSV exports

## Crime Classification Schema

From `analysis/utils.py`:

```python
CRIME_CATEGORY_MAP = {
    "Violent": {1, 2, 3, 4},  # Homicide, Rape, Robbery, Aggravated Assault
    "Property": {5, 6, 7},     # Burglary, Theft, Vehicle Theft
}
```

Classification is based on UCR hundred-bands (first digit of `ucr_general` code).

## Coordinate Bounds (Philadelphia)

From `analysis/spatial_utils.py`:
- Longitude: -75.30 to -74.95
- Latitude: 39.85 to 40.15

## Color Palette

From `analysis/config.py`:
```python
COLORS = {
    "Violent": "#E63946",
    "Property": "#457B9D",
    "Other": "#A8DADC",
}
```

## Current Milestone: v1.1 Script-Based Refactor

**Active goal:** Convert from notebook-based to script-based architecture:
- Module-based structure under `analysis/`
- CLI entry points using typer
- Configuration system (CLI args + YAML)
- New data layer with validation
- Testing framework with 90%+ coverage
- Migration of 13 notebooks to scripts
- Delete notebooks after successful conversion

See `.planning/REQUIREMENTS.md` for detailed requirements.

## Important CLI Development Rules

- CLI commands live in `analysis/cli/` (chief.py, patrol.py, policy.py, forecasting.py)
- Output artifacts go to `reports/{version}/{group}/`
- Use typer.Options with help text for all parameters
- Use Rich Progress with 5 columns for long-running operations
- Use `analysis.data.loading.load_crime_data()` for data loading
- Use `analysis.visualization.save_figure()` followed by `plt.close(fig)` for figures
- All commands must have tests in `tests/test_cli_{group}.py`
- Use `--fast` flag in tests for speed
- Use `--version test` in tests to avoid cluttering production reports
- All plots must have titles, axis labels, legends, and consistent styling
- Set seeds for stochastic processes

See `AGENTS.md` for complete CLI development guidelines.

## Code Style

- PEP 8 compliant
- Line length: 100 characters (configured in pyproject.toml)
- Avoid `from module import *`
- Use descriptive variable names
- Add Google-style docstrings (Args, Returns, Raises sections)
- Type hints encouraged (mypy compatible)
- Use Python 3.14 union syntax: `str | None` (not `Optional[str]`)

### Testing Guidelines (v1.1)

- Test files mirror module structure: `tests/test_classification.py` for `analysis/utils/classification.py`
- Use pytest fixtures for data loading (avoid loading full dataset in each test)
- Cache performance tests: time first vs second load, verify 5x+ speedup
- Coverage target: 90%+ for all new modules
- Mark slow tests with `@pytest.mark.slow` decorator
- CLI tests use `CliRunner` from `typer.testing` with `--fast` flag for fast execution
- Integration tests use `--version test` to avoid cluttering production reports directory

### CLI Development Guidelines (v1.1)

- All commands use Rich progress bars with 5 columns: SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
- Color coding: blue headers `[bold blue]`, green success `[green]`, yellow warnings `[yellow]`
- Fast mode flag `--fast` for 10% sampling in all commands
- Output files go to `reports/{version}/{group}/` directory structure
- Graceful fallback for optional dependencies (prophet, sklearn, geopandas)

### Visualization Guidelines (v1.1)

- Import from `analysis.visualization`: `save_figure()`, `setup_style()`, `plot_line()`, `plot_bar()`, `plot_heatmap()`
- All CLI figures must call `plt.close(fig)` after `save_figure()` to prevent memory leaks in tests
- Use `--output-format png|svg|pdf` argument for multi-format output support
- Figures saved to `reports/{version}/{group}/` with configurable naming

## Key Dependencies

- **Data:** pandas, numpy, geopandas, pyarrow, parquet
- **Validation:** pydantic>=2.12
- **Caching:** joblib
- **Visualization:** matplotlib, seaborn, plotly, folium, altair
- **Analysis/ML:** scikit-learn, xgboost, lightgbm, prophet, statsmodels, shap
- **CLI Framework:** typer>=0.12, rich>=13.0
- **Quality:** pytest>=8.0, black>=25.0, ruff>=0.9, mypy>=1.15, pre-commit>=4.0

## Troubleshooting

| Issue | Check |
|-------|-------|
| Config not found | `ls config/*.yaml` |
| Missing data | Verify `data/crime_incidents_combined.parquet` exists |
| Import errors | Ensure `crime` conda environment is activated |
| Quality tools not found | Run `pip install -r requirements-dev.txt` |
| mypy errors on geopandas | Use `--ignore-missing-imports` or `# type: ignore` comments |
| CLI command not found | Run `python -m analysis.cli --help` to see available commands |

## Documentation Files

- `README.md` — Project overview, quickstart
- `AGENTS.md` — Comprehensive CLI development guidelines for contributors/agents
- `.planning/PROJECT.md` — Project overview, milestones, requirements
- `.planning/REQUIREMENTS.md` — v1.1 script-based refactor requirements
- `.planning/ROADMAP.md` — Development roadmap
- `.planning/STATE.md` — Current state tracking
- `.planning/phases/*/VERIFICATION.md` — Phase verification reports with gap analysis
- `docs/` — Additional documentation (delivery summaries, forecasting, notebook reference)
