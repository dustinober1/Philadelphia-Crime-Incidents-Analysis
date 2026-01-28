---
phase: 02-core-analysis
plan: 06
executed: false
status: pending_execution
pending_artifacts:
  - notebooks/07_cross_factor_analysis.ipynb (needs execution)
  - output/figures/cross_factor/ (needs generation)
  - output/tables/cross_factor/ (needs generation)
requirements_satisfied:
  - CROSS-01: Temporal×offense interactions (pending)
  - CROSS-02: Geographic×offense patterns (pending)
  - CROSS-03: Temporal×geographic interactions (pending)
  - CROSS-04: Chi-square tests with effect sizes (pending)
  - CROSS-05: Correlation matrices (pending)
---

# Plan 02-06 Summary: Cross-Factor Analysis (Pending Execution)

## Overview
This plan implements comprehensive cross-factor analysis examining interactions between temporal, geographic, and offense dimensions with rigorous statistical testing. The notebook is created but needs to be executed to generate all output files.

## Planned Accomplishments

### Data Preparation and Framework
- Import required libraries for cross-factor analysis
- Load cleaned crime data and create factor variables
- Design cross-factor matrix with 16+ interaction tests
- Establish statistical testing framework with chi-square, ANOVA, and correlation analysis
- Apply multiple comparison correction (Bonferroni)

### Temporal×Offense Analysis
- Season × Offense type interactions with chi-square tests
- Day of week × Offense type analysis
- Hour × Offense type patterns
- Year × Offense type trend interactions
- Effect sizes calculated using Cramer's V
- Standardized residuals for identifying specific associations

### Geographic×Offense Analysis
- District × Offense type interactions
- District category × Offense type analysis
- Hotspot vs non-hotspot × Offense type comparison
- Statistical tests with effect sizes and significance correction

### Temporal×Geographic Analysis
- District × Season interactions for seasonal patterns
- District × Year trend differences
- District × Day of week patterns
- District × Hour temporal variations

### Correlation Analysis
- Pearson correlation matrix for continuous variables
- Spearman rank correlation for non-linear relationships
- Temporal autocorrelation (ACF/PACF)
- Three-way interaction analysis

## Expected Outputs

### Figures
- `season_offense_heatmap.png` - Season vs offense type distribution
- `day_offense_heatmap.png` - Day of week vs offense type
- `hour_offense_heatmap.png` - Hour vs offense type patterns
- `year_offense_trends.png` - Offense proportions by year
- `district_offense_stacked.png` - Offense distribution by district
- `district_category_offense.png` - District category vs offense type
- `hotspot_offense_comparison.png` - Hotspot status vs offense type
- `district_season_heatmap.png` - District vs season patterns
- `district_trends_comparison.png` - Trends by district category
- `district_day_heatmap.png` - District vs day of week
- `district_hour_heatmap.png` - District vs hour patterns
- `correlation_matrix_pearson.png` - Pearson correlation heatmap
- `correlation_matrix_spearman.png` - Spearman correlation heatmap
- `temporal_acf.png` - Autocorrelation function
- `three_way_interaction_faceted.png` - Three-way interaction visualization

### Tables
- `interaction_tests.csv` - Complete statistical test results with corrected p-values
- `correlation_matrix.csv` - Variable correlation matrix

## Technical Approach
- Chi-square tests for independence between categorical variables
- ANOVA for categorical-continuous interactions
- Correlation analysis for continuous variables
- Effect size calculations (Cramer's V, eta-squared, Pearson r)
- Multiple comparison correction using Bonferroni method
- Publication-quality visualizations with proper annotations

## Requirements Satisfaction
This analysis will satisfy CROSS-01 through CROSS-05 requirements:
- CROSS-01: Temporal×offense interactions analyzed
- CROSS-02: Geographic×offense patterns tested
- CROSS-03: Temporal×geographic interactions examined
- CROSS-04: Chi-square tests with effect sizes implemented
- CROSS-05: Correlation matrices and statistical tests completed

## Current Status
The notebook `notebooks/07_cross_factor_analysis.ipynb` has been created with all planned analysis but needs to be executed to generate the output files. This will be completed in the next gap closure plan (02-07).