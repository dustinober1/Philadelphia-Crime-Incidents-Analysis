## Project Reference

See: .planning/PROJECT.md (updated 2026-02-04)

**Core value:** Provide clear, reproducible, evidence-based answers to policy and operations questions about crime in Philadelphia
**Current focus:** Milestone v1.1 - Script-Based Refactor

## Memory

- Repo type: Brownfield, notebook-driven analysis project converting to script-based architecture
- v1.0 complete: All 4 phases delivered, 22 plans executed, 60+ artifacts
- v1.1 goal: Convert 13 notebooks to scripts with module-based architecture, CLI entry points, and testing
- Environment: Python, pandas, geopandas, Prophet/ARIMA, scikit-learn/XGBoost
- New tools for v1.1: typer, rich, pydantic, pytest, pytest-cov, black, ruff, mypy

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-02-04 — Milestone v1.1 started

Progress: ░░░░░░░░░░ 0% (0/0 plans complete)

## Milestone v1.1 Summary

**Requirements:** 46 total across 8 categories
**Notebooks to convert:** 13 (Chief: 3, Patrol: 4, Policy: 4, Forecasting: 2)

### Key Deliverables
- **Architecture**: Module-based structure, CLI entry points, data layer
- **Configuration**: YAML configs, CLI args, pydantic validation
- **Testing**: pytest framework, 90%+ coverage, integration tests
- **Quality**: Type hints, docstrings, linting, pre-commit hooks
- **Migration**: Convert all notebooks, verify outputs, delete notebooks

## v1.0 Completed Phases

### Phase 4 — Forecasting & Predictive Modeling COMPLETE
Goal: Deliver short-term forecasts and a violence-classification model
Requirements covered: FORECAST-01, FORECAST-02, HYP-HEAT
Artifacts: 15+ models, visualizations, and reports

### Phase 3 — Policy Deep Dives & Event Impacts COMPLETE
Goal: Provide focused evidence on retail theft, vehicle crimes, and event-day effects
Requirements covered: POLICY-01, POLICY-02, POLICY-03, HYP-EVENTS
Artifacts: 24 passed, 20+ files

### Phase 2 — Spatial & Socioeconomic Analysis COMPLETE
Goal: Identify hotspots, temporal hotspots for robbery, and per-tract crime rates
Requirements covered: PATROL-01, PATROL-02, PATROL-03, HYP-SOCIO
Artifacts: 20 artifacts validated

### Phase 1 — High-Level Trends & Seasonality COMPLETE
Goal: Establish baseline city-wide trends and seasonal patterns
Requirements covered: CHIEF-01, CHIEF-02, CHIEF-03
Artifacts: Audited, reproducible notebooks

## Accumulated Context

### v1.0 Key Decisions
| Category | Decision | Rationale |
|----------|----------|-----------|
| Analysis | Use UCR general code hundred-bands for crime mapping | Aligns with notebook expectations |
| Data | Use TIGER + ACS API for census tract population | Census Reporter API unavailable |
| Forecasting | Use Prophet for time series | Industry standard for crime data |
| Modeling | Use Random Forest + XGBoost for classification | Balance interpretability and performance |
| Validation | Implement time-aware validation without shuffling | Prevents data leakage |

### v1.1 New Decisions
| Category | Decision | Rationale |
|----------|----------|-----------|
| Architecture | Module-based structure with CLI entry points | Better code quality, testing, CI/CD |
| CLI | Use typer for CLI framework | Modern, type hints support, excellent UX |
| Config | CLI args + YAML with pydantic validation | Flexibility and type safety |
| Testing | pytest with 90%+ coverage target | High quality standard for production |
| Migration | Delete notebooks after conversion | Milestone goal is script-based architecture |

## Blockers/Concerns

None

## Session Continuity

Last session: 2026-02-04
Stopped at: Milestone v1.1 requirements defined
Resume file: None

---
*State updated: 2026-02-04*
