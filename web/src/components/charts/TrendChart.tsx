"use client";

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
import { CustomTooltip } from "./CustomTooltip";

export type ChartType = "line" | "bar" | "area";

export interface SeriesConfig {
  dataKey: string;
  color: string;
  name: string;
  stackId?: string;
}

export interface TrendChartProps {
  data: Record<string, unknown>[];
  series: SeriesConfig[];
  chartType?: ChartType;
  xAxisKey?: string;
  showXLabels?: boolean;
  historicalAverage?: number;
  height?: number | `${number}%`;
}

/**
 * TrendChart - Unified chart component for line, bar, and area charts
 * 
 * Features:
 * - Supports multiple data series with distinct colors
 * - Responsive sizing via ResponsiveContainer
 * - Custom tooltip with percent change and historical comparison
 * - Empty state handling
 * - Configurable chart type (line, bar, area)
 */
export function TrendChart({
  data,
  series,
  chartType = "line",
  xAxisKey = "month",
  showXLabels = true,
  historicalAverage,
  height = "100%" as const,
}: TrendChartProps) {
  // Handle empty state
  if (!data || data.length === 0) {
    return (
      <div 
        className="flex items-center justify-center h-full min-h-[200px] text-gray-500"
        role="status"
        aria-live="polite"
      >
        <p>No data available for the selected period.</p>
      </div>
    );
  }

  // Render appropriate chart based on type
  const renderChart = () => {
    const commonProps = {
      data,
    };

    const axisProps = {
      xAxis: (
        <XAxis 
          dataKey={xAxisKey} 
          hide={!showXLabels}
        />
      ),
      yAxis: <YAxis />,
      grid: <CartesianGrid strokeDasharray="3 3" />,
      tooltip: <Tooltip content={<CustomTooltip historicalAverage={historicalAverage} />} />,
      legend: <Legend />,
    };

    switch (chartType) {
      case "line":
        return (
          <LineChart {...commonProps}>
            {axisProps.grid}
            {axisProps.xAxis}
            {axisProps.yAxis}
            {axisProps.tooltip}
            {axisProps.legend}
            {series.map((s) => (
              <Line
                key={s.dataKey}
                type="monotone"
                dataKey={s.dataKey}
                stroke={s.color}
                name={s.name}
                dot={false}
              />
            ))}
          </LineChart>
        );

      case "area":
        return (
          <AreaChart {...commonProps}>
            {axisProps.xAxis}
            {axisProps.yAxis}
            {axisProps.tooltip}
            {series.map((s) => (
              <Area
                key={s.dataKey}
                dataKey={s.dataKey}
                stackId={s.stackId}
                stroke={s.color}
                fill={s.color}
                fillOpacity={0.3}
                name={s.name}
              />
            ))}
          </AreaChart>
        );

      case "bar":
        return (
          <BarChart {...commonProps}>
            {axisProps.xAxis}
            {axisProps.yAxis}
            {axisProps.tooltip}
            {series.map((s) => (
              <Bar
                key={s.dataKey}
                dataKey={s.dataKey}
                fill={s.color}
                name={s.name}
              />
            ))}
          </BarChart>
        );

      default:
        return null;
    }
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      {renderChart()}
    </ResponsiveContainer>
  );
}
