# Astro site (spike)

Alternative to the Jinja-built `site/`. Python stays the source of truth for
sorting, slugs and page layout (`awesome-jj export-site-data` writes
`src/data/site.json`); Astro only renders it.

```sh
cd astro && npm install
npm run dev      # export data + dev server
npm run build    # export data + build + Pagefind index into dist/
```

Not wired into CI/Pages yet.
