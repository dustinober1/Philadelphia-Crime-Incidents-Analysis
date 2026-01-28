# Phase 3: Visualization & Reporting - Context

**Gathered:** 2026-01-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Create interactive dashboard and draft academic report from completed Phase 2 analysis. Dashboard enables data exploration and presentation. Report documents methodology, findings, and limitations with full statistical rigor.

</domain>

<decisions>
## Implementation Decisions

### Dashboard Layout & Navigation
- **Structure:** Multi-tab navigation (not single-page or sidebar)
- **Tab Organization:** By analysis type — Overview, Temporal, Geographic, Offense Types, Disparities, Cross-factor
- **Overview Tab:** Summary visualizations (high-level charts: trend over time, top offenses bar chart, city map)
- **Visual Density:** 10+ charts per tab for detailed exploration with multiple angles

### Interactive Features & Filtering
- **Global Filters:** Date range picker + offense type selector + district filter
- **Filter Placement:** Each tab has its own filters (context-specific)
- **Update Behavior:** Apply button (not real-time) — changes apply only when clicked
- **Map Interactions:** Click-to-filter districts, hover for details (name and incident count), zoom and pan navigation

### Report Structure & Content
- **Format:** Markdown with embedded figures (version-control friendly, convertible to multiple formats)
- **Chapter Organization:** As specified in roadmap — Methodology → Data Quality → Temporal → Geographic → Offense → Disparity → Cross-factor → Discussion → Limitations/Conclusion
- **Executive Summary:** Both standalone document AND integrated as first chapter of report
- **Statistical Rigor:** Full details in main text — include p-values, confidence intervals, effect sizes

### Dashboard-Report Integration
- **Visualization Strategy:** Different visualizations for dashboard vs report
  - Dashboard: Interactive exploration with 10+ charts per tab
  - Report: Curated, publication-quality figures with full statistical context
- **Dashboard Purpose:** Balance between exploration and presentation equally
- **Export Capabilities:** PNG/SVG images + CSV data + PDF report generation
- **Cross-references:** Bidirectional links — dashboard links to relevant report sections, report references dashboard as supplementary tool

### Claude's Discretion
- Exact color schemes and visual styling
- Specific chart types for each visualization
- Dashboard performance optimization (sampling, lazy loading)
- Report typography and layout details
- Export implementation details

</decisions>

<specifics>
## Specific Ideas

- Dashboard tabs organized by analysis type (Overview, Temporal, Geographic, Offense Types, Disparities, Cross-factor)
- Each tab should have 10+ charts for comprehensive exploration
- Report follows academic structure with full statistical details in main text
- Executive summary serves dual purpose: standalone for stakeholders, integrated for completeness
- Bidirectional linking between dashboard and report for seamless navigation

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-visualization-reporting*
*Context gathered: 2026-01-28*
