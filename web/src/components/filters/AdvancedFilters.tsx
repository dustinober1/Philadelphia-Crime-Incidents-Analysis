"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

import type { CrimeCategory, FilterState } from "@/lib/types";
import { CRIME_CATEGORIES, PPD_DISTRICTS } from "@/lib/filters";

interface AdvancedFiltersProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  resultCount?: number;
  totalCount?: number;
}

export function AdvancedFilters({
  filters,
  onChange,
  resultCount,
  totalCount,
}: AdvancedFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  const setDateRange = (start: string, end: string) => {
    onChange({
      ...filters,
      dateRange: start && end ? { start, end } : null,
    });
  };

  const toggleDistrict = (district: number) => {
    const newDistricts = filters.districts.includes(district)
      ? filters.districts.filter((d) => d !== district)
      : [...filters.districts, district];
    onChange({ ...filters, districts: newDistricts });
  };

  const toggleCategory = (category: CrimeCategory) => {
    const newCategories = filters.categories.includes(category)
      ? filters.categories.filter((c) => c !== category)
      : [...filters.categories, category];
    onChange({ ...filters, categories: newCategories });
  };

  const clearAll = () => {
    onChange({ dateRange: null, districts: [], categories: [] });
  };

  const hasActiveFilters =
    filters.dateRange !== null ||
    filters.districts.length > 0 ||
    filters.categories.length > 0;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-900">Filters</h3>
        <div className="flex items-center gap-2">
          {resultCount !== undefined && totalCount !== undefined && (
            <span className="text-sm text-slate-600">
              {resultCount} of {totalCount} records
            </span>
          )}
          {hasActiveFilters && (
            <button
              type="button"
              onClick={clearAll}
              className="text-sm text-blue-700 hover:text-blue-900"
            >
              Clear all
            </button>
          )}
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-slate-500 hover:text-slate-700"
            aria-label={isExpanded ? "Collapse filters" : "Expand filters"}
          >
            {isExpanded ? (
              <ChevronUp className="h-5 w-5" />
            ) : (
              <ChevronDown className="h-5 w-5" />
            )}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="mt-4 space-y-4">
          {/* Date Range */}
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Date Range
            </label>
            <div className="flex flex-wrap items-center gap-2">
              <input
                type="date"
                value={filters.dateRange?.start ?? ""}
                onChange={(e) => setDateRange(e.target.value, filters.dateRange?.end ?? "")}
                className="rounded-md border border-slate-300 px-3 py-2 text-sm"
              />
              <span className="text-slate-500">to</span>
              <input
                type="date"
                value={filters.dateRange?.end ?? ""}
                onChange={(e) => setDateRange(filters.dateRange?.start ?? "", e.target.value)}
                className="rounded-md border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
          </div>

          {/* Districts */}
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Police Districts
            </label>
            <div className="flex flex-wrap gap-2">
              {PPD_DISTRICTS.map((district) => (
                <button
                  key={district}
                  type="button"
                  onClick={() => toggleDistrict(district)}
                  className={`rounded-md border px-3 py-1.5 text-sm transition-colors ${
                    filters.districts.includes(district)
                      ? "border-blue-500 bg-blue-50 text-blue-700"
                      : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  D{district}
                </button>
              ))}
            </div>
          </div>

          {/* Categories */}
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Crime Categories
            </label>
            <div className="flex flex-wrap gap-2">
              {CRIME_CATEGORIES.map((category) => (
                <button
                  key={category}
                  type="button"
                  onClick={() => toggleCategory(category)}
                  className={`rounded-md border px-3 py-1.5 text-sm transition-colors ${
                    filters.categories.includes(category)
                      ? "border-blue-500 bg-blue-50 text-blue-700"
                      : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
