"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Bar, BarChart, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useMemo, useState } from "react";
import useSWR from "swr";

import { ChartCard } from "@/components/ChartCard";
import { DataTable } from "@/components/tables/DataTable";
import { DownloadButton } from "@/components/DownloadButton";
import { TableFilters } from "@/components/tables/TableFilters";
import { fetcher } from "@/lib/api";

interface CompositionRow {
  year: number;
  crime_category: string;
  count: number;
}

export default function PolicyPage() {
  const { data: retail = [] } = useSWR("/api/v1/policy/retail-theft", fetcher);
  const { data: vehicle = [] } = useSWR("/api/v1/policy/vehicle-crimes", fetcher);
  const { data: composition = [] } = useSWR<CompositionRow[]>("/api/v1/policy/composition", fetcher);
  const { data: events = [] } = useSWR("/api/v1/policy/events", fetcher);

  const [searchFilter, setSearchFilter] = useState("");

  // Calculate total count per year for percentage calculation
  const compositionWithPercentage = useMemo(() => {
    const yearTotals = composition.reduce((acc, row) => {
      acc[row.year] = (acc[row.year] || 0) + row.count;
      return acc;
    }, {} as Record<number, number>);

    return composition.map((row) => ({
      ...row,
      percentage: yearTotals[row.year]
        ? ((row.count / yearTotals[row.year]) * 100).toFixed(1)
        : "0.0",
    }));
  }, [composition]);

  // Filter data based on search
  const filteredComposition = useMemo(() => {
    if (!searchFilter) return compositionWithPercentage;
    const lower = searchFilter.toLowerCase();
    return compositionWithPercentage.filter(
      (row) =>
        row.year.toString().includes(lower) ||
        row.crime_category.toLowerCase().includes(lower) ||
        row.count.toString().includes(lower) ||
        row.percentage.includes(lower)
    );
  }, [compositionWithPercentage, searchFilter]);

  // Define columns for composition table
  const columns = useMemo<ColumnDef<CompositionRow & { percentage: string }>[]>(
    () => [
      {
        accessorKey: "year",
        header: "Year",
        cell: (info) => info.getValue(),
      },
      {
        accessorKey: "crime_category",
        header: "Crime Category",
        cell: (info) => info.getValue(),
      },
      {
        accessorKey: "count",
        header: "Count",
        cell: (info) => info.getValue<number>().toLocaleString(),
      },
      {
        accessorKey: "percentage",
        header: "Percentage",
        cell: (info) => `${info.getValue()}%`,
      },
    ],
    []
  );

  // Metadata for all downloads
  const metadata = {
    export_timestamp: new Date().toISOString(),
    data_version: "v1.0",
    processing_notes: "Aggregated from Philadelphia Police Department data",
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Policy Analysis</h1>
      <ChartCard title="Retail theft trends" description="Monthly retail theft counts.">
        <div className="h-72"><ResponsiveContainer width="100%" height="100%"><LineChart data={retail}><XAxis dataKey="month" hide /><YAxis /><Tooltip /><Line dataKey="count" stroke="#E63946" dot={false} /></LineChart></ResponsiveContainer></div>
        <p className="text-sm text-slate-600">Retail theft remains elevated relative to the pre-pandemic baseline in multiple periods.</p>
        <div className="flex gap-2">
          <DownloadButton data={retail as Record<string, unknown>[]} filename="retail-theft-trends" format="json" metadata={metadata} />
          <DownloadButton data={retail as Record<string, unknown>[]} filename="retail-theft-trends" format="csv" metadata={metadata} />
        </div>
      </ChartCard>

      <ChartCard title="Vehicle crime trends" description="Monthly vehicle crime counts.">
        <div className="h-72"><ResponsiveContainer width="100%" height="100%"><LineChart data={vehicle}><XAxis dataKey="month" hide /><YAxis /><Tooltip /><Line dataKey="count" stroke="#457B9D" dot={false} /></LineChart></ResponsiveContainer></div>
        <p className="text-sm text-slate-600">Vehicle crime volatility aligns with corridor activity and seasonal movement patterns.</p>
        <div className="flex gap-2">
          <DownloadButton data={vehicle as Record<string, unknown>[]} filename="vehicle-crime-trends" format="json" metadata={metadata} />
          <DownloadButton data={vehicle as Record<string, unknown>[]} filename="vehicle-crime-trends" format="csv" metadata={metadata} />
        </div>
      </ChartCard>

      <ChartCard title="Crime composition" description="Category share by year.">
        <div className="h-72"><ResponsiveContainer width="100%" height="100%"><BarChart data={composition}><XAxis dataKey="year" /><YAxis /><Tooltip /><Legend /><Bar dataKey="count" fill="#A8DADC" /></BarChart></ResponsiveContainer></div>
        <p className="text-sm text-slate-600">Property categories account for the largest share in most years.</p>
        <div className="flex gap-2">
          <DownloadButton data={compositionWithPercentage as Record<string, unknown>[]} filename="crime-composition" format="json" metadata={metadata} />
          <DownloadButton data={compositionWithPercentage as Record<string, unknown>[]} filename="crime-composition" format="csv" metadata={metadata} />
        </div>
      </ChartCard>

      <ChartCard title="Composition data table" description="Sortable and filterable view of crime category shares by year.">
        <TableFilters
          onSearchChange={setSearchFilter}
          onReset={() => setSearchFilter("")}
          placeholder="Search by year, category, count, or percentage..."
        />
        <DataTable
          data={filteredComposition}
          columns={columns}
          pageSize={25}
          emptyMessage="No composition data matches your search"
        />
      </ChartCard>

      <ChartCard title="Event impact" description="Event-day vs control-day comparisons with uncertainty columns.">
        <pre className="overflow-auto rounded bg-slate-50 p-3 text-xs">{JSON.stringify(events.slice(0, 8), null, 2)}</pre>
        <p className="text-sm text-slate-600">Methodology uses matched control days similar to utilities in `analysis/event_utils.py`.</p>
        <div className="flex gap-2">
          <DownloadButton data={events as Record<string, unknown>[]} filename="event-impact" format="json" metadata={metadata} />
        </div>
      </ChartCard>
    </div>
  );
}
