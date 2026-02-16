import useSWR from "swr";
import type { FeatureCollection, GeoJsonProperties, Geometry } from "geojson";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

export const fetcher = async (path: string) => {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Failed request: ${path}`);
  }
  return response.json();
};

export interface TrendRow {
  year?: number;
  month?: string;
  crime_category?: "Violent" | "Property" | "Other" | string;
  count: number;
  dc_dist?: number; // PPD district number (1-23), present in district-scoped responses
}

export interface MetadataResponse {
  total_incidents: number;
  date_start: string;
  date_end: string;
  last_updated: string;
  source: string;
  colors: Record<string, string>;
}

export interface QuestionItem {
  id: string;
  name: string;
  question_text: string;
  answer_text: string | null;
  created_at: string;
}

export interface ForecastPoint {
  ds: string;
  yhat: number;
  yhat_lower: number;
  yhat_upper: number;
}

export interface HistoricalPoint {
  ds: string;
  y: number;
}

export interface ForecastResponse {
  model: string;
  historical: HistoricalPoint[];
  forecast: ForecastPoint[];
}

export interface FeatureImportance {
  feature: string;
  importance: number;
}

export type GeoJson = FeatureCollection<Geometry, GeoJsonProperties>;

// Spatial API shapes
export interface SpatialPoint {
  lat: number;
  lng: number;
  district?: number;
  crime_category?: string;
  dispatch_date?: string;
  text_general_code?: string;
}

export interface HotspotData {
  lat: number;
  lng: number;
  intensity: number;
}

export interface DistrictData {
  district: number;
  count: number;
  violent: number;
  property: number;
  other: number;
}

export function useAnnualTrends() {
  return useSWR<TrendRow[]>("/api/v1/trends/annual", fetcher);
}

export function useMonthlyTrends() {
  return useSWR<TrendRow[]>("/api/v1/trends/monthly", fetcher);
}

export function useSpatialData() {
  return useSWR<SpatialPoint[]>("/api/v1/spatial/incidents", fetcher);
}

export function useHotspots() {
  return useSWR<HotspotData[]>("/api/v1/spatial/hotspots", fetcher);
}

export function useDistrictStats() {
  return useSWR<DistrictData[]>("/api/v1/spatial/districts", fetcher);
}

export function useMetadata() {
  return useSWR<MetadataResponse>("/api/v1/metadata", fetcher);
}

export function useQuestions(status: "answered" | "pending") {
  return useSWR(`/api/v1/questions?status=${status}`, fetcher);
}
