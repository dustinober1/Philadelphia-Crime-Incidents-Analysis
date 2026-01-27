# Requirements Specification: Crime Incidents Philadelphia Analysis

**Version:** 1.0  
**Date:** 2026-01-27  
**Phase:** Project Initialization  
**Status:** Active (v1 requirements defined; v2 deferred)

---

## Overview

This document specifies functional and non-functional requirements for the Crime Incidents Philadelphia comprehensive analysis project. Requirements are organized by category, prioritized (v1 = in-scope, v2 = deferred), and mapped to success criteria.

### Scope Definition

**v1 Requirements (In Scope):** Requirements essential for delivering a defensible academic analysis of Philadelphia crime patterns. Focused on table stakes analysis dimensions and technical rigor.

**v2 Requirements (Deferred):** Advanced features, predictive modeling, and comparative analysis deferred to future phases pending v1 completion and stakeholder feedback.

**Out of Scope:** Non-data-analysis elements (policy recommendations, real-time systems, mobile apps).

---

## v1 Requirements (In Scope)

### Data Quality & Validation (QUAL)

| ID | Requirement | Success Criteria | Priority |
|----|-------------|------------------|----------|
| QUAL-01 | **Data Ingestion** — Load full 3.5M+ crime incident dataset from parquet format; verify completeness and schema conformance | Records loaded: 3.5M+. Schema validated: all expected columns present (cartodb_id, objectid, dc_dist, psa, dispatch_date_time, ucr_general, text_general_code, location_block, coordinates). No loading errors. | Critical |
| QUAL-02 | **Missing Value Documentation** — Analyze and document missing value patterns by district, year, crime type, and temporal period. Identify non-random missingness. | Missing value heatmaps created (district × month, crime type × year). Documentation of patterns (e.g., "older records 12% more likely to have missing coordinates"). Recommendations for handling (exclude/impute/weight) documented. | Critical |
| QUAL-03 | **Geocoding Coverage Analysis** — Quantify coordinate validity by district and crime type. Document geocoding gaps and potential bias. | Geocoding coverage report: % valid coordinates by district (target: >80% for violent crimes, >70% overall). Comparison of coverage across crime types. Impact analysis: which districts/crimes most affected by geocoding gaps. | Critical |
| QUAL-04 | **Reporting Lag Characterization** — Measure time between incident date and report entry date. Identify seasonal/temporal patterns in lag. Determine exclusion window for analysis cutoff. | Reporting lag distribution computed (median lag by crime type). Decision documented: e.g., "Last 2 months excluded due to 4-6 week lag." Sensitivity analysis: results with/without lag-adjusted exclusion. | Critical |
| QUAL-05 | **Outlier & Anomaly Detection** — Identify data quality anomalies (duplicate records, impossible dates, coordinate out-of-bounds, etc.). Document frequency and handling approach. | Anomaly report: count of invalid records by type. Handling decision documented (exclude/flag/impute). Sensitivity analysis: results robust if anomalies included/excluded. | High |
| QUAL-06 | **Data Dictionary & Provenance** — Document all columns, data types, missing value coding, validation rules, and data source/version. | Data dictionary created (all 15+ columns documented). Source provenance recorded (CartoDB, date downloaded, data version). Processing decisions logged (transformations applied, rationale). | High |
| QUAL-07 | **Cleaned Dataset Checkpoint** — Create validated dataset with documented inclusions/exclusions; save to persistent storage for reproducibility. | Clean dataset saved to `data/crime_incidents_cleaned.parquet`. Processing log documented. Random seeds set for any stochastic operations. Reproducible from raw data. | High |

### Temporal Analysis (TEMP)

