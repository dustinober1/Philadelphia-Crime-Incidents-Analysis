import useSWR from "swr";

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
}

export interface MetadataResponse {
  total_incidents: number;
  date_start: string;
  date_end: string;
  last_updated: string;
  source: string;
  colors: Record<string, string>;
}

export function useAnnualTrends() {
  return useSWR<TrendRow[]>("/api/v1/trends/annual", fetcher);
}

export function useMonthlyTrends() {
  return useSWR<TrendRow[]>("/api/v1/trends/monthly", fetcher);
}

export function useMetadata() {
  return useSWR<MetadataResponse>("/api/v1/metadata", fetcher);
}

export function useQuestions(status: "answered" | "pending") {
  return useSWR(`/api/v1/questions?status=${status}`, fetcher);
}
