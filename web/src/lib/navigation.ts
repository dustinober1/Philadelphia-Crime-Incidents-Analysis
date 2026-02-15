/**
 * Centralized navigation configuration for header, mobile menu, and sitemap generation.
 * Single source of truth for all route metadata to prevent drift between navigation systems.
 */

export interface NavItem {
  href: string;
  label: string;
}

export interface NavGroup {
  label: string;
  items: NavItem[];
}

/**
 * Primary navigation links that appear at the top level in the header.
 */
export const primaryLinks: NavItem[] = [
  { href: "/", label: "Home" },
];

/**
 * Analysis section navigation, organized into a dropdown/disclosure group.
 */
export const analysisGroup: NavGroup = {
  label: "Analysis",
  items: [
    { href: "/trends", label: "Trends" },
    { href: "/map", label: "Map" },
    { href: "/policy", label: "Policy" },
    { href: "/forecast", label: "Forecast" },
  ],
};

/**
 * Secondary navigation items (about, methodology, etc.).
 */
export const secondaryLinks: NavItem[] = [
  { href: "/questions", label: "Q&A" },
  { href: "/about", label: "About" },
];

/**
 * All navigation items flattened for sitemap generation.
 */
export function getAllRoutes(): NavItem[] {
  return [
    ...primaryLinks,
    ...analysisGroup.items,
    ...secondaryLinks,
  ];
}

/**
 * Check if a given pathname matches or is under a route.
 * Supports exact matching and section-prefix matching for nested routes.
 *
 * @param currentPath - Current pathname from usePathname()
 * @param targetHref - Target route to check against
 * @param exact - If true, only match exact paths; if false, match path prefixes
 */
export function isActiveRoute(
  currentPath: string,
  targetHref: string,
  exact = false,
): boolean {
  if (exact || targetHref === "/") {
    return currentPath === targetHref;
  }
  return currentPath === targetHref || currentPath.startsWith(`${targetHref}/`);
}

/**
 * Check if any item in a navigation group is active.
 * Used for highlighting dropdown/disclosure triggers.
 */
export function isGroupActive(currentPath: string, group: NavGroup): boolean {
  return group.items.some((item) => isActiveRoute(currentPath, item.href));
}