| ID | Requirement | Success Criteria | Priority |
|----|-------------|------------------|----------|
| TEMP-01 | **20-Year Trend Analysis** — Analyze overall crime trend from 2006-2026 (dataset scope). Include long-term changes, regime shifts, inflection points. | Trend plot created (annual total crimes, 2006-2026). Trend line fitted (linear regression) with 95% CI. Year-over-year % changes calculated. Anomalies identified (e.g., sudden shifts). | Critical |
| TEMP-02 | **Seasonal Decomposition** — Separate crime data into trend, seasonal, and residual components. Quantify seasonal variation. | Seasonal decomposition (STL method) applied. Seasonal factors extracted for each month and day-of-week. Seasonality magnitude quantified (e.g., summer crimes 15% above annual average). | Critical |
| TEMP-03 | **Day-of-Week & Hour-of-Day Patterns** — Quantify how crime varies across days of week and hours of day. Compare weekday vs weekend. | Heatmap created: offense type × hour-of-day. Heatmap created: offense type × day-of-week. Summary statistics (e.g., "weekend property crimes 20% lower than weekday"). | Critical |
| TEMP-04 | **Trend Analysis by Crime Type** — Separate analyses for major offense categories (violent, property, quality-of-life, etc.). Identify which types increasing/decreasing. | Trend plots for top 10 crime types (2006-2026). Trend direction and magnitude for each. Comparison: violent increasing, property stable/decreasing, or other patterns. | High |
| TEMP-05 | **Seasonality by Crime Type** — Quantify how seasonality differs across offense types (e.g., some crimes peak summer, others constant year-round). | Seasonal factors calculated per crime type. Heatmap: crime type × month showing seasonal variation. Comparison: which types most seasonal (e.g., outdoor crimes), least seasonal (e.g., indoor crimes). | High |
| TEMP-06 | **Year-over-Year Comparisons** — Compare same months/periods across years to isolate year-over-year changes from seasonal variation. | Year-over-year comparison table: selected years (e.g., 2006 vs 2015 vs 2025) for key months. Total crimes, violent crimes, property crimes YoY % change. | Medium |
| TEMP-07 | **Anomaly Detection & Documentation** — Identify and explain unusual temporal spikes/dips (major events, reporting changes, data quality issues). | Anomaly report documenting unusual periods (e.g., "August 2015 spike in robberies; 5% above trend, investigated and attributed to organized retail theft ring bust reporting"). | Medium |

### Geographic Analysis (GEO)

| ID | Requirement | Success Criteria | Priority |
|----|-------------|------------------|----------|
| GEO-01 | **Police District Hotspot Maps** — Create choropleth map showing crime density (total crimes) by police district. Identify highest/lowest crime districts. | Choropleth map created (22 districts). Color scale: incidents per district. Top 5 and bottom 5 districts identified. Comparison: highest district vs city average. | Critical |
| GEO-02 | **Kernel Density Estimation (KDE) Heatmaps** — Generate point-level heatmaps showing geographic concentration of crime. Multiple heatmaps for major crime types. | KDE heatmap created (whole city, incidents density). Separate KDE maps for top 5 crime types. Hotspot locations identified (specific neighborhoods/corridors). | Critical |
| GEO-03 | **Rate-Based Analysis (Per Capita)** — Calculate crime rates normalized by population (crimes per 100k residents) by district. Compare to raw counts. | Crime rate (per 100k population) calculated by district. Comparison: which districts have highest rate vs highest count (often differ). Population data source and year documented. | High |
| GEO-04 | **Spatial Autocorrelation Testing** — Quantify whether neighboring areas have similar crime rates. Calculate Moran's I and interpret. | Moran's I statistic calculated (global spatial autocorrelation). Significance tested (p-value reported). Interpretation: strong/moderate/weak clustering. Limitations noted in report. | High |
| GEO-05 | **District Crime Profiles** — For each district, summarize key metrics (total crimes, top offense types, temporal patterns, trend direction). | Profile template created for each district (22 profiles). Metrics: annual average, trend 2006-2025, top 5 offense types with % distribution, seasonal pattern. Comparison table: districts ranked by key metrics. | High |
| GEO-06 | **Neighborhood-Level Analysis** — Breakdown by neighborhoods/commercial corridors (finer than districts). Identify specific high-crime areas. | Neighborhood-level aggregation (>100 neighborhoods identified from addresses/geographic clustering). Top 20 neighborhoods by crime count and rate mapped. Specific locations identified (streets, intersections). | Medium |
| GEO-07 | **Repeat Location Analysis** — Identify if some locations (addresses, street segments) account for disproportionate crime. Measure concentration. | Top 100 repeat locations identified. Gini index calculated (measure of concentration). Finding: e.g., "20% of crime concentrated at 5% of locations" or "crime broadly distributed." Privacy implications noted. | Medium |

