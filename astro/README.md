# Site

The GitHub Pages site, built with [Astro](https://astro.build) from
`data/entries.yaml`.

Python stays the source of truth for sorting, slugs, page layout and the
Markdown in descriptions: `awesome-jj export-site-data` writes
`src/data/site.json` (gitignored), and Astro only handles presentation, the
sitemap and Pagefind search. Do not hand-edit entries here — edit
`data/entries.yaml`.

```sh
mise run build-site   # export data, build, Pagefind index -> astro/dist
mise run serve-site   # full build once, then the dev server
```

`serve-site` builds first because Pagefind only writes its index at build
time; search results in dev are as of that build, so restart to refresh.

Deployed by `.github/workflows/pages.yml` on pushes to `main`.
