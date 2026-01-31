---
phase: 02-external-data-integration
plan: 05
subsystem: correlation-analysis
tags: [spearman-correlation, detrending, fdr-correction, lagged-correlation, statsmodels]

# Dependency graph
requires:
  - phase: 02-external-data-integration
    plan: 01
    provides: Weather data fetching from Meteostat API
  - phase: 02-external-data-integration
    plan: 04
    provides: Temporal alignment utilities for multi-source data
provides:
  - Detrending utilities (linear, mean centering, first-difference)
  - Weather-crime correlation analysis with Spearman rank correlation
  - Lagged correlation analysis (1-7 day lags) for delayed weather effects
  - Correlation report generation with markdown output
affects: [02-06, 02-07, 02-08]

# Tech tracking
tech-stack:
  added: [statsmodels (tsatools.detrend)]
  patterns:
    - Detrending before correlation to prevent spurious correlations
    - FDR correction for multiple testing across weather variables
    - Cross-correlation for lagged effect detection

key-files:
  created:
    - analysis/correlation_analysis.py - Weather-crime correlation analysis module
  modified:
    - analysis/external_data.py - Added detrending utilities section

key-decisions:
  - "Detrending required before correlation: 20-year trends create spurious correlations if not removed"
  - "Mean centering for detrending: Simpler than linear detrending, sufficient for correlation analysis"
  - "Spearman correlation: Non-parametric, robust to non-normal weather and crime distributions"
  - "Lagged correlations (1-7 days): Tests delayed weather effects like 'hot today -> crime tomorrow'"

patterns-established:
  - "Import-time safety: statsmodels imported with try/except to gracefully handle missing dependency"
  - "Method parameter in detrend_series: Supports 'linear' (statsmodels) and 'mean' (simple centering)"
  - "cross_correlation returns DataFrame: Enables easy filtering and visualization of lag results"

# Metrics
duration: 6min
completed: 2026-01-31
---

# Phase 02: External Data Integration - Plan 05 Summary

**Detrending utilities with linear/mean methods, weather-crime Spearman correlation analysis with 1-7 day lagged effects, and FDR-corrected statistical testing**

## Performance

- **Duration:** 6 min
- **Started:** 2026-01-31T18:53:54Z
- **Completed:** 2026-01-31T18:59:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- **Detrending utilities:** Added `detrend_series()` with linear and mean methods, `first_difference()` for stationarity, and `cross_correlation()` for lagged analysis to `external_data.py`
- **Weather correlation module:** Created `analyze_weather_crime_correlation()` testing temperature (temp, tmax, tmin) and precipitation (prcp) against daily crime counts
- **Lagged correlation analysis:** Implemented `compute_lagged_correlation()` for testing delayed weather effects (1, 2, 3, 7, 14 day lags)
- **Report generation:** Added `generate_correlation_report()` for markdown output with significance tables and findings

## Task Commits

Each task was committed atomically:

1. **Task 1: Add detrending utilities to external_data.py** - `74f2b8c` (feat)
2. **Task 2: Add weather crime correlation analysis to correlation_analysis.py** - `9197c03` (feat)

## Files Created/Modified

### Created

- `analysis/correlation_analysis.py` - Weather-crime correlation analysis with Spearman correlation, lagged effects, and markdown report generation (360 lines added)

### Modified

- `analysis/external_data.py` - Added detrending utilities section with `detrend_series()`, `first_difference()`, and `cross_correlation()` functions (146 lines added)

## Detrending Methods Implemented

| Method | Description | Use Case |
|--------|-------------|----------|
| **Linear** | Remove best-fit line via statsmodels.detrend | Strong linear trends |
| **Mean** | Subtract series mean (centering) | Simple drift removal |
| **First Difference** | Compute y[t] - y[t-1] | Stationarity transformation |

## Weather Variables Tested

- `temp`: Average daily temperature (C)
- `tmax`: Maximum daily temperature (C)
- `tmin`: Minimum daily temperature (C)
- `prcp`: Daily precipitation (mm)

## Lag Range Supported

- **Default lags:** 1, 2, 3, 7, 14 days
- **Cross-correlation:** -max_lag to +max_lag (weather leads vs crime leads)
- **Customizable:** `max_lag` parameter in `analyze_weather_crime_correlation()`

## Statistical Tests Used

| Test | Purpose | Implementation |
|------|---------|----------------|
| **Spearman Correlation** | Non-parametric rank correlation | `scipy.stats.spearmanr` via `correlation_test()` |
| **FDR Correction** | Multiple testing correction | `apply_fdr_correction()` with Benjamini-Hochberg |
| **Confidence Intervals** | 99% CI on correlations | Available via `bootstrap_ci()` from stats_utils |

## Decisions Made

- **Detrending required:** 20-year trends in both crime and weather create spurious correlations if not removed. Mean centering is sufficient for correlation analysis.
- **Spearman over Pearson:** Non-parametric correlation is more robust to non-normal distributions common in weather and crime data.
- **statsmodels for linear detrending:** Used `statsmodels.tsa.tsatools.detrend` for professional-grade detrending with graceful fallback if not installed.
- **FDR correction applied:** Multiple weather variables tested require correction for false discovery rate.

## Deviations from Plan

None - plan executed exactly as written.

## Authentication Gates

None - no authentication required for this plan.

## Next Phase Readiness

**Ready for subsequent Phase 2 plans:**
- 02-06 (Economic Correlation Analysis): Can use same correlation framework with unemployment data
- 02-07 (Census Integration): Poverty rate correlation analysis ready
- 02-08 (External Data Report): Correlation results can be included in comprehensive report

**Dependencies satisfied:**
- Weather data fetching (02-01) complete
- Temporal alignment (02-04) complete
- Detrending prevents spurious correlations from trend drift

**No blockers or concerns.**

---
*Phase: 02-external-data-integration*
*Plan: 05*
*Completed: 2026-01-31*