### Offense Type Analysis (OFF)

| ID | Requirement | Success Criteria | Priority |
|----|-------------|------------------|----------|
| OFF-01 | **UCR Crime Category Distribution** — Distribute all crimes across FBI's UCR major categories (violent, property, quality-of-life, etc.). Create pie/bar chart of distribution. | Distribution chart created (stacked bar or pie). Major categories identified (>90% of crimes in top 8 categories). Comparison: violent (%) vs property (%) vs quality-of-life (%). | Critical |
| OFF-02 | **Top 20 Specific Offense Breakdown** — Identify and analyze top 20 specific offense types (robbery, theft from auto, simple assault, etc.). Trends for each. | Ranked list of top 20 offenses by frequency. Trend plot for each (2006-2026). Total crimes, % of total, and 20-year % change for each. | Critical |
| OFF-03 | **Severity Distribution** — Classify crimes by severity (violent vs property, felony vs misdemeanor, etc.). Analyze if severity distribution changing over time. | Severity index created (weights for major crimes > minor crimes). Severity trend analyzed (is crime becoming more or less severe?). Distribution of severity category showing % felony, % misdemeanor, % quality-of-life. | High |
| OFF-04 | **Offense Type Trends** — Separate trend analysis for major offense categories (homicide, robbery, assault, burglary, theft, auto theft, etc.). Which increasing, which decreasing? | Trend plots for top 10 offense types. Trend direction and magnitude (% change 2006-2025). Comparison: most increasing offense type vs most decreasing. | High |
| OFF-05 | **Offense Seasonality** — Which crimes peak in summer vs winter? Which constant year-round? Seasonal patterns by offense type. | Seasonal factors by offense type (top 5-10). Heatmap: offense type × month. Interpretation: which crimes most seasonal (e.g., outdoor crimes), least seasonal (e.g., indoor). | Medium |

### Cross-Factor Analysis (CROSS)

| ID | Requirement | Success Criteria | Priority |
|----|-------------|------------------|----------|
| CROSS-01 | **Temporal × Offense Heatmap** — Show how different offense types vary across hours of day and days of week. Which crimes peak when? | Heatmap created (offense type × hour-of-day). Heatmap created (offense type × day-of-week). Interpretation: robberies peak late evening, burglaries peak work hours (no one home), etc. | Critical |
| CROSS-02 | **Geographic × Offense Heatmap** — Show which neighborhoods have different crime profiles. Which crimes concentrated where? | Heatmap created (district × offense type). Chi-square test for independence: does offense distribution differ by district? (p-value reported). Top 3 crimes by district compared. | Critical |
| CROSS-03 | **Temporal × Geographic Interaction** — Does seasonal pattern vary by district? Do some neighborhoods have different seasonal profiles? | Seasonal decomposition by district (top 5-10 districts). Comparison: does district A peak in summer while district B peaks in winter? Or all similar? | High |
| CROSS-04 | **Severity × Geography** — Are violent crimes concentrated in specific districts? Are property crimes more dispersed? | Violent vs property crime distribution by district. Maps: violent crime hotspots vs property crime hotspots (often different). | Medium |
| CROSS-05 | **Year-over-Year Change by Subgroup** — Do all districts improve/worsen equally? Do all offense types change at same rate? | Comparison table: YoY change by district and by offense type. Identification: districts improving most vs deteriorating most. Offense types increasing most vs decreasing most. | Medium |

