"use client";

import { Layer, Source } from "react-map-gl/mapbox";
import type { GeoJson } from "@/lib/api";

type HeatmapLayerProps = {
  id: string;
  data: GeoJson;
  countProperty: string;
  color?: string;
};

export function HeatmapLayer({
  id,
  data,
  countProperty,
  color = "#dc2626",
}: HeatmapLayerProps) {
  return (
    <Source id={id} type="geojson" data={data}>
      <Layer
        id={`${id}-circles`}
        type="circle"
        paint={{
          "circle-color": color,
          "circle-radius": [
            "interpolate",
            ["linear"],
            ["coalesce", ["get", countProperty], 0],
            0,
            2,
            10,
            4,
            100,
            8,
            500,
            12,
            1200,
            16,
          ],
          "circle-opacity": 0.7,
          "circle-stroke-width": 1,
          "circle-stroke-color": "#ffffff",
          "circle-stroke-opacity": 0.5,
        }}
      />
    </Source>
  );
}
