import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Philadelphia Crime Explorer | Admin",
  description: "Admin moderation tools for pending community questions.",
  openGraph: {
    title: "Philadelphia Crime Explorer | Admin",
    description: "Admin moderation tools for pending community questions.",
  },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
