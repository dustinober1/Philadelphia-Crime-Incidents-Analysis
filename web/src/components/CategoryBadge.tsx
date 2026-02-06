const colors: Record<string, string> = {
  Violent: "bg-red-100 text-red-700",
  Property: "bg-blue-100 text-blue-700",
  Other: "bg-cyan-100 text-cyan-700",
};

export function CategoryBadge({ category }: { category: string }) {
  return <span className={`rounded-full px-2 py-1 text-xs font-medium ${colors[category] ?? "bg-slate-100 text-slate-700"}`}>{category}</span>;
}
