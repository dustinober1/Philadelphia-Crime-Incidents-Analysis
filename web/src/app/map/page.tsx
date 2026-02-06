"use client";

import dynamic from "next/dynamic";
import useSWR from "swr";

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

  if (!districts || !tracts || !hotspots || !corridors) {
    return <p>Loading map layers...</p>;
  }

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Interactive Map</h1>
      <p className="text-sm text-slate-600">Toggle district and tract polygon layers, overlay hotspots and vehicle corridors, and click features for details.</p>
      <DynamicMap districts={districts} tracts={tracts} hotspots={hotspots} corridors={corridors} />
    </div>
  );
}
