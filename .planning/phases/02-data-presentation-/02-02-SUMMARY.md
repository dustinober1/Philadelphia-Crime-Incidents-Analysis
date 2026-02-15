---
phase: 02-data-presentation
plan: "02"
subsystem: data-table-components
status: complete
requires:
  - 01-03 (Navigation & Layout foundation)
  - "@tanstack/react-table@8.21.3"
provides:
  - Reusable DataTable component with TanStack Table integration
  - TableFilters component for search and filtering
  - Shared TypeScript types for table data structures
  - Policy page with sortable, filterable composition data table
affects:
  - 02-03 (Can use DataTable for forecast data display)
  - 02-04 (Can add download buttons to existing tables)
  - Future data-heavy pages requiring tabular presentation
tech-stack:
  added:
    - "@tanstack/react-table": "8.21.3 (already installed by 02-01)"
  patterns:
    - Headless UI pattern with TanStack Table
    - Generic TypeScript components for reusability
    - Client-side sorting and pagination for small datasets
    - Controlled component pattern for filters
    - Computed columns with useMemo for performance
decisions:
  - use-client-side-operations: "Client-side sorting, filtering, and pagination for datasets under 1000 rows (adequate for current data volumes)"
  - use-headless-table: "TanStack Table v8 provides flexible, type-safe table logic without UI constraints"
  - percentage-calculation: "Calculate crime category percentages client-side using year totals (reduces API complexity)"
  - page-size-25: "Default 25 rows per page for composition data balances visibility and pagination utility"
key-files:
  created:
    - web/src/lib/types.ts
    - web/src/components/tables/TableFilters.tsx
    - web/src/components/tables/DataTable.tsx
  modified:
    - web/src/app/policy/page.tsx
metrics:
  tasks: 4/4
  commits: 5
  duration: "3m 26s"
  files_created: 3
  files_modified: 2
  lines_added: ~350
completed: 2026-02-15
---

# Phase 02 Plan 02: Data Table Components Summary

**One-liner:** Generic TanStack Table wrapper with sorting, pagination, and filtering; integrated on policy page for composition analysis

## Objectives Met

✅ **Reusable data table component**: Created `DataTable<TData>` with generic TypeScript support  
✅ **Sorting capability**: Click column headers to sort ascending/descending with visual indicators  
✅ **Pagination controls**: Previous/next buttons with page info, configurable page size  
✅ **Search filtering**: Global search across all columns via `TableFilters` component  
✅ **Mobile responsive**: Horizontal scroll container for small screens  
✅ **Accessibility**: ARIA labels, keyboard navigation (Enter/Space for sorting)  
✅ **Integration**: Policy page displays composition data with calculated percentages

## Implementation Summary

### Task 1: Shared Types (types.ts)

Created centralized type definitions:
- `TableColumn<TData>` generic interface for column definitions
- Re-exported `TrendRow` from api.ts
- Added `PolicyRow`, `RetailTheftRow`, `VehicleCrimeRow`, `EventRow` interfaces
- Support for custom cell renderers with ReactNode

**Files:** `web/src/lib/types.ts` (55 lines)  
**Commit:** `30fde1d`

### Task 2: TableFilters Component

Built controlled filter component:
- Search input with magnifying glass icon (lucide-react)
- Reset button (visible only when filter active)
- Responsive flex layout (column on mobile, row on desktop)
- Loading state support for async filtering
- Accessible with aria-labels

**Files:** `web/src/components/tables/TableFilters.tsx` (60 lines)  
**Commit:** `0a90028`

### Task 3: DataTable Component

Implemented headless table wrapper using TanStack Table v8:
- Generic `DataTable<TData>` component with ColumnDef support
- Three core models: `getCoreRowModel`, `getSortedRowModel`, `getPaginationRowModel`
- Sorting state management with visual indicators (ChevronUp/Down/UpDown)
- Pagination controls (prev/next, page N of M, total rows)
- Empty state with customizable message
- Keyboard navigation for sorting (Enter/Space)
- Responsive table with overflow-x-auto

**Files:** `web/src/components/tables/DataTable.tsx` (164 lines)  
**Commits:** `b328e4b`, `a7165e3` (keyboard handler fix)

### Task 4: Policy Page Integration

Enhanced policy page with composition data table:
- Added DataTable below existing composition chart
- Defined columns: year, crime_category, count, percentage
- Computed percentages using `useMemo` (count / year total × 100)
- Client-side search filtering across all columns
- 25 rows per page for composition data
- Formatted counts with `toLocaleString()` for readability
- Preserved existing chart visualizations

**Files:** `web/src/app/policy/page.tsx` (+82 lines)  
**Commit:** `a33edf0`

## Technical Decisions

### Client-Side Operations
**Decision:** Use client-side sorting, filtering, and pagination  
**Rationale:** Current datasets are small (<1000 rows), avoiding API complexity  
**Trade-off:** Won't scale to 10k+ rows, but adequate for crime analysis aggregates

### Headless UI Pattern
**Decision:** TanStack Table v8 for table logic  
**Rationale:** Separation of data/logic from presentation, full TypeScript support  
**Benefits:** Flexibility for custom styling, type safety, extensive feature set

