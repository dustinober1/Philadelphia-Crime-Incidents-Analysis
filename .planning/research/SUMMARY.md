# Project Research Summary

**Project:** Crime Incidents Philadelphia EDA with Correlation Analysis & Interactive Dashboard
**Domain:** Exploratory Data Analysis (Crime Research) with Statistical Rigor and Interactive Visualization
**Researched:** 2025-01-30
**Confidence:** HIGH

## Executive Summary

This project is a research-grade exploratory data analysis (EDA) system for Philadelphia crime incidents spanning 2006-2026 (3.4M+ records). Expert-built crime analysis EDA systems differ from basic exploration by emphasizing statistical rigor (hypothesis testing, confidence intervals, effect sizes), external data correlation (weather, economic factors), and reproducibility infrastructure (random seeds, versioned data, documented limitations). The recommended approach is to build on the existing modular analysis pipeline with three major additions: (1) a statistical testing layer that adds significance testing to all existing analyses, (2) external data integration for weather and economic correlations, and (3) an interactive Streamlit dashboard for ongoing hypothesis generation.

The research strongly supports using Streamlit (not Dash) for rapid prototyping with Plotly for interactive visualizations, statsmodels/SciPy for statistical analysis, and free APIs (Meteostat, NOAA CDO, U.S. Census, FRED) for external data. Critical risks identified include spurious time series correlations (addressed by detrending and Granger causality tests), the Modifiable Areal Unit Problem in spatial analysis (addressed by multi-scale analysis), and missing coordinate selection bias (~25% of records, addressed by profiling missingness patterns). The most significant pitfall is data dredging without multiple testing correction—this must be addressed in the correlation analysis phase before extracting insights.

The recommended roadmap structure prioritizes research-grade validity over dashboard features. Phase 1 establishes a statistical rigor layer to make existing analyses publication-ready. Phase 2 ingests external data and implements correlation analysis with proper safeguards. Phase 3 builds the interactive dashboard foundation. Phase 4 adds correlation-specific dashboard pages. Phase 5 generates publication-quality outputs. This order ensures the dashboard is built on analytically sound foundations rather than accelerating to UI before confirming underlying patterns are valid.

## Key Findings

### Recommended Stack

Research indicates a Python-based stack with Streamlit as the dashboard framework, Plotly for interactive visualizations, and statsmodels/SciPy for statistical analysis. Streamlit is recommended over Dash due to faster time-to-prototype for research dashboards and pure Python development (no HTML/CSS/JS required). For external data, free APIs (Meteostat for weather, U.S. Census for economic indicators, FRED for unemployment) provide adequate data without requiring paid services.

**Core technologies:**
- **Streamlit 1.40+**: Interactive dashboard framework — fastest prototyping for research dashboards, reactive UI with session state management, pure Python (no frontend skills required)
- **Plotly 6.0+**: Interactive visualization library — native Streamlit integration, 40+ chart types including geographic maps, WebGL-accelerated rendering for large datasets
- **statsmodels 0.14.6+**: Statistical analysis — academic-standard for hypothesis testing, time series analysis, confidence intervals, effect sizes
- **Meteostat**: Weather data API — free historical weather data (temperature, precipitation), Python SDK, avoids paid weather API costs
- **SciPy 1.16+**: Scientific computing — correlation tests (Pearson, Spearman, Kendall), chi-squared tests, linear regression
- **folium 0.20.0+**: Interactive maps — Leaflet-based choropleth maps for district-level crime visualization, GeoJSON support for Philadelphia boundaries

### Expected Features

Research reveals that "research-grade" EDA requires statistical rigor beyond basic exploration. Table stakes features include significance testing, confidence intervals, reproducibility infrastructure, and data quality documentation. Differentiators that distinguish this from basic EDA include external data correlation, granular temporal analysis (holiday effects, event-based spikes), and multi-method triangulation.

