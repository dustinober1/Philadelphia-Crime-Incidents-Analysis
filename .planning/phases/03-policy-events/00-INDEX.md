# Phase 3: Policy Deep Dives & Event Impacts

## Goal

Provide focused evidence on retail theft, vehicle crimes, and event-day effects to inform policy decisions.

## Requirements Covered

| ID | Description | Notebook |
|----|-------------|----------|
| POLICY-01 | Retail Theft 5-year trend with offense-code filters and verdict | `retail_theft_trend.ipynb` |
| POLICY-02 | Vehicle crimes geospatial with corridor overlay and quantification | `vehicle_crimes_corridors.ipynb` |
| POLICY-03 | Year-by-year violent/total crime ratio and composition analysis | `crime_composition.ipynb` |
| HYP-EVENTS | Event-day features and impact measurement | `event_impacts.ipynb` |

## Success Criteria

1. Retail Theft 5-year trend notebook with offense-code filters and a short verdict (supported / not supported) plus visualization.
2. Vehicle crimes map overlayed with major transit/highway corridors and a quantification (e.g., % within N blocks) exported.
3. Composition analysis showing violent / total ratio by year and stacked-area visualization with interpretation.
4. Event impact notebook showing difference-in-means for game/holiday days vs controls and a summary report.

## Wave Structure

### Wave 1: Infrastructure & External Data
- Create Phase 3 config file with analysis parameters
- Download/cache corridor/transit data (highways, SEPTA routes)
- Create sports/holiday calendar for Philadelphia
- Extend utility functions for event-day analysis

### Wave 2: Core Analyses (Parallel)
- POLICY-01: Retail theft trend notebook
- POLICY-02: Vehicle crimes corridor analysis notebook
- POLICY-03: Crime composition analysis notebook
- HYP-EVENTS: Event impact analysis notebook

### Wave 3: Integration & Validation
- Cross-reference outputs
- Validate all artifacts
- Create Phase 3 summary notebook
- Update orchestrator for Phase 3

## Data Inventory

### Available from Crime Data
- `text_general_code`: Includes "Thefts", "Theft from Vehicle", "Motor Vehicle Theft"
- `ucr_general`: UCR codes (600=Theft, 700=Motor Vehicle Theft)
- `dispatch_date`: For temporal analysis (2006-2026)
- `point_x`, `point_y`: WGS84 coordinates (98.4% coverage)
- `dc_dist`: Police district (for spatial aggregation)

### External Data Needed
- [ ] Philadelphia highway corridors (I-76, I-95, I-676, US-1)
- [ ] SEPTA transit lines (Market-Frankford, Broad St, Regional Rail)
- [ ] Philadelphia sports calendar (Eagles, Phillies, 76ers, Flyers)
- [ ] US holiday calendar (federal holidays, local events)

### Reusable from Phase 2
- `data/boundaries/police_districts.geojson`
- `data/boundaries/census_tracts_pop.geojson`
- `analysis/spatial_utils.py` for coordinate cleaning

## Plans

| Plan | Wave | Description | Status |
|------|------|-------------|--------|
| 03-01-PLAN.md | 1 | Infrastructure & External Data | Ready |
| 03-02-PLAN.md | 2 | Retail Theft Trend (POLICY-01) | Ready |
| 03-03-PLAN.md | 2 | Vehicle Crimes Corridors (POLICY-02) | Ready |
| 03-04-PLAN.md | 2 | Crime Composition (POLICY-03) | Ready |
| 03-05-PLAN.md | 2 | Event Impacts (HYP-EVENTS) | Ready |
| 03-06-PLAN.md | 3 | Integration & Validation | Ready |

## Dependencies

```
Wave 1: 03-01 (Infrastructure)
    |
Wave 2: 03-02, 03-03, 03-04, 03-05 (Parallel)
    |
Wave 3: 03-06 (Integration)
```

## Estimated Total Time

| Plan | Estimated |
|------|-----------|
| 03-01 | ~90 min |
| 03-02 | ~75 min |
| 03-03 | ~95 min |
| 03-04 | ~65 min |
| 03-05 | ~90 min |
| 03-06 | ~75 min |
| **Total** | **~490 min** |

*Note: Wave 2 plans can run in parallel, reducing wall-clock time.*

---
*Created: 2026-02-03*
*Phase: 03-policy-events*
