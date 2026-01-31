# Roadmap: Philadelphia Crime EDA

## Overview

This roadmap transforms an existing exploratory data analysis project (11 analysis modules, 6 report generators) into a research-grade system with statistical rigor, external data correlation, and interactive dashboard capabilities. The journey begins by establishing publication-ready statistical foundations, then integrates explanatory external data sources, explores deeper temporal patterns, builds an interactive dashboard for ongoing hypothesis generation, and concludes with publication-quality export capabilities for academic presentation.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Statistical Rigor Layer** - Add significance testing, confidence intervals, effect sizes, and reproducibility infrastructure to all existing analyses (Completed: 2025-01-31)
- [ ] **Phase 2: External Data Integration** - Ingest weather, economic, and policing data for correlation analysis
- [ ] **Phase 3: Advanced Temporal Analysis** - Deep-dive into holiday effects, individual crime types, and shift-by-shift patterns
- [ ] **Phase 4: Dashboard Foundation** - Build Streamlit dashboard with time, geographic, and crime type filters
- [ ] **Phase 5: Dashboard Cross-Filtering** - Implement linked views with cross-filtering interactions
- [ ] **Phase 6: Publication Outputs** - Generate high-DPI figures and LaTeX-ready tables for academic presentation

## Phase Details

### Phase 1: Statistical Rigor Layer
**Goal**: All existing analyses include statistical significance testing, confidence intervals, effect sizes, and reproducibility infrastructure making them publication-ready
**Depends on**: Nothing (first phase)
**Requirements**: STAT-01, STAT-02, STAT-03, STAT-04, PUB-03, PUB-04
**Success Criteria** (what must be TRUE):
  1. User can view p-values for all trend analyses, temporal comparisons, and spatial correlations across all 11 analysis modules
  2. User can view 99% confidence intervals on all visualizations showing point estimates (trend lines, comparisons, spatial clusters)
  3. User can view effect sizes (Cohen's d for comparisons, odds ratios for proportions, standardized coefficients for correlations) to assess practical significance
  4. User can view results with FDR (Benjamini-Hochberg) correction applied to all omnibus comparisons with multiple tests
  5. User can view comprehensive data quality audit documenting missing data patterns, coordinate coverage by crime type/district, and analysis limitations
  6. User can reproduce all analyses through documented random seeds, data version tracking, and explicit parameter documentation in analysis outputs
**Plans**: 6 plans in 3 waves

**Wave Structure:**
- Wave 1 (parallel): 01-01 stats_utils, 01-05 reproducibility infrastructure
- Wave 2 (parallel): 01-02 temporal analyses, 01-03 spatial/categorical analyses
- Wave 3 (sequential): 01-04 effect sizes & FDR, 01-06 data quality audit

Plans:
- [x] 01-01-PLAN.md — Create statistical testing utilities module (stats_utils.py with 10+ functions, STAT_CONFIG)
- [x] 01-05-PLAN.md — Implement reproducibility infrastructure (DataVersion, seed management, parameter docs)
- [x] 01-02-PLAN.md — Add significance testing and CIs to temporal analyses (temporal, summer_spike, covid_lockdown, safety_trend, robbery_timing)
- [x] 01-03-PLAN.md — Add significance testing and CIs to spatial analyses (spatial, red_zones, categorical, cross_analysis, weighted_severity)
- [x] 01-04-PLAN.md — Add effect sizes and FDR correction (Cliff's delta, odds ratios, verify all modules)
- [x] 01-06-PLAN.md — Generate comprehensive data quality audit report

### Phase 2: External Data Integration
**Goal**: Weather, economic, and policing data sources are ingested, cached, and aligned with crime data for correlation analysis
**Depends on**: Phase 1 (correlations require statistical rigor)
**Requirements**: CORR-01, CORR-02, CORR-03
**Success Criteria** (what must be TRUE):
  1. User can view crime-weather correlation analysis (temperature, precipitation) with appropriate detrending applied to address spurious correlation risk
  2. User can view crime-economic correlation analysis (unemployment, poverty rates, income) at district/area level with temporal alignment
  3. User can view crime-policing correlation analysis (resource allocation, arrest rates) if data is available, with clear documentation of data limitations
  4. All external data sources are cached locally with staleness checks to avoid API rate limits
  5. Temporal misalignment issues are documented and handled (daily weather vs monthly economic vs daily crime)
**Plans**: TBD

Plans:
- [ ] 02-01: Ingest and cache weather data (Meteostat API)
- [ ] 02-02: Ingest and cache economic data (U.S. Census API, FRED API)
- [ ] 02-03: Ingest and cache policing data if available
- [ ] 02-04: Implement temporal alignment and detrending utilities
- [ ] 02-05: Compute crime-weather correlations with statistical safeguards
- [ ] 02-06: Compute crime-economic correlations with statistical safeguards
- [ ] 02-07: Compute crime-policing correlations if data available
- [ ] 02-08: Generate correlation analysis report

### Phase 3: Advanced Temporal Analysis
**Goal**: Granular temporal patterns (holiday effects, individual crime types, shift-by-shift) are analyzed with statistical rigor
**Depends on**: Phase 1 (requires statistical testing infrastructure)
**Requirements**: TEMP-01, TEMP-02, TEMP-03
**Success Criteria** (what must be TRUE):
  1. User can view holiday effects analysis showing pre/post holiday crime patterns for major U.S. holidays with significance testing
  2. User can view individual crime type analysis for homicide, burglary, theft, vehicle theft, aggravated assault with temporal trends, spatial distribution, and seasonality
  3. User can view shift-by-shift temporal analysis (morning 6AM-12PM, afternoon 12PM-6PM, evening 6PM-12AM, late night 12AM-6AM) with statistical comparisons
  4. All temporal analyses include confidence intervals and significance tests from Phase 1 infrastructure
**Plans**: TBD

Plans:
- [ ] 03-01: Implement holiday effects analysis module
- [ ] 03-02: Implement individual crime type analysis module (homicide, burglary, theft, vehicle theft, aggravated assault)
- [ ] 03-03: Implement shift-by-shift temporal analysis module
- [ ] 03-04: Generate advanced temporal analysis report

### Phase 4: Dashboard Foundation
**Goal**: Interactive Streamlit dashboard with time range, geographic area, and crime type filters displaying existing analyses
**Depends on**: Phase 1 (requires statistically-validated analyses), Phase 3 (requires advanced temporal content)
**Requirements**: DASH-01, DASH-02, DASH-03
**Success Criteria** (what must be TRUE):
  1. User can filter dashboard by time range using date sliders and preset period selections (year, season, month)
  2. User can filter dashboard by geographic area using police district and neighborhood selectors
  3. User can filter dashboard by crime type using multi-select controls for UCR categories and specific crimes
  4. Dashboard loads and renders within 5 seconds using aggressive caching and data sampling
  5. All dashboard visualizations reuse analysis modules (no duplicated logic)
**Plans**: TBD

Plans:
- [ ] 04-01: Set up Streamlit project structure and configuration
- [ ] 04-02: Implement data loading with caching
- [ ] 04-03: Implement time range filter controls
- [ ] 04-04: Implement geographic filter controls
- [ ] 04-05: Implement crime type filter controls
- [ ] 04-06: Create main overview page with filtered statistics
- [ ] 04-07: Create temporal analysis page with filtered visualizations
- [ ] 04-08: Create spatial analysis page with filtered maps

### Phase 5: Dashboard Cross-Filtering
**Goal**: Dashboard views are linked with cross-filtering so selections in one component update all related visualizations
**Depends on**: Phase 4 (requires foundation dashboard), Phase 2 (requires correlation analysis content)
**Requirements**: DASH-04
**Success Criteria** (what must be TRUE):
  1. User can select a time range in temporal view and see spatial and correlation views update to reflect that period
  2. User can select a district in spatial view and see temporal trends and correlation charts update to show that area
  3. User can select a crime type in any view and see all other views filter to that crime type
  4. Cross-filtering maintains responsive performance (<3 second updates) through optimized state management
  5. Dashboard includes correlation pages displaying weather and economic correlations with filters
**Plans**: TBD

Plans:
- [ ] 05-01: Implement shared session state for cross-filtering
- [ ] 05-02: Create correlation analysis pages with external data filters
- [ ] 05-03: Implement time range cross-filtering across all views
- [ ] 05-04: Implement geographic area cross-filtering across all views
- [ ] 05-05: Implement crime type cross-filtering across all views

### Phase 6: Publication Outputs
**Goal**: High-DPI figures and LaTeX-ready tables are generated for academic presentation
**Depends on**: Phase 1 (requires stable analysis results), Phase 2 (requires correlation results), Phase 3 (requires temporal results)
**Requirements**: PUB-01, PUB-02
**Success Criteria** (what must be TRUE):
  1. User can export figures in high-DPI formats (PNG, SVG, PDF at 300+ DPI) with publication styling (fonts, colors, figure sizing)
  2. User can export tables in LaTeX-ready format with academic styling (caption, notes, significance markers)
  3. Publication outputs are generated from stable, versioned analysis results
  4. All publication figures include confidence intervals and significance markers
**Plans**: TBD

Plans:
- [ ] 06-01: Create publication output utilities module
- [ ] 06-02: Generate high-DPI temporal trend figures
- [ ] 06-03: Generate high-DPI spatial distribution figures
- [ ] 06-04: Generate high-DPI correlation analysis figures
- [ ] 06-05: Generate LaTeX-ready statistical tables
- [ ] 06-06: Document publication pipeline and figure styling standards

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Statistical Rigor Layer | 6/6 | ✓ Complete | 2025-01-31 |
| 2. External Data Integration | 0/8 | Not started | - |
| 3. Advanced Temporal Analysis | 0/4 | Not started | - |
| 4. Dashboard Foundation | 0/8 | Not started | - |
| 5. Dashboard Cross-Filtering | 0/5 | Not started | - |
| 6. Publication Outputs | 0/6 | Not started | - |

**Overall Progress:** [██░░░░░░░░░] 6/37 plans (16%)
