# Phase 1: Navigation & Layout - Research

**Researched:** February 15, 2026
**Domain:** Next.js App Router navigation, responsive layout, and mobile touch UX
**Confidence:** HIGH

## Summary

Phase 1 is primarily frontend shell work in `web/` and should stay within the existing stack already in the repository: Next.js App Router, React 19, Tailwind CSS 4, and Headless UI. The current app already has a global layout, shared `Navbar`, `Footer`, and an existing `/about` route, so this phase should be an incremental hardening pass, not a redesign.

The largest requirement gap is NAV-02/NAV-03: the current navbar is a flat link list without dropdown grouping or a dedicated mobile interaction pattern. It also uses compact hit areas (`px-3 py-1`) that may undershoot comfortable touch targets. NAV-01 and NAV-04 are partially in place (responsive utility classes and About page exist), but need stronger structure and content clarity.

**Primary recommendation:** Implement a route-config-driven navbar with desktop dropdown + mobile disclosure using Headless UI, while tightening responsive shell spacing, touch target sizing, and About page methodology/limitations structure.

## Standard Stack

The established libraries/tools for this phase:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Next.js | 15.5.2 | App Router pages/layouts | Already project foundation and route system |
| React | 19.1.1 | UI composition and state | Required by Next.js app layer |
| Tailwind CSS | 4.1.12 | Responsive layout and utility styling | Existing global styling approach |
| @headlessui/react | 2.2.7 | Accessible menus/disclosures | Already installed; avoids hand-rolled nav a11y logic |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| clsx | 2.1.1 | Conditional class composition | Active/hover/expanded nav states |
| lucide-react | 0.544.0 | Iconography for mobile toggles/carets | Optional affordance for dropdown/mobile controls |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Headless UI menu/disclosure | Custom dropdown state + keyboard handlers | Faster initial coding, higher accessibility/regression risk |
| Route config module | Hardcoded links in component | Simpler short-term, harder to maintain as sections grow |

**Installation:**
```bash
# No new dependencies needed for this phase
```

## Architecture Patterns

### Recommended Project Structure
```
web/src/
├── app/
│   ├── layout.tsx          # Global shell and responsive container
│   └── about/page.tsx      # Methodology/limitations content
├── components/
│   ├── Navbar.tsx          # Desktop + mobile navigation UI
│   └── Footer.tsx          # Data source and attribution footer
└── lib/
    └── navigation.ts       # Route groups + menu metadata
```

### Pattern 1: Route Manifest Drives Navigation
**What:** Move route labels/groups into a typed config file and render both desktop and mobile nav from that single source.
**When to use:** Any time links are reused across header, mobile menu, sitemap, or breadcrumbs.
**Example:**
```typescript
export const navGroups = [
  { label: "Analysis", items: [{ href: "/trends", label: "Trends" }] },
  { label: "Methods", items: [{ href: "/about", label: "About" }] },
];
```

### Pattern 2: Adaptive Header (Desktop Menu + Mobile Disclosure)
**What:** Render a compact desktop menubar/dropdown and a separate mobile disclosure panel with large tap targets.
**When to use:** Navigation needs to remain clear across phone, tablet, and desktop widths.
**Example:**
```tsx
<Menu>
  <MenuButton>Analysis</MenuButton>
  <MenuItems>{/* grouped links */}</MenuItems>
</Menu>
```

### Pattern 3: Shell-First Responsiveness
**What:** Fix responsive spacing and readable line lengths in `app/layout.tsx` and global styles before per-page changes.
**When to use:** Layout consistency problems span many routes.

### Anti-Patterns to Avoid
- **Flat nav sprawl:** Adding every section as a top-level link causes wrap/overflow on small screens.
- **Split route definitions:** Duplicating link labels in multiple components creates drift.
- **Tap targets below ~44px:** Looks fine on desktop but fails touch usability.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Dropdown keyboard/focus behavior | Custom keydown/focus trap code | Headless UI `Menu` | Handles accessibility edge cases consistently |
| Mobile expand/collapse semantics | Custom aria-expanded + animation state machine | Headless UI `Disclosure` | Cleaner semantics and less brittle interaction code |
| Active link class logic spread across UI | Repeated `pathname` checks everywhere | Shared helper in `lib/navigation.ts` | Reduces mismatch bugs across nav variants |

