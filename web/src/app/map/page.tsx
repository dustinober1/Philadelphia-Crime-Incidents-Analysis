"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import useSWR from "swr";

import { DownloadButton } from "@/components/DownloadButton";
import { AdvancedFilters } from "@/components/filters/AdvancedFilters";
import type { FilterState } from "@/lib/types";
import { fetcher } from "@/lib/api";

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
