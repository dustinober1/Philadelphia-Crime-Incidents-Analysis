# PITFALLS.md

Project Research — Common pitfalls and how to avoid them

1) Timestamp and timezone mismatches
- Warning signs: inconsistent daily/hourly aggregates, unexpected spikes at midnight
- Prevention: unify timestamps to UTC or local time at ingest; include reproducibility cell that prints timezone info
- Phase to address: Data QA / CHIEF analyses

2) Inaccurate geocoding or missing lat/lon
- Warning signs: many records with null geometry or points falling outside expected city bounds
- Prevention: validate coordinates against city bounding box; impute or drop only after analysis of missingness
- Phase to address: PATROL / HYP-SOCIO

3) Overfitting in predictive models (FORECAST-02)
- Warning signs: high train accuracy but poor out-of-time performance; feature importances that don't generalize
- Prevention: use time-based cross-validation, holdout recent months, prefer simpler models first
- Phase to address: FORECAST

4) Misleading choropleths due to population differences
- Warning signs: high crime counts in dense areas that disappear when normalized by population
- Prevention: always present both raw counts and per-capita rates (per 1,000 residents)
- Phase to address: HYP-SOCIO / POLICY

5) Weather join pitfalls (HYP-HEAT)
- Warning signs: many crime events without matching hourly weather rows; odd correlations at extreme temps
- Prevention: round crime timestamps to nearest hour, document join strategy, impute missing hourly temps carefully
- Phase to address: HYP-HEAT

6) Biased severity weighting
- Warning signs: one-off high-severity incidents dominate district scores
- Prevention: cap influence of single incidents (e.g., winsorize), or display both mean and median severity
- Phase to address: PATROL-03
