"use client";

import Map, { FullscreenControl, NavigationControl } from "react-map-gl/mapbox";
import { useMemo, useState } from "react";

import "mapbox-gl/dist/mapbox-gl.css";

import { GeoJson } from "@/lib/api";
import { MapPopup } from "@/components/maps/MapPopup";
import { ChoroplethLayer } from "@/components/maps/ChoroplethLayer";
import { HeatmapLayer } from "@/components/HeatmapLayer";
import { Layer, Source } from "react-map-gl/mapbox";

type PopupState = {
  lngLat: { lng: number; lat: number };
  properties: Record<string, unknown> | null;
};

export function MapContainer({
  districts,
  tracts,
  hotspots,
  corridors,
}: {
  districts: GeoJson;
  tracts: GeoJson;
  hotspots: GeoJson;
  corridors: GeoJson;
}) {
  const [activePolygon, setActivePolygon] = useState<"districts" | "tracts">("districts");
  const [showHotspots, setShowHotspots] = useState(true);
  const [showCorridors, setShowCorridors] = useState(true);
  const [popup, setPopup] = useState<PopupState | null>(null);

  const polygonData = useMemo(() => (activePolygon === "districts" ? districts : tracts), [activePolygon, districts, tracts]);
  const valueProperty = useMemo(() => (activePolygon === "districts" ? "severity_score" : "crime_rate"), [activePolygon]);

  // Generate interactive layer IDs dynamically
  const interactiveLayerIds = useMemo(() => {
    const layers = [`polygon-${activePolygon}-fill`];
    if (showHotspots) layers.push("hotspots-circles");
    return layers;
  }, [activePolygon, showHotspots]);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-3 rounded border bg-white p-3 text-sm">
        <label className="flex items-center gap-2"><input type="radio" checked={activePolygon === "districts"} onChange={() => setActivePolygon("districts")} />District severity</label>
        <label className="flex items-center gap-2"><input type="radio" checked={activePolygon === "tracts"} onChange={() => setActivePolygon("tracts")} />Tract rates</label>
        <label className="flex items-center gap-2"><input type="checkbox" checked={showHotspots} onChange={() => setShowHotspots((v) => !v)} />Hotspots</label>
        <label className="flex items-center gap-2"><input type="checkbox" checked={showCorridors} onChange={() => setShowCorridors((v) => !v)} />Corridors</label>
      </div>
      <Map
        initialViewState={{ longitude: -75.16, latitude: 39.95, zoom: 11 }}
        style={{ width: "100%", height: 620 }}
        mapStyle="mapbox://styles/mapbox/light-v11"
        mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
        interactiveLayerIds={interactiveLayerIds}
        onClick={(event) => {
          const feature = event.features?.[0];
          if (feature) {
            setPopup({
              lngLat: event.lngLat,
              properties: (feature.properties as Record<string, unknown> | null) ?? null,
            });
          }
        }}
      >
        <NavigationControl position="top-left" />
        <FullscreenControl position="top-left" />

        <ChoroplethLayer
          id={`polygon-${activePolygon}`}
          data={polygonData}
          valueProperty={valueProperty}
          colorScheme="blue"
        />

        {showHotspots && (
          <HeatmapLayer
            id="hotspots"
            data={hotspots}
            countProperty="incident_count"
            color="#dc2626"
          />
        )}

        {showCorridors && (
          <Source id="corridors" type="geojson" data={corridors}>
            <Layer id="corridor-layer" type="line" paint={{ "line-color": "#f59e0b", "line-width": 1.5, "line-opacity": 0.65 }} />
          </Source>
        )}

        {popup && (
          <MapPopup
            feature={{ properties: popup.properties }}
            longitude={popup.lngLat.lng}
            latitude={popup.lngLat.lat}
            onClose={() => setPopup(null)}
          />
        )}
      </Map>
    </div>
  );
}
