"use client";

import { Search, X } from "lucide-react";
import { useState } from "react";

interface TableFiltersProps {
  onSearchChange: (value: string) => void;
  onReset: () => void;
  placeholder?: string;
  isLoading?: boolean;
}

export function TableFilters({
  onSearchChange,
  onReset,
  placeholder = "Search...",
  isLoading = false,
}: TableFiltersProps) {
  const [searchValue, setSearchValue] = useState("");

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchValue(value);
    onSearchChange(value);
  };

  const handleReset = () => {
    setSearchValue("");
    onReset();
  };

  return (
    <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div className="relative flex-1 max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          value={searchValue}
          onChange={handleSearchChange}
          placeholder={placeholder}
          disabled={isLoading}
          className="w-full rounded-md border border-slate-300 bg-white py-2 pl-10 pr-4 text-sm placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          aria-label="Search table data"
        />
      </div>

      {searchValue && (
        <button
          onClick={handleReset}
          disabled={isLoading}
          className="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          aria-label="Reset filters"
        >
          <X className="h-4 w-4" />
          Reset
        </button>
      )}
    </div>
  );
}
