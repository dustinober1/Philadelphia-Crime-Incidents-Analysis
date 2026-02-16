"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import useSWR from "swr";

import { ChartCard } from "@/components/ChartCard";
import { NarrativeCard } from "@/components/data-story/NarrativeCard";
import { InsightBox } from "@/components/data-story/InsightBox";
import { AdvancedFilters } from "@/components/filters/AdvancedFilters";
import { useFilteredData } from "@/hooks/useFilteredData";
import { generateNarrative } from "@/lib/narratives";
import type { Insight } from "@/lib/narratives";
import type { FilterState } from "@/lib/types";
import { fetcher } from "@/lib/api";

const TrendChart = dynamic(
  () => import("@/components/charts/TrendChart").then((mod) => ({ default: mod.TrendChart })),
  {
    loading: () => <div className="h-72 animate-pulse rounded bg-slate-100" />,
    ssr: false,
  },
);

type AnnualSeriesRow = {
  year: number;
  Violent: number;
  Property: number;
  Other: number;
};

function getInitialFilters(searchParams: URLSearchParams): FilterState {
  const start = searchParams.get("start");
  const end = searchParams.get("end");
  const districts =
    searchParams
      .get("districts")
      ?.split(",")
      .map((value) => Number(value))
      .filter((value) => Number.isFinite(value) && value > 0) ?? [];
  const categories =
    searchParams
      .get("categories")
      ?.split(",")
      .filter((value) => value.length > 0) as FilterState["categories"]; // runtime-validated by AdvancedFilters

  return {
    dateRange: start && end ? { start, end } : null,
    districts,
    categories: categories ?? [],
  };
}

type RobberyCell = {
  hour: number;
  day_of_week: number;
  count: number;
};

