export default function Loading() {
  return (
    <div className="max-w-5xl animate-pulse space-y-8">
      {/* Hero Section Skeleton */}
      <div>
        <div className="h-12 w-3/4 rounded bg-slate-200 mb-4" />
        <div className="h-6 w-full rounded bg-slate-100 mb-2" />
        <div className="h-6 w-5/6 rounded bg-slate-100" />
      </div>

      {/* Downloads Section Skeleton */}
      <div className="space-y-4">
        <div className="h-8 w-1/3 rounded bg-slate-200 mb-4" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="rounded-lg border border-slate-200 p-4 space-y-3">
              <div className="h-6 w-2/3 rounded bg-slate-200" />
              <div className="h-4 w-full rounded bg-slate-100" />
              <div className="flex gap-2">
                <div className="h-8 w-24 rounded bg-slate-100" />
                <div className="h-8 w-24 rounded bg-slate-100" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Citations Section Skeleton */}
      <div className="space-y-4">
        <div className="h-8 w-1/4 rounded bg-slate-200 mb-3" />
        <div className="h-4 w-full rounded bg-slate-100 mb-2" />
        <div className="h-4 w-4/5 rounded bg-slate-100" />
      </div>

      {/* Methodology Section Skeleton */}
      <div className="space-y-4">
        <div className="h-8 w-1/4 rounded bg-slate-200 mb-3" />
        <div className="h-4 w-full rounded bg-slate-100 mb-2" />
        <div className="h-4 w-full rounded bg-slate-100 mb-2" />
        <div className="h-4 w-3/4 rounded bg-slate-100" />
      </div>

      <span className="sr-only">Loading Data & Transparency page content...</span>
    </div>
  );
}