### Percentage Calculation
**Decision:** Compute percentages client-side rather than API  
**Rationale:** Reduces API surface area, keeps calculation logic in presentation layer  
**Implementation:** `useMemo` to calculate year totals, then map rows with percentage field

### Generic Components
**Decision:** Use TypeScript generics for DataTable and TableColumn  
**Rationale:** Reusable across different data types (trends, policy, events)  
**Benefits:** Type safety for accessorKey, cell renderers; single component for all tables

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed keyboard event type error**
- **Found during:** Task 3 verification (build)
- **Issue:** Keyboard event handler tried to pass `KeyboardEvent` to mouse event handler, causing TypeScript error
- **Fix:** Changed to call `header.column.toggleSorting()` directly instead of passing event to handler
- **Files modified:** `web/src/components/tables/DataTable.tsx`
- **Commit:** `a7165e3`

**Reason:** Standard pattern for keyboard-triggered sorting in TanStack Table; handlers expect mouse events only.

## Testing & Verification

✅ **Lint:** `npm run lint` - No errors  
✅ **Typecheck:** Pre-existing errors in CustomTooltip.tsx (unrelated)  
✅ **Build:** `npm run build` - Success (static pages generated)  
✅ **Manual verification needed:** Table sorting, filtering, pagination on policy page

### Build Output
- Policy page: 243 kB First Load JS (includes DataTable, TableFilters, charts)
- All 13 routes built successfully as static pages
- Recharts warnings during SSR (expected, charts render client-side only)

## Next Phase Readiness

**For 02-03 (Forecast visualization):**
- DataTable can display forecast data if tabular view needed
- TableFilters reusable for forecast filtering
- Pattern established for computed columns (e.g., confidence intervals)

**For 02-04 (Download capabilities):**
- DataTable provides structured data perfect for CSV/JSON export
- filteredData can be passed to download utilities
- Download buttons can integrate with existing tables

**For 02-05 (Maps):**
- TableFilters pattern applicable to map filters if needed
- Types in types.ts can extend to geographic data

## Success Criteria Met

✅ **DATA-02 complete:** Data tables with sorting, filtering, and pagination  
✅ **Responsive design:** overflow-x-auto for mobile horizontal scroll  
✅ **TanStack Table standard patterns:** useReactTable, sorted/pagination models  
✅ **Performance:** Client-side operations smooth for <1000 row datasets  
✅ **Accessibility:** Keyboard navigation, ARIA labels, semantic HTML

## Files Created/Modified

**Created (3 files):**
1. `web/src/lib/types.ts` - Shared TypeScript types
2. `web/src/components/tables/TableFilters.tsx` - Search/filter controls
3. `web/src/components/tables/DataTable.tsx` - Generic table component

**Modified (1 file):**
1. `web/src/app/policy/page.tsx` - Added composition data table

## Commits

| Hash    | Type   | Message                                                      |
|---------|--------|--------------------------------------------------------------|
| 30fde1d | feat   | create shared types for data table columns                   |
| 0a90028 | feat   | create TableFilters component with search and reset          |
| b328e4b | feat   | create DataTable component with TanStack Table               |
| a7165e3 | fix    | correct keyboard event handler in DataTable                  |
| a33edf0 | feat   | add data table to policy page for composition data           |

## Known Issues / Future Improvements

**Type errors in CustomTooltip.tsx (pre-existing):**
- Not related to this plan
- Should be addressed in a future bugfix plan
- Does not block current functionality

**Performance optimization (future):**
- Current implementation loads all data then filters client-side
- For 1000+ rows, consider virtual scrolling (react-virtual) or server-side pagination
- Current approach adequate for aggregated crime data

**Enhanced filtering (future):**
- Multi-column filters (e.g., year range, category selection)
- Filter state persistence in URL query params
- Advanced operators (contains, starts with, greater than)

**Sorting improvements (future):**
- Multi-column sorting (shift+click)
- Custom sort functions for special data types
- Sort direction indicator in column header text

## Dependencies

**Runtime:**
- `@tanstack/react-table@8.21.3` (installed by parallel plan 02-01)
- `lucide-react` (icons: Search, X, ChevronUp, ChevronDown, ChevronsUpDown)
- `react`, `react-dom` (Next.js dependencies)

**Build:**
- `typescript@5.7.3`
- `next@15.5.2`

## Architecture Notes

**Component hierarchy:**
```
PolicyPage
├── ChartCard (composition chart)
└── ChartCard (composition table)
    ├── TableFilters (search/reset)
    └── DataTable<CompositionRow>
        ├── <table> (with sorting headers)
        └── Pagination controls
```

**Data flow:**
```
useSWR → composition (raw data)
       ↓
useMemo → compositionWithPercentage (computed field)
       ↓
useMemo → filteredComposition (client-side filter)
       ↓
DataTable → TanStack Table (sorting, pagination)
```

**Type safety:**
- Generic `DataTable<TData>` ensures column accessors match data keys
- `ColumnDef<TData>` from TanStack Table provides full type inference
- Custom cell renderers typed as `(data: TData) => ReactNode`

## References

- [TanStack Table v8 Docs](https://tanstack.com/table/v8/docs/introduction)
- [Next.js App Router](https://nextjs.org/docs/app)
- Plan 02-01 for TanStack Table installation
- Plan 01-03 for ChartCard component pattern
