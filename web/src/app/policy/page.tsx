"use client";

import { Bar, BarChart, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import useSWR from "swr";

import { ChartCard } from "@/components/ChartCard";
import { fetcher } from "@/lib/api";

export default function PolicyPage() {
  const { data: retail = [] } = useSWR("/api/v1/policy/retail-theft", fetcher);
  const { data: vehicle = [] } = useSWR("/api/v1/policy/vehicle-crimes", fetcher);
  const { data: composition = [] } = useSWR("/api/v1/policy/composition", fetcher);
  const { data: events = [] } = useSWR("/api/v1/policy/events", fetcher);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Policy Analysis</h1>
      <ChartCard title="Retail theft trends" description="Monthly retail theft counts.">
        <div className="h-72"><ResponsiveContainer width="100%" height="100%"><LineChart data={retail}><XAxis dataKey="month" hide /><YAxis /><Tooltip /><Line dataKey="count" stroke="#E63946" dot={false} /></LineChart></ResponsiveContainer></div>
        <p className="text-sm text-slate-600">Retail theft remains elevated relative to the pre-pandemic baseline in multiple periods.</p>
      </ChartCard>

      <ChartCard title="Vehicle crime trends" description="Monthly vehicle crime counts.">
        <div className="h-72"><ResponsiveContainer width="100%" height="100%"><LineChart data={vehicle}><XAxis dataKey="month" hide /><YAxis /><Tooltip /><Line dataKey="count" stroke="#457B9D" dot={false} /></LineChart></ResponsiveContainer></div>
        <p className="text-sm text-slate-600">Vehicle crime volatility aligns with corridor activity and seasonal movement patterns.</p>
      </ChartCard>

      <ChartCard title="Crime composition" description="Category share by year.">
        <div className="h-72"><ResponsiveContainer width="100%" height="100%"><BarChart data={composition}><XAxis dataKey="year" /><YAxis /><Tooltip /><Legend /><Bar dataKey="count" fill="#A8DADC" /></BarChart></ResponsiveContainer></div>
        <p className="text-sm text-slate-600">Property categories account for the largest share in most years.</p>
      </ChartCard>

      <ChartCard title="Event impact" description="Event-day vs control-day comparisons with uncertainty columns.">
        <pre className="overflow-auto rounded bg-slate-50 p-3 text-xs">{JSON.stringify(events.slice(0, 8), null, 2)}</pre>
        <p className="text-sm text-slate-600">Methodology uses matched control days similar to utilities in `analysis/event_utils.py`.</p>
      </ChartCard>
    </div>
  );
}
