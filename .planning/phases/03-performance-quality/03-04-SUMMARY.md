---
phase: 03-performance-quality
plan: "04"
subsystem: ui
tags: [nextjs, react, typescript, narratives, data-storytelling, lucide, tailwind]

requires:
  - phase: 02-data-presentation
    provides: Chart-based trend pages and shared Tailwind card styling
provides:
  - Rule-based narrative generation (summary + explanation + insight bullets) for trend comparisons
  - Data storytelling UI components (NarrativeCard + InsightBox) to display narrative + insights alongside charts
affects: [03-05]

tech-stack:
  added: []
  patterns:
    - Rule-based narrative generation utilities in web/src/lib for reuse across pages
    - Small, presentational card components using existing Tailwind tokens and the shared card styling

key-files:
  created:
    - web/src/lib/narratives.ts
    - web/src/components/data-story/InsightBox.tsx
    - web/src/components/data-story/NarrativeCard.tsx
  modified: []

key-decisions:
  - "Use a simple threshold-based rule engine (stable/moderate/significant) for narrative text generation"

patterns-established:
  - "Narrative model: {summary, explanation, insights, context?}"
  - "Insight model: {icon: up|down|stable, type: concern|positive|neutral, text}"

duration: "18 min"
completed: "2026-02-16"
---

# Phase 3 Plan 04: Data Storytelling Components Summary

**Rule-based narrative generation plus reusable NarrativeCard/InsightBox components for displaying explanations and key insight bullets alongside trend visualizations.**

## Performance

- **Duration:** 18 min 5 sec
- **Started:** 2026-02-16T00:48:21Z
- **Completed:** 2026-02-16T01:06:26Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Implemented `generateNarrative()` to convert a simple period-over-period trend into a summary, explanation, and insight bullets.
- Added `InsightBox` to present bullet insights with trend + status icons and color-coded emphasis.
- Added `NarrativeCard` to display a compact narrative section (summary/explanation/context) and embed the `InsightBox`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create narrative generation utilities** - `dc2074a` (feat)
2. **Task 2: Create InsightBox component** - `f3e820f` (feat)
3. **Task 3: Create NarrativeCard component** - `955952d` (feat)

## Files Created/Modified

- `web/src/lib/narratives.ts` - Exports `TrendData`, `Insight`, `Narrative`, `generateNarrative()`, and `comparePeriods()`.
- `web/src/components/data-story/InsightBox.tsx` - Renders a titled insight list with type + trend icons and Tailwind styling.
- `web/src/components/data-story/NarrativeCard.tsx` - Renders narrative sections and includes `InsightBox` when insights exist.

## Component Usage Pattern

Typical usage:

```tsx
import { generateNarrative } from "@/lib/narratives";
import { NarrativeCard } from "@/components/data-story/NarrativeCard";

const narrative = generateNarrative({
  label: "Violent",
  current: 1200,
  previous: 1000,
});

<NarrativeCard narrative={narrative} title="Analysis" />;
```

## Example Narrative Outputs

### Significant increase (> 20%)
- **Summary:** "Sharp increase in crime: 200 more incidents" (label-dependent verb)
- **Explanation:** Includes percent change and "significant shift" language
- **Insight:** `type: concern`, `icon: up`

### Moderate decrease (5% - 20%)
- **Summary:** "Property decrease: 75 fewer incidents" (label-dependent verb)
- **Explanation:** Includes percent change and "warrants monitoring" language
- **Insight:** `type: neutral`, `icon: down`

### Stable (<= 5%)
- **Summary:** "Other remains stable: 5,000 incidents"
- **Explanation:** "minimal change" language with percent variance
- **Insight:** `type: neutral`, `icon: stable`

## Decisions Made

- Used a simple threshold-based rule engine (stable/moderate/significant) instead of ML/LLM narrative generation.
  - **Rationale:** Deterministic copy, easy to test, no external services, and predictable UX.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- None affecting the final output. (TypeScript compilation succeeded; components compile cleanly.)

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Narrative generation and storytelling components are ready to be integrated into trend pages and/or future “insight” sections.

---
*Phase: 03-performance-quality*
*Completed: 2026-02-16*
