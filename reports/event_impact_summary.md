# Event Impact Analysis Report

## Executive Summary

This analysis examines the impact of major events (sports games, holidays, celebrations) on crime patterns in Philadelphia using difference-in-means testing.

**Analysis Period:** 2015-01-01 to 2026-01-20  
**Total Days Analyzed:** 4,037  
**Event Days:** 986  
**Control Days:** 3,051

### Key Finding

**14 of 21 tests** showed statistically significant results (p < 0.05).

## Significant Impacts

The following event-crime combinations showed statistically significant differences:

| Event Type | Crime Metric | % Change | 95% CI | p-value |
|------------|--------------|----------|--------|--------|
| Holiday | Total | -14.1% | [-19.0%, -9.6%] | <0.0001 |
| Holiday | Property | -8.6% | [-16.3%, -0.7%] | 0.0023 |
| Sports | Total | -1.4% | [-3.0%, +0.2%] | 0.0283 |
| Celebration | Total | -9.2% | [-19.9%, +2.2%] | 0.0122 |
| Eagles | Total | -14.4% | [-18.2%, -10.4%] | <0.0001 |
| Eagles | Property | -10.8% | [-18.2%, -3.0%] | 0.0007 |
| Phillies | Total | +5.3% | [+3.0%, +7.5%] | <0.0001 |
| Phillies | Violent | +4.3% | [+1.5%, +6.9%] | 0.0001 |
| Phillies | Property | +4.6% | [+0.6%, +8.4%] | 0.0024 |
| 76Ers | Total | -8.0% | [-11.0%, -4.8%] | <0.0001 |
| 76Ers | Violent | -5.3% | [-9.3%, -1.2%] | 0.0009 |
| 76Ers | Property | -6.5% | [-11.8%, -1.3%] | 0.0021 |
| Flyers | Total | -5.2% | [-8.1%, -2.2%] | <0.0001 |
| Flyers | Violent | -7.3% | [-11.4%, -2.9%] | <0.0001 |

### Largest Crime Increase

**Phillies** events showed a **+5.3%** increase in total crime (p=0.0000).

### Largest Crime Decrease

**Eagles** events showed a **-14.4%** decrease in total crime (p=0.0000).

## Complete Results Summary

### Total Crime by Event Type

| Event Type | Event Days | Event Mean | Control Mean | % Change | p-value | Significant |
|------------|------------|------------|--------------|----------|---------|-------------|
| Holiday | 115 | 369.1 | 429.6 | -14.1% | <0.0001 | Yes |
| Sports | 890 | 423.5 | 429.6 | -1.4% | 0.0283 | Yes |
| Celebration | 22 | 390.2 | 429.6 | -9.2% | 0.0122 | Yes |
| Eagles | 88 | 367.7 | 429.6 | -14.4% | <0.0001 | Yes |
| Phillies | 440 | 452.2 | 429.6 | +5.3% | <0.0001 | Yes |
| 76Ers | 211 | 395.2 | 429.6 | -8.0% | <0.0001 | Yes |
| Flyers | 212 | 407.1 | 429.6 | -5.2% | <0.0001 | Yes |

## Methodology

### Event Types Analyzed

- **Sports**: Home games for Eagles, Phillies, 76ers, and Flyers
- **Holidays**: Major federal holidays (New Year's Day, Memorial Day, July 4th, Labor Day, Thanksgiving)
- **Celebrations**: Special events and festivals

### Statistical Approach

1. **Daily Aggregation**: Crime incidents aggregated to daily counts
2. **Event Tagging**: Days tagged as event or control based on event calendar
3. **Difference-in-Means**: Two-sample t-test comparing event vs non-event days
4. **Confidence Intervals**: Bootstrap 95% CI (1,000 iterations)
5. **Significance Level**: p < 0.05

### Data Sources

- Crime data: Philadelphia Police Department incidents (2006-01-01 to 2026-01-20)
- Event calendar: Generated from team schedules and holiday definitions

## Caveats and Limitations

1. **Correlation vs Causation**: Associations do not imply causal relationships
2. **Confounding Factors**: Weather, concurrent events, and seasonal patterns not controlled
3. **Multiple Testing**: 21 tests increase false positive risk (consider Bonferroni correction: p < 0.0024)
4. **Schedule Approximations**: Sports schedules are estimates and may not perfectly match actual home games
5. **Reporting Bias**: Event days may have different crime reporting patterns

## Visualizations

- `event_impact_chart.png`: Main comparison of event types
- `event_impact_by_category.png`: Breakdown by crime category
- `event_spillover.png`: Day before/after effects for sports events

---
*Generated: 2026-02-02 20:23*  
*Notebook: event_impact_analysis.ipynb*
