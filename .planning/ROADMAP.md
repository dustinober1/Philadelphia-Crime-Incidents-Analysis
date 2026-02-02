# ROADMAP: Crime Incidents Philadelphia

**Phases:** 4 | **v1 requirements:** 15 total | All v1 requirements mapped ✓

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | High-Level Trends & Seasonality | Establish baseline city-wide trends and seasonal patterns to inform all downstream work | CHIEF-01, CHIEF-02, CHIEF-03 | 3 |
| 2 | Spatial & Socioeconomic Analysis | Identify where and why crimes concentrate and normalize by population | PATROL-01, PATROL-02, PATROL-03, HYP-SOCIO | 4 |
| 3 | Policy Deep Dives & Event Impacts | Validate specific narratives (retail theft, vehicle crimes) and measure event impacts | POLICY-01, POLICY-02, POLICY-03, HYP-EVENTS | 4 |
| 4 | Forecasting & Predictive Modeling | Build short-term forecasts and classification models for operational use and hypothesis testing | FORECAST-01, FORECAST-02, HYP-HEAT | 4 |

---

## Phase Details

### Phase 1 — High-Level Trends & Seasonality
Goal: Produce audited, reproducible answers to: Is Philadelphia getting safer? Is there a summer spike? How did COVID change the landscape?
Requirements covered: CHIEF-01, CHIEF-02, CHIEF-03
Success criteria:
1. A reproducible notebook that aggregates incidents annually (last 10 years) and outputs a clean trend PNG and Markdown summary.
2. Monthly seasonality decomposition notebook with month-level boxplots and a numeric summary statement (e.g., percent increase July vs January) exported.
3. A time-series notebook comparing pre/during/post COVID windows including an annotated time series chart (lockdown marked) and displacement analysis for burglary types.
4. All analyses run headless via nbconvert and generate artifacts in `reports/`.

### Phase 2 — Spatial & Socioeconomic Analysis
Goal: Identify hotspots, temporal hotspots for robbery, and per-tract crime rates normalized by population.
Requirements covered: PATROL-01, PATROL-02, PATROL-03, HYP-SOCIO
Success criteria:
1. Hotspot notebook producing cluster outputs (centroids, cluster labels) and a heatmap PNG and GeoJSON for review.
2. Hour × Weekday heatmap for Robbery with a short recommendation note for patrol timing.
3. District choropleth showing severity score and a table ranking districts by severity and by per-capita crime rate.
4. Census tract join notebook that outputs per-1000-residents crime rates and flags inconsistencies in tract population data.

### Phase 3 — Policy Deep Dives & Event Impacts
Goal: Provide focused evidence on retail theft, vehicle crimes, and event-day effects to inform policy decisions.
Requirements covered: POLICY-01, POLICY-02, POLICY-03, HYP-EVENTS
Success criteria:
1. Retail Theft 5-year trend notebook with offense-code filters and a short verdict (supported / not supported) plus visualization.
2. Vehicle crimes map overlayed with major transit/highway corridors and a quantification (e.g., % within N blocks) exported.
3. Composition analysis showing violent / total ratio by year and stacked-area visualization with interpretation.
4. Event impact notebook showing difference-in-means for game/holiday days vs controls and a summary report.

### Phase 4 — Forecasting & Predictive Modeling
Goal: Deliver short-term forecasts and a violence-classification model with interpretable importances to support operational alerts and deeper research.
Requirements covered: FORECAST-01, FORECAST-02, HYP-HEAT
Success criteria:
1. Forecast notebook (Prophet/ARIMA) with 30–60 day horizon, CI bands, and a clear threshold definition for anomalies; artifacts exported.
2. Classification model notebook with data splits, time-aware CV, feature importance plot, and a short model card describing limitations.
3. Heat hypothesis notebook merging hourly weather and crime, producing correlation plots and hypothesis test results (with documented join strategy).
4. All models include reproducible training seeds and code to re-run in a single-step pipeline (notebook or script).

---

## Traceability Checklist

- All CHIEF-* requirements are in Phase 1
- PATROL-* and HYP-SOCIO are in Phase 2
- POLICY-* and HYP-EVENTS are in Phase 3
- FORECAST-* and HYP-HEAT are in Phase 4

## Next Steps

1. Approve this roadmap to commit `ROADMAP.md` and update `REQUIREMENTS.md` traceability and `.planning/STATE.md` current focus.
2. `/gsd-discuss-phase 1` — gather implementation-level context for Phase 1 (data QA, notebook owners, deliverable formats).
3. `/gsd-plan-phase 1` — generate execution plans and tasks for Phase 1.
