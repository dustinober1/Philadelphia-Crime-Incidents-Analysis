# Data Quality Assessment Report
**Generated:** February 01, 2026 at 17:35 UTC
**Dataset:** 3,496,353 crime incidents (29 columns)
**Date Range:** 2006-01-01 to 2026-01-20
**SHA256:** 2a45f7eb1102e7f0...

---

## Overall Data Quality Score
### 97.83/100 - A (Excellent)

### Component Scores
| Dimension | Score | Weight |
|-----------|-------|--------|
| Completeness | 96.39% | 40% |
| Accuracy | 98.39% | 30% |
| Consistency | 100.0% | 15% |
| Validity | 98.39% | 15% |

## Coordinate Coverage Analysis
- **Valid Coordinates:** 3,440,053 (98.39%)
- **Invalid Coordinates:** 56,300 (1.61%)

## Duplicate Records Analysis
- **Total Duplicates:** 0 (0.00%)
- **Clean Records:** 3,496,353

## Missing Data Analysis
### Top 10 Columns with Missing Data
| Column | Missing | Percentage |
|--------|---------|------------|
| coord_issue | 3,440,053 | 98.39% |
| the_geom_webmercator | 55,927 | 1.6% |
| point_x | 55,912 | 1.6% |
| point_y | 55,912 | 1.6% |
| the_geom | 55,810 | 1.6% |
| psa | 1,296 | 0.04% |
| location_block | 187 | 0.01% |

## Recommendations
### Safe Analyses
- Temporal trend analysis (minimal impact from missing coordinates)
- Categorical analysis by crime type (complete data)
- District-level aggregations

### Statistical Validity
All statistical tests use 99% confidence intervals for conservative inference. Missing data patterns have been tested for bias (chi-square tests of independence).

<details>
<summary>Analysis Configuration</summary>

```yaml
# Analysis executed at: 2026-02-01T17:36:04.523581+00:00
# Dataset: 3,496,353 rows, 29 columns
# Confidence Level: 99%
```

</details>
