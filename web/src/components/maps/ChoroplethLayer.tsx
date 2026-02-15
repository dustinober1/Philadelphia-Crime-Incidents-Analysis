"use client";

import { Layer, Source } from "react-map-gl/mapbox";
import type { FillLayer, LineLayer } from "react-map-gl/mapbox";

type ColorScheme = "blue" | "red" | "green";

type ChoroplethLayerProps = {
  id: string;
  data: unknown;
  valueProperty: string;
  colorScheme?: ColorScheme;
};

const COLOR_SCHEMES: Record<ColorScheme, [string, string, string]> = {
  blue: ["#dbeafe", "#60a5fa", "#1d4ed8"],
  red: ["#fee2e2", "#f87171", "#dc2626"],
  green: ["#dcfce7", "#4ade80", "#16a34a"],
};

export function ChoroplethLayer({
  id,
  data,
  valueProperty,
  colorScheme = "blue",
}: ChoroplethLayerProps) {
  const [lightColor, midColor, darkColor] = COLOR_SCHEMES[colorScheme];

  const fillLayer: FillLayer = {
    id: `${id}-fill`,
    type: "fill",
    paint: {
      "fill-color": [
        "interpolate",
        ["linear"],
        ["coalesce", ["get", valueProperty], 0],
        0,
        lightColor,
        30,
        midColor,
        70,
        darkColor,
      ],
      "fill-opacity": 0.45,
    },
  };

  const outlineLayer: LineLayer = {
    id: `${id}-outline`,
    type: "line",
    paint: {
      "line-color": "#334155",
      "line-width": 1,
    },
  };

  return (
    <Source id={id} type="geojson" data={data}>
      <Layer {...fillLayer} />
      <Layer {...outlineLayer} />
    </Source>
  );
}
