import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import pagefind from "astro-pagefind";
import site from "./src/data/site.json" with { type: "json" };

// One .html file per page (books.html, tools-gui.html, ...) so URLs match the
// current Jinja-built site. `site.url` comes from data/sections.yaml.
export default defineConfig({
  site: site.url,
  build: { format: "file" },
  integrations: [sitemap(), pagefind()],
});
