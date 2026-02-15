export default function Loading() {
  return (
    <div className="max-w-4xl animate-pulse">
      <div className="h-12 w-3/4 rounded bg-slate-200 mb-6" />
      <div className="h-6 w-full rounded bg-slate-100 mb-4" />
      <div className="h-6 w-5/6 rounded bg-slate-100 mb-4" />
      <div className="space-y-8 mt-8">
        <div>
          <div className="h-8 w-1/3 rounded bg-slate-200 mb-3" />
          <div className="h-4 w-full rounded bg-slate-100 mb-2" />
          <div className="h-4 w-full rounded bg-slate-100 mb-2" />
          <div className="h-4 w-4/5 rounded bg-slate-100" />
        </div>
        <div>
          <div className="h-8 w-1/3 rounded bg-slate-200 mb-3" />
          <div className="h-4 w-full rounded bg-slate-100 mb-2" />
          <div className="h-4 w-full rounded bg-slate-100 mb-2" />
          <div className="h-4 w-3/4 rounded bg-slate-100" />
        </div>
      </div>
      <span className="sr-only">Loading about page content...</span>
    </div>
  );
}