**Must have (table stakes):**
- **Statistical testing layer** — significance tests, p-values, confidence intervals, effect sizes on all existing analyses (academic research standard)
- **Reproducibility infrastructure** — random seeds, version tracking, parameter documentation (required for publication)
- **Publication-quality outputs** — high-DPI figure export (PNG/SVG/PDF), citation-ready formats (papers require specific DPI)
- **Data quality audit report** — comprehensive documentation of limitations, missing coordinate bias analysis (~25% missing data)

**Should have (competitive):**
- **External data correlation** — weather (temperature, precipitation), economic (unemployment, poverty) factors (moves beyond descriptive to explanatory analysis)
- **Interactive dashboard** — Streamlit with filters, cross-filtering, zoom, time range selection (enables ongoing hypothesis generation)
- **Granular temporal analysis** — holiday effects, event-based spikes, shift-by-shift patterns (reveals patterns hidden in monthly aggregation)
- **Multi-method triangulation** — spatial + temporal + categorical confirmation of patterns (robust findings survive different approaches)

**Defer (v2+):**
- **State persistence (URL encoding)** — permalink generation for specific filtered views (nice-to-have, not essential for research)
- **Crime-type deep dives** — individual analysis for homicide, burglary, theft (valuable but can wait after external correlations validated)
- **Predictive modeling/forecasting** — out of scope for exploratory analysis, requires separate validation framework

### Architecture Approach

The recommended architecture follows a layered approach: storage layer (parquet files, external data caches), data layer (loaders, external ingestion), analysis layer (statistical modules, correlation analysis), and presentation layer (report generators, dashboard, publication outputs). The key insight is that analysis modules should return standardized results dictionaries with base64-encoded plots, enabling reuse across report generators, dashboard, and publication outputs. Dashboard should call analysis modules directly (not duplicate logic), with aggressive use of `@st.cache_data` for performance.

