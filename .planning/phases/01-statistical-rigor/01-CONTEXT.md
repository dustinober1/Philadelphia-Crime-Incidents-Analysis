# Phase 1: Statistical Rigor Layer - Context

**Gathered:** 2025-01-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Add significance testing, confidence intervals, effect sizes, multiple testing correction, and reproducibility infrastructure to all 11 existing analysis modules. This is a horizontal upgrade — no new analyses, just making existing ones publication-ready.

</domain>

<decisions>
## Implementation Decisions

### Significance testing approach
- **Framework**: Both SciPy and statsmodels (use case-based)
  - SciPy (scipy.stats) for simple tests: t-tests, Mann-Whitney U, chi-square
  - statsmodels for econometric-style analysis and detailed regression output
- **Non-normal data**: Test then decide (Shapiro-Wilk normality assessment)
  - If normal: parametric tests (t-test, ANOVA, Pearson)
  - If not normal: non-parametric alternatives (Mann-Whitney, Kruskal-Wallis, Spearman)
- **Temporal trends**: Mann-Kendall trend test
  - Non-parametric, robust to outliers and non-linear trends
  - Appropriate for 20-year crime trend analysis
- **Multi-group comparisons**: ANOVA + Tukey's HSD
  - ANOVA first to test overall significance
  - Tukey's HSD for pairwise comparisons (controls family-wise error rate)

### Confidence intervals & effect sizes
- **Confidence level**: 99% CI
  - More conservative than standard 95%, appropriate given exploratory nature
- **Effect size for means**: Context-dependent
  - Cohen's d for parametric comparisons (small=0.2, medium=0.5, large=0.8)
  - Cliff's delta for non-parametric/ordinal comparisons
- **Effect size for proportions**: Odds ratio (OR)
  - Standard in epidemiology and crime research
- **Presentation**: Both text + plots
  - Text outputs include CI in format: 5.2 [3.1, 7.3]
  - Plots show error bands or shaded regions for CIs

### Multiple testing correction
- **Method**: Report both uncorrected and corrected
  - Primary: FDR Benjamini-Hochberg (less conservative, appropriate for EDA)
  - Secondary: Bonferroni for key comparisons (very conservative)
- **Omnibus trigger**: Same hypothesis rule
  - Apply correction when testing the same hypothesis across multiple groups/categories
  - Examples: 23 districts compared, 12 crime types tested
- **Reporting**: Both raw and FDR-adjusted p-values
  - Reader can see the effect of correction
- **Significance threshold**: No fixed threshold
  - Report exact p-values; let context determine interpretation
  - Note: 99% CI choice suggests preferring p < 0.01 as significant

### Reproducibility & data audit
- **Random seeds**: Global with override
  - Set global seed at module import for reproducibility
  - Allow override via parameter for sensitivity analysis
- **Data version tracking**: Both hash + metadata
  - SHA256 hash of input file for definitive fingerprinting
  - Metadata snapshot: row count, date range, columns
- **Parameter documentation**: Both docstrings + reports
  - Docstring 'Parameters' section for code readers
  - 'Analysis Configuration' section in markdown reports for end users
- **Data quality audit**: Comprehensive
  - Missing data patterns by column
  - Coordinate coverage by crime type/district
  - Duplicate detection
  - Outlier detection
  - Distribution summaries
  - Temporal gaps
  - Quality scores
  - Recommendations for analysis limitations

### Claude's Discretion
- Exact implementation of normality testing thresholds (e.g., Shapiro-Wilk p-value cutoff)
- Bootstrap/resampling methods if non-parametric tests prove insufficient
- Visualization styling for confidence intervals (error bars vs bands, colors)
- Data quality scoring algorithm design

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard statistical practice for research-grade analysis.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-statistical-rigor*
*Context gathered: 2025-01-30*
