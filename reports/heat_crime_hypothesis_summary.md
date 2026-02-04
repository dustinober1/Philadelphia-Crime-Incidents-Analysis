# Heat-Crime Hypothesis Test Results

**Analysis Date:** 2026-02-03

## Research Question

Is there a statistically significant relationship between temperature and crime rates in Philadelphia, particularly for violent crimes?

## Data

- Crime incidents: 3,496,353 records (2006-2026)
- Daily observations: 7,324 days
- Weather data: Daily temperature readings from Philadelphia station

## Key Findings

### 1. Correlation Analysis

- **Total Crime:** r = 0.3612 (p < 0.001), medium effect
- **Violent Crime:** r = 0.2987 (p < 0.001), small effect
- **Property Crime:** r = 0.3113 (p < 0.001), medium effect

### 2. Hot vs. Cold Period Comparison

Temperature thresholds: Cold ≤6.2°C, Hot ≥22.7°C

**Violent Crime:**
- Cold period: 40.7 incidents/day
- Hot period: 48.9 incidents/day
- Change: +20.2% (p < 0.001)
- Effect size (Cohen's d): 0.764

### 3. Linear Regression

Violent crimes increase by **0.36 incidents/day** for every 1°C increase in temperature.

## Conclusion

**✓ HYPOTHESIS SUPPORTED**

There is a statistically significant positive relationship between temperature and violent crime in Philadelphia. The effect size is small, with a correlation of r = 0.2987. During hot periods (≥22.7°C), violent crime rates are 20.2% higher than during cold periods.

## Limitations

- Single weather station may not capture micro-climate variations
- Daily aggregation loses intra-day temperature variations
- Correlation does not imply causation
- Other confounding factors (e.g., holidays, events) not controlled

## Methodology

1. **Data merging:** Daily crime aggregation matched with daily weather observations
2. **Correlation analysis:** Pearson, Spearman, and Kendall tau methods
3. **Hypothesis testing:** Independent t-tests comparing hot vs. cold periods
4. **Effect sizes:** Cohen's d and correlation coefficients
5. **Significance level:** α = 0.05
