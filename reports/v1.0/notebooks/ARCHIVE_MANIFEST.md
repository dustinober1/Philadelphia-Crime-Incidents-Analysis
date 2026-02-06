# v1.0 Notebook Archive

These notebooks were migrated to v1.1 CLI commands in February 2026.
They are preserved here for historical reference.

## Migration Mapping

See [docs/MIGRATION.md](../../../docs/MIGRATION.md) for the complete
notebook-to-CLI mapping and usage examples.

## Notebooks Archived

### Chief (3 notebooks)
- philadelphia_safety_trend_analysis.ipynb → `python -m analysis.cli chief trends`
- summer_crime_spike_analysis.ipynb → `python -m analysis.cli chief seasonality`
- covid_lockdown_crime_landscape.ipynb → `python -m analysis.cli chief covid`

### Patrol (4 notebooks)
- hotspot_clustering.ipynb → `python -m analysis.cli patrol hotspots`
- robbery_temporal_heatmap.ipynb → `python -m analysis.cli patrol robbery-heatmap`
- district_severity.ipynb → `python -m analysis.cli patrol district-severity`
- census_tract_rates.ipynb → `python -m analysis.cli patrol census-rates`

### Policy (4 notebooks)
- retail_theft_trend.ipynb → `python -m analysis.cli policy retail-theft`
- vehicle_crimes_corridors.ipynb → `python -m analysis.cli policy vehicle-crimes`
- crime_composition.ipynb → `python -m analysis.cli policy composition`
- event_impact_analysis.ipynb → `python -m analysis.cli policy events`

### Forecasting (2 notebooks)
- 04_forecasting_crime_ts.ipynb → `python -m analysis.cli forecasting time-series`
- 04_classification_violence.ipynb → `python -m analysis.cli forecasting classification`

## Archive Date

2026-02-05

## v1.1 CLI System

All analysis functionality has been migrated to script-based commands
under `analysis/cli/`. See README.md for usage examples.
