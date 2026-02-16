---
phase: 03-performance-quality
verified: 2026-02-16T02:17:15Z
status: gaps_found
score: 16/23 must-haves verified
gaps:
  - truth: "User can filter by police district (all 23 PPD districts)"
    status: failed
    reason: "District filter UI exists, but Trends aggregates lack a district field so selecting districts does not change trend charts/narratives."
    artifacts:
      - path: "web/src/lib/api.ts"
        issue: "TrendRow does not include district; /api/v1/trends/* hooks fetch citywide aggregates only."
      - path: "web/src/lib/filters.ts"
        issue: "applyFilters only filters by district when item.district is present; TrendRow items have no district so they pass through unchanged."
      - path: "web/src/app/trends/page.tsx"
        issue: "Uses useFilteredData(endpoint, filters), but fetched TrendRow[] cannot be district-filtered client-side."
    missing:
      - "Either API support for district-filtered trend endpoints (query params) or trend responses including district dimension"
      - "Client refetch keyed by district filter (instead of only client-side filtering)"

  - truth: "Filters work together (all three can be active simultaneously)"
    status: partial
    reason: "Date/category filters affect TrendRow-derived charts, but district filter does not affect trends; Map page only applies district to district polygons and explicitly does not apply date/category to spatial layers."
    artifacts:
      - path: "web/src/app/map/page.tsx"
        issue: "Spatial Insights explicitly state category/date filters are not applied to spatial layers; filtering is limited to district polygon selection."
      - path: "web/src/app/trends/page.tsx"
        issue: "District selection updates URL and filter insights, but does not change annual/monthly series because TrendRow has no district."
    missing:
      - "Consistent semantics for what each filter applies to on each page"
      - "Back-end or front-end changes so district/date/category simultaneously constrain the same datasets where expected"

  - truth: "Trends page displays narrative insights below each chart"
    status: failed
    reason: "NarrativeCard + generateNarrative are integrated for the Annual trends card only; other Trend charts use short static text insights (not narrative components)."
    artifacts:
      - path: "web/src/app/trends/page.tsx"
        issue: "Only the Annual trends ChartCard renders NarrativeCard/InsightBox narrative section; Monthly/COVID/Seasonality/Robbery cards do not."
    missing:
      - "NarrativeCard/InsightBox integration (or equivalent narrative components) for each major chart on the Trends page"
      - "Narrative logic tied to the chart’s underlying dataset (and filters)"
---

# Phase 3: Performance & Quality Verification Report

Phase Goal (from ROADMAP.md)
- Site loads completely within 3 seconds on standard broadband connections
- User can filter displayed data by custom date ranges, police districts, and crime types
- User can read narrative explanations and data-driven insights alongside visualizations

Verified: 2026-02-16T02:17:15Z
Status: gaps_found

## Goal Achievement

### Observable Truths (must_haves from 03-01..03-05)

| # | Truth | Status | Evidence |
|---:|-------|--------|----------|
| 1 | Next.js version is 15.5.7 or higher (CVE-2025-66478 patched) | VERIFIED | `web/package.json` has `"next": "15.5.12"` |
| 2 | Static pages render to HTML with progressive loading for data-fetching pages | UNCERTAIN | `web/next.config.ts` sets `output: "export"`; needs build output + browser timing |
| 3 | Code splitting is enabled for heavy chart and map components | VERIFIED | `web/src/app/trends/page.tsx` + `web/src/app/map/page.tsx` use `next/dynamic` with `ssr:false` |
| 4 | Root layout includes Suspense boundaries for streaming | VERIFIED | `web/src/app/layout.tsx` imports `Suspense` and wraps `{children}` |
| 5 | User can filter by date range with start and end date inputs | VERIFIED | `AdvancedFilters` renders two `type="date"` inputs; `FilterState.dateRange` exists |
| 6 | User can filter by police district (all 23 PPD districts) | FAILED | UI shows 1-23, but trends datasets lack district so charts don’t change |
| 7 | User can filter by crime category (Violent, Property, Other) | VERIFIED | `filters.ts` normalizes categories; trends series derived from `useFilteredData(..., filters)` |
| 8 | Filters work together (all three can be active simultaneously) | PARTIAL | date/category apply; district doesn’t affect trends; map only applies district polygon filtering |
| 9 | Filtered data updates charts and tables in real-time | PARTIAL | trends annual/monthly update for some filters; district selection doesn’t change series |
| 10 | Trends page uses AdvancedFilters component | VERIFIED | `web/src/app/trends/page.tsx` imports and renders `<AdvancedFilters ...>` |
| 11 | Trends page charts update when filters change | PARTIAL | recomputes from `annual.data/monthly.data`; district filter doesn’t change TrendRow |
| 12 | Map page filters data by district when districts selected | VERIFIED | `filteredDistricts` filters GeoJSON features by `dist_num` |
| 13 | Filter state persists across page navigation via URL params | VERIFIED | trends + map read query params and sync via `router.replace` |
| 14 | Clear filters button resets all filters to default state | VERIFIED | `AdvancedFilters.clearAll()` sets `{ dateRange:null, districts:[], categories:[] }` |
| 15 | InsightBox component displays bullet-point insights with icons | VERIFIED | `InsightBox.tsx` maps `insight.type` and `insight.icon` to Lucide icons |
| 16 | NarrativeCard component displays explanatory text with data context | VERIFIED | `NarrativeCard.tsx` renders Summary/Explanation/Context + embedded `InsightBox` |
| 17 | generateNarrative function creates text from trend data | VERIFIED | `web/src/lib/narratives.ts` exports `generateNarrative(TrendData)` |
| 18 | Narratives respond to data changes (increases, decreases, stability) | VERIFIED | narrative logic branches on magnitude + direction |
| 19 | Trends page displays narrative insights below each chart | FAILED | only Annual trends uses `NarrativeCard`; other charts use static `<p>` strings |
| 20 | Narratives update dynamically when filter state changes | PARTIAL | annual narratives depend on `annualSeries`; district filter doesn’t affect it |
| 21 | Annual trends chart shows year-over-year comparison narrative | VERIFIED | trends page compares latest vs previous year and calls `generateNarrative` |
| 22 | Map page displays narrative about spatial distribution | VERIFIED | map renders `InsightBox` + a `NarrativeCard` for `hotspotNarrative` |
| 23 | Insight boxes appear with context-aware messages | VERIFIED | trends `filterInsights`, map `spatialInsights`, policy `policyInsights` |

