export interface TrendData {
  current: number;
  previous: number;
  label: string;
}

export interface Insight {
  icon: "up" | "down" | "stable";
  text: string;
  type: "concern" | "positive" | "neutral";
}

export interface Narrative {
  summary: string;
  explanation: string;
  insights: Insight[];
  context?: string;
}

export function generateNarrative(data: TrendData): Narrative {
  const change = data.current - data.previous;
  const percentChange = data.previous > 0 ? (change / data.previous) * 100 : 0;
  const isIncrease = change > 0;
  const magnitude = Math.abs(percentChange);

  let summary: string;
  let explanation: string;
  const insights: Insight[] = [];

  if (magnitude > 20) {
    // Significant change
    summary = isIncrease
      ? `Sharp ${increaseVerb(data.label)}: ${formatNumber(change)} more incidents`
      : `Major ${decreaseVerb(data.label)}: ${formatNumber(Math.abs(change))} fewer incidents`;
    explanation = isIncrease
      ? `${data.label} increased by ${percentChange.toFixed(1)}%, marking a significant shift that may warrant attention from community stakeholders.`
      : `${data.label} decreased by ${percentChange.toFixed(1)}%, representing substantial progress in crime reduction efforts.`;
    insights.push({
      icon: isIncrease ? "up" : "down",
      text: `${percentChange.toFixed(1)}% ${isIncrease ? "increase" : "decrease"} compared to previous period`,
      type: isIncrease ? "concern" : "positive",
    });
  } else if (magnitude > 5) {
    // Moderate change
    summary = isIncrease
      ? `${data.label} ${increaseVerb(data.label)}: ${formatNumber(change)} more incidents`
      : `${data.label} ${decreaseVerb(data.label)}: ${formatNumber(Math.abs(change))} fewer incidents`;
    explanation = `${data.label} changed by ${percentChange.toFixed(1)}%, reflecting ${isIncrease ? "an upward" : "a downward"} trend that warrants monitoring.`;
    insights.push({
      icon: isIncrease ? "up" : "down",
      text: `${percentChange.toFixed(1)}% ${isIncrease ? "increase" : "decrease"} year-over-year`,
      type: "neutral",
    });
  } else {
    // Stable
    summary = `${data.label} remains stable: ${formatNumber(data.current)} incidents`;
    explanation = `${data.label} showed minimal change (${percentChange.toFixed(1)}%), indicating stable conditions in this category.`;
    insights.push({
      icon: "stable",
      text: `Stable trend with ${percentChange.toFixed(1)}% variation`,
      type: "neutral",
    });
  }

  // Add contextual insight based on category
  if (data.label.toLowerCase().includes("violent")) {
    insights.push({
      icon: magnitude > 10 && isIncrease ? "up" : "stable",
      text: "Violent crime typically correlates with community resources and policing strategies",
      type: "neutral",
    });
  } else if (data.label.toLowerCase().includes("property")) {
    insights.push({
      icon: magnitude > 10 && isIncrease ? "up" : "stable",
      text: "Property crime often follows economic cycles and seasonal patterns",
      type: "neutral",
    });
  }

  return { summary, explanation, insights };
}

function increaseVerb(label: string): string {
  const lower = label.toLowerCase();
  if (lower.includes("crime")) return "increase in crime";
  if (lower.includes("incident")) return "rise in incidents";
  return "increase";
}

function decreaseVerb(label: string): string {
  const lower = label.toLowerCase();
  if (lower.includes("crime")) return "decrease in crime";
  if (lower.includes("incident")) return "drop in incidents";
  return "decrease";
}

function formatNumber(n: number): string {
  return Math.abs(n).toLocaleString();
}

export function comparePeriods(
  currentData: { [key: string]: number },
  previousData: { [key: string]: number },
): Narrative[] {
  const narratives: Narrative[] = [];

  for (const key of Object.keys(currentData)) {
    const current = currentData[key];
    const previous = previousData[key] ?? 0;
    narratives.push(generateNarrative({ current, previous, label: key }));
  }

  return narratives;
}
