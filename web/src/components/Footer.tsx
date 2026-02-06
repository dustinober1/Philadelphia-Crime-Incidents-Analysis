"use client";

import useSWR from "swr";

import { fetcher } from "@/lib/api";

export function Footer() {
  const { data } = useSWR("/api/v1/metadata", fetcher);
  return (
    <footer className="mt-12 border-t border-slate-200 bg-white/70">
      <div className="mx-auto flex max-w-7xl flex-col gap-1 px-4 py-6 text-sm text-slate-600">
        <p>Source: Philadelphia Police Department, OpenDataPhilly</p>
        <p>Data last updated: {data?.last_updated ? new Date(data.last_updated).toLocaleDateString() : "Loading..."}</p>
        <a className="text-blue-700 underline" href="https://github.com" target="_blank" rel="noreferrer">
          GitHub Repository
        </a>
      </div>
    </footer>
  );
}
