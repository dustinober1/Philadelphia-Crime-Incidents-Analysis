---
phase: 02-external-data-integration
plan: 06
subsystem: correlation-analysis
tags: [economic-correlation, unemployment, spearman-correlation, bootstrap-ci, fdr-correction, detrending]

# Dependency graph
requires:
  - phase: 02-external-data-integration
    plan: 02
    provides: FRED API integration (fetch_fred_data)
  - phase: 02-external-data-integration
    plan: 04
    provides: Temporal alignment utilities (align_temporal_data, aggregate_crime_by_period)
provides:
  - Economic-crime correlation analysis module with unemployment rate support
  - Time series detrending utility to avoid spurious correlations
  - Period comparison analysis for high/low economic conditions
  - Placeholder for district-level correlation (requires Census crosswalk)
affects: [02-07-weather-crime-correlation, 03-dashboard-foundation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Spearman correlation for non-normal time series data
    - Linear detrending to avoid spurious correlations from shared trends
    - Bootstrap confidence intervals with 99% confidence level
    - FDR (Benjamini-Hochberg) correction for multiple testing
    - Effect size interpretation for correlations and Cohen's d

key-files:
  created:
    - analysis/correlation_analysis.py
  modified: []

key-decisions:
  - "Spearman correlation chosen over Pearson for robustness to non-normality"
  - "Detrending enabled by default to prevent spurious correlations from shared long-term trends"
  - "District-level analysis deferred due to missing Census tract-to-district crosswalk"

patterns-established:
  - "Pattern: Economic correlation functions follow external_data.py temporal alignment pattern"
  - "Pattern: All statistical tests include FDR correction and effect size interpretation"

# Metrics
duration: 5min
completed: 2026-01-31
---

# Phase 02: Economic-Crime Correlation Analysis Summary

**Economic-crime correlation module using FRED unemployment data with detrending, Spearman correlation, bootstrap 99% CI, and FDR correction**

## Performance

- **Duration:** 5 min
- **Started:** 2026-01-31T19:15:00Z
- **Completed:** 2026-01-31T19:20:00Z
- **Tasks:** 1
- **Files created:** 1

## Accomplishments

- Created `analysis/correlation_analysis.py` with economic-crime correlation analysis
- Implemented `analyze_economic_crime_correlation()` function with unemployment rate support
- Added `detrend_series()` utility to remove linear trends from time series
- Implemented `compare_periods()` for high/low economic condition comparison
- Added placeholder `compute_district_level_correlation()` for future district-level analysis
- All functions include bootstrap confidence intervals, FDR correction, and effect size interpretation

## Task Commits

Each task was committed atomically:

1. **Task 1: Add economic correlation analysis to correlation_analysis.py** - `e090199` (feat)

**Plan metadata:** N/A (summary commit pending)

## Files Created/Modified

- `analysis/correlation_analysis.py` - Economic-crime correlation analysis module with:
  - `analyze_economic_crime_correlation()`: Main correlation function with unemployment support
  - `detrend_series()`: Linear detrending utility
  - `compare_periods()`: High/low economic period comparison
  - `compute_district_level_correlation()`: Placeholder for district-level analysis
  - Helper functions: `_interpret_correlation_effect()`, `_interpret_cohens_d()`

## Economic Variables Supported

| Variable | Source | Description | Frequency |
|----------|--------|-------------|-----------|
| PAPHIL5URN | FRED API | Philadelphia County unemployment rate | Monthly |

## Statistical Methods

- **Correlation:** Spearman rank correlation (robust to non-normality)
- **Confidence Intervals:** Bootstrap 99% CI (9,999 resamples)
- **Multiple Testing:** FDR correction (Benjamini-Hochberg method)
- **Effect Sizes:** Correlation magnitude (negligible/small/medium/large), Cohen's d
- **Detrending:** Linear trend removal to avoid spurious correlations

## Resolution Options

- **Monthly:** Crime + weather + unemployment (2006-2025)
- **Annual:** Crime + weather + unemployment + Census (2010-2023)

## Decisions Made

- **Spearman correlation:** Chosen over Pearson for robustness to non-normal time series data
- **Detrending default:** Enabled by default because 20-year crime and economic series both trend downward, creating spurious high correlations if not detrended
- **District-level placeholder:** Deferred because Census tract to police district crosswalk data must be sourced from OpenDataPhilly first

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

**FRED API key required for unemployment data fetching.** See `.env.example` for setup instructions:
- Get free API key at: https://fred.stlouisfed.org/docs/api/api_key.html
- Add `FRED_API_KEY=your_key_here` to `.env` file

## Next Phase Readiness

- Economic correlation infrastructure complete
- Ready for weather-crime correlation analysis (Plan 02-07)
- District-level analysis blocked on Census crosswalk data acquisition

---
*Phase: 02-external-data-integration*
*Plan: 06*
*Completed: 2026-01-31*
