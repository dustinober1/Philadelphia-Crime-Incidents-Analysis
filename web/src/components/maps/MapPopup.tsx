"use client";

import { Popup } from "react-map-gl/mapbox";

type MapPopupProps = {
  feature: {
    properties: Record<string, unknown> | null;
  };
  longitude: number;
  latitude: number;
  onClose: () => void;
};

export function MapPopup({ feature, longitude, latitude, onClose }: MapPopupProps) {
  const properties = feature.properties ?? {};

  // Extract common properties with fallbacks
  const label = (properties.label as string | undefined) 
    || (properties.name as string | undefined) 
    || (properties.district_name as string | undefined)
    || (properties.tract_id as string | undefined)
    || "Unknown";

  const count = (properties.incident_count as number | undefined) 
    || (properties.count as number | undefined) 
    || 0;

  const rate = properties.crime_rate as number | undefined;
  const severityScore = properties.severity_score as number | undefined;

  // Trend calculation if previous data available
  const currentCount = count;
  const previousCount = properties.previous_count as number | undefined;
  let trendPercent: number | null = null;
  let trendDirection: "up" | "down" | "stable" = "stable";

  if (previousCount !== undefined && previousCount > 0) {
    trendPercent = ((currentCount - previousCount) / previousCount) * 100;
    if (trendPercent > 5) {
      trendDirection = "up";
    } else if (trendPercent < -5) {
      trendDirection = "down";
    }
  }

  // City average comparison
  const cityAverage = properties.city_average as number | undefined;
  const vsAverage = cityAverage && count > 0 
    ? ((count - cityAverage) / cityAverage) * 100 
    : null;

  return (
    <Popup
      longitude={longitude}
      latitude={latitude}
      onClose={onClose}
      closeOnClick={false}
      className="map-popup"
    >
      <div className="min-w-[200px] space-y-2 text-sm">
        <h3 className="font-semibold text-slate-900">{label}</h3>
        
        <div className="space-y-1">
          <div className="flex justify-between">
            <span className="text-slate-600">Incidents:</span>
            <span className="font-medium">{count.toLocaleString()}</span>
          </div>

          {rate !== undefined && (
            <div className="flex justify-between">
              <span className="text-slate-600">Crime Rate:</span>
              <span className="font-medium">{rate.toFixed(1)}</span>
            </div>
          )}

          {severityScore !== undefined && (
            <div className="flex justify-between">
              <span className="text-slate-600">Severity:</span>
              <span className="font-medium">{severityScore.toFixed(1)}</span>
            </div>
          )}

          {trendPercent !== null && (
            <div className="flex justify-between">
              <span className="text-slate-600">Trend:</span>
              <span className={`font-medium ${trendDirection === "up" ? "text-red-600" : trendDirection === "down" ? "text-green-600" : "text-slate-600"}`}>
                {trendDirection === "up" ? "↑" : trendDirection === "down" ? "↓" : "→"} {Math.abs(trendPercent).toFixed(1)}%
              </span>
            </div>
          )}

          {vsAverage !== null && (
            <div className="flex justify-between">
              <span className="text-slate-600">vs City Avg:</span>
              <span className={`font-medium ${vsAverage > 0 ? "text-red-600" : "text-green-600"}`}>
                {vsAverage > 0 ? "+" : ""}{vsAverage.toFixed(1)}%
              </span>
            </div>
          )}
        </div>

        <a
          href="#details"
          className="mt-2 block text-xs text-blue-600 hover:text-blue-800 hover:underline"
        >
          View detailed statistics →
        </a>
      </div>
    </Popup>
  );
}
