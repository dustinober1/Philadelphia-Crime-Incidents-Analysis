# Phase 2: Spatial & Socioeconomic Analysis - Context

**Gathered:** 2026-02-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Identify where crimes concentrate (hotspots), when robberies peak (hour x weekday), and how crime rates vary when normalized by population at the Census tract level. Outputs include district severity rankings and patrol timing recommendations.

Requirements covered: PATROL-01 (hotspots), PATROL-02 (robbery heatmap), PATROL-03 (district severity), HYP-SOCIO (census tract rates)

</domain>

<decisions>
## Implementation Decisions

### Hotspot Visualization
- Output both static PNG (for reports) and interactive HTML map (for exploration)
- Color scheme: Yellow-Orange-Red gradient for intensity
- Visualization method and crime category breakdown: Claude's discretion

### Severity Scoring Method
- Use multi-factor composite score with four factors:
  - Total crime count
  - Violent crime ratio
  - Trend direction (year-over-year)
  - Per-capita rate
- Present as both choropleth map and ranked table with score breakdown
- Factor weights: Claude's discretion

### Population Normalization
- Use per 100,000 residents (matches FBI UCR convention)
- Output includes both crime rates and raw counts for context
- Census tract boundary handling: Claude's discretion
- Low-population tract handling: Claude's discretion

### Robbery Temporal Patterns
- Use 4-hour time bins x 7 weekdays (42 cells)
- Show both city-wide patterns and per-district breakdown if meaningful differences exist
- Combined all robbery types with subtype breakdown available if useful
- Present recommendations as both narrative summary and bullet-point actionable items

### Claude's Discretion
- Hotspot visualization method (kernel density, hex bins, point clusters)
- Whether to show crimes by category (aggregate, separate maps, or filterable)
- Factor weights for severity composite score
- Census tract boundary incident assignment method
- Low-population tract threshold and handling

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches for spatial crime analysis. The user deferred most technical visualization and methodology choices.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-spatial-socioeconomic*
*Context gathered: 2026-02-02*
