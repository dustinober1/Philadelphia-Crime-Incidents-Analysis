/**
 * Shared TypeScript types for data tables and components
 */

import type { ReactNode } from "react";

// Re-export TrendRow from api.ts for convenience
export type { TrendRow } from "./api";

/**
 * Generic table column definition
 */
export interface TableColumn<TData> {
  id: string;
  header: string;
  accessorKey?: keyof TData;
  cell?: (data: TData) => ReactNode;
}

/**
 * Policy data row for composition analysis
 */
export interface PolicyRow {
  year: number;
  crime_category: string;
  count: number;
}

/**
 * Retail theft trend row
 */
export interface RetailTheftRow {
  month: string;
  count: number;
}

/**
 * Vehicle crime trend row
 */
export interface VehicleCrimeRow {
  month: string;
  count: number;
}

/**
 * Event impact analysis row
 */
export interface EventRow {
  event_name?: string;
  event_date?: string;
  event_count?: number;
  control_count?: number;
  difference?: number;
  [key: string]: string | number | undefined;
}