**Major components:**
1. **Core Data Loader** (utils.py) — load parquet dataset, validate coordinates, extract temporal features (used by all analysis modules)
2. **External Data Ingestion** (NEW) — fetch weather/economic/policing data from APIs, cache locally, handle temporal alignment (enables correlation analysis)
3. **Analysis Modules** — perform statistical analysis, return results dicts with base64 plots (reusable across reports/dashboard)
4. **Correlation Analysis** (NEW) — compute crime-external correlations with significance tests, detrending, Granger causality (core research value-add)
5. **Statistical Analysis Layer** (NEW) — add confidence intervals, effect sizes, multiple testing correction to all analyses (publication requirement)
6. **Dashboard** (Streamlit) — interactive UI with filters, cached data loading, real-time visualization (reuses analysis modules, doesn't duplicate logic)
7. **Publication Outputs** (NEW) — generate high-DPI figures, LaTeX tables, academic-formatted summaries (separate from interactive assets)

### Critical Pitfalls

Research identified 8 major pitfalls across statistical validity, spatial analysis, data quality, and dashboard performance. The top three are spurious time series correlations, the Modifiable Areal Unit Problem (MAUP), and missing coordinate selection bias.

1. **Spurious Time Series Correlations** — time series with shared drift (crime increasing, ice cream sales increasing) produce high correlations without causal relationships. Prevention: detrend before correlation (first-differencing or residualization), use Granger causality tests, split-sample validation.
2. **Modifiable Areal Unit Problem (MAUP)** — crime patterns change dramatically based on spatial aggregation level (district vs tract vs block). Prevention: multi-scale analysis (report at multiple resolutions), coordinate-based point analysis where possible, test robustness across 3+ spatial units.
3. **Missing Coordinate Selection Bias** — filtering to `valid_coord=True` (removing ~25% of records) creates biased results because missingness is systematic (certain crime types, neighborhoods, time periods). Prevention: compare valid vs missing characteristics, report "missingness profile," explicitly state analyses apply to geocoded subset only.
4. **Incomplete Year Trend Artifacts** — including partial 2026 data (January 1-20 only) creates artificial drops in trend analysis. Prevention: `is_complete_year()` function, auto-exclude years with <90% expected records, visualize annual counts first.
5. **Data Dredging Without Multiple Testing Correction** — testing dozens of correlations without correction guarantees false discoveries. Prevention: track ALL tests (not just significant), apply Benjamini-Hochberg FDR correction, pre-register hypotheses.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Statistical Rigor Layer
**Rationale:** Existing analyses lack statistical significance testing, confidence intervals, and effect sizes—making them non-publication-ready. This must be addressed first to establish analytically sound foundations before adding complexity.
**Delivers:** Statistical testing utilities, updated analysis modules with p-values/CIs, reproducibility infrastructure (seeds, versioning), data quality audit report documenting missing coordinate bias.
**Addresses:** Table stakes features (statistical testing, reproducibility, data quality documentation)
**Avoids:** HARKing (hypothesizing after results known), p-value fixation, hidden limitations

### Phase 2: External Data Integration & Correlation Analysis
**Rationale:** Cannot perform correlation analysis without external data. This phase fetches weather/economic data, implements correlations with proper safeguards (detrending, Granger tests, multiple testing correction), and generates correlation report.
**Delivers:** External data ingestion modules (weather, economic, policing), cached external datasets, correlation analysis with statistical safeguards, correlation-focused report generator.
**Uses:** Meteostat (weather), U.S. Census API (economic), FRED API (unemployment), statsmodels/SciPy (statistical tests)
**Implements:** Architecture Pattern 2 (External Data Ingestion with Caching)
**Avoids:** Spurious correlations (detrending, Granger causality), data dredging (FDR correction), temporal misalignment

### Phase 3: Dashboard Foundation
**Rationale:** Basic dashboard can display existing analyses immediately, providing early value while correlation modules are being built. Runs in parallel with Phase 2.
**Delivers:** Streamlit project structure, basic app.py with existing analysis modules, filter components (time range, district, crime type), dashboard utilities (shared functions).
**Uses:** Streamlit 1.40+, Plotly Express, `@st.cache_data` for performance
**Implements:** Architecture Pattern 3 (Dashboard as Analysis Orchestrator)
**Avoids:** Dashboard-side data processing logic, performance collapse (aggressive caching, sampling for viz)

### Phase 4: Dashboard Correlation Pages
**Rationale:** Correlation-specific dashboard pages require working correlation analysis functions (Phase 2). Adds interactive exploration of weather/economic correlations.
**Delivers:** Correlation dashboard pages, external data filters, interactive correlation visualizations, cross-filtering (district × weather × crime type).
**Uses:** Correlation analysis modules from Phase 2
**Implements:** Architecture Pattern 3 (Dashboard reuses analysis modules)
**Avoids:** Cherry-picking UX (provide context, show full time range alongside selections), overwhelming filters (layered "basic" vs "advanced" modes)

### Phase 5: Publication-Quality Outputs
**Rationale:** Requires stable analysis results (from Phases 1-2) before generating publication figures. Generates high-DPI figures, LaTeX tables, academic-formatted summaries.
**Delivers:** Publication output utilities, high-DPI figure generation (temporal, spatial, correlation), LaTeX table export, documentation of publication pipeline.
**Uses:** matplotlib with publication config, Kaleido for static image export
**Implements:** Architecture Pattern 4 (Publication Output Generation)
**Avoids:** Mixing interactive/publication figure styles (separate generation paths)

### Phase Ordering Rationale

- **Statistical rigor first**: Without significance testing and confidence intervals, findings are not publication-ready. Building correlations or dashboards on shaky foundations risks wasting effort on invalid patterns.
- **External data before correlation**: Obvious dependency—cannot correlate with non-existent data.
- **Dashboard foundation in parallel**: Basic dashboard can show existing analyses immediately, providing early value and user feedback while complex correlation modules are built.
- **Dashboard correlation pages after correlation analysis**: Cannot build interactive correlation exploration without working correlation functions.
- **Publication outputs last**: Need stable, validated analysis results before investing in publication-quality figure generation.

This order addresses critical pitfalls early: Phase 1 addresses HARKing and p-value fixation; Phase 2 addresses spurious correlations, data dredging, and temporal misalignment; Phase 3 addresses dashboard performance collapse; Phase 4 addresses cherry-picking UX.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (External Data Integration):** API rate limits, temporal alignment strategies for mismatched granularities (daily weather vs monthly economic), need validation on actual API responses
- **Phase 4 (Dashboard Correlation Pages):** Interactive correlation visualization patterns (how to display lag relationships, cross-filtering UX), may need prototyping

Phases with standard patterns (skip research-phase):
- **Phase 1 (Statistical Rigor):** Well-documented patterns (statsmodels, scipy), existing codebase has statistical test examples
- **Phase 3 (Dashboard Foundation):** Streamlit multipage apps are standard pattern, extensive documentation and examples
- **Phase 5 (Publication Outputs):** Matplotlib publication styling is well-established, clear patterns for DPI/font sizing

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified with official documentation (Streamlit, Plotly, statsmodels, Meteostat, Census/FRED APIs). Alternatives considered and justified. |
| Features | MEDIUM | Based on academic literature review and crime analysis dashboard examples. Table stakes features well-supported; differentiators inferred from research gaps in existing dashboards. |
| Architecture | HIGH | Verified with official Streamlit documentation (caching, multipage apps). Patterns validated against existing codebase structure. |
| Pitfalls | HIGH | Statistical pitfalls verified with academic sources (MAUP, spurious correlations). Dashboard pitfalls verified with Streamlit/Dash performance docs. |

**Overall confidence:** HIGH

### Gaps to Address

- **External data API rate limits:** Research identified free APIs (Meteostat, NOAA CDO, Census, FRED) but actual rate limits may impact implementation. Handle during Phase 2 planning by testing API responses and implementing caching with staleness checks.
- **Dashboard performance at 3.5M scale:** Research recommends aggressive caching and sampling, but actual performance must be validated. Handle during Phase 3 by testing with full dataset early (not just samples).
- **Spatiotemporal granularity mismatch:** Weather data is point-based (city center), economic data is district/tract-level, crime data is point-level. Research doesn't specify optimal merge strategy. Handle during Phase 2 by testing multiple merge approaches and documenting limitations.

## Sources

### Primary (HIGH confidence)
- Streamlit Documentation — Caching (@st.cache_data), multipage apps, session state, performance best practices
- Plotly.py Documentation — Geographic scatter maps, time series charts, WebGL acceleration (scattergl), large dataset handling
- statsmodels Documentation — Statistical modeling, hypothesis tests, time series analysis, confidence intervals
- SciPy Documentation (v1.16.2) — Correlation tests (Pearson, Spearman, Kendall), chi-squared tests, linear regression
- Meteostat Documentation — Daily/hourly weather API, available variables, Python SDK usage
- U.S. Census API Documentation — ACS 5-year estimates, geographic granularity, query structure
- FRED API Documentation — Economic time series, Philadelphia unemployment rate series, query parameters

### Secondary (MEDIUM confidence)
- Springer 2025: "Exploratory data analysis, time series analysis, crime type prediction" — research-grade EDA features
- Oxford Academic 2025: "Information Analysis in Criminal Investigations" — statistical rigor requirements
- ScienceDirect 2024: "Temperature and Crime Correlation" — external correlation patterns, non-linear relationships
- ScienceDirect 2024: "Economic correlates of crime in Houston" — economic-crime correlation methodologies
- DOJ COPS: "Designing an Effective Law Enforcement Data Dashboard" — dashboard feature requirements for crime analysis
- Taylor & Francis 2012: "Issues in the aggregation and spatial analysis of crime" — MAUP in crime analysis
- PubMed Central 2016: "Common pitfalls in statistical analysis: The use of correlation" — spurious correlation prevention

### Tertiary (LOW confidence)
- Yellowfin BI, Databox 2025: Dashboard design mistakes — cherry-picking UX patterns (needs validation with users)
- Medium blog posts: Data visualization errors — confirmation bias in visualization (general principles, specific to crime analysis needs testing)

---
*Research completed: 2025-01-30*
*Ready for roadmap: yes*
