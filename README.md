# Crime Incidents - Philadelphia

A reproducible analysis project for Philadelphia crime incidents. This repository contains data loading and cleaning utilities, domain-specific analyses (chief, patrol, policy, forecasting), automated report generation, and a script-first CLI workflow for reproducible outputs.

## Highlights
- Script-based CLI architecture with 13 analysis commands.
- Reproducible data processing and validation pipelines.
- Automated report generation into `reports/{version}/{group}/`.
- Comprehensive pytest coverage for CLI commands and core analysis modules.

## Requirements
- Python 3.14+
- Conda environment `crime` (see `environment.yml`)

## Quickstart

### Prerequisites
- Python 3.14+
- Conda environment `crime` (see `environment.yml`)

### Installation

```bash
# Create conda environment
conda env create -f environment.yml
conda activate crime

# Install dev dependencies (for testing)
pip install -r requirements-dev.txt
```

### Running Analyses

**v1.1 CLI (Recommended):**

All analyses are available as CLI commands:

```bash
# Chief-level analyses (trends, seasonality, COVID)
python -m analysis.cli chief trends --fast
python -m analysis.cli chief seasonality --fast
python -m analysis.cli chief covid --fast

# Patrol analyses (hotspots, robbery, district severity, census rates)
python -m analysis.cli patrol hotspots --fast
python -m analysis.cli patrol robbery-heatmap --fast
python -m analysis.cli patrol district-severity --fast
python -m analysis.cli patrol census-rates --fast

# Policy analyses (retail theft, vehicle crimes, composition, events)
python -m analysis.cli policy retail-theft --fast
python -m analysis.cli policy vehicle-crimes --fast
python -m analysis.cli policy composition --fast
python -m analysis.cli policy events --fast

# Forecasting (time series, classification)
python -m analysis.cli forecasting time-series --fast
python -m analysis.cli forecasting classification --fast

# See all available commands
python -m analysis.cli --help
```

**Command options:**
- `--fast`: Fast mode with 10% sample (for testing)
- `--version`: Output version tag (default: v1.0)
- `--output-format`: Figure format (png, svg, pdf)

**Output:** All artifacts saved to `reports/{version}/{group}/` with PNG/SVG/PDF figures and text summaries.

**Note:** The v1.0 notebook-based workflow has been migrated to CLI scripts. See [docs/MIGRATION.md](docs/MIGRATION.md) for the complete mapping of notebooks to CLI commands.

## Repository Layout

- `analysis/` - Analysis modules and CLI commands
  - `cli/` - CLI entry points using typer (chief, patrol, policy, forecasting)
  - `data/` - Data layer with loading, validation, preprocessing
  - `utils/` - Utility functions (classification, temporal, spatial)
  - `visualization/` - Publication-quality visualization utilities
  - `config/` - Configuration management with YAML schemas
- `tests/` - Pytest tests for all modules and CLI commands
- `data/` - Data storage (cleaned parquet, boundaries, external)
- `reports/` - Analysis outputs (figures, markdown reports, manifests)
- `config/` - YAML configuration files for each analysis group
- `docs/` - Additional documentation (migration guide, summaries)

## Development Guidelines

This project follows script-based development with CLI commands. See `AGENTS.md` for complete contribution guidelines including:

- Script structure using typer and Rich
- Testing with pytest and CliRunner
- Code quality standards (black, ruff, mypy)
- Pre-commit hooks for automated checks
- Documentation patterns

For the v1.0 -> v1.1 migration guide, see [docs/MIGRATION.md](docs/MIGRATION.md).

## Data & Privacy
- Keep raw datasets with personally-identifiable information (PII) out of version control.
- Store local raw inputs under `data/raw/` and document external data provenance.

## Common Workflows

**Run all tests:**
```bash
pytest tests/
```

**Run tests with coverage:**
```bash
pytest tests/ --cov=analysis --cov-report=term-missing
```

**Run specific analysis:**
```bash
python -m analysis.cli chief trends --output-format svg
```

**Check CLI help:**
```bash
python -m analysis.cli --help
python -m analysis.cli chief trends --help
```

## v1.1 Release Notes

The v1.1 release introduces a script-based architecture replacing the
notebook-based workflow from v1.0. Key improvements:

- **CLI Commands:** All 13 analyses available as `python -m analysis.cli` commands
- **Testing:** Comprehensive pytest tests with 90%+ coverage
- **Configuration:** YAML configs with CLI argument overrides
- **Quality:** Automated linting, formatting, type checking
- **Visualization:** Multi-format output (PNG, SVG, PDF) with consistent styling
- **Performance:** Faster execution without Jupyter overhead

See [docs/MIGRATION.md](docs/MIGRATION.md) for the complete notebook-to-CLI mapping.

## Quick Reference: All 13 Commands

### Chief (3 commands)
- `trends`: Annual crime trends analysis
- `seasonality`: Seasonal patterns and summer spike
- `covid`: Pre/during/post COVID comparison

### Patrol (4 commands)
- `hotspots`: Spatial clustering analysis
- `robbery-heatmap`: Temporal heatmap for robbery
- `district-severity`: Per-district severity scoring
- `census-rates`: Population-normalized crime rates

### Policy (4 commands)
- `retail-theft`: Retail theft trend analysis
- `vehicle-crimes`: Vehicle crime corridor analysis
- `composition`: Crime composition breakdown
- `events`: Event-day impact analysis

### Forecasting (2 commands)
- `time-series`: Prophet-based time series forecasting
- `classification`: Violence classification with feature importance

## Legacy Notebooks

Original v1.0 notebooks have been archived to `reports/v1.0/notebooks/`.
They are no longer maintained but preserved for historical reference.
