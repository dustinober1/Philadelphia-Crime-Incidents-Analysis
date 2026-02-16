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

/**
 * Advanced filtering types
 */

export type CrimeCategory = "Violent" | "Property" | "Other";

export interface FilterState {
  dateRange:
    | {
        start: string; // ISO date string
        end: string; // ISO date string
      }
    | null;
  districts: number[]; // PPD district numbers (1-23)
  categories: CrimeCategory[];
}

export interface FilterOptions {
  availableDistricts: number[];
  availableCategories: string[];
}

export interface CrimeIncident {
  dispatch_date: string;
  dispatch_time: string;
  district?: number;
  crime_category: string;
  text_general_code?: string;
  point?: { lat: number; lng: number };
}
