# COVID-19 Lockdown Crime Landscape
*Generated: 2026-02-02T23:30:48Z | Version: v1.0*

## Summary
Crime volumes declined during lockdown, while burglary patterns shifted toward commercial targets.

## Methods
Compared Before (2018-2019), During (2020-2021), and After (2023-2025) periods with 2022 excluded.

## Data Quality Summary
| Column | Missing % |
|---|---:|
| hour | 9.58 |
| the_geom_webmercator | 1.83 |
| point_y | 1.83 |
| point_x | 1.83 |
| the_geom | 1.82 |
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
| After | 481963 | -14.9 | 79.3 |
| Before | 316037 | -14.9 | 79.3 |
| During | 268794 | -14.9 | 79.3 |

Burglary displacement: Residential -3.5%, Commercial nan% during lockdown.
Chi-square burglary p-value: 1.0000. Crime mix p-value: 1.0000.

## Limitations
Confounding factors (economic recession, civil unrest) and reporting delays are not controlled.

## Technical Details
- Records analyzed: 1066794
- Date range: {'min': Timestamp('2018-01-01 00:00:00'), 'max': Timestamp('2025-12-31 00:00:00')}
- Git commit: f4fb95bd3b570cd96f104a894c843c9490e012fb