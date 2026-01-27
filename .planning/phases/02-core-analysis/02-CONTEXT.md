# Phase 2: Core Analysis - Context

**Gathered:** 2026-01-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Conduct comprehensive statistical analysis of 3.5M Philadelphia crime incidents (2006-2026) — temporal trends, geographic hotspots, offense patterns, cross-factor interactions, and disparities. This phase delivers the analytical foundation for the dashboard and report.

</domain>

<decisions>
## Implementation Decisions

### Statistical Rigor Approach
- **Multiple comparisons:** Bonferroni correction to control family-wise error rate
- **Temporal granularity:** Both monthly and annual trends for comprehensive view
- **Spatial autocorrelation:** Use Moran's I and spatial lag models for formal spatial statistics
- **Confidence intervals:** Claude's discretion on whether to use CIs, p-values, or both

### Claude's Discretion
- Statistical significance framework (user deferred to standard academic practice)
- Specific confidence levels (95% vs other thresholds)
- Exact implementation details of spatial models
- Figure generation strategy (static vs interactive, formats)
- Analysis prioritization if time-constrained
- Validation approach and external sources

</decisions>

<specifics>
## Specific Ideas

- Analysis should align with known Philadelphia patterns (summer peaks, weekday variation)
- Geographic hotspots should be stable across sensitivity tests
- Offense distribution should match expected UCR hierarchy
- All findings must be defensible under peer review

</specifics>

<deferred>
## Deferred Ideas

- Figure generation strategy — deferred to planning
- Analysis prioritization — deferred to planning
- Validation approach — deferred to planning

</deferred>

---

*Phase: 02-core-analysis*
*Context gathered: 2026-01-27*
