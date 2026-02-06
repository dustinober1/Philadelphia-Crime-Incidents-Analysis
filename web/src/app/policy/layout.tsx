import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Philadelphia Crime Explorer | Policy",
  description: "Retail theft, vehicle crimes, composition, and event impact analyses.",
  openGraph: {
    title: "Philadelphia Crime Explorer | Policy",
    description: "Retail theft, vehicle crimes, composition, and event impact analyses.",
  },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
