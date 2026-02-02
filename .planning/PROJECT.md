# Crime Incidents Philadelphia

## What This Is

A Python-first, notebook-driven data science repository that answers high-value public-safety questions for the City of Philadelphia. The project produces reproducible analyses and static report artifacts (charts, maps, Markdown) that directly address operational questions for commanders, policymakers, and forecasters.

## Core Value

Provide clear, reproducible, evidence-based answers to policy and operations questions about crime in Philadelphia so leaders can make defensible deployment and policy decisions.

## Requirements

### Validated

- ✓ Notebook-driven, reproducible analyses (existing) — inferred from repository notebooks
- ✓ Data artifact layer with cleaned Parquet inputs (existing) — `data/crime_incidents_combined.parquet`
- ✓ Report export pipeline to `reports/` (existing) — generated figures and Markdown artifacts

### Active

- [ ] CHIEF-01: Annual aggregation and trend analysis for Violent vs Property crime (year-over-year)
- [ ] CHIEF-02: Monthly seasonality decomposition and month-by-month distribution (boxplots)
- [ ] CHIEF-03: Pre/during/post COVID comparative time series with lockdown annotation
- [ ] PATROL-01: Spatial hotspot detection (clustering) and heatmap outputs with centroids
- [ ] PATROL-02: Hour × Weekday heatmap for Robbery to inform shift timing
- [ ] PATROL-03: District-level weighted severity scoring and choropleth
- [ ] POLICY-01: Focused Retail Theft 5-year trend analysis (validate media claims)
- [ ] POLICY-02: Vehicle-related crime spatial localization and corridor overlay
- [ ] POLICY-03: Yearly violent/total composition ratio and stacked area visualization
- [ ] FORECAST-01: Short-term time-series forecast for incident counts (30–60 days)
- [ ] FORECAST-02: Classification model to predict violent vs non-violent incidents with feature importances
- [ ] HYP-HEAT: Merge hourly weather and test heat–crime relationships (temperature thresholds)
- [ ] HYP-SOCIO: Spatial join to Census tracts and compute crime rates per 1,000 residents
- [ ] HYP-EVENTS: Event-day feature engineering (games, holidays) and event-impact analysis

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
*Last updated: 2026-02-02 after initial questioning and project initialization*
