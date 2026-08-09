"""URL-set bookkeeping shared by discover.py (tool candidates) and media.py
(article/video candidates): excluding already-known URLs, and splitting
what's left into "new since last run" vs. "still outstanding" against a
persisted snapshot.

Generic over any object with a `.url` attribute — Candidate (discover.py)
and MediaCandidate (media.py) both qualify, so this logic isn't duplicated
between the two sweeps.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol


class HasUrl(Protocol):
    url: str


def load_url_snapshot(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(json.loads(path.read_text(encoding="utf-8")))


def save_url_snapshot(urls: set[str], path: Path) -> None:
    path.write_text(json.dumps(sorted(urls), indent=2) + "\n", encoding="utf-8")


def filter_missing(items: list[Any], excluded_urls: set[str]) -> list[Any]:
    """Items not already accounted for by `excluded_urls` (entries.yaml + ignored.yaml)."""
    excluded = {u.rstrip("/") for u in excluded_urls}
    return [i for i in items if i.url.rstrip("/") not in excluded]


def split_new_vs_outstanding(
    items: list[Any], previous_snapshot_urls: set[str]
) -> tuple[list[Any], list[Any]]:
    """Split currently-missing items into (new since last run, still outstanding).

    Unlike a permanent seen/suppress list, this never drops an item from the
    report just because it was mentioned once — only actually adding it (or
    it falling out of the sweep entirely) makes it stop showing.
    """
    previous = {u.rstrip("/") for u in previous_snapshot_urls}
    new = [i for i in items if i.url.rstrip("/") not in previous]
    outstanding = [i for i in items if i.url.rstrip("/") in previous]
    return new, outstanding
