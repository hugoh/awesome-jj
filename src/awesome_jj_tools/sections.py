"""Section layout, sorting, and slugging feeding the README.md Jinja template.

Deliberately holds no prose and no string-formatting/templating logic — the
prose (header/footer/section intros) lives in templates/readme.md.j2 itself.
This module owns the data model: section order, sort order, slugs.
"""

from __future__ import annotations

import re
from typing import Any

TOOLS_SUBSECTIONS = [
    ("gui", "GUI"),
    ("tui", "TUI"),
    ("editor_integration", "Editor Integration"),
    ("diff_merge_drivers", "Diff and Merge Drivers"),
    ("workflows", "Workflows"),
    ("shell_integration", "Shell Integration"),
    ("misc_tools", "Misc Tools"),
]

TOP_SECTIONS = [
    ("official_resources", "Official Resources", "list"),
    ("articles", "Articles", "dated"),
    ("books", "Books", "book"),
    ("videos", "Videos", "dated_video"),
    ("tools", "Tools", "tools"),
    ("forges", "Forges", "list_sorted"),
    ("miscellaneous", "Miscellaneous", "list"),
    ("community", "Community", "list_sorted"),
]


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


def build_context(data: dict[str, Any]) -> dict[str, Any]:
    """A fully sorted, self-contained rendering context: no further logic needed downstream."""
    sections = []
    for key, title, kind in TOP_SECTIONS:
        section: dict[str, Any] = {
            "key": key,
            "title": title,
            "slug": slug(title),
            "kind": kind,
            "subsections": [],
            "entries": [],
        }
        if kind == "tools":
            tools_data = data.get("tools", {})
            section["subsections"] = [
                {
                    "key": sub_key,
                    "title": sub_title,
                    "slug": slug(sub_title),
                    "entries": sorted_items("list_sorted", tools_data.get(sub_key, [])),
                }
                for sub_key, sub_title in TOOLS_SUBSECTIONS
            ]
        else:
            section["entries"] = sorted_items(kind, data.get(key, []))
        sections.append(section)
    return {"sections": sections}
