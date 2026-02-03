# Retail Theft Trend Analysis Report (POLICY-01)

## Executive Summary

**Verdict: SUPPORTED**

The data **supports** a significant increase in theft incidents. Theft has increased +66.8% from the pre-COVID baseline, exceeding the 25% threshold.

## Key Findings

### 5-Year Trend
- **Baseline average** (2018-2019): **24,234** thefts/year
- **Latest complete year** (2024): **40,423** thefts/year
- **Change from baseline**: **+66.8%**

### Year-by-Year Breakdown

| Year | Count | YoY Change | vs Baseline |
|------|-------|------------|-------------|
| 2018 | 23,369.0 | — | -3.6% |
| 2019 | 25,099.0 | +7.4% | +3.6% |
| 2020 | 20,914.0 | -16.7% | -13.7% |
| 2021 | 24,567.0 | +17.5% | +1.4% |
| 2022 | 33,116.0 | +34.8% | +36.7% |
| 2023 | 37,054.0 | +11.9% | +52.9% |
| 2024 | 40,423.0 | +9.1% | +66.8% |

### Seasonal Patterns
- Holiday shopping season (Nov-Dec) shows **+3.6%** premium over other months
- Peak month: **Oct** with average 2,804 incidents

### COVID-19 Impact
- 2020 saw a significant dip due to pandemic lockdowns and business closures
- Post-COVID recovery began in 2021 and accelerated through 2023-2024

## Methodology

- **Data source**: Philadelphia Police Department crime incident data
- **Category**: "Thefts" (`text_general_code = 'Thefts'`)
- **UCR Code**: 600 (Theft/Larceny)
- **Analysis period**: 2019-2024
- **Baseline period**: 2018-2019
- **Verdict threshold**: >25% increase from baseline = "SUPPORTED"

## Caveats

1. **Proxy measure**: This analysis uses "Thefts" as a proxy for retail theft. The data does not distinguish between retail theft, shoplifting, and other theft categories.
2. **Reporting changes**: Changes in reporting practices may affect year-over-year comparisons.
3. **COVID distortion**: The 2020-2021 pandemic period created abnormal conditions that may distort trend analysis.
4. **Population changes**: This is a raw count analysis; per-capita rates may differ.

## Visualizations

- `retail_theft_trend.png` - 5-year trend with baseline comparison
- `retail_theft_monthly_heatmap.png` - Monthly patterns by year

---
*Generated: 2026-02-02 20:23*  
*Notebook: retail_theft_trend.ipynb*  
*Requirement: POLICY-01*
