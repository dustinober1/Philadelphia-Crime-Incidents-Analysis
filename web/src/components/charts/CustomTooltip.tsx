import type { TooltipProps } from "recharts";

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    name?: string;
    value?: number;
    color?: string;
    dataKey?: string;
    payload?: any;
  }>;
  label?: string | number;
  historicalAverage?: number;
}

/**
 * CustomTooltip - Reusable Recharts tooltip component
 * 
 * Displays:
 * - Date/period label
 * - Value with proper formatting
 * - Percent change from previous period
 * - Comparison to historical average (if available)
 */
export function CustomTooltip({ 
  active, 
  payload, 
  label, 
  historicalAverage 
}: CustomTooltipProps) {
  // Return null if tooltip is not active or no data
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  // Calculate percent change from previous period
  const calculatePercentChange = (currentValue: number, index: number): number | null => {
    // We can't calculate percent change for the first data point
    if (index === 0) {
      return null;
    }
    
    // Access previous value from the same series
    // This assumes payload structure from Recharts
    const prevValue = (payload[0].payload as any)?.previousValue;
    
    if (prevValue === undefined || prevValue === null || prevValue === 0) {
      return null;
    }
    
    return ((currentValue - prevValue) / prevValue) * 100;
  };

  // Format number with locale string
  const formatNumber = (value: number): string => {
    return value.toLocaleString('en-US', { maximumFractionDigits: 0 });
  };

  // Format percent change with color
  const formatPercentChange = (change: number | null) => {
    if (change === null) {
      return null;
    }
    
    const isPositive = change > 0;
    const color = isPositive ? 'text-red-600' : 'text-green-600';
    const sign = isPositive ? '+' : '';
    
    return (
      <span className={color}>
        {sign}{change.toFixed(1)}%
      </span>
    );
  };

  // Calculate comparison to historical average
  const formatHistoricalComparison = (currentValue: number) => {
    if (!historicalAverage || historicalAverage === 0) {
      return null;
    }
    
    const diff = ((currentValue - historicalAverage) / historicalAverage) * 100;
    const isAbove = diff > 0;
    
    return (
      <div className="text-xs text-gray-500 mt-1">
        {isAbove ? '↑' : '↓'} {Math.abs(diff).toFixed(1)}% vs. avg ({formatNumber(historicalAverage)})
      </div>
    );
  };

  return (
    <div 
      className="bg-white border border-gray-300 rounded-lg shadow-lg p-3"
      role="tooltip"
      aria-live="polite"
    >
      {/* Period label */}
      <div className="font-semibold text-sm mb-2 text-gray-900">
        {label}
      </div>
      
      {/* Data series */}
      {payload.map((entry, index) => {
        const value = entry.value as number;
        const percentChange = calculatePercentChange(value, index);
        
        return (
          <div key={entry.name} className="space-y-1">
            {/* Series name and value */}
            <div className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-sm" 
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-sm font-medium text-gray-700">
                {entry.name}:
              </span>
              <span className="text-sm font-bold text-gray-900">
                {formatNumber(value)}
              </span>
            </div>
            
            {/* Percent change */}
            {percentChange !== null && (
              <div className="text-xs ml-5">
                Change: {formatPercentChange(percentChange)}
              </div>
            )}
            
            {/* Historical comparison */}
            {index === 0 && formatHistoricalComparison(value)}
          </div>
        );
      })}
    </div>
  );
}
