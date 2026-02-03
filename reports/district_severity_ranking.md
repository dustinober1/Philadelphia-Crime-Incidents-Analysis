# District Severity Ranking

*Analysis period: 2006-2026*

## Scoring Methodology

Composite score based on four weighted factors:
- **Crime count** (weight: 0.25): Total incidents - measures resource demand
- **Violent crime ratio** (weight: 0.3): Percentage of violent crimes - measures severity
- **YoY trend** (weight: 0.2): Year-over-year change (2024 to 2025) - measures momentum
- **Per-capita rate** (weight: 0.25): Crimes per 100,000 residents - population-normalized

**Notes:**
- Per-capita rate uses FBI UCR convention (crimes per 100,000 residents)
- District population aggregated from census tract data via centroid-based spatial join
- Total population: 1,577,664 across 21 districts
- Only 21 geographic districts scored (excludes administrative codes)

## Ranking

|   Rank |   District |   Severity Score |   Total Crimes |   Violent % |   YoY Change % |   Rate per 100K |   Population |
|-------:|-----------:|-----------------:|---------------:|------------:|---------------:|----------------:|-------------:|
|      1 |         24 |             81.6 |         249408 |         9.6 |            9.4 |          387304 |        64396 |
|      2 |         22 |             79.6 |         218812 |        11.9 |           -3.3 |          334003 |        65512 |
|      3 |         25 |             77.8 |         222837 |        12.5 |           -1.3 |          276782 |        80510 |
|      4 |         15 |             72.7 |         277255 |        10.5 |           -6.3 |          201753 |       137423 |
|      5 |         12 |             71.4 |         199793 |        10.7 |           -9.7 |          288052 |        69360 |
|      6 |         39 |             70.1 |         166880 |        11.6 |          -15.5 |          291947 |        57161 |
|      7 |         35 |             68.7 |         204706 |        11.9 |           -4.9 |          187859 |       108968 |
|      8 |         19 |             67.5 |         222868 |         9.2 |           -7.6 |          247222 |        90149 |
|      9 |         18 |             65.2 |         173208 |        10.4 |           -3.4 |          230520 |        75138 |
|     10 |         16 |             62.9 |         118345 |        10   |           -0.2 |          282993 |        41819 |
|     11 |         26 |             61.5 |         138266 |         9   |            3   |          266280 |        51925 |
|     12 |         14 |             59.7 |         193247 |         9.4 |           -9.6 |          165854 |       116516 |
|     13 |         17 |             58.8 |         108917 |         8.9 |           14.9 |          249655 |        43627 |
|     14 |          2 |             55.9 |         179128 |         8.7 |           -6   |          147596 |       121364 |
|     15 |          3 |             51.4 |         141970 |         7.6 |           -3.9 |          166274 |        85383 |
|     16 |          1 |             49.2 |          71708 |         8.8 |           -4.1 |          187212 |        38303 |
|     17 |          9 |             48.8 |         154574 |         6   |            6.7 |          154081 |       100320 |
|     18 |          8 |             43   |         117026 |         6.4 |           -5.9 |          121293 |        96482 |
|     19 |          7 |             33.1 |          71472 |         5.3 |          -12.3 |           79396 |        90020 |
|     20 |          5 |             32.6 |          50843 |         4.7 |           -9.9 |          117453 |        43288 |
|     21 |         77 |             19   |          14345 |         0.9 |          -28   |             nan |            0 |

## Interpretation

- **High severity (70+):** Priority districts for resource allocation
- **Medium severity (40-70):** Standard patrol coverage
- **Low severity (<40):** Baseline monitoring
