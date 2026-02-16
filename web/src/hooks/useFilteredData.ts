"use client";

import { useMemo } from "react";
import useSWR from "swr";

import { fetcher } from "@/lib/api";
import type { FilterState, TrendRow } from "@/lib/types";
import { applyFilters } from "@/lib/filters";

export function useFilteredData(endpoint: string, filters: FilterState) {
  // Build query params for district filtering
  const params = new URLSearchParams();
  const selectedDistrict = filters.districts.length === 1 ? filters.districts[0] : null;

  if (selectedDistrict !== null) {
    params.set("district", String(selectedDistrict));
  }

  const queryString = params.toString();
  const url = queryString ? `${endpoint}?${queryString}` : endpoint;

  // SWR key includes district so changing district triggers refetch
  const swrKey = url;

  const { data, error, isLoading } = useSWR<TrendRow[]>(swrKey, fetcher);

  const filteredData = useMemo(() => {
    if (!data) return [];
    return applyFilters(data, filters);
  }, [data, filters]);

  return {
    data: filteredData,
    allData: data,
    isLoading,
    error,
    filteredCount: filteredData.length,
    totalCount: data?.length ?? 0,
  };
}
