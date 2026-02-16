import {
  AlertTriangle,
  CheckCircle,
  Info,
  Minus,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

import type { Insight } from "@/lib/narratives";

interface InsightBoxProps {
  insights: Insight[];
  title?: string;
}

const iconMap = {
  up: TrendingUp,
  down: TrendingDown,
  stable: Minus,
};

const typeConfig = {
  concern: {
    icon: AlertTriangle,
    bgColor: "bg-amber-50",
    borderColor: "border-amber-200",
    textColor: "text-amber-900",
  },
  positive: {
    icon: CheckCircle,
    bgColor: "bg-emerald-50",
    borderColor: "border-emerald-200",
    textColor: "text-emerald-900",
  },
  neutral: {
    icon: Info,
    bgColor: "bg-blue-50",
    borderColor: "border-blue-200",
    textColor: "text-blue-900",
  },
};

export function InsightBox({ insights, title = "Key Insights" }: InsightBoxProps) {
  if (insights.length === 0) return null;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <h4 className="mb-3 flex items-center gap-2 font-semibold text-slate-900">
        <Info className="h-5 w-5 text-blue-500" />
        {title}
      </h4>
      <ul className="space-y-2">
        {insights.map((insight, index) => {
          const config = typeConfig[insight.type];
          const TrendIcon = iconMap[insight.icon];
          const TypeIcon = config.icon;

          return (
            <li
              key={index}
              className={`flex items-start gap-3 rounded-md border ${config.borderColor} ${config.bgColor} px-3 py-2`}
            >
              <TypeIcon
                className={`mt-0.5 h-4 w-4 flex-shrink-0 ${config.textColor}`}
              />
              <TrendIcon
                className={`mt-0.5 h-4 w-4 flex-shrink-0 ${
                  insight.icon === "up"
                    ? "text-red-500"
                    : insight.icon === "down"
                      ? "text-emerald-500"
                      : "text-slate-400"
                }`}
              />
              <span className={`text-sm ${config.textColor}`}>{insight.text}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
