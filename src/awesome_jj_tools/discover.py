"""Sweep GitHub/GitLab/Codeberg/crates.io for candidates, and flag stale existing entries."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx2
import yaml

from awesome_jj_tools.candidates import (
    filter_missing,
    load_url_snapshot,
    save_url_snapshot,
    split_new_vs_outstanding,
)
from awesome_jj_tools.entries import (
    DEFAULT_ENTRIES_PATH,
    GitHubRepoRef,
    all_urls,
    github_repos,
    load_entries,
)
from awesome_jj_tools.http import get_json, gh_repo_info, gh_search_repos, new_client
from awesome_jj_tools.progress import parallel_map

DEFAULT_CANDIDATES_SNAPSHOT_PATH = DEFAULT_ENTRIES_PATH.parent / "candidates-snapshot.json"
DEFAULT_IGNORED_PATH = DEFAULT_ENTRIES_PATH.parent / "ignored.yaml"

STALE_AFTER = timedelta(days=365)

GITHUB_TOPICS = ["jujutsu", "jj-vcs"]
GITLAB_TOPIC = "jujutsu"
CODEBERG_QUERY = "jujutsu"
CRATES_RDEP_CRATE = "jj-lib"

# GitHub's jujutsu/jj-vcs topics are tagged on plenty of dotfiles repos,
# personal experiments, and agent-generated toys with zero real traction —
# a real run against this topic found 111 candidates, 53 of them at 0-1
# stars. This is a coarse, easily-explained proxy for "has anyone but the
# author looked at this," not a judgment on quality — CONTRIBUTING.md's
# actual bar still applies to whatever clears it.
MIN_GITHUB_STARS = 2


@dataclass(frozen=True)
class Candidate:
    name: str
    url: str
    description: str
    source: str
    stars: int = 0


@dataclass(frozen=True)
class StaleEntry:
    name: str
    url: str
    reason: str


async def fetch_github_candidates(
    client: httpx2.AsyncClient,
    fetcher: Callable[[httpx2.AsyncClient, str], Awaitable[list[dict[str, Any]]]] = gh_search_repos,
) -> list[Candidate]:
    candidates: dict[str, Candidate] = {}
    results = await asyncio.gather(*(fetcher(client, topic) for topic in GITHUB_TOPICS))
    for repos in results:
        for repo in repos:
            url = repo["url"]
            candidates[url] = Candidate(
                name=repo["fullName"],
                url=url,
                description=repo.get("description") or "",
                source="github",
                stars=repo.get("stargazersCount") or 0,
            )
    return list(candidates.values())


async def fetch_gitlab_candidates(
    client: httpx2.AsyncClient,
    fetcher: Callable[[httpx2.AsyncClient, str], Awaitable[Any]] = get_json,
) -> list[Candidate]:
    projects = await fetcher(
        client,
        f"https://gitlab.com/api/v4/projects?topic={GITLAB_TOPIC}&order_by=last_activity_at&per_page=100",
    )
    return [
        Candidate(
            name=p["name_with_namespace"],
            url=p["web_url"],
            description=p.get("description") or "",
            source="gitlab",
        )
        for p in projects
    ]


async def fetch_codeberg_candidates(
    client: httpx2.AsyncClient,
    fetcher: Callable[[httpx2.AsyncClient, str], Awaitable[Any]] = get_json,
) -> list[Candidate]:
    result = await fetcher(
        client, f"https://codeberg.org/api/v1/repos/search?q={CODEBERG_QUERY}&limit=50"
    )
    return [
        Candidate(
            name=r["full_name"],
            url=r["html_url"],
            description=r.get("description") or "",
            source="codeberg",
        )
        for r in result.get("data", [])
    ]


async def fetch_crates_candidates(
    client: httpx2.AsyncClient,
    fetcher: Callable[[httpx2.AsyncClient, str], Awaitable[Any]] = get_json,
) -> list[Candidate]:
    result = await fetcher(
        client, f"https://crates.io/api/v1/crates/{CRATES_RDEP_CRATE}/reverse_dependencies"
    )
    crate_names: list[str] = []
    for dep in result.get("versions", result.get("dependencies", [])):
        crate_id = dep.get("crate") or dep.get("crate_id")
        if crate_id and crate_id not in crate_names:
            crate_names.append(crate_id)

    async def resolve(name: str) -> Candidate:
        # crates.io's own crate page is almost never the useful link — most of these
        # are already listed here by their GitHub repo (e.g. `lumen`), just not
        # reachable from a bare reverse-deps entry. Resolve to `repository`/`homepage`
        # so filter_missing can actually recognize "already have this one."
        crates_io_url = f"https://crates.io/crates/{name}"
        try:
            info = await fetcher(client, f"https://crates.io/api/v1/crates/{name}")
        except Exception:  # noqa: BLE001 - fall back to the crates.io page itself
            return Candidate(name=name, url=crates_io_url, description="", source="crates.io")

        crate = info.get("crate", {})
        url = crate.get("repository") or crate.get("homepage") or crates_io_url
        # crates.io descriptions can be multi-line free text; collapse to one
        # line so they don't break the markdown list they're rendered into.
        description = " ".join((crate.get("description") or "").split())
        return Candidate(name=name, url=url, description=description, source="crates.io")

    return await parallel_map(resolve, crate_names, description="Resolving crates.io repos")


def load_candidates_snapshot(path: Path = DEFAULT_CANDIDATES_SNAPSHOT_PATH) -> set[str]:
    return load_url_snapshot(path)


def save_candidates_snapshot(urls: set[str], path: Path = DEFAULT_CANDIDATES_SNAPSHOT_PATH) -> None:
    save_url_snapshot(urls, path)


def load_ignored_urls(path: Path = DEFAULT_IGNORED_PATH) -> set[str]:
    """URLs that legitimately keep surfacing but should never be reported — see ignored.yaml."""
    if not path.exists():
        return set()
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {item["url"] for item in data.get("ignored", [])}


def filter_low_signal(
    candidates: list[Candidate], min_github_stars: int = MIN_GITHUB_STARS
) -> list[Candidate]:
    """Drop near-zero-traction GitHub noise. Other sources have no comparable signal yet."""
    return [c for c in candidates if c.source != "github" or c.stars >= min_github_stars]


async def check_staleness(
    client: httpx2.AsyncClient,
    repo_refs: list[GitHubRepoRef],
    fetcher: Callable[[httpx2.AsyncClient, str, str], Awaitable[dict[str, Any]]] = gh_repo_info,
    now: datetime | None = None,
) -> list[StaleEntry]:
    now = now or datetime.now(UTC)

    async def check_one(ref: GitHubRepoRef) -> StaleEntry | None:
        info = await fetcher(client, ref.owner, ref.repo)
        if info.get("archived"):
            return StaleEntry(name=ref.entry_name, url=ref.url, reason="archived")
        pushed_at = info.get("pushed_at")
        if pushed_at:
            pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            if now - pushed > STALE_AFTER:
                return StaleEntry(
                    name=ref.entry_name,
                    url=ref.url,
                    reason=f"no push since {pushed.date().isoformat()}",
                )
        return None

    results = await parallel_map(check_one, repo_refs, description="Checking existing entries")
    return [s for s in results if s is not None]


def _render_candidate_group(
    heading: str, candidates: list[Candidate], empty_message: str
) -> list[str]:
    lines = [f"### {heading}", ""]
    if candidates:
        by_source: dict[str, list[Candidate]] = {}
        for c in candidates:
            by_source.setdefault(c.source, []).append(c)
        for source, items in sorted(by_source.items()):
            lines.append(f"#### {source}")
            lines.append("")
            for c in sorted(items, key=lambda c: c.name.lower()):
                desc = f" — {c.description}" if c.description else ""
                lines.append(f"- [{c.name}]({c.url}){desc}")
            lines.append("")
    else:
        lines.append(empty_message)
        lines.append("")
    return lines


def render_report(
    new_candidates: list[Candidate],
    outstanding_candidates: list[Candidate],
    stale_entries: list[StaleEntry],
) -> str:
    lines = ["## Discovery report", ""]

    lines.extend(_render_candidate_group("New candidates", new_candidates, "None since last run."))
    lines.extend(
        _render_candidate_group(
            "Still outstanding (missing, not yet triaged)",
            outstanding_candidates,
            "Nothing outstanding.",
        )
    )

    lines.append("### Possibly stale, consider removing")
    lines.append("")
    if stale_entries:
        for s in stale_entries:
            lines.append(f"- [{s.name}]({s.url}) — {s.reason}")
    else:
        lines.append("No existing entries flagged as stale this run.")
    lines.append("")

    return "\n".join(lines)


async def run(
    entries_path: Path = DEFAULT_ENTRIES_PATH,
    snapshot_path: Path = DEFAULT_CANDIDATES_SNAPSHOT_PATH,
    ignored_path: Path = DEFAULT_IGNORED_PATH,
) -> tuple[str, bool]:
    """Returns (report_text, has_findings)."""
    data = load_entries(entries_path)
    excluded_urls = all_urls(data) | load_ignored_urls(ignored_path)
    previous_snapshot_urls = load_candidates_snapshot(snapshot_path)

    async with new_client() as client:
        github, gitlab, codeberg, crates = await asyncio.gather(
            fetch_github_candidates(client),
            fetch_gitlab_candidates(client),
            fetch_codeberg_candidates(client),
            fetch_crates_candidates(client),
        )
        all_candidates = filter_low_signal([*github, *gitlab, *codeberg, *crates])

        missing = filter_missing(all_candidates, excluded_urls)
        new_candidates, outstanding_candidates = split_new_vs_outstanding(
            missing, previous_snapshot_urls
        )
        save_candidates_snapshot({c.url for c in missing}, snapshot_path)

        repo_refs = github_repos(data)
        stale_entries = await check_staleness(client, repo_refs)

    report = render_report(new_candidates, outstanding_candidates, stale_entries)
    has_findings = bool(new_candidates or outstanding_candidates or stale_entries)
    return report, has_findings
