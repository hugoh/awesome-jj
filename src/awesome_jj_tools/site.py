"""Render a browsable index.html from data/entries.yaml, for GitHub Pages.

Same data model as generate.py's README.md renderer (sections.build_context),
different template (templates/index.html.j2) and no rumdl pass — that's a
markdown-specific formatter, HTML doesn't need it. Search is added at deploy
time by running Pagefind over the built site/ directory (see
.github/workflows/pages.yml) — this module only renders the page itself.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape

from awesome_jj_tools.entries import DEFAULT_ENTRIES_PATH, load_entries
from awesome_jj_tools.last_updated import DEFAULT_LAST_UPDATED_PATH, load_snapshot
from awesome_jj_tools.sections import build_context, iter_pages
from awesome_jj_tools.templating import env

SITE_DIR = DEFAULT_ENTRIES_PATH.parents[1] / "site"
INDEX_PATH = SITE_DIR / "index.html"
STATIC_DIR = Path(__file__).resolve().parent / "static"


def page_url(context: dict[str, Any], filename: str) -> str:
    """Same convention `render` uses for canonical/og:url — index.html is the bare site
    root, every other page is that root plus its filename."""
    return context["url"] if filename == "index.html" else context["url"] + filename


def render_sitemap(context: dict[str, Any], filenames: list[str], updated_at: str) -> str:
    """A sitemap.xml listing every rendered page, per the sitemaps.org protocol."""
    lastmod = f"\n    <lastmod>{updated_at}</lastmod>" if updated_at else ""
    urls = "\n".join(
        f"  <url>\n    <loc>{xml_escape(page_url(context, filename))}</loc>{lastmod}\n  </url>"
        for filename in filenames
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )


def render_robots(context: dict[str, Any]) -> str:
    """Allow all crawlers and point them at the sitemap."""
    return f"User-agent: *\nAllow: /\n\nSitemap: {context['url']}sitemap.xml\n"


def render(data: dict[str, Any], updated_at: str) -> dict[str, str]:
    """One rendered page per section, keyed by output filename — see
    `sections.iter_pages` for the filename convention (Tools is index.html).
    """
    context = build_context(data) | {"updated_at": updated_at}
    template = env.get_template("index.html.j2")
    pages = {}
    for page in iter_pages(context):
        section = page["section"]
        is_index = page["filename"] == "index.html"
        page_title = context["title"] if is_index else f"{section['title']} — {context['title']}"
        pages[page["filename"]] = template.render(
            **context,
            page=page,
            section=section,
            nav=page["nav"],
            page_title=page_title,
            page_description=context["description"],
            page_url=page_url(context, page["filename"]),
        )
    pages["sitemap.xml"] = render_sitemap(context, list(pages), updated_at)
    pages["robots.txt"] = render_robots(context)
    return pages


def generate(
    entries_path: Path = DEFAULT_ENTRIES_PATH,
    index_path: Path = INDEX_PATH,
    last_updated_path: Path = DEFAULT_LAST_UPDATED_PATH,
) -> dict[str, str]:
    """Reads whatever date `generate.py`'s README pass already recorded — the
    site build never mints its own date, it's a pure read of committed state.
    """
    data = load_entries(entries_path)
    snapshot = load_snapshot(last_updated_path)
    updated_at = snapshot.date if snapshot else ""
    pages = render(data, updated_at)
    site_dir = index_path.parent
    site_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in pages.items():
        (site_dir / filename).write_text(content, encoding="utf-8")
    for asset in STATIC_DIR.iterdir():
        shutil.copy(asset, site_dir / asset.name)
    return pages
