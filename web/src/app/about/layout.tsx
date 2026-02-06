import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Philadelphia Crime Explorer | About",
  description: "Data sources, methods, caveats, and project attribution.",
  openGraph: {
    title: "Philadelphia Crime Explorer | About",
    description: "Data sources, methods, caveats, and project attribution.",
  },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
