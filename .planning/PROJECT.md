# Crime Incidents Philadelphia

## What This Is

A Python-first, notebook-driven data science repository that answers high-value public-safety questions for the City of Philadelphia. The project produces reproducible analyses and static report artifacts (charts, maps, Markdown) that directly address operational questions for commanders, policymakers, and forecasters.

## Core Value

Provide clear, reproducible, evidence-based answers to policy and operations questions about crime in Philadelphia so leaders can make defensible deployment and policy decisions.

## Current Milestone: v1.1 Script-Based Refactor

**Goal:** Convert from notebook-based to script-based architecture with module structure, CLI entry points, and comprehensive testing for better code quality and maintainability.

**Target features:**
- Module-based structure under `analysis/` with reusable utilities
- CLI entry points for all 13 analyses using typer
- Configuration system (CLI args + YAML files) with pydantic validation
- New data layer with validation and caching
- Testing framework (pytest) with 90%+ coverage
- Rich progress bars and configurable output formats
- Migration of all notebooks to scripts with verification
- Delete notebooks after successful conversion

## Requirements

### Validated

- ✓ All v1 notebook-driven analyses delivered — Phase 1-4 complete (22 plans executed)
- ✓ Data artifact layer with cleaned Parquet inputs — `data/crime_incidents_combined.parquet`
- ✓ Report export pipeline to `reports/` — 60+ artifacts delivered
- ✓ Predictive models — Prophet forecasts, violence classification, heat-crime hypothesis

### Active

- [ ] ARCH-01 through ARCH-06: Module-based architecture with CLI entry points
- [ ] CONFIG-01 through CONFIG-05: Configuration system (CLI args + YAML)
- [ ] DATA-01 through DATA-05: New data layer with validation and caching
- [ ] VIZ-01 through VIZ-05: Visualization utilities with multi-format output
- [ ] TEST-01 through TEST-08: Testing framework with 90%+ coverage
- [ ] DOCS-01 through DOCS-05: Documentation updates for script-based workflow
- [ ] MIGRATE-01 through MIGRATE-08: Convert 13 notebooks to scripts and verify
- [ ] QUAL-01 through QUAL-06: Code quality standards and tooling

### Out of Scope

- Real-time streaming dashboard — out of scope; this repo produces static reports and notebooks
- Production web API or hosted service — delivery is analytic reports (not a deployed service)

## Context

- Repository is analysis-first and notebook-driven; key notebooks exist in `notebooks/` (trend, seasonality, COVID analysis, data audit).
- Primary languages/tools: Python, pandas, geopandas, Jupyter, Prophet/ARIMA, scikit-learn/XGBoost for modeling, folium for maps.
- Data artifacts: cleaned Parquet in `data/` and external weather Parquet are present (see `data/external/`).

## Constraints

- **Language**: Python only — notebooks and supporting scripts (to keep reproducibility and tooling consistent)
- **Outputs**: Static reports (PNG, SVG, Markdown, HTML) — no web UI in v1
- **Reproducibility**: Notebooks must include reproducibility cell and pinned environment (`requirements.txt` / `environment.yml`)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python-only, notebook-driven workflows | Existing codebase and team familiarity; fastest path to reproducible analysis and reports | — Pending |
| Focus on report artifacts, not deployed services | Stakeholders want repeatable, inspectable analyses and static deliverables | — Pending |
| Use Prophet/ARIMA for forecasting; XGBoost/RandomForest for classification | Balance between explainability and predictive power; supported in Python ecosystem | — Pending |

---
*Last updated: 2026-02-04 after milestone v1.1 initiation*
