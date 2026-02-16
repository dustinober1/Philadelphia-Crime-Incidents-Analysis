import type { Metadata } from "next";

import "./globals.css";
import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";
import { Suspense } from "react";

function LoadingFallback() {
  return (
    <div className="animate-pulse space-y-4" aria-busy="true" aria-live="polite">
      <div className="h-8 w-1/3 rounded bg-slate-200" />
      <div className="h-64 rounded bg-slate-200" />
    </div>
  );
}

export const metadata: Metadata = {
  title: "Philadelphia Crime Explorer",
  description: "Interactive analysis of Philadelphia crime trends, maps, policy, forecasts, and Q&A.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col">
        <Navbar />
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <Suspense fallback={<LoadingFallback />}>{children}</Suspense>
        </main>
        <Footer />
      </body>
    </html>
  );
}