Score: 16/23 truths verified

## Required Artifacts (existence, substantive, wired)

| Artifact | Expected | Status | Details |
|---------|----------|--------|---------|
| `web/package.json` | Next.js >= 15.5.7 | VERIFIED | `next` 15.5.12; `eslint-config-next` 15.5.12 |
| `web/src/app/layout.tsx` | Root layout with Suspense | VERIFIED | `<Suspense fallback={<LoadingFallback />}>{children}</Suspense>` |
| `web/next.config.ts` | Next.js config for performance | PARTIAL | exists and used, but very thin (only `output: "export"`) |
| `web/src/components/filters/AdvancedFilters.tsx` | Unified filter UI | VERIFIED | substantive; used by trends + map |
| `web/src/lib/filters.ts` | `applyFilters` + constants | VERIFIED | exports `applyFilters`, `PPD_DISTRICTS`, `CRIME_CATEGORIES` |
| `web/src/hooks/useFilteredData.ts` | SWR + filtering hook | VERIFIED | exported + used in `trends/page.tsx` |
| `web/src/lib/narratives.ts` | narrative generation | VERIFIED | exported + used in trends/map |
| `web/src/components/data-story/InsightBox.tsx` | insight component | VERIFIED | exported + used in trends/map/policy |
| `web/src/components/data-story/NarrativeCard.tsx` | narrative component | VERIFIED | exported + used in trends/map |
| `web/src/app/trends/page.tsx` | trends integration | VERIFIED | filters + narratives + dynamic chart |
| `web/src/app/map/page.tsx` | map integration | VERIFIED | district filtering + narratives + dynamic map |
| `web/src/app/policy/page.tsx` | policy insights | VERIFIED | InsightBox integrated |

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `web/src/app/layout.tsx` | React Suspense | import + JSX | WIRED | `import { Suspense } from "react"` and `<Suspense ...>` |
| `web/src/app/trends/page.tsx` | `AdvancedFilters` | import + render | WIRED | imports + renders `<AdvancedFilters ...>` |
| `web/src/app/trends/page.tsx` | `useFilteredData` | import + call | WIRED | `useFilteredData("/api/v1/trends/annual", filters)` |
| `web/src/hooks/useFilteredData.ts` | `applyFilters` | import + call | WIRED | `return applyFilters(data, filters)` |
| trends/map pages | URL params | `useSearchParams` + `router.replace` | WIRED | query params round-trip |
| `NarrativeCard.tsx` | `InsightBox.tsx` | import + render | WIRED | `NarrativeCard` embeds `<InsightBox ...>` |

## Requirements Coverage (Phase 3)

| Requirement | Status | Blocking Issue |
|------------|--------|----------------|
| PERF-01: site load performance improvements | NEEDS HUMAN | Under-3-second claim requires measurement (Lighthouse/DevTools). Structural improvements exist (dynamic imports + static export + Suspense). |
| PERF-02: advanced filtering by date range, district, crime type | BLOCKED | district filtering does not affect trends aggregates; map page does not apply date/category to spatial layers. |
| PERF-03: narrative explanations and insights | PARTIAL | narrative components exist and are used, but Trends lacks narrative components for each chart; narratives don’t respond to district filter on trends. |

## Anti-Patterns Found

No blocker stub patterns detected in `web/src` via search (no TODO/FIXME/placeholder stubs; no console.log-only implementations found).

## Human Verification Required

### 1. PERF-01 load-time measurement

Test: Run Lighthouse (mobile + desktop) or measure with DevTools for `/`, `/trends`, `/map`.
Expected: Fully loaded within 3 seconds on standard broadband.
Why human: requires runtime measurement in a browser (cannot be verified structurally).

### 2. District filtering on Trends

Test: On `/trends`, select 1-2 districts and observe Annual/Monthly charts.
Expected: Trend lines/series change to reflect selected districts.
Why human: confirms the structural gap manifests in UX (current code suggests it will not).

## Gaps Summary

Phase 03 shows substantial delivery (Next.js upgraded, dynamic imports for heavy UI, filter UI + URL syncing, narrative components + some page integration), but does not fully achieve the phase goal due to:

1. District filtering not actually constraining trend data (missing district dimension or API support).
2. Filters not consistently applying together across pages/datasets.
3. Trends page narratives not integrated below each chart (annual-only).

Verified: 2026-02-16T02:17:15Z
Verifier: Claude (gsd-verifier)
