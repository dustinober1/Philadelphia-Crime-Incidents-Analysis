"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import useSWR from "swr";

import { DownloadButton } from "@/components/DownloadButton";
import { NarrativeCard } from "@/components/data-story/NarrativeCard";
import { InsightBox } from "@/components/data-story/InsightBox";
import { AdvancedFilters } from "@/components/filters/AdvancedFilters";
import { generateNarrative } from "@/lib/narratives";
import type { Insight, Narrative } from "@/lib/narratives";
import type { FilterState } from "@/lib/types";
import { fetcher } from "@/lib/api";
import type { GeoJson } from "@/lib/api";

const DynamicMap = dynamic(() => import("@/components/MapContainer").then((m) => m.MapContainer), {
  ssr: false,
  loading: () => <p>Loading map...</p>,
});

function getInitialFilters(searchParams: URLSearchParams): FilterState {
  const start = searchParams.get("start");
  const end = searchParams.get("end");
  const districts =
    searchParams
      .get("districts")
      ?.split(",")
      .map((value) => Number(value))
      .filter((value) => Number.isFinite(value) && value > 0) ?? [];
  const categories =
    searchParams
      .get("categories")
      ?.split(",")
      .filter((value) => value.length > 0) as FilterState["categories"]; // runtime-validated by AdvancedFilters

  return {
    dateRange: start && end ? { start, end } : null,
    districts,
    categories: categories ?? [],
  };
}

