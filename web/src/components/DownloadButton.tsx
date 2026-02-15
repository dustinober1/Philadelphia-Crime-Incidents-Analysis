"use client";

import { Download } from "lucide-react";
import { downloadAsJson, downloadAsCsv } from "@/lib/csv-export";

export interface DownloadButtonProps {
  data: Record<string, unknown>[];
  filename: string;
  format: "json" | "csv";
  metadata?: Record<string, unknown>;
}

/**
 * DownloadButton - Reusable button for downloading data as JSON or CSV
 */
export function DownloadButton({
  data,
  filename,
  format,
  metadata,
}: DownloadButtonProps) {
  const handleClick = () => {
    // Merge metadata into data if provided
    const exportData = metadata
      ? [{ _metadata: metadata }, ...data]
      : data;

    if (format === "json") {
      downloadAsJson(exportData, filename);
    } else {
      // For CSV, extract metadata as a separate comment or skip it
      // since CSV doesn't support nested structures well
      downloadAsCsv(data, filename);
    }
  };

  const label = format === "json" ? "Download JSON" : "Download CSV";

  return (
    <button
      onClick={handleClick}
      className="inline-flex items-center gap-2 rounded px-3 py-2 text-sm text-blue-700 hover:bg-blue-50 transition-colors"
      type="button"
    >
      <Download className="h-4 w-4" />
      {label}
    </button>
  );
}
