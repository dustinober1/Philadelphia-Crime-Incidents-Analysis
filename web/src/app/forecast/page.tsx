"use client";

import { Area, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis, Bar, BarChart } from "recharts";
import useSWR from "swr";

import { ChartCard } from "@/components/ChartCard";
import { fetcher, type FeatureImportance, type ForecastResponse } from "@/lib/api";

export default function ForecastPage() {
  const { data: forecast } = useSWR<ForecastResponse>("/api/v1/forecasting/time-series", fetcher);
  const { data: features = [] } = useSWR<FeatureImportance[]>(
    "/api/v1/forecasting/classification",
    fetcher,
  );

  const chartData = [
    ...(forecast?.historical?.map((row) => ({
      ds: row.ds,
      historical: row.y,
      forecast: null,
      low: null,
      high: null,
    })) ?? []),
    ...(forecast?.forecast?.map((row) => ({
      ds: row.ds,
      historical: null,
      forecast: row.yhat,
      low: row.yhat_lower,
      high: row.yhat_upper,
    })) ?? []),
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Forecasting</h1>
      <ChartCard title="Time series forecast" description="Historical observations and projected values with confidence bands.">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData}>
              <XAxis dataKey="ds" hide />
              <YAxis />
              <Tooltip />
              <Area dataKey="high" stroke="none" fill="#bfdbfe" fillOpacity={0.45} />
              <Area dataKey="low" stroke="none" fill="#ffffff" fillOpacity={1} />
              <Line dataKey="historical" stroke="#1f2937" dot={false} />
              <Line dataKey="forecast" stroke="#2563eb" strokeDasharray="5 5" dot={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
        <p className="text-sm text-slate-600">Historical values are solid; forecast values are dashed with uncertainty shading.</p>
        <p className="text-sm text-slate-600">Model note: Prophet captures trend/seasonality but is not a guarantee of future incidents.</p>
      </ChartCard>

      <ChartCard title="Violence classification insights" description="Top feature importances from violence/non-violence classification.">
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart layout="vertical" data={features}>
              <XAxis type="number" />
              <YAxis type="category" dataKey="feature" width={120} />
              <Tooltip />
              <Bar dataKey="importance" fill="#E63946" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p className="text-sm text-slate-600">These drivers reflect statistical signal strength, not causal certainty.</p>
      </ChartCard>

      <p className="text-sm text-slate-500">Methodology limitations: model quality depends on historic reporting patterns and available features.</p>
    </div>
  );
}
