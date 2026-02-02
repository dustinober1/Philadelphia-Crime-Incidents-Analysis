## Project Reference

See: .planning/PROJECT.md (updated 2026-02-02)

**Core value:** Provide clear, reproducible, evidence-based answers to policy and operations questions about crime in Philadelphia
**Current focus:** Phase 1 — High-level trends & seasonality analyses

## Memory

- Repo type: Brownfield, notebook-driven analysis project; data artifacts present under `data/`.
- Key notebooks present: `philadelphia_safety_trend_analysis.ipynb`, `summer_crime_spike_analysis.ipynb`, `covid_lockdown_crime_landscape.ipynb`.
- Environment: Python, pandas, geopandas, Prophet/ARIMA, scikit-learn/XGBoost.

## Current Position

Phase: 1 of 4 (High-Level Trends & Seasonality)
Plan: 4 of 5 in current phase
Status: In progress
Last activity: 2026-02-02 - Completed 04-PLAN-seasonality.md

Progress: ██████░░░░ 60%

## Decisions

| Phase | Decision | Rationale |
| --- | --- | --- |
| 01-01 | Use UCR general code hundred-bands for crime category mapping | Aligns with notebook expectations and supports Violent/Property/Other rollups |
| 01-01 | Store Phase 1 parameters in external YAML config | Enables versioned, repeatable notebook runs |
| 01-02 | Define REPORTS_DIR from repo_root in notebooks, not re-import from analysis.config | Ensures artifacts save to correct location when notebooks run from notebooks/ directory |
| 01-04 | Fix analysis/config.py to use absolute paths via __file__ | Ensures all modules work regardless of working directory |

## Blockers/Concerns Carried Forward

None.

## Session Continuity

Last session: 2026-02-02 23:30 UTC
Stopped at: Completed 04-PLAN-seasonality.md, ready for 05-PLAN-covid.md or 06-PLAN-integration.md
Resume file: None

---
*State updated: 2026-02-02*
