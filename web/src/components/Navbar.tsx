"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, MenuButton, MenuItem, MenuItems, Disclosure, DisclosureButton, DisclosurePanel } from "@headlessui/react";
import { ChevronDown, Menu as MenuIcon, X } from "lucide-react";
import clsx from "clsx";
import {
  primaryLinks,
  analysisGroup,
  secondaryLinks,
  isActiveRoute,
  isGroupActive,
} from "@/lib/navigation";

export function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur">
      <nav className="mx-auto max-w-7xl px-4 py-3">
        {/* Desktop Navigation */}
        <div className="hidden items-center gap-6 md:flex">
          <Link href="/" className="mr-2 text-lg font-bold text-slate-900">
            Philadelphia Crime Explorer
          </Link>

          {/* Primary Links */}
          {primaryLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={clsx(
                "rounded px-4 py-2 text-sm font-medium transition-colors",
                isActiveRoute(pathname, link.href, true)
                  ? "bg-slate-900 text-white"
                  : "text-slate-700 hover:bg-slate-100",
              )}
            >
              {link.label}
            </Link>
          ))}

          {/* Analysis Dropdown */}
          <Menu as="div" className="relative">
            <MenuButton
              className={clsx(
                "flex items-center gap-1 rounded px-4 py-2 text-sm font-medium transition-colors",
                isGroupActive(pathname, analysisGroup)
                  ? "bg-slate-900 text-white"
                  : "text-slate-700 hover:bg-slate-100",
              )}
              aria-label="Analysis sections menu"
            >
              {analysisGroup.label}
              <ChevronDown className="h-4 w-4" aria-hidden="true" />
            </MenuButton>
            <MenuItems
              className="absolute left-0 mt-2 w-48 origin-top-left rounded-md border border-slate-200 bg-white shadow-lg focus:outline-none"
              transition
            >
              {analysisGroup.items.map((item) => (
                <MenuItem key={item.href}>
                  <Link
                    href={item.href}
                    className={clsx(
                      "block px-4 py-2 text-sm transition-colors",
                      isActiveRoute(pathname, item.href)
                        ? "bg-slate-900 text-white"
                        : "text-slate-700 hover:bg-slate-100",
                    )}
                  >
                    {item.label}
                  </Link>
                </MenuItem>
              ))}
            </MenuItems>
          </Menu>

          {/* Secondary Links */}
          {secondaryLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={clsx(
                "rounded px-4 py-2 text-sm font-medium transition-colors",
                isActiveRoute(pathname, link.href, true)
                  ? "bg-slate-900 text-white"
                  : "text-slate-700 hover:bg-slate-100",
              )}
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* Mobile Navigation */}
        <Disclosure as="div" className="md:hidden">
          {({ open }) => (
            <>
              <div className="flex items-center justify-between">
                <Link href="/" className="text-lg font-bold text-slate-900">
                  Philadelphia Crime Explorer
                </Link>
                <DisclosureButton
                  className="rounded p-2 text-slate-700 hover:bg-slate-100"
                  aria-label={open ? "Close menu" : "Open menu"}
                >
                  {open ? (
                    <X className="h-6 w-6" aria-hidden="true" />
                  ) : (
                    <MenuIcon className="h-6 w-6" aria-hidden="true" />
                  )}
                </DisclosureButton>
              </div>

              <DisclosurePanel className="mt-4 space-y-2">
                {/* Primary Links */}
                {primaryLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={clsx(
                      "block rounded px-4 py-3 text-base font-medium transition-colors",
                      isActiveRoute(pathname, link.href, true)
                        ? "bg-slate-900 text-white"
                        : "text-slate-700 hover:bg-slate-100",
                    )}
                  >
                    {link.label}
                  </Link>
                ))}

                {/* Analysis Section */}
                <div className="space-y-1">
                  <div className="px-4 py-2 text-sm font-semibold text-slate-500">
                    {analysisGroup.label}
                  </div>
                  {analysisGroup.items.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={clsx(
                        "block rounded px-4 py-3 text-base font-medium transition-colors",
                        isActiveRoute(pathname, item.href)
                          ? "bg-slate-900 text-white"
                          : "text-slate-700 hover:bg-slate-100",
                      )}
                    >
                      {item.label}
                    </Link>
                  ))}
                </div>

                {/* Secondary Links */}
                {secondaryLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={clsx(
                      "block rounded px-4 py-3 text-base font-medium transition-colors",
                      isActiveRoute(pathname, link.href, true)
                        ? "bg-slate-900 text-white"
                        : "text-slate-700 hover:bg-slate-100",
                    )}
                  >
                    {link.label}
                  </Link>
                ))}
              </DisclosurePanel>
            </>
          )}
        </Disclosure>
      </nav>
    </header>
  );
}
