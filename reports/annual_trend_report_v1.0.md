# Annual Crime Trends Analysis
*Generated: 2026-02-02 18:30 | Version: v1.0*

## Summary
Philadelphia crime incidents peaked in 2015 at 176,768 incidents, falling to 160,389 by 2024 (9.3% decline from peak).

## Methods
Annual counts were computed from dispatch timestamps, with incidents classified into Violent, Property, and Other categories using UCR hundred-bands.

## Data Quality Summary
| Column | Missing % |
|---|---:|
| hour | 6.54 |
| the_geom | 1.42 |
| the_geom_webmercator | 1.42 |
| point_y | 1.42 |
| point_x | 1.42 |
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

## Findings
Annual totals show a sustained downward trend from the mid-2010s peak. The linear trend is decreasing at 1,332 incidents per year (p=0.402).

## Limitations
2026 data were excluded because only a partial year is available. Recent months may be affected by reporting delays, and classification changes over time are not captured.

## Technical Details
- Records analyzed: 1562489
- Date range: {'min': Timestamp('2015-01-01 00:00:00'), 'max': Timestamp('2024-12-31 00:00:00')}
- Git commit: f4fb95bd3b570cd96f104a894c843c9490e012fb