import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import pagefind from "astro-pagefind";
import site from "./src/data/site.json" with { type: "json" };

// build.format "file" emits books.html rather than books/index.html, keeping
// the URLs the site has always had.
export default defineConfig({
  site: site.url,
  build: { format: "file" },
  integrations: [
    sitemap({
      serialize: (item) => (site.updated_at ? { ...item, lastmod: site.updated_at } : item),
    }),
    pagefind(),
  ],
});
