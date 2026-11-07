"""Export the per-page rendering context for the Astro site (astro/) as JSON.

Sorting, slugs, page layout and description Markdown all stay in Python, shared
with the README renderer (sections.build_context); Astro only handles
presentation, sitemap and search. See astro/README.md.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from awesome_jj_tools.entries import DEFAULT_ENTRIES_PATH, load_entries
from awesome_jj_tools.last_updated import DEFAULT_LAST_UPDATED_PATH, load_snapshot
from awesome_jj_tools.sections import build_context, iter_pages
from awesome_jj_tools.templating import md_inline

DEFAULT_SITE_DATA_PATH = DEFAULT_ENTRIES_PATH.parents[1] / "astro" / "src" / "data" / "site.json"


def site_data(data: dict[str, Any], updated_at: str) -> dict[str, Any]:
    context = build_context(data) | {"updated_at": updated_at}
    pages = []
    for page in iter_pages(context):
        section = page["section"]
        for entry in section["entries"] + [
            e for sub in section["subsections"] for e in sub["entries"]
        ]:
            entry["description_html"] = str(md_inline(entry["description"]) or "")
        is_index = page["filename"] == "index.html"
        page_title = context["title"] if is_index else f"{section['title']} — {context['title']}"
        pages.append(page | {"page_title": page_title})
    return {k: context[k] for k in ("title", "description", "intro", "url", "updated_at")} | {
        "pages": pages
    }


def export_site_data(
    output_path: Path = DEFAULT_SITE_DATA_PATH,
    entries_path: Path = DEFAULT_ENTRIES_PATH,
    last_updated_path: Path = DEFAULT_LAST_UPDATED_PATH,
) -> None:
    """Reads whatever date `generate.py`'s README pass already recorded — the site
    build never mints its own date, it's a pure read of committed state.
    """
    data = load_entries(entries_path)
    snapshot = load_snapshot(last_updated_path)
    payload = site_data(data, snapshot.date if snapshot else "")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", "utf-8")
