"""Diff each listed tool's releases.atom feed against the last-seen release per repo."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

import httpx2

from awesome_jj_tools.entries import DEFAULT_ENTRIES_PATH, GitHubRepoRef, github_repos, load_entries
from awesome_jj_tools.http import get_text, new_client
from awesome_jj_tools.progress import parallel_map

DEFAULT_LAST_SEEN_PATH = DEFAULT_ENTRIES_PATH.parent / "last-seen-releases.json"

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


@dataclass(frozen=True)
class Release:
    repo_name: str
    repo_url: str
    release_title: str
    release_id: str
    release_link: str


def parse_latest_release(atom_xml: str) -> tuple[str, str, str] | None:
    """Return (id, title, link) of the newest entry in a releases.atom feed, or None if empty."""
    root = ET.fromstring(atom_xml)
    entry = root.find("atom:entry", ATOM_NS)
    if entry is None:
        return None
    entry_id = entry.findtext("atom:id", default="", namespaces=ATOM_NS)
    title = entry.findtext("atom:title", default="", namespaces=ATOM_NS)
    link_el = entry.find("atom:link", ATOM_NS)
    link = link_el.get("href", "") if link_el is not None else ""
    return entry_id, title, link


def load_last_seen(path: Path = DEFAULT_LAST_SEEN_PATH) -> dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_last_seen(data: dict[str, str], path: Path = DEFAULT_LAST_SEEN_PATH) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


async def check_releases(
    client: httpx2.AsyncClient,
    repo_refs: list[GitHubRepoRef],
    last_seen: dict[str, str],
    fetcher: Callable[[httpx2.AsyncClient, str], Awaitable[str]] = get_text,
) -> tuple[list[Release], dict[str, str]]:
    """Returns (new releases since last_seen, updated last_seen map)."""

    async def check_one(
        ref: GitHubRepoRef,
    ) -> tuple[GitHubRepoRef, str, bool, str, str] | None:
        feed_url = f"https://github.com/{ref.owner}/{ref.repo}/releases.atom"
        try:
            atom_xml = await fetcher(client, feed_url)
        except Exception:  # noqa: BLE001 - a repo with no releases page is not a hard failure
            return None

        latest = parse_latest_release(atom_xml)
        if latest is None:
            return None

        entry_id, title, link = latest
        is_new = last_seen.get(ref.url) != entry_id
        return ref, entry_id, is_new, title, link

    results = await parallel_map(check_one, repo_refs, description="Checking releases")

    new_releases = []
    updated = dict(last_seen)
    for result in results:
        if result is None:
            continue
        ref, entry_id, is_new, title, link = result
        if is_new:
            new_releases.append(
                Release(
                    repo_name=ref.entry_name,
                    repo_url=ref.url,
                    release_title=title,
                    release_id=entry_id,
                    release_link=link,
                )
            )
            updated[ref.url] = entry_id

    return new_releases, updated


def render_report(new_releases: list[Release]) -> str:
    lines = ["### New releases", ""]
    if not new_releases:
        lines.append("No new releases since the last run.")
        return "\n".join(lines)

    for r in sorted(new_releases, key=lambda r: r.repo_name.lower()):
        lines.append(f"- **{r.repo_name}**: [{r.release_title}]({r.release_link})")
    return "\n".join(lines)


async def run(
    entries_path: Path = DEFAULT_ENTRIES_PATH, last_seen_path: Path = DEFAULT_LAST_SEEN_PATH
) -> tuple[str, bool]:
    """Returns (report_text, has_findings)."""
    data = load_entries(entries_path)
    last_seen = load_last_seen(last_seen_path)
    repo_refs = github_repos(data)

    async with new_client() as client:
        new_releases, updated = await check_releases(client, repo_refs, last_seen)

    save_last_seen(updated, last_seen_path)
    return render_report(new_releases), bool(new_releases)
