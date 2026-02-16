import type { CrimeCategory, CrimeIncident, FilterOptions, FilterState } from "./types";

export type { CrimeCategory, CrimeIncident, FilterOptions, FilterState } from "./types";

function normalizeCategory(category: string): CrimeCategory {
  const normalized = category.toLowerCase();
  if (normalized.includes("violent")) return "Violent";
  if (normalized.includes("property")) return "Property";
  return "Other";
}

export function applyFilters<T extends Partial<CrimeIncident>>(
  data: T[],
  filters: FilterState
): T[] {
  return data.filter((item) => {
    // Date filter
    if (filters.dateRange) {
      const itemDateString = item.dispatch_date ?? (item as unknown as { month?: string }).month ?? (item as unknown as { year?: number }).year;
      if (itemDateString) {
        const itemDate = new Date(String(itemDateString));
        const startDate = new Date(filters.dateRange.start);
        const endDate = new Date(filters.dateRange.end);

        if (Number.isNaN(itemDate.getTime())) {
          return false;
        }
        if (itemDate < startDate || itemDate > endDate) {
          return false;
        }
      }
    }

    // District filter
    if (filters.districts.length > 0) {
      const district = item.district;
      if (typeof district === "number") {
        if (!filters.districts.includes(district)) {
          return false;
        }
      }
    }

    // Category filter
    if (filters.categories.length > 0) {
      const categoryValue = item.crime_category;
      if (typeof categoryValue === "string" && categoryValue.length > 0) {
        const itemCategory = normalizeCategory(categoryValue);
        if (!filters.categories.includes(itemCategory)) {
          return false;
        }
      }
    }

    return true;
  });
}

export const PPD_DISTRICTS = Array.from({ length: 23 }, (_, i) => i + 1);
export const CRIME_CATEGORIES = ["Violent", "Property", "Other"] as const;