### Disparities & Comparisons (DISP)

| ID | Requirement | Success Criteria | Priority |
|----|-------------|------------------|----------|
| DISP-01 | **Cross-District Comparison** — Compare crime metrics across all 22 districts. Quantify variation (range, std dev). Identify disparities. | Comparison table: districts ranked by rate, count, trend. Standard deviation across districts calculated. Highest district vs lowest (fold difference) quantified. | High |
| DISP-02 | **Disparity Metrics Documentation** — Document that analysis observes variation by district but doesn't explain causation (avoids ecological fallacy). Limitations on inference explicit. | Limitations section in report: "Reported crime reflects both victimization and enforcement intensity. District-level patterns don't imply individual-level behavior. Reporting bias documented." | High |
| DISP-03 | **Data-Driven District Characterization** — Summarize each district's unique profile (is it primarily violent vs property? Trending up or down? Peak season? Specific offense concentration?). | District profile document (22 profiles). Each: crime mix (%), trend, seasonality, notable concentrations, comparison to city average. | Medium |

### Dashboard & Visualization (DASH)

| ID | Requirement | Success Criteria | Priority |
|----|-------------|------------------|----------|
| DASH-01 | **Interactive Dashboard** — Create web-based interactive dashboard (Plotly + Folium) allowing exploration of crime by date range, offense type, and geography. | Dashboard created as HTML (self-contained). Filters functional: date picker, offense type selector, geography (district/neighborhood). Charts update dynamically on filter change. | High |
| DASH-02 | **Static Publication-Quality Figures** — Generate 30-50 publication-quality static plots (matplotlib/seaborn) suitable for academic report. High resolution (≥300 DPI), clear legends, colorblind-friendly palettes. | Figure set created (all PNG + PDF formats). Each figure has clear caption (substantive, not just "Crimes by District"). Color palette colorblind-friendly (viridis/cividis). | High |
| DASH-03 | **Map Visualizations** — Choropleth maps (crimes by district), heatmaps (KDE), and marked location maps (repeat locations, hotspots). | Choropleth map created (districts, color by crime rate). KDE heatmap created (whole city). Top locations map created (marked on base map). All include legends and scale. | High |

### Report Generation & Academic Rigor (REPORT)

| ID | Requirement | Success Criteria | Priority |
|----|-------------|------------------|----------|
| REPORT-01 | **Formal Research Report** — Write academic report with methodology, findings, limitations, and conclusions. Support PDF and markdown outputs. | Report structure: executive summary, methodology (data sources, analysis methods), results (findings by section), discussion, limitations, conclusion. 50-100 pages target. | Critical |
| REPORT-02 | **Methodology Chapter** — Document data sources, processing decisions, analysis approaches, and justifications. Transparent enough for replication. | Methodology section (10-15 pages): data source and quality, exclusion criteria, analysis techniques (with citations), statistical methods, software tools used. | Critical |
| REPORT-03 | **Results Presentation** — Present findings with statistics (means, medians, ranges), confidence intervals (95%), and significance tests where applicable. No bare point estimates. | Every result includes: point estimate + 95% CI, or median [IQR]. Hypothesis tests reported with p-value + effect size. Baseline comparisons provided (e.g., "8% above city average (95% CI: 6-10%)"). | Critical |
| REPORT-04 | **Limitations Section** — Explicitly document data quality limitations, confounds, and generalizability bounds. Honest assessment of what can and cannot be concluded. | Limitations section (5-10 pages): reporting bias, geocoding gaps, seasonal confounds, spatial autocorrelation, MAUP, data recency (lag), recommendations for future work. | Critical |
| REPORT-05 | **Figure Integration** — All figures in report are publication-quality, with substantive captions explaining what figure shows and key insight. No orphan figures. | Every figure captioned with: title (descriptive), explanation of axes/colors, key finding (e.g., "Summer crimes average 18% higher than winter (95% CI: 16-20%)"). | High |
| REPORT-06 | **Executive Summary** — One-page summary of key findings, aimed at non-technical audience (city council, community). Highlights top insights. | Executive summary (1 page): headline findings, top 3 insights, interpretation for policy (e.g., "Robbery concentrated in 3 districts; uniform prevention approach unlikely optimal."). | High |
| REPORT-07 | **Reproducibility Documentation** — Code, data processing steps, and exact software versions documented for independent reproduction. | README in repo with: dependencies (requirements.txt + versions), data source and location, script execution order, how to generate report (nbconvert command). Random seeds pinned. | High |

