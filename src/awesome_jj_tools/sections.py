"""Turns data/entries.yaml + data/sections.yaml into a rendering context.

Holds no hardcoded page title/description/intro, section list, titles, or
prose — that's all in data/sections.yaml (see its comments). This module
only implements the mechanics: sort order per kind, slugging, and
assembling the two config files into the shape both Jinja templates expect.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from awesome_jj_tools.entries import DEFAULT_ENTRIES_PATH

DEFAULT_SECTIONS_CONFIG_PATH = DEFAULT_ENTRIES_PATH.parent / "sections.yaml"


def load_config(path: Path = DEFAULT_SECTIONS_CONFIG_PATH) -> dict[str, Any]:
    """The full sections.yaml: title/description/intro plus the sections list."""
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def slug(title: str) -> str:
    return re.sub(r"[^a-z0-9- ]", "", title.lower()).replace(" ", "-")


def sort_key(name: str) -> str:
    return re.sub(r'^["\'()]+', "", name).lower()


OPTIONAL_FIELDS = ("description", "author", "date", "suffix")


def _normalize(entry: dict[str, Any]) -> dict[str, Any]:
    """Every optional field present with a value or None, so templates never hit a missing key."""
    return {field: entry.get(field) for field in OPTIONAL_FIELDS} | entry


def _with_date_parts(entry: dict[str, Any]) -> dict[str, Any]:
    year, month = entry["date"].split("-")
    return {**entry, "year": year, "month": month}


def sorted_items(kind: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort a section's raw entries per its kind, annotating dated ones with year/month."""
    if kind == "list":
        entries = items
    elif kind in ("list_sorted", "book"):
        entries = sorted(items, key=lambda e: sort_key(e["name"]))
    elif kind in ("dated", "dated_video"):
        entries = [_with_date_parts(e) for e in sorted(items, key=lambda e: e["date"])]
    else:
        raise ValueError(f"unknown section kind: {kind}")
    return [_normalize(e) for e in entries]


def _assign_unique_entry_slugs(sections: list[dict[str, Any]]) -> None:
    """Give every entry a unique `slug` (for HTML anchors), de-duplicating across the whole page."""
    seen: dict[str, int] = {}
    entry_lists = []
    for section in sections:
        entry_lists.append(section["entries"])
        entry_lists.extend(sub["entries"] for sub in section["subsections"])
    for entries in entry_lists:
        for entry in entries:
            base = slug(entry["name"])
            count = seen.get(base, 0)
            seen[base] = count + 1
            entry["slug"] = base if count == 0 else f"{base}-{count + 1}"


def build_context(data: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    """A fully sorted, self-contained rendering context: no further logic needed downstream."""
    if config is None:
        config = load_config()

    sections = []
    for section_cfg in config["sections"]:
        key, title, kind = section_cfg["key"], section_cfg["title"], section_cfg["kind"]
        section: dict[str, Any] = {
            "key": key,
            "title": title,
            "slug": slug(title),
            "kind": kind,
            "subsections": [],
            "entries": [],
            "intro": section_cfg.get("intro"),
        }
        if kind == "tools":
            tools_data = data.get("tools", {})
            section["subsections"] = [
                {
                    "key": sub_cfg["key"],
                    "title": sub_cfg["title"],
                    "slug": slug(sub_cfg["title"]),
                    "entries": sorted_items("list_sorted", tools_data.get(sub_cfg["key"], [])),
                }
                for sub_cfg in section_cfg.get("subsections", [])
            ]
        else:
            section["entries"] = sorted_items(kind, data.get(key, []))
        sections.append(section)
    _assign_unique_entry_slugs(sections)

    return {
        "title": config["title"],
        "description": config["description"],
        "intro": config["intro"],
        "url": config["url"],
        "sections": sections,
    }


def page_filename(section: dict[str, Any]) -> str:
    """The Tools section's hub page is the site's landing page; every other
    top-level section gets its own file named after its slug."""
    return "index.html" if section["key"] == "tools" else f"{section['slug']}.html"


def subsection_filename(sub: dict[str, Any]) -> str:
    """Each Tools subsection gets its own file, so Pagefind's category filter
    can gate a whole page instead of a fragment within the combined Tools
    page (see the pagefind-modal markup in index.html.j2)."""
    return f"tools-{sub['slug']}.html"


def iter_pages(context: dict[str, Any]) -> list[dict[str, Any]]:
    """One entry per output page: its filename, the section data to render,
    the shared top-level nav (title + filename for every top-level section),
    and — for the Tools hub and its subsection pages only — `tools_nav`
    (title + filename for every Tools subsection)."""
    nav = [
        {
            "title": section["title"],
            "filename": page_filename(section),
            "href": "./" if section["key"] == "tools" else page_filename(section),
        }
        for section in context["sections"]
    ]

    pages = []
    for section in context["sections"]:
        if section["key"] != "tools":
            pages.append(
                {
                    "filename": page_filename(section),
                    "section": section,
                    "nav": nav,
                    "tools_nav": [],
                }
            )
            continue

        tools_nav = [
            {"title": sub["title"], "filename": subsection_filename(sub)}
            for sub in section["subsections"]
        ]
        pages.append(
            {"filename": "index.html", "section": section, "nav": nav, "tools_nav": tools_nav}
        )
        for sub in section["subsections"]:
            sub_section = {
                "key": sub["key"],
                "title": sub["title"],
                "slug": sub["slug"],
                "kind": "list_sorted",
                "entries": sub["entries"],
                "subsections": [],
                "intro": None,
            }
            pages.append(
                {
                    "filename": subsection_filename(sub),
                    "section": sub_section,
                    "nav": nav,
                    "tools_nav": tools_nav,
                }
            )
    return pages
