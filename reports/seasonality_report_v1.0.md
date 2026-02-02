# Seasonality Report

**Version:** v1.0
**Generated:** 2026-02-02 23:30 UTC

## Summary
Yes, summer months show 19.5% more crimes than winter months. July vs January difference: 18.3%. Test: p = 2.83e-08.

## Methods
**Data source:** Philadelphia Police Department crime incidents dataset.

**Analysis period:** 2006-2025 (20 years of monthly data).

**Seasonal definitions:**
- Summer months: June, July, August
- Winter months: January, February, March

**Statistical approach:** Two-sample independent t-test comparing summer vs winter monthly crime counts.

## Findings

### Month-by-Month Summary
| Month     |    Mean |   Median |     Std |   Rank | Season   |
|:----------|--------:|---------:|--------:|-------:|:---------|
| January   | 13436.9 |  13109   | 2158.09 |     10 | Winter   |
| February  | 12210.6 |  11866.5 | 1740.82 |     12 | Winter   |
| March     | 14039.6 |  13636.5 | 2525.59 |      8 | Winter   |
| April     | 14612.4 |  14368.5 | 2599.16 |      7 |          |
| May       | 15623.6 |  15881.5 | 2309.09 |      3 |          |
| June      | 15543.2 |  15475   | 2349.48 |      4 | Summer   |
| July      | 15895   |  16133   | 2563.17 |      2 | Summer   |
| August    | 15973.5 |  15933.5 | 2602.02 |      1 | Summer   |
| September | 14981.6 |  14721   | 1903.99 |      6 |          |
| October   | 15251.5 |  14574   | 1874.56 |      5 |          |
| November  | 13656.5 |  13099.5 | 1912.55 |      9 |          |
| December  | 13216   |  12745   | 1856.87 |     11 |          |

### Statistical Test
- t-statistic: 5.9522
- p-value: 0.000000

### Visualizations
- Box plot: seasonality_boxplot_v1.0.png
- Monthly trend: monthly_trend_v1.0.png

## Limitations
1. Seasonal definitions are arbitrary (different month groupings may yield different results).
2. Analysis assumes consistent reporting across all months and years.
3. Does not control for day-of-week effects within months.
4. Temperature and weather data not incorporated for causal analysis.