### Statistical Validation & Rigor (STAT)

| ID | Requirement | Success Criteria | Priority |
|----|-------------|------------------|----------|
| STAT-01 | **Hypothesis Testing Framework** — Primary hypotheses pre-registered. Tests conducted with proper α levels and multiple comparison corrections if applicable. | Pre-registration document: planned hypotheses listed before analysis. Multiple comparison correction applied if >5 tests (Bonferroni, FDR). Report distinguishes primary vs exploratory analyses. | High |
| STAT-02 | **Effect Size Reporting** — All findings reported with effect sizes, not just p-values. Practical significance discussed alongside statistical significance. | Each major finding reports: effect size (Cohen's d, % difference, correlation r, etc.) + p-value. Interpretation: "Statistically significant (p<0.01) but modest effect size (d=0.15)." | High |
| STAT-03 | **Sensitivity Analysis** — Key findings tested for robustness. Results stable if assumptions changed, data subsets included/excluded? | Sensitivity analysis table: results of primary finding with variations (e.g., exclude/include recent months, different seasonal adjustments, different cutoffs). Findings robust if conclusions don't change. | High |
| STAT-04 | **Confidence Intervals** — All rate estimates, proportions, and trends include 95% confidence intervals. No bare point estimates in final report. | Every estimate in report includes 95% CI. Examples: "Robbery increased from 3.2% (95% CI: 3.1-3.3%) to 3.5% (95% CI: 3.3-3.7%) of total crimes." | Critical |
| STAT-05 | **Parametric Assumptions Testing** — Data checked for normality, homogeneity of variance, etc. before applying parametric tests. Non-parametric alternatives used if assumptions violated. | Assumption testing: Q-Q plots, Levene's test, etc. documented. Non-parametric methods used (Mann-Whitney, Kruskal-Wallis) if parametric assumptions violated. Report documents which tests applied and why. | Medium |

### Data & Documentation (DATA)

| ID | Requirement | Success Criteria | Priority |
|----|-------------|------------------|----------|
| DATA-01 | **Input Data Management** — Original parquet file versioned and documented. No modifications to raw data; all processing in code. | Raw data: `data/crime_incidents_combined.parquet` in git-lfs or linked to CartoDB source. Data dictionary created (all fields documented). Download date/version recorded. | High |
| DATA-02 | **Processed Data Checkpoints** — Intermediate aggregations (crime by district, by hour, etc.) saved to persistent storage for re-use and verification. | Processed data saved: `data/processed/crime_by_district_month.parquet`, `data/processed/crime_by_ucr_hour.parquet`, etc. All versioned in git. | High |
| DATA-03 | **Analysis Outputs Versioning** — All figures, statistics, and aggregations versioned. Outputs timestamped and reproducible. | Output files include timestamp: `output/figures/temporal_trend_2026-01-27.pdf`. Can re-run analysis and get identical outputs (deterministic). | Medium |

---

## v2 Requirements (Deferred to Future Phases)

### Advanced Demographic Analysis (DEMO)

| ID | Requirement | Rationale | Deferred |
|----|-------------|-----------|----------|
| DEMO-01 | **Census Data Integration** — Join demographic data (income, education, race) by district/tract. Analyze correlation with crime rates. | Requires external Census dataset; adds complexity and time. Deferred pending v1 completion and stakeholder interest. | Phase 4 |
| DEMO-02 | **Disparity Analysis** — Detailed investigation of crime disparities by demographic factors. Include confounding analysis. | Methodologically sensitive (risk of ecological fallacy, stigmatization); recommend deferring for peer review discussion. | Phase 4 |
| DEMO-03 | **Income × Crime Correlation** — Test if lower-income neighborhoods have higher crime. Include confounding analysis (is causation or reporting bias?). | Requires careful framing to avoid stigmatization. Defer for dedicated disparity analysis phase. | Phase 4 |

### Predictive & Advanced Statistical (PRED)

| ID | Requirement | Rationale | Deferred |
|----|-------------|-----------|----------|
| PRED-01 | **Time Series Forecasting** — Forecast total crimes 1-2 years ahead using ARIMA/Prophet. | Out of current scope; predictive modeling deferred to future phase per project constraints. | Phase 5 |
| PRED-02 | **Predictive Hotspot Mapping** — Machine learning models to predict next week's hotspots. | Raises fairness/bias concerns (predictive policing controversy); defer for dedicated research. | Phase 5 |
| PRED-03 | **Repeat Offender / Victim Analysis** — Identify if certain individuals/locations are repeat victims/perpetrators. | Privacy-sensitive; requires individual-level data not in current dataset. Defer. | Phase 5 |

### Comparative & External (COMP)

| ID | Requirement | Rationale | Deferred |
|----|-------------|-----------|----------|
| COMP-01 | **Comparison to National Trends** — Compare Philadelphia crime trends to US national data. | Adds complexity; Philadelphia-focused analysis sufficient for v1. Defer to Phase 5. | Phase 5 |
| COMP-02 | **Comparison to Prior Years' Reports** — Compare current findings to prior Philadelphia crime analysis. Validate consistency. | Depends on availability of prior reports; not essential for v1. Defer. | Phase 4 |
| COMP-03 | **Police Intervention Impact Analysis** — Measure if specific police initiatives (enforcement, community programs) correlate with crime changes. | Requires external intervention timeline data; not available in current dataset. Defer. | Future |

### Policy & Outreach (POLICY)

| ID | Requirement | Rationale | Deferred |
|----|-------------|-----------|----------|
| POLICY-01 | **Policy Recommendation Section** — Translate findings into policy recommendations for city/police. | Out of current scope; project focuses on findings, not recommendations. Defer to policy phase. | Future |
| POLICY-02 | **Community Outreach Materials** — Simplified visualizations and summaries for community organizations. | Lower priority than academic report. Defer to Phase 3-4. | Phase 4 |
| POLICY-03 | **Data Equity Assessment** — Discuss implications of crime data for equity, bias, fairness. | Important but complex; recommend dedicated effort. Defer. | Future |

---

## Out of Scope (Explicit)

| Item | Reason |
|------|--------|
| **Real-Time Data Pipeline** | Project is batch analysis of historical data, not live monitoring. |
| **Mobile Application** | Dashboard is web-based only. |
| **Predictive Modeling** | Descriptive analysis only; forecasting deferred to future phase. |
| **Policy Recommendations** | Report presents findings; recommendations excluded (separate phase). |
| **Comparison to Other Cities** | Philadelphia-focused; comparative analysis out of scope. |
| **Live Crime Monitoring** | Not a real-time system; one-time comprehensive analysis. |

---

## Traceability Matrix (To Be Populated by Roadmapper)

| Requirement ID | Phase | Notebook | Status | Owner |
|---|---|---|---|---|
| QUAL-01 | 1 | 01_data_loading | ✓ Complete | — |
| QUAL-02 | 1 | 01_data_loading | ✓ Complete | — |
| QUAL-03 | 1 | 01_data_loading | ✓ Complete | — |
| QUAL-04 | 1 | 01_data_loading | ✓ Complete | — |
| QUAL-05 | 1 | 01_data_loading | ✓ Complete | — |
| QUAL-06 | 1 | 01_data_loading | ✓ Complete | — |
| QUAL-07 | 1 | 01_data_loading | ✓ Complete | — |
| TEMP-01 | 2 | 03_temporal_analysis | — Pending | — |
| TEMP-02 | 2 | 03_temporal_analysis | — Pending | — |
| TEMP-03 | 2 | 03_temporal_analysis | — Pending | — |
| TEMP-04 | 2 | 03_temporal_analysis | — Pending | — |
| TEMP-05 | 2 | 03_temporal_analysis | — Pending | — |
| TEMP-06 | 2 | 03_temporal_analysis | — Pending | — |
| TEMP-07 | 2 | 03_temporal_analysis | — Pending | — |
| GEO-01 | 2 | 04_geographic_analysis | — Pending | — |
| GEO-02 | 2 | 04_geographic_analysis | — Pending | — |
| GEO-03 | 2 | 04_geographic_analysis | — Pending | — |
| GEO-04 | 2 | 04_geographic_analysis | — Pending | — |
| GEO-05 | 2 | 04_geographic_analysis | — Pending | — |
| GEO-06 | 2 | 04_geographic_analysis | — Pending | — |
| GEO-07 | 2 | 04_geographic_analysis | — Pending | — |
| OFF-01 | 2 | 05_offense_breakdown | — Pending | — |
| OFF-02 | 2 | 05_offense_breakdown | — Pending | — |
| OFF-03 | 2 | 05_offense_breakdown | — Pending | — |
| OFF-04 | 2 | 05_offense_breakdown | — Pending | — |
| OFF-05 | 2 | 05_offense_breakdown | — Pending | — |
| CROSS-01 | 2 | 07_cross_factor_analysis | — Pending | — |
| CROSS-02 | 2 | 07_cross_factor_analysis | — Pending | — |
| CROSS-03 | 2 | 07_cross_factor_analysis | — Pending | — |
| CROSS-04 | 2 | 07_cross_factor_analysis | — Pending | — |
| CROSS-05 | 2 | 07_cross_factor_analysis | — Pending | — |
| DISP-01 | 2 | 06_disparity_analysis | — Pending | — |
| DISP-02 | 2 | 06_disparity_analysis | — Pending | — |
| DISP-03 | 2 | 06_disparity_analysis | — Pending | — |
| DASH-01 | 3 | 08_dashboard | — Pending | — |
| DASH-02 | 2 | 03-07 | — Pending | — |
| DASH-03 | 3 | 08_dashboard | — Pending | — |
| REPORT-01 | 3 | 09_report_generation | — Pending | — |
| REPORT-02 | 3 | 09_report_generation | — Pending | — |
| REPORT-03 | 3 | 09_report_generation | — Pending | — |
| REPORT-04 | 3 | 09_report_generation | — Pending | — |
| REPORT-05 | 3 | 09_report_generation | — Pending | — |
| REPORT-06 | 3 | 09_report_generation | — Pending | — |
| REPORT-07 | 2-3 | All | — Pending | — |
| STAT-01 | 1 | 02_exploratory_analysis | ✓ Complete | — |
| STAT-02 | 2-3 | All | — Pending | — |
| STAT-03 | 3 | 09_report_generation | — Pending | — |
| STAT-04 | 2-3 | All | — Pending | — |
| STAT-05 | 2-3 | All | — Pending | — |
| DATA-01 | 1 | 01_data_loading | ✓ Complete | — |
| DATA-02 | 2 | 02_exploratory_analysis | — Pending | — |
| DATA-03 | 3 | 09_report_generation | — Pending | — |

---

## Requirements Summary

**Total v1 Requirements:** 49  
**Critical:** 12  
**High:** 24  
**Medium:** 13  

**v2 Requirements (Deferred):** 9  
**Out of Scope:** 6  

---

*Created: 2026-01-27*  
*Status: Ready for roadmap development*  
*Traceability: To be completed by roadmapper*
