import type { Metadata } from "next";

import "./globals.css";
import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Philadelphia Crime Explorer",
  description: "Interactive analysis of Philadelphia crime trends, maps, policy, forecasts, and Q&A.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
