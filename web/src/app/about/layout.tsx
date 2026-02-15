import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Philadelphia Crime Explorer | About",
  description: "Transparent methodology, data sources, and known limitations for Philadelphia crime incident analysis. Built on 1.5M+ records from the Philadelphia Police Department.",
  openGraph: {
    title: "Philadelphia Crime Explorer | About & Methodology",
    description: "Evidence-based crime analysis using Philadelphia Police Department data. Learn about our data sources, analytical methods, and important limitations.",
    type: "website",
  },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
