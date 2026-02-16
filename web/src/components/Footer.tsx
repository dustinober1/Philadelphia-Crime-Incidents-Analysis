"use client";

import Link from "next/link";
import useSWR from "swr";

import { fetcher } from "@/lib/api";

export function Footer() {
  const { data } = useSWR("/api/v1/metadata", fetcher);
  
  return (
    <footer className="mt-auto border-t border-slate-200 bg-white/70">
      <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-3 text-sm text-slate-700 sm:gap-2">
          {/* Primary attribution */}
          <div className="flex flex-col gap-1">
            <p className="font-semibold text-slate-900">
              Data Source
            </p>
            <p>
              Philadelphia Police Department, OpenDataPhilly
            </p>
          </div>
          
          {/* Update timestamp */}
          <p className="text-slate-600">
            Last updated:{" "}
            {data?.last_updated 
              ? new Date(data.last_updated).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })
              : "Loading..."}
          </p>
          
          {/* External links with touch-friendly spacing */}
          <div className="mt-2 flex flex-wrap gap-4">
            <Link
              className="inline-flex min-h-[44px] items-center text-blue-700 underline underline-offset-2 hover:text-blue-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
              href="/data"
            >
              Data
            </Link>
            <a
              className="inline-flex min-h-[44px] items-center text-blue-700 underline underline-offset-2 hover:text-blue-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
            >
              GitHub Repository
            </a>
            <a
              className="inline-flex min-h-[44px] items-center text-blue-700 underline underline-offset-2 hover:text-blue-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
              href="https://www.opendataphilly.org/"
              target="_blank"
              rel="noreferrer"
            >
              OpenDataPhilly
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