**Key insight:** Navigation UX failures usually come from many small state/accessibility edge cases; use the installed primitives instead of custom behavior.

## Common Pitfalls

### Pitfall 1: Active State Mismatch on Nested Routes
**What goes wrong:** Parent items do not highlight for nested routes (`/map/...`).
**Why it happens:** Exact string equality checks only.
**How to avoid:** Add `isActivePath` helper supporting exact and section-prefix matching.
**Warning signs:** Header shows no active section after navigating deeper URLs.

### Pitfall 2: Desktop-Only QA
**What goes wrong:** Navigation appears complete but fails on touch devices.
**Why it happens:** Validation only in wide desktop viewport.
**How to avoid:** Require manual checks at phone and tablet widths with keyboard and touch interactions.
**Warning signs:** Tiny touch zones, clipped menu text, accidental close/open behavior.

### Pitfall 3: About Page as Unstructured Paragraph Dump
**What goes wrong:** Methodology/limitations exist but are hard to scan.
**Why it happens:** Content is present but not sectioned for readability.
**How to avoid:** Add clear sections (Data Sources, Methodology, Limitations, Update Cadence, Contact).
**Warning signs:** Long single block text and weak heading hierarchy.

## Code Examples

Verified patterns from this repository:

### Existing Global Shell
```tsx
// Source: web/src/app/layout.tsx
<Navbar />
<main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
<Footer />
```

### Existing Navbar Baseline
```tsx
// Source: web/src/components/Navbar.tsx
const links = [
  ["/", "Home"],
  ["/trends", "Trends"],
  ["/map", "Map"],
  ["/policy", "Policy"],
  ["/forecast", "Forecast"],
  ["/questions", "Q&A"],
  ["/about", "About"],
];
```

### Existing About Page Baseline
```tsx
// Source: web/src/app/about/page.tsx
<h1>About / Methodology</h1>
<p>Source: Philadelphia Police Department, OpenDataPhilly incident records.</p>
<p>Limitations: reporting practices, geocoding coverage...</p>
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Flat header links for all sections | Grouped navigation with desktop dropdown + mobile disclosure | Current phase target | Better clarity and small-screen behavior |
| Single unstructured About content block | Sectioned methodology and limitations content | Current phase target | Easier scanning and trust/transparency |

**Deprecated/outdated:**
- Flat, wrap-heavy header as the only navigation mode for all viewport sizes.

## Open Questions

1. **Phase directory naming inconsistency**
   - What we know: Two directories exist (`01-navigation-` and `01-navigation-&-layout`) and both are empty.
   - What's unclear: Which naming convention future automation expects.
   - Recommendation: Use `01-navigation-` for this run because phase discovery (`ls ... | head -1`) resolves to it.

2. **Depth of mobile gesture support**
   - What we know: Requirement calls out touch interactions (tap, swipe).
   - What's unclear: Whether explicit swipe gestures are needed beyond robust tap interactions.
   - Recommendation: Treat tap-first interaction quality as required; defer swipe gestures unless user confirms they are in scope.

## Sources

### Primary (HIGH confidence)
- `web/package.json` - Frontend stack and versions
- `web/src/app/layout.tsx` - Existing global shell
- `web/src/components/Navbar.tsx` - Existing navigation implementation
- `web/src/app/about/page.tsx` - Existing methodology/limitations content
- `.planning/REQUIREMENTS.md` - NAV-01 through NAV-04 requirements
- `.planning/ROADMAP.md` - Phase 1 success criteria

### Secondary (MEDIUM confidence)
- `.planning/codebase/STRUCTURE.md` - Codebase-level structure guidance

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - directly from current `web/package.json`
- Architecture: HIGH - derived from existing file structure and installed libraries
- Pitfalls: HIGH - based on current implementation gaps vs stated phase requirements

**Research date:** February 15, 2026
**Valid until:** March 17, 2026
