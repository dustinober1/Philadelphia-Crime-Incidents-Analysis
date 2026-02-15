# Phase 02: Data Presentation - Research

**Researched:** 2026-02-15
**Domain:** React data visualization with Next.js 15, Recharts, react-map-gl, TanStack Table
**Confidence:** HIGH

## Summary

This research investigated the established architecture and standard stack for implementing Phase 02: Data Presentation in a Next.js 15 application. The phase requires building interactive charts (line, bar, area), data tables with sorting, interactive maps with choropleth and heatmap visualizations, data export functionality, and data source citations.

The standard ecosystem for React data visualization in 2025-2026 consists of:
- **Recharts** for declarative chart composition with React components
- **react-map-gl** for Mapbox-based interactive maps with GeoJSON layers
- **TanStack Table** (v8) for headless, powerful data tables with sorting/filtering
- **SWR** for client-side data fetching with caching and revalidation
- Next.js 15 App Router with server/client component separation

The existing codebase already has Recharts (v3.1.2), react-map-gl (v8.0.4), and SWR (v2.3.6) installed, aligning with the standard stack. The primary gap is TanStack Table for data table functionality.

**Primary recommendation:** Use the existing stack (Recharts + react-map-gl + SWR) and add TanStack Table for data presentation. Follow established patterns for ResponsiveContainer wrapping, custom Tooltips, GeoJSON Source/Layer composition, and SWR data fetching hooks.

## Standard Stack

The established libraries/tools for data presentation in Next.js 15:

### Core Visualization

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **Recharts** | 3.1.2+ | Declarative React charts (line, bar, area) | Composable API, native SVG, built on D3, excellent React 19 support |
| **react-map-gl** | 8.0.4+ | Mapbox GL JS React bindings | Official vis.gl suite, GeoJSON support, performant rendering |
| **mapbox-gl** | 3.14.0+ | Map rendering engine (peer dependency) | WebGL-based maps, vector tiles, industry standard |
| **@tanstack/react-table** | 8.x | Headless table for sorting/pagination | Framework-agnostic, TypeScript-first, performant |

### Data Fetching

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **SWR** | 2.3.6+ | Client-side data fetching with caching | Client components needing auto-revalidation, caching, deduplication |
| **Next.js fetch** | 15.x | Server-side data fetching in async components | Server Components, SSR, static generation with cache control |

### UI Components (Existing)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **@headlessui/react** | 2.2.7 | Accessible dropdown/dialog/tabs | Need keyboard navigation, ARIA compliance, existing from Phase 1 |
| **lucide-react** | 0.544.0 | Icon library | Icons for download buttons, filter controls |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Recharts | Chart.js, Victory, Nivo | Recharts has better React composition; alternatives require more imperative code |
| react-map-gl | Leaflet, Google Maps | Mapbox has better GeoJSON support and performance; alternatives have simpler APIs but fewer features |
| TanStack Table | MUI DataGrid, AG Grid | TanStack is headless (more control); others are pre-built but less flexible |
| SWR | React Query, RTK Query | SWR is lighter weight; React Query has more features but larger bundle |

**Installation:**
```bash
# TanStack Table is the only addition needed
npm install @tanstack/react-table

# Existing stack already installed:
# recharts@3.1.2, react-map-gl@8.0.4, mapbox-gl@3.14.0
# swr@2.3.6, @headlessui/react@2.2.7, lucide-react@0.544.0
```

## Architecture Patterns

### Recommended Project Structure

```
web/src/
├── app/
│   ├── trends/page.tsx           # Trends dashboard (charts)
│   ├── map/page.tsx              # Spatial visualization (map)
│   ├── policy/page.tsx           # Policy analysis (tables)
│   └── about/page.tsx            # Data sources/citations
├── components/
│   ├── charts/
│   │   ├── LineChart.tsx         # Recharts wrapper
│   │   ├── BarChart.tsx          # Recharts wrapper
│   │   ├── AreaChart.tsx         # Recharts wrapper
│   │   └── CustomTooltip.tsx     # Shared tooltip component
│   ├── tables/
│   │   ├── DataTable.tsx         # TanStack Table wrapper
│   │   └── TableFilters.tsx      # Filter controls
│   ├── maps/
│   │   ├── ChoroplethMap.tsx     # GeoJSON fill layer
│   │   ├── HeatmapLayer.tsx      # Heatmap circle layer
│   │   └── MapPopup.tsx          # Interactive popup
│   ├── ChartCard.tsx             # Existing: card wrapper
│   ├── StatCard.tsx              # Existing: metric display
│   └── DownloadButton.tsx        # NEW: JSON/CSV export
├── lib/
│   ├── api.ts                    # Existing: SWR hooks
│   ├── api-helpers.ts            # NEW: download helpers
│   └── csv-export.ts             # NEW: CSV conversion utilities
└── types/
    └── data.ts                   # NEW: shared TypeScript types
```

