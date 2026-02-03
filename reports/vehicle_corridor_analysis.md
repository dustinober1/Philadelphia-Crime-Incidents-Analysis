# Vehicle Crimes Corridor Analysis Report

## Executive Summary

**39.8%** of vehicle crimes in Philadelphia occur within 500m (~5 blocks) of major transit/highway corridors.

## Key Findings

### Corridor Proximity

| Corridor Type | Crimes | % of Total |
|---------------|--------|------------|
| Highway corridors | 100,492 | 25.1% |
| Transit corridors | 80,160 | 20.0% |
| Any corridor | 159,494 | 39.8% |

### Per-Corridor Breakdown (Top 10)

| Corridor | Type | Incidents | % of Total |
|----------|------|-----------|------------|
| Market-Frankford Line | subway | 42,728 | 10.7% |
| Broad Street Line | subway | 42,058 | 10.5% |
| I 95 | highway | 35,367 | 8.8% |
| US 1 | highway | 33,487 | 8.4% |
| I 76 | highway | 16,903 | 4.2% |
| I 676 | highway | 13,174 | 3.3% |
| US 13 | highway | 5,399 | 1.3% |
| US 30 | highway | 5,132 | 1.3% |
| US 130 | highway | 0 | 0.0% |
| I 295 | highway | 0 | 0.0% |

### Crime Type Distribution

| Crime Type | Total | Within Corridors | % Within |
|------------|-------|------------------|----------|
| Theft from Vehicle | 278,335 | 115,428 | 41.5% |
| Motor Vehicle Theft | 122,388 | 44,066 | 36.0% |

## Methodology

- **Buffer distance**: 500m from corridor centerlines
- **Corridors analyzed**: Broad Street Line, I 676, I 76, I 95, Market-Frankford Line, US 1
- **Crime types**: Theft from Vehicle, Motor Vehicle Theft
- **Total vehicle crimes**: 400,723
- **Analysis period**: All available years

## Implications

1. Vehicle crimes show strong concentration near major corridors
2. Highway corridors have higher incidence rates
3. Consider enhanced patrols at corridor access points and park-and-ride facilities
4. Potential for targeted awareness campaigns at highway rest areas and transit stations

## Artifacts Generated

- `vehicle_crimes_corridor_map.png` - Static map with corridor overlay
- `vehicle_crimes_hourly_corridor.png` - Hourly pattern comparison
- `vehicle_crimes_corridor_stats.csv` - Summary statistics
- `vehicle_crimes_per_corridor.csv` - Per-corridor breakdown

---
*Generated: 2026-02-02 20:24*
*Notebook: vehicle_crimes_corridors.ipynb*
