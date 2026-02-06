import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Philadelphia Crime Explorer | Forecast",
  description: "Time-series forecast and violence classification feature insights.",
  openGraph: {
    title: "Philadelphia Crime Explorer | Forecast",
    description: "Time-series forecast and violence classification feature insights.",
  },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
