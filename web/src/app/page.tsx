"use client";

import Link from "next/link";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { ChartCard } from "@/components/ChartCard";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { StatCard } from "@/components/StatCard";
import { useAnnualTrends, useMetadata } from "@/lib/api";

export default function HomePage() {
  const { data: metadata } = useMetadata();
  const { data: annual, isLoading } = useAnnualTrends();

  const latestViolent = annual
    ?.filter((row) => row.crime_category === "Violent")
    .sort((a, b) => (a.year ?? 0) - (b.year ?? 0))
    .at(-1)?.count;

  return (
    <div className="space-y-8">
      <section className="rounded-2xl bg-slate-900 p-8 text-white">
        <h1 className="text-3xl font-bold">Explore Crime in Philadelphia</h1>
        <p className="mt-2 max-w-3xl text-slate-200">Track long-term trends, inspect neighborhood-level risk patterns, and review evidence-based policy signals.</p>
      </section>

      <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total incidents" value={metadata ? metadata.total_incidents.toLocaleString() : "..."} />
        <StatCard label="Date range" value={metadata ? `${metadata.date_start} to ${metadata.date_end}` : "..."} />
        <StatCard label="Districts" value="21" />
        <StatCard label="Latest violent count" value={latestViolent ? latestViolent.toLocaleString() : "..."} />
      </section>

      <ChartCard title="Annual trend snapshot" description="Last 10 years of annual incident counts by category.">
        {isLoading ? (
          <LoadingSpinner />
        ) : (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={annual?.slice(-30)}>
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip />
                <Line dataKey="count" stroke="#457B9D" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </ChartCard>

      <section className="grid gap-3 md:grid-cols-3">
        <article className="card">Violent crime has declined from the pandemic-era peak in most recent years.</article>
        <article className="card">Property crime still dominates total incident volume across districts.</article>
        <article className="card">Late-night and weekend intervals remain persistent risk windows.</article>
      </section>

      <section className="grid gap-3 md:grid-cols-5">
        {[
          ["/trends", "Trends"],
          ["/map", "Interactive Map"],
          ["/policy", "Policy"],
          ["/forecast", "Forecast"],
          ["/questions", "Q&A"],
        ].map(([href, label]) => (
          <Link key={href} href={href} className="card text-center font-semibold text-slate-800 hover:bg-slate-50">
            {label}
          </Link>
        ))}
      </section>
    </div>
  );
}
