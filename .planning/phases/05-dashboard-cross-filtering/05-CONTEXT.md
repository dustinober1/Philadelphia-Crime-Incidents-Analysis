# Phase 5: Dashboard Cross-Filtering - Context

**Gathered:** 2026-02-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Dashboard views are linked with cross-filtering so selections in one component update all related visualizations. This phase implements state management, filter interactions, and visual feedback across all dashboard views without adding new analysis capabilities.
</domain>

<decisions>
## Implementation Decisions

### Cross-filter directionality

**Architecture pattern:** Hybrid - sidebar filters drive all views, views can suggest filters
- Sidebar filters are the primary source of truth for all views
- Views can trigger cross-filters on other views (view-to-view filtering enabled)
- Sidebar checkboxes remain completely independent from view selections
- Two parallel filter systems: sidebar (explicit) and view-to-view (exploratory)

**Visual treatment of filtered data:** Dim/highlight approach
- Filtered-out elements are dimmed with 30% opacity but remain visible
- Filtered elements show at full color/opacity
- Users see context of what's filtered out, not just what remains
- Complete plot replacement using st.empty() for filtered views

**Example behavior:** Clicking District 22 on the spatial map dims other districts in temporal view and updates correlation charts to show only District 22 data. Sidebar district checkboxes remain unchanged.

### Update trigger timing

**Sidebar filters:** Explicit apply button required
- Users change sidebar filters freely without triggering recomputations
- "Apply Filters" button enables when filters change, disables when all applied
- All sidebar filter changes applied at once with single button click
- Prevents unnecessary recomputations during multi-step filter configuration

**View-to-view cross-filters:** Instant updates
- Clicking/selecting in a view immediately updates all other views
- No apply button needed for view-triggered cross-filters
- Exploratory interaction pattern: click to see, click again to deselect
- Responsive but lightweight (views already cached from sidebar filters)

**Hybrid approach rationale:** Sidebar filters are deliberate selections (user knows what they want) while view interactions are exploratory (user is discovering patterns).

### State persistence approach

**Single source of truth:** Split architecture
- Sidebar filters: st.session_state primary, URL sync on apply
- View-to-view cross-filters: URL encoded for shareability

**URL encoding:** Unified namespace
- Sidebar and view params share same URL query string
- Example: `?districts=22&years=2020,2021,2022&active_view=spatial&active_district=22`
- Active view and active selection encoded together with sidebar filters
- Fully shareable URLs capture both sidebar and view state

**Session state organization:**
- Sidebar state: `filter_time`, `filter_geo`, `filter_crime` (syncs to URL)
- View state: `active_view`, `active_selection` (syncs to URL, ephemeral)
- Apply button state: `pending_filters` (boolean, UI-only)

**State flow:**
1. Page load: Read URL params → initialize session state
2. Sidebar change: Update session state, enable apply button (no URL update)
3. Apply clicked: Sync session state to URL, trigger filter recomputation
4. View interaction: Update URL + session state instantly, trigger cross-filter

### Visual feedback patterns

**Active filter indicators:** Per-filter highlighting in sidebar
- Visual indicator (dot, icon, or border) next to each changed filter
- Clear which filters have unapplied changes
- Apply button disabled when no pending changes
- Users see exactly what will change before clicking apply

**Dimmed data visual style:** Opacity-based highlighting
- Filtered-out elements: 30% opacity (alpha=0.3)
- Filtered elements: Full opacity (alpha=1.0)
- Applies to all plot types: bars, points, lines, map markers
- Color palette unchanged, only opacity modified

**No filter summary banner:** Minimalist approach
- Sidebar highlighting provides sufficient feedback
- No separate banner or badges needed
- Reduces visual clutter
- Users can see active state by looking at sidebar

**Feedback hierarchy:**
1. Sidebar: Dot indicator next to changed filters
2. Apply button: Enabled/disabled state shows pending changes
3. Views: Dimmed elements show what's filtered out
4. URL: Query params encode full state for sharing

### Claude's Discretion

**UI implementation details:**
- Exact indicator style (dot vs icon vs border) - choose what works with Streamlit theming
- Apply button placement and styling - follow dashboard design patterns
- Opacity value for dimmed elements - 30% is starting point, adjust for readability

**State management implementation:**
- Exact session state key naming - follow existing dashboard patterns
- URL parameter encoding format - use query params or hash as appropriate
- Debouncing strategy - implement if needed for performance

**Performance optimization:**
- Caching strategy for cross-filtered views - extend existing cache.py patterns
- Incremental filter updates vs full recomputation - choose based on profiling
- Lazy loading of correlation content on cross-filter - defer expensive computations

</decisions>

<specifics>
## Specific Ideas

**Hybrid architecture rationale:** "Sidebar for when I know what I want to filter, view clicks for exploring patterns as I discover them."

**Shareable URLs:** "If I find an interesting pattern in District 22 during 2020, I should be able to share that exact view with someone else via URL."

**Visual feedback preference:** "Show me what's filtered out with dimming - I want to see the context, not just the filtered data. Helps me understand what I'm excluding."

**Apply button behavior:** "Don't recompute on every slider movement. Let me set up my filters, then apply once. But view interactions should be instant - those are exploratory."

</specifics>

<deferred>
## Deferred Ideas

- Real-time streaming data updates - out of scope for static dataset analysis
- Machine learning-based filter suggestions - future enhancement
- Custom filter combinations saved as presets - could be separate phase
- Collaborative annotations on filtered views - belongs in sharing/collaboration phase

</deferred>

---

*Phase: 05-dashboard-cross-filtering*
*Context gathered: 2026-02-01*
