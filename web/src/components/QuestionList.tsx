"use client";

import useSWR from "swr";

import { fetcher } from "@/lib/api";

export function QuestionList() {
  const { data, isLoading } = useSWR("/api/v1/questions?status=answered", fetcher);

  if (isLoading) {
    return <p className="text-sm text-slate-500">Loading answered questions...</p>;
  }

  if (!data?.length) {
    return <p className="rounded border bg-white p-4 text-sm text-slate-600">Questions are being reviewed - check back soon!</p>;
  }

  return (
    <div className="space-y-3">
      {data.slice(0, 10).map((item: any) => (
        <article key={item.id} className="card space-y-2">
          <p className="text-xs text-slate-500">{item.name} - {new Date(item.created_at).toLocaleDateString()}</p>
          <p className="font-medium text-slate-900">{item.question_text}</p>
          <p className="text-sm text-slate-700">{item.answer_text}</p>
        </article>
      ))}
    </div>
  );
}
