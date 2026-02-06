import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://phillycrime.info";
  return ["", "/trends", "/map", "/policy", "/forecast", "/questions", "/about"].map((path) => ({
    url: `${base}${path}`,
    lastModified: new Date(),
  }));
}
