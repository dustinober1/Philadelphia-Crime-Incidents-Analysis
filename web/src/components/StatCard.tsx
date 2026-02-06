export function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <article className="card">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="text-2xl font-bold text-slate-900">{value}</p>
    </article>
  );
}
