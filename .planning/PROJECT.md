# Philadelphia Crime EDA

## What This Is

A research-grade exploratory data analysis project for Philadelphia crime incidents spanning 2006-2026 (~3.4M records). The project combines comprehensive statistical analysis of temporal, spatial, and categorical patterns with external data correlation (weather, economic, policing) and an interactive dashboard for academic research publication.

**Dataset**: `data/crime_incidents_combined.parquet` — ~3.5M records, 2006-2026

## Core Value

Rigorous, publication-quality insights into Philadelphia crime patterns through systematic analysis of temporal, spatial, and contextual factors with interactive exploration capabilities.

If everything else fails, these must work:
1. **Statistical rigor** — All analyses must be methodologically sound and reproducible
2. **Interactive exploration** — Dashboard must enable flexible querying and discovery
3. **Publication-ready outputs** — Results suitable for academic presentation

## Requirements

### Validated

<!-- Shipped and confirmed valuable. Existing analysis modules. -->

- ✓ Data quality assessment — Missing data analysis, coordinate validation, duplicate detection (existing)
- ✓ Temporal analysis — Long-term trends, seasonal patterns, day/hour heatmaps (existing)
- ✓ Categorical analysis — Crime type distribution, police districts, UCR categories (existing)
- ✓ Spatial analysis — Geographic distribution, density maps, coordinate validation (existing)
- ✓ Cross analysis — Crime × Time, Crime × Location, District × Time patterns (existing)
- ✓ Safety trend analysis — Violent vs property crime trends (2016-2025) (existing)
- ✓ Summer spike analysis — July-August crime surge patterns (existing)
- ✓ Red zones/hotspots — DBSCAN clustering for patrol deployment insights (existing)
- ✓ COVID lockdown impact — Pre/during/post lockdown comparison (existing)
- ✓ Robbery timing patterns — Hour-of-day and day-of-week analysis (existing)
- ✓ Weighted severity scoring — District-level severity distinguishing high-volume/low-risk vs low-volume/high-risk areas (existing)

### Active

<!-- Current scope. Building toward these. -->

- [ ] **Audit existing analyses** — Systematic review of all 11 analysis modules for gaps, methodological issues, and completeness
- [ ] **Crime type deep-dive** — Expand beyond robbery: analyze homicide, assault, burglary, theft, vehicle theft patterns individually
- [ ] **Temporal granularity** — Holiday effects, major events, day-of-week nuances, shift-by-shift patterns
- [ ] **Weather correlation** — Source Philadelphia weather data and correlate with crime incidence (temperature, precipitation, extreme conditions)
- [ ] **Economic correlation** — Source economic indicators (unemployment, poverty rates, income) by district/area and correlate with crime patterns
- [ ] **Policing correlation** — Source policing data (resources, arrest rates, response times if available) and correlate with crime outcomes
- [ ] **Interactive dashboard** — Web-based dashboard (Streamlit or Dash) with time range, geographic (district/neighborhood), and crime type filters
- [ ] **Publication outputs** — Generate academic-quality figures, tables, and summaries suitable for research paper

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- **Real-time data integration** — Dataset is historical through 2026; live updates not required for research goals
- **Predictive modeling/forecasting** — EDA focus is understanding past patterns, not predicting future crime
- **Machine learning classification** — Not building crime prediction or classification models
- **Mobile app** — Web dashboard sufficient; mobile adds complexity without research value
- **Causal inference claims** — Correlation analysis only; causal claims require experimental design beyond EDA scope

## Context

**Existing Codebase:**
- Python-based with modular analysis pipeline pattern
- 11 analysis modules in `analysis/` directory
- 6 report generators producing markdown with embedded visualizations
- Comprehensive documentation in `CLAUDE.md`

**Data Characteristics:**
- ~3.5M records spanning 20 years (2006-2026)
- ~25% of records lack valid coordinates
- 2026 data is incomplete (through January 20 only)
- UCR crime classification system used (Violent/Property/Other)
- Philadelphia-specific: police districts, lat/lon coordinates

**Research Goals:**
- Academic/research context — potential for paper or thesis
- Focus on rigorous statistical analysis and pattern discovery
- Interactive exploration to enable ongoing hypothesis generation

**Known Gotchas:**
- Missing coordinates require filtering with `valid_coord` flag
- District values may be strings or floats; convert with `int(float(value))`
- Large dataset requires sampling for visualizations
- 2026 incomplete year must be excluded from trend analysis

## Constraints

- **Data Sources**: External data must be freely available (weather APIs, open government data) — No paid datasets
- **Tech Stack**: Python ecosystem (pandas, numpy, matplotlib, seaborn, scikit-learn, streamlit or dash) — Existing codebase pattern
- **Compute**: Local execution — Design for standard consumer hardware (16GB RAM baseline)
- **Timeline**: No hard deadline — Focus on quality and completeness

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Dashboard framework | Choose between Streamlit (simpler, faster) vs Dash (more customizable, steeper learning curve) | — Pending |
| External data sourcing | Identify specific APIs/datasets for Philadelphia weather, economic, policing data | — Pending |
| Statistical rigor standards | Define what constitutes publication-quality analysis (significance tests, confidence intervals, effect sizes) | — Pending |
| Audit methodology | Define review criteria for existing analyses (completeness, methodology, reproducibility) | — Pending |

---
*Last updated: 2025-01-30 after initialization*
