import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Philadelphia Crime Explorer | Interactive Map",
  description: "District severity, tract rates, hotspot clusters, and vehicle corridors.",
  openGraph: {
    title: "Philadelphia Crime Explorer | Interactive Map",
    description: "District severity, tract rates, hotspot clusters, and vehicle corridors.",
  },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
