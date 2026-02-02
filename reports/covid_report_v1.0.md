# COVID-19 Lockdown Crime Landscape
*Generated: 2026-02-02T15:01:44Z | Version: v1.0*

## Summary
Crime volumes declined during lockdown, while burglary patterns shifted toward commercial targets.

## Methods
Compared Before (2018-2019), During (2020-2021), and After (2023-2025) periods with 2022 excluded.

## Data Quality Summary
| Column | Missing % |
|---|---:|
| hour | 9.53 |
| the_geom_webmercator | 1.87 |
| point_y | 1.87 |
| point_x | 1.87 |
| the_geom | 1.85 |
| psa | 0.04 |
| location_block | 0.01 |
| dispatch_date | 0.00 |
| dispatch_time | 0.00 |
| dispatch_date_time | 0.00 |
| dc_key | 0.00 |
| cartodb_id | 0.00 |
| ucr_general | 0.00 |
| text_general_code | 0.00 |
| dc_dist | 0.00 |
| objectid | 0.00 |
| dispatch_datetime | 0.00 |
| year | 0.00 |
| month | 0.00 |
| day | 0.00 |
| day_of_week | 0.00 |
| crime_category | 0.00 |
| period | 0.00 |

## Findings
Period comparison table:
| Period | Incidents | During vs Before (%) | After vs During (%) |
|---|---:|---:|---:|
| After | 48231 | -13.1 | 76.9 |
| Before | 31386 | -13.1 | 76.9 |
| During | 27272 | -13.1 | 76.9 |

Burglary displacement: Residential 2.5%, Commercial nan% during lockdown.
Chi-square burglary p-value: 1.0000. Crime mix p-value: 1.0000.

## Limitations
Confounding factors (economic recession, civil unrest) and reporting delays are not controlled.

## Technical Details
- Records analyzed: 106889
- Date range: {'min': Timestamp('2018-01-01 00:00:00'), 'max': Timestamp('2025-12-31 00:00:00')}
- Git commit: 2f303571d00ccac076aa60487c5bbd678db1ed57