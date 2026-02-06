# Notebook to CLI Migration Guide

## Overview

This guide explains how v1.0 Jupyter notebooks map to v1.1 CLI commands.
All 13 analysis notebooks have been converted to script-based commands
using typer, providing better testability, reproducibility, and CI/CD integration.

## Migration Mapping

### Phase 1 (Chief) Notebooks -> Chief Commands

| Notebook | CLI Command | Verification Test |
|----------|-------------|-------------------|
| `philadelphia_safety_trend_analysis.ipynb` | `python -m analysis.cli chief trends` | `tests/test_cli_chief.py::TestChiefTrends` |
| `summer_crime_spike_analysis.ipynb` | `python -m analysis.cli chief seasonality` | `tests/test_cli_chief.py::TestChiefSeasonality` |
| `covid_lockdown_crime_landscape.ipynb` | `python -m analysis.cli chief covid` | `tests/test_cli_chief.py::TestChiefCovid` |

### Phase 2 (Patrol) Notebooks -> Patrol Commands

| Notebook | CLI Command | Verification Test |
|----------|-------------|-------------------|
| `hotspot_clustering.ipynb` | `python -m analysis.cli patrol hotspots` | `tests/test_cli_patrol.py::TestPatrolHotspots` |
| `robbery_temporal_heatmap.ipynb` | `python -m analysis.cli patrol robbery-heatmap` | `tests/test_cli_patrol.py::TestPatrolRobberyHeatmap` |
| `district_severity.ipynb` | `python -m analysis.cli patrol district-severity` | `tests/test_cli_patrol.py::TestPatrolDistrictSeverity` |
| `census_tract_rates.ipynb` | `python -m analysis.cli patrol census-rates` | `tests/test_cli_patrol.py::TestPatrolCensusRates` |

### Phase 3 (Policy) Notebooks -> Policy Commands

| Notebook | CLI Command | Verification Test |
|----------|-------------|-------------------|
| `retail_theft_trend.ipynb` | `python -m analysis.cli policy retail-theft` | `tests/test_cli_policy.py::TestPolicyRetailTheft` |
| `vehicle_crimes_corridors.ipynb` | `python -m analysis.cli policy vehicle-crimes` | `tests/test_cli_policy.py::TestPolicyVehicleCrimes` |
| `crime_composition.ipynb` | `python -m analysis.cli policy composition` | `tests/test_cli_policy.py::TestPolicyComposition` |
| `event_impact_analysis.ipynb` | `python -m analysis.cli policy events` | `tests/test_cli_policy.py::TestPolicyEvents` |

### Phase 4 (Forecasting) Notebooks -> Forecasting Commands

| Notebook | CLI Command | Verification Test |
|----------|-------------|-------------------|
| `04_forecasting_crime_ts.ipynb` | `python -m analysis.cli forecasting time-series` | `tests/test_cli_forecasting.py::TestForecastingTimeSeries` |
| `04_classification_violence.ipynb` | `python -m analysis.cli forecasting classification` | `tests/test_cli_forecasting.py::TestForecastingClassification` |

## Usage Examples

### Example 1: Chief Trends Analysis

**v1.0 (Notebook):**
```bash
jupyter notebook notebooks/philadelphia_safety_trend_analysis.ipynb
# Run all cells, wait 3-5 minutes
# Output saved to reports/
```

**v1.1 (CLI):**
```bash
# Full run
python -m analysis.cli chief trends

# Fast mode (10% sample, ~30 seconds)
python -m analysis.cli chief trends --fast

# Custom date range
python -m analysis.cli chief trends --start-year 2018 --end-year 2022

# SVG output for publication
python -m analysis.cli chief trends --output-format svg

# Custom version tag
python -m analysis.cli chief trends --version v2.0
```

**Output:** `reports/{version}/chief/annual_trends_report_*`

### Example 2: Patrol Hotspots

**v1.0 (Notebook):**
```bash
jupyter notebook notebooks/hotspot_clustering.ipynb
# Run all cells, wait 5-7 minutes
```

**v1.1 (CLI):**
```bash
python -m analysis.cli patrol hotspots --fast
```

**Output:** `reports/{version}/patrol/hotspots_*`

### Example 3: Forecasting

**v1.0 (Notebook):**
```bash
jupyter notebook notebooks/04_forecasting_crime_ts.ipynb
# Run all cells, wait 5-10 minutes (Prophet is slow)
```

**v1.1 (CLI):**
```bash
python -m analysis.cli forecasting time-series --fast
```

**Output:** `reports/{version}/forecasting/time_series_*`

## Common Arguments

All CLI commands support these common arguments:

- `--fast`: Fast mode with 10% sample (for testing)
- `--version`: Output version tag (default: v1.0)
- `--output-format`: Figure format (png, svg, pdf)

## Getting Help

**Top-level help:**
```bash
python -m analysis.cli --help
```

**Group-level help:**
```bash
python -m analysis.cli chief --help
python -m analysis.cli patrol --help
python -m analysis.cli policy --help
python -m analysis.cli forecasting --help
```

**Command-level help:**
```bash
python -m analysis.cli chief trends --help
python -m analysis.cli patrol hotspots --help
```

## Verification Tests

All CLI commands have corresponding tests in `tests/test_cli_*.py`.
Tests verify:
- Command executes successfully (exit_code == 0)
- Expected output files are created
- Output content matches expected patterns

Run tests:
```bash
# Run all CLI tests
pytest tests/test_cli_*.py

# Run specific test group
pytest tests/test_cli_chief.py

# Run with coverage
pytest tests/test_cli_*.py --cov=analysis/cli --cov-report=term-missing
```

## Migration Benefits

**Why migrate from notebooks to CLI scripts?**

1. **Testability:** Commands can be tested automatically with pytest
2. **CI/CD:** Scripts integrate with continuous integration pipelines
3. **Performance:** No Jupyter overhead, faster execution
4. **Reproducibility:** Version-controlled scripts with deterministic behavior
5. **Documentation:** CLI `--help` provides built-in command documentation
6. **Flexibility:** CLI arguments allow runtime configuration without editing code

## Breaking Changes from v1.0

- **Invocation:** Changed from `jupyter notebook` to `python -m analysis.cli`
- **Configuration:** CLI arguments replace notebook cell parameters
- **Output:** All outputs go to `reports/{version}/{group}/` (structured directories)
- **Figures:** Saved as PNG/SVG/PDF via `--output-format` argument
- **Fast mode:** `--fast` flag replaces manual data sampling in notebooks

## Archived Notebooks

Original v1.0 notebooks have been archived to `reports/v1.0/notebooks/` for
historical reference. They are no longer used for analysis but may be useful
for understanding the original implementation.

## Questions?

See CLAUDE.md for development guidelines or AGENTS.md for contribution rules.
