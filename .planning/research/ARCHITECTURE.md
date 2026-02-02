# ARCHITECTURE.md

Project Research — Recommended architecture patterns for analyses and artifacts

Overview
- Keep the existing notebook-first pattern, but introduce a small `analysis/` module for reusable helpers (IO, geospatial utilities, plotting helpers) to avoid duplication across notebooks.

Suggested layout
- analysis/
  - io.py — data loading helpers (read canonical Parquet, validate schema)
  - spatial.py — spatial join helpers, tract lookups
  - viz.py — common plotting utilities (map basemap, color palettes)
- notebooks/ — single-purpose notebooks that call helpers from `analysis/`
- data/raw, data/external, data/processed — as defined in STACK.md
- reports/ — exported figures and Markdown

Component responsibilities
- Notebooks: orchestrate analysis flow, include reproducibility cell
- `analysis/` module: reusable functions, unit-tested where helpful
- CI: headless notebook execution (`nbconvert`) for smoke runs and artifact generation

Build order & dependencies
1. Data QA and canonical Parquet creation (`data/processed/`) — ensures downstream notebooks are stable
2. Core trend and seasonality analyses (CHIEF) — gives broad context
3. Spatial analyses (PATROL/HYP-SOCIO) — depends on cleaned geometry fields and tract shapefiles
4. Forecasting and classification (FORECAST) — depends on aggregated series and feature-engineered datasets

Why this structure
- Reusable helpers reduce copy/paste and make testing easier without changing the existing notebook-first workflow.
