import type { ReactNode } from "react";

export const metadata = {
  title: "Philadelphia Crime Explorer | Data & Transparency",
  description: "Download crime data, view source citations, and understand methodology and limitations.",
};

export default function DataLayout({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {children}
    </div>
  );
}
