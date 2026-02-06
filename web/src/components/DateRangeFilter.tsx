"use client";

export function DateRangeFilter({
  start,
  end,
  onStart,
  onEnd,
}: {
  start: number;
  end: number;
  onStart: (value: number) => void;
  onEnd: (value: number) => void;
}) {
  return (
    <div className="flex flex-wrap gap-3 text-sm">
      <label className="flex items-center gap-2">
        Start year
        <input className="rounded border px-2 py-1" type="number" value={start} onChange={(e) => onStart(Number(e.target.value))} />
      </label>
      <label className="flex items-center gap-2">
        End year
        <input className="rounded border px-2 py-1" type="number" value={end} onChange={(e) => onEnd(Number(e.target.value))} />
      </label>
    </div>
  );
}
