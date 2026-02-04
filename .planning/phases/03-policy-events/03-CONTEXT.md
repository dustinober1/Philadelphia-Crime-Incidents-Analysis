# Phase 3: Policy Deep Dives & Event Impacts - Context

**Gathered:** 2026-02-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Validate specific policy narratives (retail theft trends, vehicle crime corridors) and measure event-day impacts on crime to inform evidence-based policy decisions.

Requirements covered: POLICY-01 (retail theft), POLICY-02 (vehicle crimes), POLICY-03 (crime composition), HYP-EVENTS (event impacts)

</domain>

<decisions>
## Implementation Decisions

### Retail Theft Analysis (POLICY-01)
- Focus on "Thefts" category (UCR 600) for 5-year trend (2019-2024)
- Compare to pre-pandemic baseline (2018-2019 average)
- Verdict: "supported" if >25% increase from baseline, "not supported" otherwise
- Include month-by-month breakdown to identify specific periods of increase

### Vehicle Crimes Analysis (POLICY-02)
- Include "Theft from Vehicle" and "Motor Vehicle Theft"
- Overlay with major transit/highway corridors:
  - Highways: I-76, I-95, I-676, US-1
  - SEPTA lines: Market-Frankford, Broad Street Line
- Buffer distance: 500m (approximately 5 city blocks)
- Output: % of incidents within corridor buffers

### Crime Composition (POLICY-03)
- Calculate violent/total ratio using UCR-based classification
- Violent = Homicide (100), Rape (200), Robbery (300), Aggravated Assault (400)
- Create stacked area chart showing category proportions by year
- Interpret trends in context of overall crime volume changes

### Event Impact Analysis (HYP-EVENTS)
- Event categories:
  - Sports: Eagles, Phillies, 76ers, Flyers home games
  - Holidays: New Year's, 4th of July, Thanksgiving, Labor Day, Memorial Day
- Control days: Same day-of-week in non-event weeks
- Test: Difference-in-means with confidence intervals
- Output: Impact estimates by event type and crime category

### Claude's Discretion
- Corridor data sources (OpenStreetMap, SEPTA API, manual GeoJSON)
- Sports schedule acquisition method
- Statistical test methodology for event impacts
- Visualization styles and color schemes

</decisions>

<specifics>
## Specific Ideas

- For retail theft, consider sub-annual patterns to identify if increases are concentrated in specific months (e.g., holiday shopping season)
- For vehicle crimes, consider time-of-day patterns along corridors
- For event impacts, consider spillover to adjacent days (day before/after)

</specifics>

<deferred>
## Deferred Ideas

None — analysis scope defined by requirements

</deferred>

---

*Phase: 03-policy-events*
*Context gathered: 2026-02-03*
