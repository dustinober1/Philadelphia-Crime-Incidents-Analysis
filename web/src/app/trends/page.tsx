"use client";

import { useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import useSWR from "swr";

import { ChartCard } from "@/components/ChartCard";
import { DateRangeFilter } from "@/components/DateRangeFilter";
import { fetcher, useAnnualTrends, useMonthlyTrends } from "@/lib/api";

export default function TrendsPage() {
  const { data: annual = [] } = useAnnualTrends();
  const { data: monthly = [] } = useMonthlyTrends();
  const { data: covid = [] } = useSWR("/api/v1/trends/covid", fetcher);
  const { data: seasonality } = useSWR("/api/v1/trends/seasonality", fetcher);
  const { data: robberyHeat = [] } = useSWR("/api/v1/trends/robbery-heatmap", fetcher);
  const [startYear, setStartYear] = useState(2015);
  const [endYear, setEndYear] = useState(2025);

  const annualSeries = useMemo(() => {
    const byYear = new Map<number, any>();
    annual.forEach((row) => {
      const year = Number(row.year);
      if (!byYear.has(year)) {
        byYear.set(year, { year, Violent: 0, Property: 0, Other: 0 });
      }
      byYear.get(year)[row.crime_category || "Other"] = row.count;
    });
    return Array.from(byYear.values()).sort((a, b) => a.year - b.year);
  }, [annual]);

  const monthlySeries = useMemo(() => {
    const filtered = monthly.filter((row) => {
      const year = Number(String(row.month).slice(0, 4));
      return year >= startYear && year <= endYear;
    });
    const byMonth = new Map<string, any>();
    filtered.forEach((row) => {
      const month = String(row.month).slice(0, 7);
      if (!byMonth.has(month)) {
        byMonth.set(month, { month, Violent: 0, Property: 0, Other: 0 });
      }
      byMonth.get(month)[row.crime_category || "Other"] = row.count;
    });
    return Array.from(byMonth.values());
  }, [monthly, startYear, endYear]);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Crime Trends</h1>

      <ChartCard title="Annual trends" description="Violent, Property, and Other incidents by year.">
        <div className="h-72" aria-label="Annual trends chart">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={annualSeries}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="Violent" stroke="#E63946" dot={false} />
              <Line type="monotone" dataKey="Property" stroke="#457B9D" dot={false} />
              <Line type="monotone" dataKey="Other" stroke="#A8DADC" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <p className="text-sm text-slate-600">Insight: Property incidents drive total volume while violent incidents fluctuate in narrower bands.</p>
        <a href="/api/v1/trends/annual" className="text-sm text-blue-700 underline">Download data</a>
      </ChartCard>

      <ChartCard title="Monthly trends" description="Monthly totals with date range filtering.">
        <DateRangeFilter start={startYear} end={endYear} onStart={setStartYear} onEnd={setEndYear} />
        <div className="h-72" aria-label="Monthly trends chart">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={monthlySeries}>
              <XAxis dataKey="month" hide />
              <YAxis />
              <Tooltip />
              <Area dataKey="Violent" stackId="1" stroke="#E63946" fill="#E63946" fillOpacity={0.3} />
              <Area dataKey="Property" stackId="1" stroke="#457B9D" fill="#457B9D" fillOpacity={0.3} />
              <Area dataKey="Other" stackId="1" stroke="#A8DADC" fill="#A8DADC" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <p className="text-sm text-slate-600">Insight: Seasonal variability recurs year-over-year with mid-summer and late-fall lifts.</p>
        <a href="/api/v1/trends/monthly" className="text-sm text-blue-700 underline">Download data</a>
      </ChartCard>

      <ChartCard title="COVID comparison" description="Pre, during, and post-pandemic totals.">
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={covid}>
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#457B9D" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p className="text-sm text-slate-600">Date ranges: Pre (2006-01-01 to 2020-02-29), During (2020-03-01 to 2021-12-31), Post (2022-01-01 onward).</p>
        <a href="/api/v1/trends/covid" className="text-sm text-blue-700 underline">Download data</a>
      </ChartCard>

      <ChartCard title="Seasonality" description="Crime counts by month, day-of-week, and hour.">
        <pre className="overflow-auto rounded bg-slate-50 p-3 text-xs">{JSON.stringify(seasonality, null, 2)}</pre>
        <p className="text-sm text-slate-600">Insight: Hourly concentration increases in evening windows and on weekend days.</p>
        <a href="/api/v1/trends/seasonality" className="text-sm text-blue-700 underline">Download data</a>
      </ChartCard>

      <ChartCard title="Robbery hour x day heatmap" description="Robbery counts by hour and weekday.">
        <div className="overflow-auto">
          <table className="w-full border-collapse text-xs">
            <thead>
              <tr>
                <th className="border p-1">Hour</th>
                {[0, 1, 2, 3, 4, 5, 6].map((d) => (<th key={d} className="border p-1">{d}</th>))}
              </tr>
            </thead>
            <tbody>
              {Array.from({ length: 24 }).map((_, hour) => (
                <tr key={hour}>
                  <td className="border p-1">{hour}</td>
                  {[0, 1, 2, 3, 4, 5, 6].map((d) => {
                    const hit = robberyHeat.find((x: any) => x.hour === hour && x.day_of_week === d);
                    const value = hit?.count || 0;
                    const intensity = Math.min(255, 40 + Math.floor(value / 2));
                    return <td key={`${hour}-${d}`} className="border p-1" style={{ backgroundColor: `rgb(${intensity}, ${245 - intensity / 2}, ${245 - intensity / 2})` }}>{value}</td>;
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-sm text-slate-600">Insight: Peak robbery intensity clusters around evening commuter and nightlife hours.</p>
        <a href="/api/v1/trends/robbery-heatmap" className="text-sm text-blue-700 underline">Download data</a>
      </ChartCard>
    </div>
  );
}
