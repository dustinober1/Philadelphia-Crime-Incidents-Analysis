---
phase: 03-performance-quality
plan: "05"
subsystem: ui
tags: [nextjs, react, typescript, data-storytelling, narratives, swr, mapbox]

requires:
  - phase: 03-performance-quality
    provides: NarrativeCard/InsightBox components + generateNarrative() utilities (03-04)
  - phase: 03-performance-quality
    provides: URL-synced AdvancedFilters + filtered trend/map pages (03-03)
provides:
  - Trends page year-over-year narratives derived from filtered annual series
  - Policy page insight box with context-aware, data-derived messages
  - Map page spatial insight box and hotspot concentration narrative derived from GeoJSON layer properties
affects: [performance-quality, ui, trends, policy, map, storytelling]

tech-stack:
  added: []
  patterns:
    - Derive narratives/insights from current page state via useMemo so they update with filters/data
    - Prefer InsightBox for short context messages and NarrativeCard for comparison narratives

key-files:
  created: []
  modified:
    - web/src/app/trends/page.tsx
    - web/src/app/policy/page.tsx
    - web/src/app/map/page.tsx

key-decisions:
  - "Compute trends narratives from latest vs previous year in the filtered annual series (clear YoY framing)."
  - "Map narrative/insights read from existing GeoJSON properties (severity_score, incident_count) instead of introducing new endpoints."

patterns-established:
  - "Page narrative pattern: memoize computed insights/narratives from loaded + filtered series, render below primary visualization."

metrics:
  duration: "20m 12s"
  started: "2026-02-16T01:46:48Z"
  completed: "2026-02-16T02:07:00Z"
---

# Phase 3 Plan 05: Narrative integration across Trends/Policy/Map — Summary

**Data-driven NarrativeCard + InsightBox sections are now integrated across /trends, /policy, and /map, updating dynamically as filters and data change.**

## Performance

- **Duration:** 20m 12s
- **Started:** 2026-02-16T01:46:48Z
- **Completed:** 2026-02-16T02:07:00Z
- **Tasks:** 3 planned tasks (+1 blocking fix)
- **Files modified:** 3

## Accomplishments

- Added **year-over-year narrative cards** to the Trends page annual chart using `generateNarrative()` against the filtered annual series.
- Added **policy insight messaging** on the Policy page to help interpret retail/vehicle trend direction and composition context.
- Added **spatial distribution insights** on the Map page using GeoJSON layer properties (district severity, hotspots, corridors) plus a hotspot concentration narrative.

## Task Commits

Each task was committed atomically:

1. **Task 1: Integrate narratives into Trends page** — `8a8e6d2` (feat)
2. **Task 2: Integrate insights into Policy page** — `4161b89` (feat)
3. **Task 3: Integrate spatial insights into Map page** — `2a85891` (feat)

Auto-fix commit:

- `c2a3f06` (fix) — strict TypeScript typing fixes for the new Map insights helpers

## Files Created/Modified

- `web/src/app/trends/page.tsx` — Adds NarrativeCard + InsightBox sections under Annual trends, derived from filtered annual series.
- `web/src/app/policy/page.tsx` — Adds a Policy Insights InsightBox above charts with context-aware messaging.
- `web/src/app/map/page.tsx` — Adds Spatial Insights InsightBox + hotspot concentration NarrativeCard derived from GeoJSON properties.

## Manual Verification (Checkpoint)

User approved the checkpoint after confirming:

- Narrative cards appear below the annual trends chart and update when filters change.
- Policy insights render above charts.
- Map spatial insights render and hotspot narrative appears when hotspot data supports it.

## Decisions Made

- Compute trend narratives as a **latest-vs-previous year** comparison within the filtered annual series for clear year-over-year framing.
- Use **existing spatial GeoJSON properties** to derive map insights (severity_score, incident_count, feature counts) without adding new backend endpoints.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fix strict TypeScript errors introduced by map insight helpers**
- **Found during:** overall verification (`npm run typecheck`)
- **Issue:** Several callback parameters inferred as `any` in `web/src/app/map/page.tsx`
- **Fix:** Added explicit `GeoJson` feature typing for map/filter/reduce callbacks
- **Files modified:** `web/src/app/map/page.tsx`
- **Verification:** `cd web && npm run typecheck` (passes)
- **Committed in:** `c2a3f06`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary to keep strict TypeScript checks green; no scope creep.

## Issues Encountered

- Next.js static export build emits pre-existing Recharts warnings about container width/height during prerender. Build succeeds.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Narrative/insight presentation is now consistent across key pages and reacts to filter state.
- If deeper story-specific narratives are desired (e.g., monthly seasonality explanations, event impact narratives), extend `web/src/lib/narratives.ts` with additional generators.

---
*Phase: 03-performance-quality*
*Completed: 2026-02-16*
