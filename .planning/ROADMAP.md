# Roadmap: Philadelphia Crime EDA

## Overview

This roadmap transforms an existing exploratory data analysis project (11 analysis modules, 6 report generators) into a research-grade system with statistical rigor, external data correlation, and interactive dashboard capabilities. The journey begins by establishing publication-ready statistical foundations, then integrates explanatory external data sources, explores deeper temporal patterns, builds an interactive dashboard for ongoing hypothesis generation, and concludes with publication-quality export capabilities for academic presentation.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Statistical Rigor Layer** - Add significance testing, confidence intervals, effect sizes, and reproducibility infrastructure to all existing analyses (Completed: 2025-01-31)
- [x] **Phase 2: External Data Integration** - Ingest weather, economic, and policing data for correlation analysis (Completed: 2025-01-31)
- [x] **Phase 3: Advanced Temporal Analysis** - Deep-dive into holiday effects, individual crime types, and shift-by-shift patterns (Completed: 2026-01-31)
- [x] **Phase 4: Dashboard Foundation** - Build Streamlit dashboard with time, geographic, and crime type filters (Completed: 2026-01-31)
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
- [x] 02-01-PLAN.md — Ingest and cache weather data (Meteostat API)
- [x] 02-02-PLAN.md — Ingest and cache economic data (FRED, Census APIs)
- [x] 02-03-PLAN.md — Implement caching infrastructure (requests-cache)
- [x] 02-04-PLAN.md — Implement temporal alignment and detrending utilities
- [x] 02-05-PLAN.md — Compute crime-weather correlations with statistical safeguards
- [x] 02-06-PLAN.md — Compute crime-economic correlations with statistical safeguards
- [x] 02-07-PLAN.md — Assess policing data availability
- [x] 02-08-PLAN.md — Generate correlation analysis report

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
**Plans**: 8 plans in 4 waves

**Wave Structure:**
- Wave 1 (parallel): 02-01 weather ingestion (Meteostat), 02-02 economic ingestion (FRED, Census)
- Wave 2 (parallel): 02-03 caching infrastructure, 02-04 temporal alignment
- Wave 3 (parallel): 02-05 crime-weather correlations, 02-06 crime-economic correlations
- Wave 4 (parallel): 02-07 policing data assessment, 02-08 correlation report generator

Plans:
- [ ] 02-01-PLAN.md — Ingest and cache weather data (Meteostat API, fetch_weather_data, load_cached_weather)
- [ ] 02-02-PLAN.md — Ingest and cache economic data (FRED API, Census API, fetch_fred_data, fetch_census_data)
- [ ] 02-03-PLAN.md — Implement caching infrastructure (requests-cache, CACHE_CONFIG, get_cached_session)
- [ ] 02-04-PLAN.md — Implement temporal alignment and detrending utilities (align_temporal_data, detrend_series)
- [ ] 02-05-PLAN.md — Compute crime-weather correlations with statistical safeguards (analyze_weather_crime_correlation, lagged correlations)
- [ ] 02-06-PLAN.md — Compute crime-economic correlations with statistical safeguards (analyze_economic_crime_correlation, bootstrap CI)
- [ ] 02-07-PLAN.md — Assess policing data availability (assess_policing_data_availability, POLICING_DATA_CONFIG)
- [ ] 02-08-PLAN.md — Generate correlation analysis report (12_report_correlations.py)

### Phase 3: Advanced Temporal Analysis
**Goal**: Granular temporal patterns (holiday effects, individual crime types, shift-by-shift) are analyzed with statistical rigor
**Depends on**: Phase 1 (requires statistical testing infrastructure)
**Requirements**: TEMP-01, TEMP-02, TEMP-03
**Success Criteria** (what must be TRUE):
  1. User can view holiday effects analysis showing pre/post holiday crime patterns for major U.S. holidays with significance testing
  2. User can view individual crime type analysis for homicide, burglary, theft, vehicle theft, aggravated assault with temporal trends, spatial distribution, and seasonality
  3. User can view shift-by-shift temporal analysis (morning 6AM-12PM, afternoon 12PM-6PM, evening 6PM-12AM, late night 12AM-6AM) with statistical comparisons
  4. All temporal analyses include confidence intervals and significance tests from Phase 1 infrastructure
**Plans**: 4 plans in 2 waves

**Wave Structure:**
- Wave 1 (parallel): 03-01 holiday effects, 03-02 crime type profiles, 03-03 shift analysis
- Wave 2 (sequential): 03-04 unified report generator

Plans:
- [x] 03-01-PLAN.md — Holiday effects analysis module (workalendar integration, chi-square tests)
- [x] 03-02-PLAN.md — Individual crime type profiles (homicide, burglary, theft, vehicle theft, aggravated assault)
- [x] 03-03-PLAN.md — Shift-by-shift temporal analysis (4 shifts, ANOVA + FDR post-hoc)
- [x] 03-04-PLAN.md — Unified advanced temporal report generator

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
**Plans**: 6 plans in 3 waves

**Wave Structure:**
- Wave 1 (parallel): 04-01 project structure + config, 04-02 data loading with caching
- Wave 2 (parallel): 04-03 time filters, 04-04 geo filters, 04-05 crime filters
- Wave 3 (sequential): 04-06 main app with tabs and visualizations

Plans:
- [x] 04-01-PLAN.md — Set up Streamlit project structure and configuration
- [x] 04-02-PLAN.md — Implement data loading with caching
- [x] 04-03-PLAN.md — Implement time range filter controls
- [x] 04-04-PLAN.md — Implement geographic filter controls
- [x] 04-05-PLAN.md — Implement crime type filter controls
- [x] 04-06-PLAN.md — Create main dashboard with tabs and visualizations

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
**Plans**: 5 plans in 3 waves

**Wave Structure:**
- Wave 1 (parallel): 05-01 state management infrastructure, 05-02 apply button pattern
- Wave 2 (parallel): 05-03 plotly selection events, 05-04 view-to-view cross-filtering
- Wave 3 (sequential): 05-05 unified URL state encoding

Plans:
- [ ] 05-01-PLAN.md — Create state management infrastructure (pending/applied separation, apply button tracking)
- [ ] 05-02-PLAN.md — Integrate apply button pattern into sidebar filters (pending state, visual indicators)
- [ ] 05-03-PLAN.md — Create Plotly selection event handling infrastructure (on_select="rerun", selection state)
- [ ] 05-04-PLAN.md — Implement view-to-view cross-filtering with opacity dimming (all pages)
- [ ] 05-05-PLAN.md — Implement unified URL state encoding for sidebar + view selections

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
| 2. External Data Integration | 8/8 | ✓ Complete | 2025-01-31 |
| 3. Advanced Temporal Analysis | 4/4 | ✓ Complete | 2026-01-31 |
| 4. Dashboard Foundation | 6/6 | ✓ Complete | 2026-01-31 |
| 5. Dashboard Cross-Filtering | 0/5 | Ready to execute | - |
| 6. Publication Outputs | 0/6 | Not started | - |

**Overall Progress:** [██████████░░] 30/35 plans (86%)
