"use client";

import Map, { FullscreenControl, Layer, NavigationControl, Popup, Source } from "react-map-gl/mapbox";
import { useMemo, useState } from "react";

import "mapbox-gl/dist/mapbox-gl.css";

export function MapContainer({ districts, tracts, hotspots, corridors }: { districts: any; tracts: any; hotspots: any; corridors: any }) {
  const [activePolygon, setActivePolygon] = useState<"districts" | "tracts">("districts");
  const [showHotspots, setShowHotspots] = useState(true);
  const [showCorridors, setShowCorridors] = useState(true);
  const [popup, setPopup] = useState<any>(null);

  const polygonData = useMemo(() => (activePolygon === "districts" ? districts : tracts), [activePolygon, districts, tracts]);

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
        interactiveLayerIds={["polygon-layer", "hotspot-layer"]}
        onClick={(event) => {
          const feature = event.features?.[0];
          if (feature) {
            setPopup({ lngLat: event.lngLat, properties: feature.properties });
          }
        }}
      >
        <NavigationControl position="top-left" />
        <FullscreenControl position="top-left" />

        <Source id="polygons" type="geojson" data={polygonData}>
          <Layer
            id="polygon-layer"
            type="fill"
            paint={{
              "fill-color": [
                "interpolate",
                ["linear"],
                ["coalesce", ["get", activePolygon === "districts" ? "severity_score" : "crime_rate"], 0],
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

        {showHotspots && (
          <Source id="hotspots" type="geojson" data={hotspots}>
            <Layer
              id="hotspot-layer"
              type="circle"
              paint={{
                "circle-color": "#dc2626",
                "circle-radius": ["interpolate", ["linear"], ["coalesce", ["get", "incident_count"], 0], 10, 4, 1200, 14],
                "circle-opacity": 0.8,
              }}
            />
          </Source>
        )}

        {showCorridors && (
          <Source id="corridors" type="geojson" data={corridors}>
            <Layer id="corridor-layer" type="line" paint={{ "line-color": "#f59e0b", "line-width": 1.5, "line-opacity": 0.65 }} />
          </Source>
        )}

        {popup && (
          <Popup longitude={popup.lngLat.lng} latitude={popup.lngLat.lat} onClose={() => setPopup(null)} closeOnClick={false}>
            <pre className="max-w-xs whitespace-pre-wrap text-xs">{JSON.stringify(popup.properties, null, 2)}</pre>
          </Popup>
        )}
      </Map>
    </div>
  );
}