export default function TrendsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const [filters, setFilters] = useState<FilterState>(() => getInitialFilters(searchParams));

  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());

    if (filters.dateRange?.start && filters.dateRange?.end) {
      params.set("start", filters.dateRange.start);
      params.set("end", filters.dateRange.end);
    } else {
      params.delete("start");
      params.delete("end");
    }

    if (filters.districts.length > 0) {
      params.set("districts", filters.districts.join(","));
    } else {
      params.delete("districts");
    }

    if (filters.categories.length > 0) {
      params.set("categories", filters.categories.join(","));
    } else {
      params.delete("categories");
    }

    const queryString = params.toString();
    const nextUrl = queryString.length > 0 ? `${pathname}?${queryString}` : pathname;
    const currentUrl = searchParams.toString().length > 0 ? `${pathname}?${searchParams.toString()}` : pathname;

    if (nextUrl !== currentUrl) {
      router.replace(nextUrl, { scroll: false });
    }
  }, [filters, pathname, router, searchParams]);

  const annual = useFilteredData("/api/v1/trends/annual", filters);
  const monthly = useFilteredData("/api/v1/trends/monthly", filters);

  const { data: covid = [] } = useSWR("/api/v1/trends/covid", fetcher);
  const { data: seasonality } = useSWR("/api/v1/trends/seasonality", fetcher);
  const { data: robberyHeat = [] } = useSWR("/api/v1/trends/robbery-heatmap", fetcher);

  const annualSeries = useMemo(() => {
    const byYear = new Map<number, AnnualSeriesRow>();
    annual.data.forEach((row) => {
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
  }, [annual.data]);

  // Narrative insights derived from filtered annual series
  const annualNarratives = useMemo(() => {
    if (annualSeries.length < 2) return [];

    const latest = annualSeries[annualSeries.length - 1];
    const previous = annualSeries[annualSeries.length - 2];

    return [
      generateNarrative({ current: latest.Violent, previous: previous.Violent, label: "Violent Crime" }),
      generateNarrative({ current: latest.Property, previous: previous.Property, label: "Property Crime" }),
      generateNarrative({ current: latest.Other, previous: previous.Other, label: "Other Incidents" }),
    ];
  }, [annualSeries]);

  const filterInsights: Insight[] = useMemo(() => {
    const insights: Insight[] = [];

    const districtCount = filters.districts.length;
    if (districtCount === 1) {
      insights.push({
        icon: "stable",
        type: "neutral",
        text: `Showing District ${filters.districts[0]} data. Annual and monthly charts reflect district-specific trends.`,
      });
      insights.push({
        icon: "stable",
        type: "neutral",
        text: "COVID comparison and seasonality charts show citywide patterns (inherently citywide analyses).",
      });
    } else if (districtCount > 1) {
      insights.push({
        icon: "stable",
        type: "neutral",
        text: `${districtCount} districts selected. Showing citywide data filtered client-side.`,
      });
    }

    const categoryCount = filters.categories.length;
    if (categoryCount > 0) {
      insights.push({
        icon: "stable",
        type: "neutral",
        text: `Viewing ${categoryCount} selected crime categor${categoryCount === 1 ? "y" : "ies"} in the time series.`,
      });
    }

    if (annualSeries.length < 2) {
      insights.push({
        icon: "stable",
        type: "neutral",
        text: "Select a broader date range to enable year-over-year comparison narratives.",
      });
    }

    return insights;
  }, [annualSeries.length, filters.categories.length, filters.districts]);

  const monthlySeries = useMemo(() => {
    const byMonth = new Map<string, { month: string; Violent: number; Property: number; Other: number }>();
    monthly.data.forEach((row) => {
      const monthValue = row.month;
      if (!monthValue) return;
      const month = String(monthValue).slice(0, 7);
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
  }, [monthly.data]);

  const monthlyInsights: Insight[] = useMemo(() => {
    const insights: Insight[] = [];

    if (monthlySeries.length === 0) {
      insights.push({
        icon: "stable",
        type: "neutral",
        text: "No monthly data available for the selected filters.",
      });
      return insights;
    }

    // Find the most recent month
    const latest = monthlySeries[monthlySeries.length - 1];
    const previous = monthlySeries.length > 1 ? monthlySeries[monthlySeries.length - 2] : null;

    if (previous) {
      const latestTotal = (latest.Violent ?? 0) + (latest.Property ?? 0) + (latest.Other ?? 0);
      const prevTotal = (previous.Violent ?? 0) + (previous.Property ?? 0) + (previous.Other ?? 0);
      const change = latestTotal - prevTotal;
      const pctChange = prevTotal > 0 ? (change / prevTotal) * 100 : 0;

      if (Math.abs(pctChange) > 10) {
        insights.push({
          icon: change > 0 ? "up" : "down",
          type: change > 0 ? "concern" : "positive",
          text: `${latest.month}: ${Math.abs(pctChange).toFixed(1)}% ${change > 0 ? "increase" : "decrease"} vs prior month (${Math.abs(change)} incidents).`,
        });
      } else {
        insights.push({
          icon: "stable",
          type: "neutral",
          text: `${latest.month}: Stable month-over-month trend with ${pctChange.toFixed(1)}% change.`,
        });
      }
    }

    // Seasonality insight
    insights.push({
      icon: "stable",
      type: "neutral",
      text: "Monthly totals show seasonal patterns with mid-summer and late-fall peaks typical of urban crime cycles.",
    });

    return insights;
  }, [monthlySeries]);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Crime Trends</h1>

      <AdvancedFilters
        filters={filters}
        onChange={setFilters}
        resultCount={annual.filteredCount}
        totalCount={annual.totalCount}
      />

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

        {/* Narrative analysis */}
        <div className="mt-4 space-y-3">
          <h3 className="text-sm font-semibold text-slate-700">Year-over-Year Analysis</h3>

          {annualNarratives.length > 0 ? (
            annualNarratives.map((narrative, idx) => (
              <NarrativeCard key={idx} narrative={narrative} title={idx === 0 ? "Violent Crime" : idx === 1 ? "Property Crime" : "Other Incidents"} />
            ))
          ) : (
            <InsightBox
              title="Not enough data for comparison"
              insights={[
                {
                  icon: "stable",
                  type: "neutral",
                  text: "Widen your date range or clear filters so at least two years are available for year-over-year narratives.",
                },
              ]}
            />
          )}

          {filterInsights.length > 0 && <InsightBox title="Current filter context" insights={filterInsights} />}
        </div>

        <a href="/api/v1/trends/annual" className="text-sm text-blue-700 underline">Download data</a>
      </ChartCard>

      <ChartCard title="Monthly trends" description="Monthly totals with date range filtering.">
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

        <div className="mt-4">
          <InsightBox title="Monthly Insights" insights={monthlyInsights} />
        </div>

        <a href="/api/v1/trends/monthly" className="text-sm text-blue-700 underline">Download data</a>
      </ChartCard>

      <ChartCard title="COVID comparison" description="Pre, during, and post-pandemic totals (citywide).">
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
        <p className="text-xs text-slate-500 italic">This analysis compares pandemic periods at citywide level.</p>
        <a href="/api/v1/trends/covid" className="text-sm text-blue-700 underline">Download data</a>
      </ChartCard>

      <ChartCard title="Seasonality" description="Crime counts by month, day-of-week, and hour (citywide).">
        <pre className="overflow-auto rounded bg-slate-50 p-3 text-xs">{JSON.stringify(seasonality, null, 2)}</pre>
        <p className="text-sm text-slate-600">Insight: Hourly concentration increases in evening windows and on weekend days.</p>
        <p className="text-xs text-slate-500 italic">Seasonality patterns are analyzed at citywide level.</p>
        <a href="/api/v1/trends/seasonality" className="text-sm text-blue-700 underline">Download data</a>
      </ChartCard>

      <ChartCard title="Robbery hour x day heatmap" description="Robbery counts by hour and weekday (citywide).">
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
        <p className="text-xs text-slate-500 italic">Temporal heatmap patterns are analyzed at citywide level.</p>
        <a href="/api/v1/trends/robbery-heatmap" className="text-sm text-blue-700 underline">Download data</a>
      </ChartCard>
    </div>
  );
}
