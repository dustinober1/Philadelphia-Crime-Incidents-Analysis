import { ReactNode } from "react";

export function ChartCard({ title, description, children }: { title: string; description: string; children: ReactNode }) {
  return (
    <section className="card space-y-3">
      <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
      <p className="text-sm text-slate-600">{description}</p>
      {children}
    </section>
  );
}
