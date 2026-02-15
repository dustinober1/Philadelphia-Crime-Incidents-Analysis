"use client";

import dynamic from "next/dynamic";
import useSWR from "swr";

import { DownloadButton } from "@/components/DownloadButton";
import { fetcher } from "@/lib/api";

const DynamicMap = dynamic(() => import("@/components/MapContainer").then((m) => m.MapContainer), {
  ssr: false,
  loading: () => <p>Loading map...</p>,
});

export default function MapPage() {
  const { data: districts } = useSWR("/api/v1/spatial/districts", fetcher);
  const { data: tracts } = useSWR("/api/v1/spatial/tracts", fetcher);
  const { data: hotspots } = useSWR("/api/v1/spatial/hotspots", fetcher);
  const { data: corridors } = useSWR("/api/v1/spatial/corridors", fetcher);

  // Metadata for GeoJSON downloads
  const metadata = {
    export_timestamp: new Date().toISOString(),
    data_version: "v1.0",
    processing_notes: "GeoJSON format for GIS applications - Aggregated from Philadelphia Police Department data",
  };

  if (!districts || !tracts || !hotspots || !corridors) {
    return <p>Loading map layers...</p>;
  }

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Interactive Map</h1>
      <p className="text-sm text-slate-600">Toggle district and tract polygon layers, overlay hotspots and vehicle corridors, and click features for details.</p>
      <DynamicMap districts={districts} tracts={tracts} hotspots={hotspots} corridors={corridors} />
      
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
