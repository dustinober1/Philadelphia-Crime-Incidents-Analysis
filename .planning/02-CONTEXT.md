# Phase 2: Data Presentation - Implementation Context

**Phase:** 2 of 3 (Data Presentation)
**Status:** Ready for Research
**Created:** February 15, 2026

## Overview

Phase 2 implements web-based data visualization and presentation for crime incident analysis. This includes interactive charts, maps, tables, data downloads, and transparency documentation. The API endpoints already exist; this phase focuses on frontend presentation and user interaction.

## Decisions by Area

### 1. Chart Visualization Strategy

**Time Granularity:**
- Default view: **Monthly** (smoothest, best for long-term patterns)
- Users can adjust granularity (daily/weekly/monthly) via controls

**Tooltip Content:**
- Basic value (count/rate)
- Date/period label
- Percent change from previous period
- Comparison to historical average

**Series Display:**
- **Multiple series simultaneously** - overlay 2-3 related crime types with different colors
- Good for comparative analysis (e.g., violent vs. property crime trends)

**Empty State Handling:**
- Show empty chart area with message explaining why no data is available
- No automatic retry or fallback to cached data

### 2. Interactive Map Experience

**Initial Map View:**
- **Zoomed out to show all Philadelphia** (all districts visible)
- Provides city-wide context on load

**Filter Interaction:**
- **Real-time updates** - map updates instantly as users adjust filters
- Filter controls: date range, crime type checkboxes, district selector

**Click Popup Information:**
- Label and count
- Detailed statistics (rate, ranking, comparison)
- Trend indicators (up/down arrows, percent change)
- Link to related data (charts, tables, detailed view)

**Performance Strategy:**
- **Clustering** - group nearby points into clusters with count badges
- Clicking a cluster zooms in to show individual points
- Balances performance with detail exploration

### 3. Tabular Data Presentation

**Pagination:**
- **10-25 rows per page** (default)
- Prioritizes readability over information density

**Default Sort Order:**
- **Date (newest first)**
- Shows most recent incidents immediately on load

**Search/Filtering:**
- **Both combined** - global search bar + per-column filters
- Global search: searches all columns
- Per-column filters: date range, crime type, district (common filters)

**Inline Actions per Row:**
- **View on map** - highlights this incident on map view
- **View details** - opens modal with full incident info and stats
- **Export row** - download single record as JSON/CSV

### 4. Data Download & Transparency

**Download Scope:**
- **Full dataset only** - complete dataset regardless of current filters
- All time periods, all crime types, all districts

**Download Placement:**
- **Dedicated "Data & Transparency" page**
- Centralized location for all downloads, methodology, and citations
- Accessible via navigation and footer

**Metadata in Downloads:**
- **Basic metadata** included:
  - Export timestamp
  - Data version
  - Processing notes
  - Helps with reproducibility

**Citation Detail Level:**
- **Source names and URLs only**
- Philadelphia Police Department
- Census Bureau
- Minimal, factual attribution
- Detailed methodology exists elsewhere on site

## Deferred Ideas

*(Capture ideas that emerged during discussion but are out of scope for this phase)*

None identified during discussion.

## Technical Constraints

- **Chart library:** Recharts (already installed in web/)
- **Map library:** Mapbox GL + react-map-gl (already installed)
- **Data fetching:** SWR (already installed)
- **API endpoints:** All endpoints exist in api/ (no new backend work)
- **Static export:** Next.js static export (no server-side rendering)

## Success Criteria Mapping

Decisions directly support Phase 2 success criteria:

✅ **User can view line, bar, and area charts**
- Multiple series support enables comparative views
- Monthly default provides clear trend visualization

✅ **User can browse and sort tabular data**
- Combined search/filtering enables flexible exploration
- Inline actions connect table to other views (map, details)

✅ **User can explore spatial patterns**
- Clustering enables performance with large datasets
- Rich popups provide context and navigation

✅ **User can view multiple visualization types**
- Charts, maps, tables all implemented with consistent interaction patterns

✅ **User can download crime data**
- Full dataset export enables external analysis
- Dedicated transparency page centralizes access

✅ **User can view citations and transparency**
- Clear source attribution
- Dedicated methodology page

## Next Steps

1. **Research Phase** (`gsd-research-phase 2`)
   - Investigate Recharts patterns for time series with multiple series
   - Explore Mapbox clustering implementations with react-map-gl
   - Research table component patterns (pagination, sorting, filtering)
   - Study static export patterns for Next.js with data downloads

2. **Planning Phase** (`gsd-plan-phase 2`)
   - Create detailed implementation plans for DATA-01 through DATA-06
   - Define component architecture (ChartViewer, MapExplorer, DataTable, etc.)
   - Plan state management for filters, selections, and cross-view navigation

3. **Execution** (`gsd-execute-phase 2`)
   - Implement visualization components
   - Wire up API integration
   - Test interactions and edge cases
   - Verify success criteria
