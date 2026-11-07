# Astro site (spike)

Alternative to the Jinja-built `site/`. Python stays the source of truth for
sorting, slugs and page layout (`awesome-jj export-site-data` writes
`src/data/site.json`); Astro only renders it.

```sh
cd astro && npm install
npm run dev      # full build once (Pagefind only indexes at build), then dev server;
                 # search results are as of that build, restart to refresh
npm run build    # export data + build + Pagefind index into dist/
```

Not wired into CI/Pages yet.
