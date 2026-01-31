# Phase 3: Advanced Temporal Analysis - Context

**Gathered:** 2026-01-31
**Status:** Ready for planning

## Phase Boundary

Analysis modules and report for granular temporal patterns—holiday effects, individual crime types, and shift-by-shift patterns—all with statistical rigor from Phase 1. This phase produces ANALYSIS CODE and a MARKDOWN REPORT, not a visual dashboard (that's Phase 4).

## Implementation Decisions

### Holiday Effects Scope
- **Holidays included**: All federal observances (15+ holidays: New Year's, MLK Day, Presidents Day, Memorial Day, Juneteenth, Independence Day, Labor Day, Columbus Day, Veterans Day, Thanksgiving, Christmas, plus others as designated)
- **Window definition**: 3 days before through 3 days after (7-day "holiday week" centered on holiday)
- **Baseline comparison**: Surrounding weeks (2 weeks before and 2 weeks after) to control for seasonality
- **Moving holidays**: Both approaches
  - Holiday-based: Aggregate all instances (e.g., all Thanksgivings) for overall patterns
  - Date-based: Treat each year's occurrence separately for year-specific effects

### Crime Type Analysis Depth
- **Scope**: The 5 required crimes (homicide, burglary, theft, vehicle theft, aggravated assault) plus any additional crimes with sufficient data for statistical analysis
- **Analysis depth per crime**: Full profile
  - Temporal: Trends, seasonality, day-of-week, hour-of-day patterns
  - Spatial: Distribution and hotspots
  - Victim demographics (if available in data)
  - Clearance rates (if available in data)
- **Sample size handling**: Adaptive methods
  - Small samples (n < 30): Use exact tests (Fisher's exact)
  - Large samples (n >= 30): Use asymptotic tests (chi-square, t-tests)
  - Document limitations for rare crimes in report

### Shift Analysis Approach
- **Weekend handling**: Same treatment as weekdays (let patterns emerge from data rather than forcing a separation)
- **Crime-by-shift**: Full breakdown—shift × crime type matrix showing every crime's distribution across the 4 shifts
- **Shift definitions** (from requirements):
  - Morning: 6AM–12PM
  - Afternoon: 12PM–6PM
  - Evening: 6PM–12AM
  - Late Night: 12AM–6AM
- **Statistical comparisons**: ANOVA omnibus test for shift differences, followed by post-hoc pairwise comparisons with FDR correction

### Report Structure
- **Executive summary**: Yes, at the front with 5-10 key actionable findings
- **Statistical presentation**: Tiered approach
  - Key findings: Inline text with significance markers
  - Detailed statistics: Collapsible sections or appendix with full p-values, effect sizes, confidence intervals
- **Visualization mix**: Balanced combination
  - Time series with confidence intervals (trends)
  - Heatmaps (day × hour, month × crime, shift × crime)
  - Bar charts (comparisons)
  - Spatial maps (where relevant for crime type analysis)

### Claude's Discretion

The following areas are delegated to Claude's discretion during planning and implementation:

**Holiday Effects:**
- Crime type detail level: Which specific crimes get analyzed for holiday-specific patterns (e.g., DUI on New Year's)
- Threshold for "significant holiday effect" (effect size cutoff)

**Crime Type Analysis:**
- Which additional crimes beyond the 5 required have sufficient data for analysis
- Report organization: By analysis type, temporal scale, or findings-led
- Temporal scope for shift analysis: Full dataset aggregate, era comparison, or trend analysis

**Technical Implementation:**
- Exact statistical tests for each comparison (within the categories specified above)
- Visualization styling (colors, fonts, layouts) matching existing report patterns
- Module structure: How to organize functions across `03-01`, `03-02`, `03-03`, `03-04`

## Specific Ideas

None provided — open to standard analytical approaches.

## Deferred Ideas

None — discussion stayed within phase scope.

---

*Phase: 03-advanced-temporal-analysis*
*Context gathered: 2026-01-31*
