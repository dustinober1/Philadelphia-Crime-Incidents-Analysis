# Summary: 02-04 District Severity Scoring

**Status:** Complete
**Date:** 2026-02-03
**Requirement:** PATROL-03

## What Was Done

Created `notebooks/district_severity.ipynb` implementing a multi-factor composite severity scoring system for Philadelphia's 21 police districts.

### Scoring Methodology

Four weighted factors combine into a 0-100 composite score:

| Factor | Weight | Description |
|--------|--------|-------------|
| Crime Count | 0.25 | Total incidents - measures resource demand |
| Violent Crime Ratio | 0.30 | Percentage violent crimes - measures severity |
| YoY Trend | 0.20 | Year-over-year change (2024-2025) - measures momentum |
| Per-Capita Rate | 0.25 | Crimes per 100,000 residents - population-normalized |

### Key Findings

**Top 5 Priority Districts:**
1. District 24: Score 81.6 (high per-capita rate: 387K/100K, +9.4% YoY)
2. District 22: Score 79.6 (high violent ratio: 11.9%)
3. District 25: Score 77.8 (highest violent ratio: 12.5%)
4. District 15: Score 72.7 (highest volume: 277K crimes)
5. District 12: Score 71.4 (high per-capita: 288K/100K)

**Districts with High Severity (>=70):** 6 districts (24, 22, 25, 15, 12, 39)

**District 77 (Center City):** Commercial district with 0 census population, uses area-based rate fallback. Score 19.0 (lowest).

### Technical Notes

**Bug Fixed:** District code type mismatch - GeoDataFrame stored `dist_num` as float (1.0, 2.0...) but crime data used string integers ('1', '2'...). Fixed by converting float->int->str before merge.

**Population Source:** Census tract centroids spatially joined to districts, aggregating to ~1.58M total population across 21 districts.

## Artifacts Created

| Artifact | Description |
|----------|-------------|
| `notebooks/district_severity.ipynb` | Main analysis notebook |
| `reports/district_severity_choropleth.png` | Choropleth map with district labels and scores |
| `reports/district_severity_ranking.csv` | Ranked table with all factors |
| `reports/district_severity_ranking.md` | Methodology and ranking documentation |
| `reports/districts_scored.geojson` | GeoJSON with severity scores for downstream use |

## Validation Checklist

- [x] Notebook executes end-to-end without errors
- [x] Reproducibility cell present with version info
- [x] `reports/district_severity_choropleth.png` exists at 300 DPI
- [x] All 21 geographic districts colored and labeled on choropleth
- [x] `reports/district_severity_ranking.csv` contains all districts
- [x] Ranking includes all four factors (count, violent %, YoY, per-capita rate per 100K)
- [x] Per-capita rate uses FBI UCR convention (per 100,000 residents)
- [x] District population derived from census tract aggregation (sum 1,577,664)
- [x] `reports/districts_scored.geojson` loadable and has severity_score column
- [x] Weights documented in ranking markdown file

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Use 0.30 weight for violent ratio | Violence severity should have highest priority for resource allocation |
| Use per-capita rate (not area-based) as primary density factor | True population-normalized metric per FBI UCR convention |
| District 77 fallback to area-based rate | Commercial district with 0 census population |
| Convert float->int->str for district codes | Fixes merge mismatch between GeoDataFrame and crime data |

---
*Summary created: 2026-02-03*
