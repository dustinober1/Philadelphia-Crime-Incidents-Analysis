import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Philadelphia Crime Explorer | Trends",
  description: "Annual, monthly, COVID-period, seasonality, and robbery timing patterns.",
  openGraph: {
    title: "Philadelphia Crime Explorer | Trends",
    description: "Annual, monthly, COVID-period, seasonality, and robbery timing patterns.",
  },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
