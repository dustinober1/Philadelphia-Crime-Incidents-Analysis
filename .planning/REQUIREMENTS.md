# Requirements: Crime Incidents Philadelphia

**Defined:** 2026-02-02
**Core Value:** Provide clear, reproducible, evidence-based answers to policy and operations questions about crime in Philadelphia

## v1 Requirements

### Chief (High-Level Trends)

- [ ] **CHIEF-01**: Annual aggregation of crime counts for the last 10 years and trend line comparing Violent vs Property crimes
- [ ] **CHIEF-02**: Monthly seasonality decomposition and month-level boxplots; quantify month-to-month percentage differences (e.g., July vs January)
- [ ] **CHIEF-03**: Comparative pre/during/post COVID time series with lockdown annotation and analysis of displacement effects

### Patrol (Resource Allocation)

- [ ] **PATROL-01**: Spatial clustering (DBSCAN/KMeans) to identify hotspots; export centroids and heatmap tiles
- [ ] **PATROL-02**: Hour × Weekday heatmap for Robbery incidents and peak-hour identification
- [ ] **PATROL-03**: District-level severity scoring (weighted by crime severity) and choropleth map

### Policy (Deep Dives)

- [ ] **POLICY-01**: Retail Theft 5-year trend filtered to specific offense codes and a report validating/invalidating the media narrative
- [ ] **POLICY-02**: Vehicle-related crimes geospatial analysis with corridor overlay and neighborhood localization
- [ ] **POLICY-03**: Year-by-year violent / total crime ratio and stacked area chart of composition changes

### Forecasting (Predictive Analytics)

- [ ] **FORECAST-01**: Short-term time-series forecast (Prophet/ARIMA) with 30–60 day horizon and prediction intervals
- [ ] **FORECAST-02**: Classification model (RandomForest/XGBoost) to predict violent vs non-violent incidents and generate feature-importances

### Hypotheses & External Data

- [ ] **HYP-HEAT**: Merge hourly weather and test heat–crime relationships; find temperature thresholds where violent crime changes
- [ ] **HYP-SOCIO**: Spatially join crimes to Census tracts and compute crime rates per 1,000 residents
- [ ] **HYP-EVENTS**: Engineer event-day features (sports games, holidays) and measure event impacts on crime categories

## v2 Requirements

- (deferred items such as interactive dashboards, real-time alerts, mobile app integrations)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time streaming dashboard | Focus is reproducible analysis and static reports for v1 |
| Production API / Hosted Service | Not required for stakeholder deliverables in v1 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CHIEF-01 | Phase 1 | Pending |
| CHIEF-02 | Phase 1 | Pending |
| CHIEF-03 | Phase 1 | Pending |
| PATROL-01 | Phase 2 | Pending |
| PATROL-02 | Phase 2 | Pending |
| PATROL-03 | Phase 2 | Pending |
| POLICY-01 | Phase 3 | Pending |
| POLICY-02 | Phase 3 | Pending |
| POLICY-03 | Phase 3 | Pending |
| FORECAST-01 | Phase 4 | Pending |
| FORECAST-02 | Phase 4 | Pending |
| HYP-HEAT | Phase 4 | Pending |
| HYP-SOCIO | Phase 2 | Pending |
| HYP-EVENTS | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-02*
