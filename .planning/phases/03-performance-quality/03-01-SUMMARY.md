---
phase: 03-performance-quality
plan: 01
subsystem: web
tags: [nextjs, react, performance, security, suspense, code-splitting]

requires:
  - phase: 02-data-presentation
    provides: Next.js 15 app with charts/maps/data pages
provides:
  - Next.js upgraded to a patched 15.5.x release
  - Root layout Suspense boundary + skeleton fallback for streaming UI
  - Code-splitting for heavy chart component via next/dynamic
affects: [web, ui, build, security]

tech-stack:
  added: []
  patterns:
    - Root layout streaming boundary via React Suspense
    - Code-splitting heavy client components via next/dynamic (ssr: false)

key-files:
  modified:
    - web/package.json
    - web/package-lock.json
    - web/src/app/layout.tsx
    - web/src/app/trends/page.tsx

decisions:
  - "Upgraded to next@15.5.12 (instead of planned 15.5.9) because npm audit indicated additional high-severity Next.js advisories fixed in 15.5.10+."

metrics:
  duration: 18m 41s
  started: 2026-02-16T00:49:16Z
  completed: 2026-02-16
---

# Phase 03 Plan 01: Next.js upgrade + streaming + code-splitting — Summary

**One-liner:** Patched Next.js upgrade plus root Suspense streaming boundary and dynamic-import code splitting for heavy charts.

## What Changed

### 1) Next.js security upgrade
- Updated `next` and `eslint-config-next` from **15.5.2 → 15.5.12**.
- Confirmed `npm audit` reports **0 vulnerabilities** after upgrade.

### 2) Streaming boundary in root layout
- Added `Suspense` import and wrapped `{children}` in a root-level `<Suspense fallback={...}>`.
- Added an inline `LoadingFallback()` skeleton.

File: `web/src/app/layout.tsx`

### 3) Code splitting for heavy components
- Converted the Trends page chart import to a dynamic import:
  - `web/src/app/trends/page.tsx` now loads `TrendChart` via `next/dynamic` with a skeleton fallback and `ssr: false`.
- Map page already used dynamic import for `MapContainer` (`web/src/app/map/page.tsx`) prior to this plan.

## Verification Evidence

### Build
- `cd web && npm run build` succeeds on Next.js **15.5.12**.

### Must-haves
- **Patched Next.js:** `"next": "15.5.12"` in `web/package.json`.
- **Suspense boundary:** `import { Suspense } from "react";` present and `<Suspense fallback={<LoadingFallback />}>{children}</Suspense>` in root layout.
- **Dynamic imports present:**
  - `web/src/app/trends/page.tsx` imports `next/dynamic`.
  - `web/src/app/map/page.tsx` imports `next/dynamic`.

### Static HTML renders immediately
Because this project uses `output: "export"`, `next start` is not supported. To verify HTML rendering, the exported `web/out/` was served with a simple static server and fetched:
- `python3 -m http.server 4010 --directory web/out` then `curl -I http://localhost:4010/` returned **HTTP 200** and `curl http://localhost:4010/` returned HTML.

## Task Commits

| Task | Name | Commit | Key files |
|---:|------|--------|----------|
| 1 | Upgrade Next.js to patched version | `2dd9616` | `web/package.json`, `web/package-lock.json` |
| 2 | Add Suspense boundaries to root layout | `4229b71` | `web/src/app/layout.tsx` |
| 3 | Enable dynamic imports for heavy components | `0f14899` | `web/src/app/trends/page.tsx` |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Upgraded beyond planned 15.5.9**
- **Found during:** Task 1
- **Issue:** `npm audit` reported additional Next.js advisories with fix available in 15.5.12 (range affected `<15.5.10`).
- **Fix:** Upgraded to `next@15.5.12` / `eslint-config-next@15.5.12`.
- **Commit:** `2dd9616`

**2. [Rule 3 - Blocking] Adjusted runtime verification for static export**
- **Found during:** overall verification
- **Issue:** `next start` fails when `next.config.ts` uses `output: "export"`.
- **Fix:** Verified initial HTML via static server against `web/out/`.
- **Commit:** none (verification-only change)

## Notes / Follow-ups

- The build prints repeated Recharts warnings about container width/height during static generation. This plan did not change chart sizing behavior; dynamic import on `/trends` reduces initial bundle and avoids SSR for charts, but the warning still appears during build.
