import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Philadelphia Crime Explorer | Questions",
  description: "Ask a question and browse answered community Q&A.",
  openGraph: {
    title: "Philadelphia Crime Explorer | Questions",
    description: "Ask a question and browse answered community Q&A.",
  },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
