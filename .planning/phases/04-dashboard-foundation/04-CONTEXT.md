# Phase 4: Dashboard Foundation - Context

**Gathered:** 2026-01-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Interactive Streamlit dashboard displaying existing analyses with time range, geographic area, and crime type filters. Dashboard provides filtered views of statistical analyses from Phases 1-3 with reusable components for future cross-filtering (Phase 5).

</domain>

<decisions>
## Implementation Decisions

### Layout structure
- Sidebar + Tabs organization: persistent sidebar for filters, tabbed content areas
- Filters are page-specific (grouped by analysis context)
- 5 tabs: Overview/Stats, Temporal Trends, Spatial Maps, Correlations, Advanced Temporal
- Main page: Title → Summary stats → Tabbed content
- Filters change based on active tab (e.g., Temporal shows time+crime filters, Spatial shows geo+crime)

### Data loading strategy
- Lazy load per page: summary stats on startup, full data loaded per-page as needed
- Hybrid approach for analysis results: static reports reuse cached outputs, interactive filters recompute
- Full data everywhere (no sampling for visualizations)
- URL encoding for filter state (shareable links with full filter parameters)
- Trust Streamlit caching to handle 3.5M record performance

### Visualization presentation
- Matplotlib + selective interactivity: keep existing matplotlib plots, add interactive where valuable
- Interactive (Plotly) for: temporal trends, choropleth maps, bar charts
- Static (matplotlib) for: complex heatmaps, statistical plots, niche visualizations
- Existing reports embedded as expandable sections on each tab
- Narrative-then-plots presentation: text summary of findings first, then supporting visualizations

### Filter behavior
- Cascading filters: selections narrow available options (e.g., selecting year narrows month slider)
- Default view: full dataset (2006-2025), no filters applied on initial load
- No-results state: helpful message with suggestions (e.g., "Try expanding date range or changing filters")
- Reset options: global reset button (return to full dataset) + per-filter resets

### Claude's Discretion
- Exact spacing and styling of filter widgets
- Performance optimization details (hash functions for cache keys, aggregation strategies)
- Visual design of metric cards and summary statistics
- Specific Plotly chart types and configurations

</decisions>

<specifics>
## Specific Ideas

- Dashboard should feel like a research tool, not a consumer app — narrative-driven, data-first
- Shareable URLs are important for collaboration and reporting findings
- Hybrid caching approach prioritizes both speed (cached reports) and flexibility (interactive recomputation)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-dashboard-foundation*
*Context gathered: 2026-01-31*
