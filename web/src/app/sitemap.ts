import type { MetadataRoute } from "next";
import { getAllRoutes } from "@/lib/navigation";

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://phillycrime.info";
  const routes = getAllRoutes();

  return routes.map((route) => ({
    url: `${base}${route.href}`,
    lastModified: new Date(),
  }));
}
