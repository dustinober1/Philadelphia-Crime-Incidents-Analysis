---
phase: 03-performance-quality
plan: 03
subsystem: ui
tags: [nextjs, react, typescript, swr, filtering, url-state, mapbox]

requires:
  - phase: 03-performance-quality
    provides: Next.js patched upgrade + streaming SSR baseline (03-01)
  - phase: 03-performance-quality
    provides: AdvancedFilters + applyFilters + useFilteredData primitives (03-02)
provides:
  - Trends page filtering with URL-synchronized FilterState and live chart updates
  - Map page district filtering using AdvancedFilters + URL params
  - Filter persistence across /trends ↔ /map navigation via preserved query params
affects: [03-performance-quality, ui, trends, map]

tech-stack:
  added: []
  patterns:
    - URL-driven filter state (initialize from query params, sync via router.replace)
    - Page-level integration of AdvancedFilters + useFilteredData for reactive charts

key-files:
  created: []
  modified:
    - web/src/lib/api.ts
    - web/src/app/trends/page.tsx
    - web/src/app/map/page.tsx
    - web/src/components/Navbar.tsx
    - web/src/lib/filters.ts

key-decisions:
  - "Map filtering implemented by filtering district GeoJSON features; /api/v1/spatial/incidents does not exist yet in the backend."

patterns-established:
  - "Preserve filter query params for /trends and /map links to keep filters sticky across navigation"

metrics:
  duration: 9m 18s
  started: 2026-02-16T01:33:44Z
  completed: 2026-02-16T01:43:02Z
---

# Phase 03 Plan 03: Trends + Map filter integration — Summary

**AdvancedFilters is now wired into /trends and /map with URL-synchronized FilterState and district-based map filtering.**

## Performance

- **Duration:** 9m 18s
- **Started:** 2026-02-16T01:33:44Z
- **Completed:** 2026-02-16T01:43:02Z
- **Tasks:** 3 planned tasks (+2 auto-fixes)
- **Files modified:** 5

## Accomplishments

- Integrated `AdvancedFilters` into the Trends page and switched annual/monthly data to `useFilteredData()` so charts react immediately to filter changes.
- Integrated `AdvancedFilters` into the Map page and filtered **district GeoJSON features** when districts are selected.
- Implemented filter persistence across navigation by preserving filter query params when navigating between `/trends` and `/map`.

## Task Commits

Each planned task was committed atomically:

1. **Task 1: Add spatial data endpoints to API client** - `dc9b73e` (feat)
2. **Task 2: Integrate AdvancedFilters into Trends page** - `4af2089` (feat)
3. **Task 3: Integrate AdvancedFilters into Map page** - `e1a9b4f` (feat)

Additional auto-fix commits:

- `8cf11dc` (fix) — unblock build by fixing hook order + removing unused import
- `fba9c21` (fix) — preserve filter params during navigation between `/trends` and `/map`

**Plan metadata:** (this summary commit)

## Files Created/Modified

- `web/src/lib/api.ts` — adds spatial SWR hooks (`useSpatialData`, `useHotspots`, `useDistrictStats`) and related interfaces
- `web/src/app/trends/page.tsx` — AdvancedFilters + URL init/sync + `useFilteredData()`-driven chart updates
- `web/src/app/map/page.tsx` — AdvancedFilters + URL init/sync + district GeoJSON feature filtering
- `web/src/components/Navbar.tsx` — preserves filter params when navigating to `/trends` and `/map`
- `web/src/lib/filters.ts` — import cleanup (unused type)

## Decisions Made

- **District filtering on Map uses GeoJSON district boundaries** rather than incident points because the backend currently does **not** expose `/api/v1/spatial/incidents`. The `useSpatialData()` hook was added per plan, but Map filtering is implemented against the existing `/api/v1/spatial/districts` data.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed conditional hook call so `npm run build` succeeds**
- **Found during:** overall verification
- **Issue:** `useMemo` was called after an early return in `MapPage`, violating Rules of Hooks; build failed.
- **Fix:** Moved memoized filtering computation above the conditional return path.
- **Files modified:** `web/src/app/map/page.tsx`
- **Verification:** `web && npm run build`
- **Committed in:** `8cf11dc`

**2. [Rule 2 - Missing Critical] Persisted filter URL params across `/trends` ↔ `/map` navigation**
- **Found during:** checkpoint readiness review for must-have “persists across page navigation via URL params”
- **Issue:** URL-sync existed per-page, but clicking nav links dropped the query string.
- **Fix:** Appended `start/end/districts/categories` to `/trends` and `/map` links.
- **Files modified:** `web/src/components/Navbar.tsx`
- **Verification:** manual checkpoint verification (approved)
- **Committed in:** `fba9c21`

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 missing critical)
**Impact on plan:** Both fixes were required to meet must-haves and keep build green; no scope creep.

## Issues Encountered

- Next.js static export build emits pre-existing Recharts “width/height should be > 0” warnings during generation. Build succeeds; warning tracked in STATE concerns already.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Trends and Map pages now share a consistent filtering UX and URL-driven state.
- If incident-level filtering on the map is desired (points/heatmaps filtered by district/date/category), backend will need a real incidents endpoint (or a generated incident export) with district + coordinates.

---
*Phase: 03-performance-quality*
*Completed: 2026-02-16*
