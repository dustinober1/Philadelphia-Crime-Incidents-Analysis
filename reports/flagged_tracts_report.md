# Flagged Census Tracts Report

## Summary

- Total census tracts: 408
- Tracts with reliable population (>= 100): 389
- Tracts flagged as unreliable: 19

## Methodology

Crime rates are calculated per 100,000 residents (FBI UCR convention).
Tracts with population below 100 are flagged as unreliable because:
- Small population denominators produce unstable rates
- May represent non-residential areas (parks, industrial zones)
- Statistical inference unreliable with small populations

## Flagged Tracts (population < 100)

| GEOID | Population | Total Crimes | Note |
|-------|------------|--------------|------|
| 42101036901 | 0 | 2236 | Zero pop |
| 42101980001 | 0 | 6051 | Zero pop |
| 42101980002 | 50 | 6248 | Low pop (50) |
| 42101980003 | 0 | 3391 | Zero pop |
| 42101980100 | 45 | 3110 | Low pop (45) |
| 42101980300 | 0 | 8732 | Zero pop |
| 42101980400 | 0 | 4226 | Zero pop |
| 42101980500 | 0 | 1813 | Zero pop |
| 42101980600 | 0 | 5594 | Zero pop |
| 42101980701 | 0 | 1264 | Zero pop |
| 42101980702 | 0 | 12213 | Zero pop |
| 42101980800 | 0 | 1955 | Zero pop |
| 42101980901 | 0 | 14607 | Zero pop |
| 42101980902 | 0 | 18 | Zero pop |
| 42101980903 | 0 | 261 | Zero pop |
| 42101980904 | 0 | 217 | Zero pop |
| 42101980905 | 0 | 30 | Zero pop |
| 42101980906 | 0 | 562 | Zero pop |
| 42101989200 | 0 | 442 | Zero pop |

## Recommendation

Exclude flagged tracts from rate-based analyses. Use raw counts instead for these tracts.
For socioeconomic hypothesis testing, focus on the 389 reliable tracts.

---
*Generated: 2026-02-02T19:54:15.460974*
