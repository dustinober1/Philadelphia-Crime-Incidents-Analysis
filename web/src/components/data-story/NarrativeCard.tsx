import { BookOpen } from "lucide-react";

import type { Narrative } from "@/lib/narratives";

import { InsightBox } from "./InsightBox";

interface NarrativeCardProps {
  narrative: Narrative;
  title?: string;
}

export function NarrativeCard({ narrative, title = "Analysis" }: NarrativeCardProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5">
      <h4 className="mb-3 flex items-center gap-2 font-semibold text-slate-900">
        <BookOpen className="h-5 w-5 text-blue-500" />
        {title}
      </h4>

      <div className="space-y-3">
        {/* Summary */}
        <div>
          <h5 className="text-sm font-medium text-slate-700">Summary</h5>
          <p className="mt-1 text-sm text-slate-900">{narrative.summary}</p>
        </div>

        {/* Explanation */}
        <div>
          <h5 className="text-sm font-medium text-slate-700">Explanation</h5>
          <p className="mt-1 text-sm text-slate-600">{narrative.explanation}</p>
        </div>

        {/* Context (optional) */}
        {narrative.context && (
          <div>
            <h5 className="text-sm font-medium text-slate-700">Context</h5>
            <p className="mt-1 text-sm text-slate-600">{narrative.context}</p>
          </div>
        )}

        {/* Insights */}
        {narrative.insights.length > 0 && (
          <InsightBox insights={narrative.insights} title="Key Insights" />
        )}
      </div>
    </div>
  );
}
