"""Load/save data/entries.yaml, the source of record for README.md."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_ENTRIES_PATH = Path(__file__).resolve().parents[2] / "data" / "entries.yaml"

GITHUB_REPO_RE = re.compile(r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/?$")


@dataclass(frozen=True)
class GitHubRepoRef:
    owner: str
    repo: str
    url: str
    entry_name: str
    section_path: tuple[str, ...]


def load_entries(path: Path = DEFAULT_ENTRIES_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def save_entries(data: dict[str, Any], path: Path = DEFAULT_ENTRIES_PATH) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, width=1000)


def _walk(data: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], dict[str, Any]]]:
    """Yield (section_path, entry_dict) for every leaf entry in the tree."""
    items: list[tuple[tuple[str, ...], dict[str, Any]]] = []
    if isinstance(data, dict):
        for key, value in data.items():
            items.extend(_walk(value, (*path, key)))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "url" in item:
                items.append((path, item))
    return items


def all_entries(data: dict[str, Any]) -> list[tuple[tuple[str, ...], dict[str, Any]]]:
    """Every entry in the tree, as (section_path, entry) pairs."""
    return _walk(data)


def all_urls(data: dict[str, Any]) -> set[str]:
    return {entry["url"] for _, entry in all_entries(data)}


def github_repos(data: dict[str, Any]) -> list[GitHubRepoRef]:
    """Every entry whose URL is a bare GitHub repo (owner/repo)."""
    refs = []
    for section_path, entry in all_entries(data):
        match = GITHUB_REPO_RE.match(entry["url"])
        if match:
            refs.append(
                GitHubRepoRef(
                    owner=match["owner"],
                    repo=match["repo"],
                    url=entry["url"],
                    entry_name=entry["name"],
                    section_path=section_path,
                )
            )
    return refs