export default function MapPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const [filters, setFilters] = useState<FilterState>(() => getInitialFilters(searchParams));

  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());

    if (filters.dateRange?.start && filters.dateRange?.end) {
      params.set("start", filters.dateRange.start);
      params.set("end", filters.dateRange.end);
    } else {
      params.delete("start");
      params.delete("end");
    }

    if (filters.districts.length > 0) {
      params.set("districts", filters.districts.join(","));
    } else {
      params.delete("districts");
    }

    if (filters.categories.length > 0) {
      params.set("categories", filters.categories.join(","));
    } else {
      params.delete("categories");
    }

    const queryString = params.toString();
    const nextUrl = queryString.length > 0 ? `${pathname}?${queryString}` : pathname;
    const currentUrl = searchParams.toString().length > 0 ? `${pathname}?${searchParams.toString()}` : pathname;

    if (nextUrl !== currentUrl) {
      router.replace(nextUrl, { scroll: false });
    }
  }, [filters, pathname, router, searchParams]);

  const { data: districts, error: districtsError, isLoading: districtsLoading } = useSWR("/api/v1/spatial/districts", fetcher);
  const { data: tracts, error: tractsError, isLoading: tractsLoading } = useSWR("/api/v1/spatial/tracts", fetcher);
  const { data: hotspots, error: hotspotsError, isLoading: hotspotsLoading } = useSWR("/api/v1/spatial/hotspots", fetcher);
  const { data: corridors, error: corridorsError, isLoading: corridorsLoading } = useSWR("/api/v1/spatial/corridors", fetcher);

  // Metadata for GeoJSON downloads
  const metadata = {
    export_timestamp: new Date().toISOString(),
    data_version: "v1.0",
    processing_notes: "GeoJSON format for GIS applications - Aggregated from Philadelphia Police Department data",
  };

  // Check for errors
  const hasError = districtsError || tractsError || hotspotsError || corridorsError;
  const isLoading = districtsLoading || tractsLoading || hotspotsLoading || corridorsLoading;

  const filteredDistricts = useMemo(() => {
    if (!districts || filters.districts.length === 0) return districts;

    const districtSet = new Set(filters.districts.map((value) => String(value)));

    return {
      ...districts,
      features: districts.features.filter((feature: { properties?: Record<string, unknown> }) => {
        const distNum = feature.properties?.dist_num;
        if (typeof distNum !== "string") return false;
        return districtSet.has(distNum);
      }),
    };
  }, [districts, filters.districts]);

  function toFiniteNumber(value: unknown): number | null {
    if (typeof value === "number") return Number.isFinite(value) ? value : null;
    if (typeof value === "string") {
      const parsed = Number(value);
      return Number.isFinite(parsed) ? parsed : null;
    }
    return null;
  }

  function median(values: number[]): number | null {
    if (values.length === 0) return null;
    const sorted = [...values].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    if (sorted.length % 2 === 0) {
      return (sorted[mid - 1] + sorted[mid]) / 2;
    }
    return sorted[mid];
  }

  const spatialInsights: Insight[] = useMemo(() => {
    const insights: Insight[] = [];

    const displayedDistrictCount = filteredDistricts?.features?.length ?? 0;
    const totalDistrictCount = districts?.features?.length ?? 0;

    if (filters.districts.length > 0) {
      insights.push({
        icon: "stable",
        type: "neutral",
        text: `Displaying ${displayedDistrictCount} of ${totalDistrictCount} districts based on your district filter.`,
      });
    }

    const districtEntries = (filteredDistricts?.features ?? [])
      .map((feature: GeoJson["features"][number]) => {
        const props = (feature as { properties?: Record<string, unknown> }).properties;
        const distNum = props?.dist_num;
        const severity = toFiniteNumber(props?.severity_score);
        return {
          district: typeof distNum === "string" ? distNum : null,
          severity,
        };
      })
      .filter(
        (row: { district: string | null; severity: number | null }): row is { district: string; severity: number } =>
          typeof row.district === "string" && row.severity !== null,
      );

    if (districtEntries.length > 0) {
      const maxRow = districtEntries.reduce(
        (a: { district: string; severity: number }, b: { district: string; severity: number }) =>
          a.severity >= b.severity ? a : b,
      );
      const severityValues = districtEntries.map((row: { district: string; severity: number }) => row.severity);
      const med = median(severityValues);

      const severityType: Insight["type"] = maxRow.severity >= 70 ? "concern" : maxRow.severity <= 30 ? "positive" : "neutral";
      const severityIcon: Insight["icon"] = maxRow.severity >= 70 ? "up" : maxRow.severity <= 30 ? "down" : "stable";

      insights.push({
        icon: severityIcon,
        type: severityType,
        text: `Highest district severity score is ${maxRow.severity.toFixed(1)} (District ${maxRow.district})${med !== null ? ` vs median ${med.toFixed(1)}.` : "."}`,
      });
    }

    const hotspotCounts = (hotspots.features ?? [])
      .map((feature: GeoJson["features"][number]) => {
        const props = (feature as { properties?: Record<string, unknown> }).properties;
        return toFiniteNumber(props?.incident_count);
      })
      .filter((value: number | null): value is number => value !== null);

    if (hotspotCounts.length > 0) {
      const top = Math.max(...hotspotCounts);
      insights.push({
        icon: "stable",
        type: "neutral",
        text: `Hotspots layer contains ${hotspotCounts.length.toLocaleString()} points; the highest-intensity hotspot represents ${top.toLocaleString()} incidents.`,
      });
    }

    const corridorCount = corridors.features?.length ?? 0;
    if (corridorCount > 0) {
      insights.push({
        icon: "stable",
        type: "neutral",
        text: `Corridors layer shows ${corridorCount.toLocaleString()} high-activity segments that can help contextualize concentration areas.`,
      });
    }

    if (filters.dateRange) {
      insights.push({
        icon: "stable",
        type: "neutral",
        text: `Date range filter is set (${filters.dateRange.start} → ${filters.dateRange.end}). Spatial layers reflect exported aggregates; use trends for time-sliced comparisons.`,
      });
    }

    if (filters.categories.length > 0) {
      insights.push({
        icon: "stable",
        type: "neutral",
        text: `Category filter is set (${filters.categories.join(", ")}). Spatial layers are not category-specific; use trends/policy pages for category narratives.`,
      });
    }

    return insights;
  }, [corridors.features, districts?.features?.length, filters.categories, filters.dateRange, filters.districts.length, filteredDistricts?.features, hotspots.features]);

  const hotspotNarrative: Narrative | null = useMemo(() => {
    const hotspotCounts = (hotspots.features ?? [])
      .map((feature: GeoJson["features"][number]) => {
        const props = (feature as { properties?: Record<string, unknown> }).properties;
        return toFiniteNumber(props?.incident_count);
      })
      .filter((value: number | null): value is number => value !== null);

    if (hotspotCounts.length < 2) return null;

    const top = Math.max(...hotspotCounts);
    const med = median(hotspotCounts);
    if (med === null) return null;

    return generateNarrative({
      current: top,
      previous: med,
      label: "Hotspot incidents",
    });
  }, [hotspots.features]);

  if (hasError) {
    return (
      <div className="space-y-4">
        <h1 className="text-3xl font-bold">Interactive Map</h1>
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
          <h2 className="mb-2 font-semibold">Error Loading Map Data</h2>
          <p className="text-sm">
            Failed to load spatial data layers. Please check that the API is running and try again.
          </p>
          {districtsError && <p className="mt-2 text-xs">Districts: {districtsError.message}</p>}
          {tractsError && <p className="mt-2 text-xs">Tracts: {tractsError.message}</p>}
          {hotspotsError && <p className="mt-2 text-xs">Hotspots: {hotspotsError.message}</p>}
          {corridorsError && <p className="mt-2 text-xs">Corridors: {corridorsError.message}</p>}
        </div>
      </div>
    );
  }

  if (isLoading || !districts || !tracts || !hotspots || !corridors) {
    return (
      <div className="space-y-4">
        <h1 className="text-3xl font-bold">Interactive Map</h1>
        <div className="flex items-center gap-3 rounded-lg border bg-white p-6">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-500 border-t-transparent"></div>
          <p className="text-slate-600">Loading map layers (districts, tracts, hotspots, corridors)...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Interactive Map</h1>

      <AdvancedFilters
        filters={filters}
        onChange={setFilters}
        resultCount={filteredDistricts?.features?.length}
        totalCount={districts.features.length}
      />

      <div className="space-y-3">
        <InsightBox title="Spatial Insights" insights={spatialInsights} />
        {hotspotNarrative && (
          <NarrativeCard narrative={hotspotNarrative} title="Hotspot concentration" />
        )}
      </div>

      <div className="rounded-lg border bg-blue-50 p-4 text-sm text-blue-900">
        <h2 className="mb-2 font-semibold">Map Layer Controls</h2>
        <ul className="space-y-1 text-blue-800">
          <li><strong>District Severity:</strong> Shows police districts colored by crime severity score (0-100)</li>
          <li><strong>Tract Rates:</strong> Displays census tracts colored by crime rate per 1,000 residents</li>
          <li><strong>Hotspots:</strong> Crime concentration points sized by incident count</li>
          <li><strong>Corridors:</strong> High-activity transportation corridors with elevated crime</li>
        </ul>
        <p className="mt-3 text-xs italic">
          Click any map feature to view detailed statistics, trends, and comparisons to city averages.
        </p>
      </div>

      <DynamicMap districts={filteredDistricts} tracts={tracts} hotspots={hotspots} corridors={corridors} />

      <div className="rounded-lg bg-white p-4 shadow-sm">
        <h2 className="mb-3 text-lg font-semibold">Download GeoJSON Data</h2>
        <p className="mb-4 text-sm text-slate-600">Download spatial data layers in standard GeoJSON format for use in GIS applications.</p>
        <div className="flex flex-wrap gap-3">
          <DownloadButton data={districts as Record<string, unknown>[]} filename="police-districts" format="json" metadata={metadata} />
          <DownloadButton data={tracts as Record<string, unknown>[]} filename="census-tracts" format="json" metadata={metadata} />
          <DownloadButton data={hotspots as Record<string, unknown>[]} filename="crime-hotspots" format="json" metadata={metadata} />
        </div>
      </div>
    </div>
  );
}
