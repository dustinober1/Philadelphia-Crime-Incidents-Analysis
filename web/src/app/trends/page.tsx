"use client";

import { useMemo, useState } from "react";
import useSWR from "swr";

import { ChartCard } from "@/components/ChartCard";
import { DateRangeFilter } from "@/components/DateRangeFilter";
import { DownloadButton } from "@/components/DownloadButton";
import { TrendChart } from "@/components/charts/TrendChart";
import { fetcher, useAnnualTrends, useMonthlyTrends } from "@/lib/api";

type AnnualSeriesRow = {
  year: number;
  Violent: number;
  Property: number;
  Other: number;
};

type RobberyCell = {
  hour: number;
  day_of_week: number;
  count: number;
};

export default function TrendsPage() {
  const { data: annual = [] } = useAnnualTrends();
  const { data: monthly = [] } = useMonthlyTrends();
  const { data: covid = [] } = useSWR("/api/v1/trends/covid", fetcher);
  const { data: seasonality } = useSWR("/api/v1/trends/seasonality", fetcher);
  const { data: robberyHeat = [] } = useSWR("/api/v1/trends/robbery-heatmap", fetcher);
  const [startYear, setStartYear] = useState(2015);
  const [endYear, setEndYear] = useState(2025);

  const annualSeries = useMemo(() => {
    const byYear = new Map<number, AnnualSeriesRow>();
    annual.forEach((row) => {
      const year = Number(row.year);
      if (!byYear.has(year)) {
        byYear.set(year, { year, Violent: 0, Property: 0, Other: 0 });
      }
      const bucket = byYear.get(year);
      if (!bucket) {
        return;
      }
      const category = row.crime_category;
      if (category === "Violent" || category === "Property" || category === "Other") {
        bucket[category] = row.count;
      } else {
        bucket.Other = row.count;
      }
    });
    return Array.from(byYear.values()).sort((a, b) => a.year - b.year);
  }, [annual]);

  const monthlySeries = useMemo(() => {
    const filtered = monthly.filter((row) => {
      const year = Number(String(row.month).slice(0, 4));
      return year >= startYear && year <= endYear;
    });
    const byMonth = new Map<string, { month: string; Violent: number; Property: number; Other: number }>();
    filtered.forEach((row) => {
      const month = String(row.month).slice(0, 7);
      if (!byMonth.has(month)) {
        byMonth.set(month, { month, Violent: 0, Property: 0, Other: 0 });
      }
      const bucket = byMonth.get(month);
      if (!bucket) {
        return;
      }
      const category = row.crime_category;
      if (category === "Violent" || category === "Property" || category === "Other") {
        bucket[category] = row.count;
      } else {
        bucket.Other = row.count;
      }
    });
    return Array.from(byMonth.values());
  }, [monthly, startYear, endYear]);

  // Metadata for all downloads
  const metadata = {
    export_timestamp: new Date().toISOString(),
    data_version: "v1.0",
    processing_notes: "Aggregated from Philadelphia Police Department data",
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Crime Trends</h1>

      <ChartCard title="Annual trends" description="Violent, Property, and Other incidents by year.">
        <div className="h-72" aria-label="Annual trends chart">
          <TrendChart
            data={annualSeries}
            series={[
              { dataKey: "Violent", color: "#E63946", name: "Violent" },
              { dataKey: "Property", color: "#457B9D", name: "Property" },
              { dataKey: "Other", color: "#A8DADC", name: "Other" },
            ]}
            chartType="line"
            xAxisKey="year"
            showXLabels={true}
          />
        </div>
        <p className="text-sm text-slate-600">Insight: Property incidents drive total volume while violent incidents fluctuate in narrower bands.</p>
        <div className="flex gap-2">
          <DownloadButton data={annualSeries} filename="annual-trends" format="json" metadata={metadata} />
          <DownloadButton data={annualSeries} filename="annual-trends" format="csv" metadata={metadata} />
        </div>
      </ChartCard>

      <ChartCard title="Monthly trends" description="Monthly totals with date range filtering.">
        <DateRangeFilter start={startYear} end={endYear} onStart={setStartYear} onEnd={setEndYear} />
        <div className="h-72" aria-label="Monthly trends chart">
          <TrendChart
            data={monthlySeries}
            series={[
              { dataKey: "Violent", color: "#E63946", name: "Violent", stackId: "1" },
              { dataKey: "Property", color: "#457B9D", name: "Property", stackId: "1" },
              { dataKey: "Other", color: "#A8DADC", name: "Other", stackId: "1" },
            ]}
            chartType="area"
            xAxisKey="month"
            showXLabels={false}
          />
        </div>
        <p className="text-sm text-slate-600">Insight: Seasonal variability recurs year-over-year with mid-summer and late-fall lifts.</p>
        <div className="flex gap-2">
          <DownloadButton data={monthlySeries} filename="monthly-trends" format="json" metadata={metadata} />
          <DownloadButton data={monthlySeries} filename="monthly-trends" format="csv" metadata={metadata} />
        </div>
      </ChartCard>

      <ChartCard title="COVID comparison" description="Pre, during, and post-pandemic totals.">
        <div className="h-64">
          <TrendChart
            data={covid}
            series={[
              { dataKey: "count", color: "#457B9D", name: "Count" },
            ]}
            chartType="bar"
            xAxisKey="period"
            showXLabels={true}
          />
        </div>
        <p className="text-sm text-slate-600">Date ranges: Pre (2006-01-01 to 2020-02-29), During (2020-03-01 to 2021-12-31), Post (2022-01-01 onward).</p>
        <div className="flex gap-2">
          <DownloadButton data={covid as Record<string, unknown>[]} filename="covid-comparison" format="json" metadata={metadata} />
          <DownloadButton data={covid as Record<string, unknown>[]} filename="covid-comparison" format="csv" metadata={metadata} />
        </div>
      </ChartCard>

      <ChartCard title="Seasonality" description="Crime counts by month, day-of-week, and hour.">
        <pre className="overflow-auto rounded bg-slate-50 p-3 text-xs">{JSON.stringify(seasonality, null, 2)}</pre>
        <p className="text-sm text-slate-600">Insight: Hourly concentration increases in evening windows and on weekend days.</p>
        <div className="flex gap-2">
          <DownloadButton data={seasonality as Record<string, unknown>[]} filename="seasonality" format="json" metadata={metadata} />
        </div>
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
                    const hit = (robberyHeat as RobberyCell[]).find(
                      (x) => x.hour === hour && x.day_of_week === d,
                    );
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
        <div className="flex gap-2">
          <DownloadButton data={robberyHeat as Record<string, unknown>[]} filename="robbery-heatmap" format="csv" metadata={metadata} />
        </div>
      </ChartCard>
    </div>
  );
}