### Pattern 1: SWR Data Fetching Hooks

**What:** Centralized data fetching hooks in `lib/api.ts` using SWR for caching and revalidation.

**When to use:** All client components fetching from API endpoints.

**Example:**
```typescript
// lib/api.ts
import useSWR from "swr";

const fetcher = async (path: string) => {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) throw new Error(`Failed request: ${path}`);
  return response.json();
};

// Reusable hooks for each endpoint
export function useAnnualTrends() {
  return useSWR<TrendRow[]>("/api/v1/trends/annual", fetcher);
}

export function useMonthlyTrends(startYear?: number, endYear?: number) {
  const params = new URLSearchParams();
  if (startYear) params.set("start_year", String(startYear));
  if (endYear) params.set("end_year", String(endYear));
  return useSWR<TrendRow[]>(`/api/v1/trends/monthly?${params}`, fetcher);
}
```

**Source:** [Context7 - SWR Basic Data Fetching](https://context7.com/vercel/swr/llms.txt)

### Pattern 2: Recharts with ResponsiveContainer

**What:** Wrap all charts in `ResponsiveContainer` for adaptive sizing and use composition for building charts.

**When to use:** Any chart rendering in the application.

**Example:**
```typescript
"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { CustomTooltip } from "@/components/charts/CustomTooltip";

interface ChartProps {
  data: Array<{ month: string; Violent: number; Property: number; Other: number }>;
}

export function MonthlyTrendsChart({ data }: ChartProps) {
  return (
    <div className="h-72" aria-label="Monthly trends chart">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" hide />
          <YAxis />
          <Tooltip content={<CustomTooltip />} />
          <Area
            dataKey="Violent"
            stackId="1"
            stroke="#E63946"
            fill="#E63946"
            fillOpacity={0.3}
          />
          <Area
            dataKey="Property"
            stackId="1"
            stroke="#457B9D"
            fill="#457B9D"
            fillOpacity={0.3}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
```

**Source:** [Context7 - Recharts ResponsiveContainer](https://context7.com/recharts/recharts/llms.txt)

### Pattern 3: react-map-gl GeoJSON Layers

**What:** Use `Source` and `Layer` components for rendering GeoJSON with interactive popups.

**When to use:** Spatial visualization with district boundaries, hotspots, or corridors.

**Example:**
```typescript
"use client";

import Map, { Layer, Popup, Source } from "react-map-gl/mapbox";
import { useState } from "react";

interface ChoroplethMapProps {
  geojsonData: GeoJSON.FeatureCollection;
  valueProperty: string;
}

export function ChoroplethMap({ geojsonData, valueProperty }: ChoroplethMapProps) {
  const [popup, setPopup] = useState<{ lng: number; lat: number; properties: any } | null>(null);

  return (
    <Map
      initialViewState={{ longitude: -75.16, latitude: 39.95, zoom: 11 }}
      style={{ width: "100%", height: 620 }}
      mapStyle="mapbox://styles/mapbox/light-v11"
      mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
      interactiveLayerIds={["polygon-layer"]}
      onClick={(event) => {
        const feature = event.features?.[0];
        if (feature) {
          setPopup({
            lng: event.lngLat.lng,
            lat: event.lngLat.lat,
            properties: feature.properties,
          });
        }
      }}
    >
      <Source id="polygons" type="geojson" data={geojsonData}>
        <Layer
          id="polygon-layer"
          type="fill"
          paint={{
            "fill-color": [
              "interpolate",
              ["linear"],
              ["coalesce", ["get", valueProperty], 0],
              0,
              "#dbeafe",
              30,
              "#60a5fa",
              70,
              "#1d4ed8",
            ],
            "fill-opacity": 0.45,
          }}
        />
        <Layer id="polygon-outline" type="line" paint={{ "line-color": "#334155", "line-width": 1 }} />
      </Source>

      {popup && (
        <Popup
          longitude={popup.lng}
          latitude={popup.lat}
          onClose={() => setPopup(null)}
          closeOnClick={false}
        >
          <pre className="max-w-xs text-xs">{JSON.stringify(popup.properties, null, 2)}</pre>
        </Popup>
      )}
    </Map>
  );
}
```

**Source:** [Context7 - react-map-gl GeoJSON](https://context7.com/visgl/react-map-gl/llms.txt)

### Pattern 4: TanStack Table for Data Tables

**What:** Use `useReactTable` hook with `getSortedRowModel` for client-side sorting.

**When to use:** Tabular data presentation with sorting requirements.

**Example:**
```typescript
"use client";

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useState } from "react";

interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
}

export function DataTable<T>({ data, columns }: DataTableProps<T>) {
  const [sorting, setSorting] = useState([]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: { sorting },
  });

  return (
    <div className="overflow-auto rounded border">
      <table className="w-full border-collapse text-sm">
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id} className="border-b bg-slate-50">
              {headerGroup.headers.map((header) => (
                <th key={header.id} className="border p-2 text-left font-semibold">
                  {header.isPlaceholder ? null : (
                    <div
                      className={header.column.getCanSort() ? "cursor-pointer" : ""}
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getIsSorted() === "asc" ? " 🔼" : null}
                      {header.column.getIsSorted() === "desc" ? " 🔽" : null}
                    </div>
                  )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className="border-b">
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="border p-2">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

**Source:** [Context7 - TanStack Table Sorting](https://context7.com/tanstack/table/llms.txt)

### Pattern 5: File Download with Blob API

**What:** Use JavaScript `Blob` and `URL.createObjectURL()` to trigger file downloads for JSON and CSV.

**When to use:** DATA-05 requirement for data export functionality.

**Example:**
```typescript
// lib/csv-export.ts
export function downloadAsJson(data: unknown[], filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${filename}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function downloadAsCsv(data: Record<string, unknown>[], filename: string) {
  if (data.length === 0) return;

  const headers = Object.keys(data[0]);
  const csvRows = [
    headers.join(","),
    ...data.map((row) =>
      headers
        .map((header) => {
          const value = row[header];
          // Escape quotes and wrap values containing commas in quotes
          const stringValue = String(value ?? "");
          return stringValue.includes(",") ? `"${stringValue.replace(/"/g, '""')}"` : stringValue;
        })
        .join(",")
    ),
  ];

  // Add UTF-8 BOM for Excel compatibility
  const blob = new Blob(["\uFEFF", csvRows.join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${filename}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// components/DownloadButton.tsx
interface DownloadButtonProps {
  data: unknown[];
  filename: string;
  format: "json" | "csv";
}

export function DownloadButton({ data, filename, format }: DownloadButtonProps) {
  const handleDownload = () => {
    if (format === "json") {
      downloadAsJson(data, filename);
    } else {
      downloadAsCsv(data as Record<string, unknown>[], filename);
    }
  };

  return (
    <button
      onClick={handleDownload}
      className="flex items-center gap-2 rounded px-3 py-2 text-sm text-blue-700 hover:bg-blue-50"
    >
      <DownloadIcon className="h-4 w-4" />
      Download {format.toUpperCase()}
    </button>
  );
}
```

**Source:** [WebSearch 2025 - Blob File Downloads](https://blog.csdn.net/weixin_35636570/article/details/152009084)

### Anti-Patterns to Avoid

- **Hand-rolling table sorting:** TanStack Table provides battle-tested sorting logic; custom implementations often miss edge cases (null handling, multi-column sort, type coercion).
- **Skipping ResponsiveContainer:** Recharts without ResponsiveContainer have fixed dimensions and break responsive layouts.
- **Inline event handlers in Map:** Use `useCallback` for map event handlers to prevent unnecessary re-renders of the entire map component.
- **CSV escaping without quotes:** Simple `join(",")` breaks on values containing commas; must quote-wrap and escape double quotes.
- **Direct mapbox-gl imports:** Use `react-map-gl/mapbox` subpath for proper tree-shaking and React 19 compatibility.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Table sorting | Custom click handlers + array sort | TanStack Table `getSortedRowModel` | Handles null values, multi-column sort, type coercion, accessibility (ARIA sort attributes) |
| Chart tooltips | Custom mouse tracking + absolute positioning | Recharts `Tooltip` component with `content` prop | Built-in positioning, hover detection, keyboard navigation, screen reader support |
| Map popups | Manual div positioning with lat/lng to pixel conversion | react-map-gl `Popup` component | Auto-positioning, anchoring, close-on-click, responsive to map movement |
| CSV generation | String concatenation with edge cases | Proper CSV library or robust utility | Handles quoting, escaping commas/quotes/newlines, UTF-8 BOM for Excel |
| Data fetch caching | Manual useState + useEffect with dependency arrays | SWR `useSWR` hook | Deduplication, revalidation, focus tracking, error retry, cache management |
| Chart responsiveness | Manual resize listeners + CSS media queries | Recharts `ResponsiveContainer` | Automatic container observation, debounce, proper cleanup |

**Key insight:** Custom solutions for these problems inevitably miss edge cases (accessibility, null handling, encoding issues, memory leaks). Existing libraries have years of battle-testing and community patches.

## Common Pitfalls

### Pitfall 1: Recharts Performance with Large Datasets

**What goes wrong:** Charts render 10,000+ data points and become laggy or freeze the browser.

**Why it happens:** Recharts renders SVG elements for every data point. SVG doesn't handle thousands of elements well compared to Canvas-based solutions.

**How to avoid:**
- Aggregate or sample data before passing to charts (use backend APIs for aggregation)
- Enable `isAnimationActive={false}` to disable animations for large datasets
- Use `React.memo` on chart components to prevent unnecessary re-renders
- For time-series with >1000 points, consider data resampling (e.g., show daily instead of hourly)

**Warning signs:** Chart interactions feel sluggish, CPU spikes during hover, browser becomes unresponsive.

**Source:** [StackOverflow - Recharts Performance Issues](https://stackoverflow.com/questions/79394313/performance-issues-with-rendering-large-datasets-in-recharts-how-to-optimize) (2025)

### Pitfall 2: Mapbox Token Exposure

**What goes wrong:** Mapbox access token committed to public repository, leading to quota theft or billing surprises.

**Why it happens:** Developers hardcode token in source code or commit `.env.local` file.

**How to avoid:**
- Always use environment variables (`NEXT_PUBLIC_MAPBOX_TOKEN`)
- Add `.env.local` to `.gitignore` (verify it's already there)
- Use restricted Mapbox tokens with URL referrer restrictions for production
- Rotate token if accidentally exposed

**Warning signs:** Token visible in GitHub repository history, map stops working after quota exceeded.

### Pitfall 3: SWR Infinite Revalidation Loops

**What goes wrong:** API endpoint called continuously in infinite loop, browser tab becomes unresponsive.

**Why it happens:** Passing object/array arguments to `useSWR` without memoization creates new references on every render, triggering re-fetch.

**How to avoid:**
```typescript
// BAD - creates new array on every render
useSWR(["/api/data", filterValues], fetcher)

// GOOD - useMemo for stable reference
const params = useMemo(() => ({ filters: filterValues }), [filterValues]);
useSWR([`/api/data?${new URLSearchParams(params)}`], fetcher)
```

**Warning signs:** Network tab shows hundreds of identical requests, CPU usage remains high after page load.

### Pitfall 4: CSV Encoding Issues in Excel

**What goes wrong:** CSV opens in Excel with garbled characters for non-ASCII text (Chinese, accented letters).

**Why it happens:** Excel on Windows expects UTF-8 with BOM (Byte Order Mark) to detect encoding properly.

**How to avoid:**
```typescript
// Add UTF-8 BOM before CSV content
const blob = new Blob(["\uFEFF", csvContent], { type: "text/csv;charset=utf-8" });
```

**Warning signs:** Users report broken characters when opening downloaded CSVs in Excel.

**Source:** [Chinese blog - JSON to CSV solution](https://comate.baidu.com/zh/page/8www9692bec) (2025)

### Pitfall 5: Missing Loading and Error States

**What goes wrong:** Users see blank screens during data fetch, no feedback when API fails.

**Why it happens:** SWR returns `isLoading` and `error` states but components don't handle them.

**How to avoid:**
```typescript
const { data, error, isLoading } = useSWR("/api/data", fetcher);

if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorMessage error={error} />;
if (!data) return null;

// Render data
```

**Warning signs:** Blank page during initial load, console errors visible to users but no UI feedback.

### Pitfall 6: GeoJSON Coordinate Precision Issues

**What goes wrong:** Map rendering artifacts, gaps between polygons, or performance issues.

**Why it happens:** GeoJSON with unnecessary decimal precision (e.g., 10+ decimal places) increases file size and rendering complexity.

**How to avoid:**
- Round coordinates to 6 decimal places (~0.1 meter precision) in backend data export
- Use GeoJSON simplification algorithms (e.g., simplify.js or backend PostGIS ST_Simplify)

**Warning signs:** GeoJSON files >5MB, slow map load times, visible gaps between adjacent polygons.

## Code Examples

Verified patterns from official sources:

### Recharts Custom Tooltip with Accessibility

```typescript
"use client";

import { TooltipProps } from "recharts";

export function CustomTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload || !payload.length) return null;

  return (
    <div
      className="rounded border bg-white p-3 shadow-lg"
      role="status"
      aria-live="assertive"
    >
      <p className="font-semibold">{label}</p>
      {payload.map((entry) => (
        <p key={entry.name} style={{ color: entry.color }}>
          {entry.name}: {entry.value?.toLocaleString()}
        </p>
      ))}
    </div>
  );
}
```

**Source:** [Context7 - Recharts Custom Tooltip](https://context7.com/recharts/recharts/llms.txt)

### Mapbox Choropleth with Data-Driven Styling

```typescript
<Source id="districts" type="geojson" data={districtsGeoJSON}>
  <Layer
    id="districts-fill"
    type="fill"
    paint={{
      "fill-color": [
        "interpolate",
        ["linear"],
        ["coalesce", ["get", "crime_rate"], 0],
        0,
        "#fee2e2",    // red-100
        50,
        "#fca5a5",    // red-300
        100,
        "#ef4444",    // red-500
        200,
        "#b91c1c",    // red-700
      ],
      "fill-opacity": 0.6,
    }}
  />
  <Layer
    id="districts-border"
    type="line"
    paint={{
      "line-color": "#ffffff",
      "line-width": 2,
    }}
  />
</Source>
```

**Source:** [Context7 - react-map-gl GeoJSON](https://context7.com/visgl/react-map-gl/llms.txt)

### SWR with Error Handling and Retry

```typescript
import useSWR from "swr";

const fetcher = async (url: string) => {
  const res = await fetch(url);
  if (!res.ok) {
    const error = new Error("Failed to fetch data");
    (error as any).status = res.status;
    throw error;
  }
  return res.json();
};

export function useTrendsData() {
  const { data, error, isLoading } = useSWR("/api/v1/trends/annual", fetcher, {
    revalidateOnFocus: false,
    revalidateOnReconnect: true,
    shouldRetryOnError: true,
    errorRetryCount: 3,
  });

  return {
    data,
    error,
    isLoading,
    isError: !!error,
  };
}
```

**Source:** [Context7 - SWR Error Handling](https://context7.com/vercel/swr/llms.txt)

### TanStack Table with Column Definitions

```typescript
import { ColumnDef } from "@tanstack/react-table";

export type TrendRow = {
  year: number;
  crime_category: string;
  count: number;
};

export const trendsColumns: ColumnDef<TrendRow>[] = [
  {
    accessorKey: "year",
    header: "Year",
    cell: (info) => info.getValue(),
  },
  {
    accessorKey: "crime_category",
    header: "Category",
    cell: (info) => info.getValue(),
  },
  {
    accessorKey: "count",
    header: "Incidents",
    cell: (info) => info.getValue()?.toLocaleString() ?? 0,
  },
];
```

**Source:** [Context7 - TanStack Table Columns](https://context7.com/tanstack/table/llms.txt)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| React Table v7 | TanStack Table v8 | 2022-2023 | TypeScript-first, framework agnostic, headless architecture |
| chart.js, nivo | Recharts for React | 2020-2024 | Better React composition, declarative API, native SVG |
| Manual fetch/useState | SWR/React Query | 2020-2025 | Built-in caching, revalidation, loading/error states |
| Class components | React Hooks (Server/Client Components) | React 18+ | Next.js 15 requires "use client" directive for interactivity |
| getServerSideProps | Next.js App Router async components | Next.js 13+ | Simplified data fetching, co-located with components |

**Deprecated/outdated:**
- **Recharts 2.x:** Upgrade to 3.x for React 19 support and custom component composition
- **Class-based map components:** Use functional components with hooks for react-map-gl
- **Next.js Pages router:** App Router is the default for Next.js 15; pages directory still works but is legacy
- **Chart.js:** Imperative API doesn't align with React's declarative patterns; use Recharts instead

## Open Questions

1. **Mapbox token cost and quota limits**
   - What we know: Mapbox requires public access token; current `.env.local` has `NEXT_PUBLIC_MAPBOX_TOKEN`
   - What's unclear: What are the current tier limits? Is the token using the free tier (200k loads/month)?
   - Recommendation: Verify Mapbox account tier in billing dashboard; consider adding token referrer restrictions for production

2. **Data volume for chart performance**
   - What we know: Recharts can struggle with >1000 data points; existing trends API returns annual (~20 rows) and monthly (~240 rows) data
   - What's unclear: Will any endpoints return larger datasets (e.g., daily trends = 7000+ rows)?
   - Recommendation: Check API responses during integration; implement data sampling if endpoints return >5000 rows

3. **Server-side vs client-side data table operations**
   - What we know: TanStack Table supports both client-side and server-side sorting/filtering
   - What's unclear: Should tables sort/filter in browser (client-side) or via API params (server-side)?
   - Recommendation: Use client-side for datasets <1000 rows (simpler); server-side for >1000 rows (better performance)

## Sources

### Primary (HIGH confidence)

- [Context7 - /recharts/recharts](https://context7.com/recharts/recharts/llms.txt) - ResponsiveContainer, custom tooltips, accessibility, synchronized charts
- [Context7 - /visgl/react-map-gl](https://context7.com/visgl/react-map-gl/llms.txt) - Map component, Source/Layer patterns, event handling, popups
- [Context7 - /tanstack/table](https://context7.com/tanstack/table/llms.txt) - useReactTable hook, sorting, pagination, column definitions
- [Context7 - /vercel/swr](https://context7.com/vercel/swr/llms.txt) - useSWR hook, error handling, conditional fetching
- [Context7 - /vercel/next.js](https://context7.com/vercel/next.js/llms.txt) - App Router data fetching, server/client components

### Secondary (MEDIUM confidence)

- [TanStack Table Official Documentation](https://tanstack.com/table/v8) - Comprehensive table implementation guide
- [react-map-gl Examples](https://visgl.github.io/react-map-gl/examples) - Official examples gallery
- [Mapbox GL JS Performance Guide](https://docs.mapbox.com/help/troubleshooting/mapbox-gl-js-performance/) - Map optimization strategies
- [I Built an Enterprise-Grade Data Table for Next.js](https://dev.to/jacksonkasi/i-built-an-enterprise-grade-data-table-for-nextjs-now-available-via-shadcn-registry-406h) (2025-10-02) - Production-ready TanStack Table patterns

### Tertiary (LOW confidence)

- [How to download CSV and JSON files in React](https://theroadtoenterprise.com/blog/how-to-download-csv-and-json-files-in-react) (2021-08-27) - Blob API patterns (verified by multiple sources)
- [Recharts vs. Chart.js: Performance Maze](http://oreateai.com/blog/recharts-vs-chartjs-navigating-the-performance-maze-for-big-data-visualizations/cf527fb7ad5dcb1d746994de18bdea30) (2026-01-27) - Large dataset performance benchmarks
- [基于JavaScript的前端文件下载解决方案实战项目](https://blog.csdn.net/weixin_35636570/article/details/152009084) (2025-09-22) - Modern Blob download approaches

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Context7 documentation + existing package.json confirms Recharts, react-map-gl, SWR are standard; TanStack Table is well-documented
- Architecture: HIGH - Context7 provides verified code examples for all major patterns (Recharts composition, react-map-gl Source/Layer, SWR hooks, TanStack Table)
- Pitfalls: MEDIUM - Performance issues verified by multiple sources; Mapbox token issue is common knowledge; SWR revalidation loop is documented but less frequently discussed

**Research date:** 2026-02-15
**Valid until:** 2026-05-15 (90 days - React ecosystem moves fast but these libraries are mature)

**Existing infrastructure confirmed:**
- Recharts 3.1.2 ✅
- react-map-gl 8.0.4 ✅
- mapbox-gl 3.14.0 ✅
- SWR 2.3.6 ✅
- API endpoints at `/api/v1/trends/*`, `/api/v1/spatial/*`, `/api/v1/policy/*`, `/api/v1/forecasting/*` ✅
