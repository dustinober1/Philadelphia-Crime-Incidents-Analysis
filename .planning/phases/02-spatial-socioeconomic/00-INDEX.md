# Phase 2: Spatial & Socioeconomic Analysis

## Goal

Identify where and why crimes concentrate and normalize by population.

## Requirements Covered

| ID | Description | Notebook |
|----|-------------|----------|
| PATROL-01 | Spatial hotspot detection (clustering) and heatmap outputs with centroids | `hotspot_clustering.ipynb` |
| PATROL-02 | Hour × Weekday heatmap for Robbery to inform shift timing | `robbery_temporal_heatmap.ipynb` |
| PATROL-03 | District-level weighted severity scoring and choropleth | `district_severity.ipynb` |
| HYP-SOCIO | Spatial join to Census tracts and compute crime rates per 1,000 residents | `census_tract_rates.ipynb` |

## Success Criteria

1. Hotspot notebook producing cluster outputs (centroids, cluster labels) and a heatmap PNG and GeoJSON for review.
2. Hour × Weekday heatmap for Robbery with a short recommendation note for patrol timing.
3. District choropleth showing severity score and a table ranking districts by severity and by per-capita crime rate.
4. Census tract join notebook that outputs per-1000-residents crime rates and flags inconsistencies in tract population data.

## Wave Structure

### Wave 1: Infrastructure & Data Prep
- Extend config for Phase 2 parameters (clustering eps, severity weights)
- Download/cache boundary files (police districts, Census tracts)
- Create spatial utility functions (coordinate cleaning, spatial joins)

### Wave 2: Core Analyses (Parallel)
- PATROL-01: Hotspot clustering notebook
- PATROL-02: Robbery hour×weekday heatmap notebook
- PATROL-03: District severity notebook
- HYP-SOCIO: Census tract rates notebook

### Wave 3: Integration & Validation
- Cross-reference outputs
- Validate all artifacts
- Update orchestrator for Phase 2

## Data Inventory

### Available in Crime Data
- `point_x`, `point_y`: WGS84 coordinates (98.4% coverage)
- `dc_dist`: Police district (25 unique, 100% coverage)
- `psa`: Police Service Area (32 unique)
- `hour`: Hour of day (97% coverage)
- `dispatch_date_time`: Full datetime for day-of-week extraction
- `ucr_general`: UCR code for crime type classification

### External Data Needed
- [ ] Philadelphia Police District boundaries (GeoJSON/Shapefile)
- [ ] Philadelphia Census Tract boundaries with population (2020 Census)
- [ ] UCR severity weights (define in config)

## Plans

| Plan | Wave | Description | Status |
|------|------|-------------|--------|
| 02-01-PLAN.md | 1 | Infrastructure & boundary data | Pending |
| 02-02-PLAN.md | 2 | Hotspot clustering (PATROL-01) | Pending |
| 02-03-PLAN.md | 2 | Robbery heatmap (PATROL-02) | Pending |
| 02-04-PLAN.md | 2 | District severity (PATROL-03) | Pending |
| 02-05-PLAN.md | 2 | Census tract rates (HYP-SOCIO) | Pending |
| 02-06-PLAN.md | 3 | Integration & validation | Pending |

---
*Created: 2026-02-03*
