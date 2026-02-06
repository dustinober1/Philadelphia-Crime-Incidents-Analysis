"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";

const links = [
  ["/", "Home"],
  ["/trends", "Trends"],
  ["/map", "Map"],
  ["/policy", "Policy"],
  ["/forecast", "Forecast"],
  ["/questions", "Q&A"],
  ["/about", "About"],
];

export function Navbar() {
  const pathname = usePathname();
  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur">
      <nav className="mx-auto flex max-w-7xl flex-wrap items-center gap-3 px-4 py-3">
        <Link href="/" className="mr-4 text-lg font-bold text-slate-900">
          Philadelphia Crime Explorer
        </Link>
        {links.map(([href, label]) => (
          <Link
            key={href}
            href={href}
            className={clsx(
              "rounded px-3 py-1 text-sm",
              pathname === href ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100",
            )}
          >
            {label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
