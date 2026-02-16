"use client";

import { useMemo } from "react";
import useSWR from "swr";

import { fetcher } from "@/lib/api";
import type { FilterState, TrendRow } from "@/lib/types";
import { applyFilters } from "@/lib/filters";

export function useFilteredData(endpoint: string, filters: FilterState) {
  const { data, error, isLoading } = useSWR<TrendRow[]>(endpoint, fetcher);

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
