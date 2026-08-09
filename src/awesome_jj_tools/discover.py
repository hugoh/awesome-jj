"""Sweep GitHub/GitLab/Codeberg/crates.io for candidates, and flag stale existing entries."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from awesome_jj_tools.entries import (
    DEFAULT_ENTRIES_PATH,
    GitHubRepoRef,
    all_urls,
    github_repos,
    load_entries,
)
from awesome_jj_tools.http import get_json, gh_repo_info, gh_search_repos

DEFAULT_SEEN_CANDIDATES_PATH = DEFAULT_ENTRIES_PATH.parent / "seen-candidates.json"

STALE_AFTER = timedelta(days=365)

GITHUB_TOPICS = ["jujutsu", "jj-vcs"]
GITLAB_TOPIC = "jujutsu"
CODEBERG_QUERY = "jujutsu"
CRATES_RDEP_CRATE = "jj-lib"


@dataclass(frozen=True)
class Candidate:
    name: str
    url: str
    description: str
    source: str


@dataclass(frozen=True)
class StaleEntry:
    name: str
    url: str
    reason: str


def fetch_github_candidates(
    fetcher: Callable[[str], list[dict[str, Any]]] = gh_search_repos,
) -> list[Candidate]:
    candidates: dict[str, Candidate] = {}
    for topic in GITHUB_TOPICS:
        for repo in fetcher(topic):
            url = repo["url"]
            candidates[url] = Candidate(
                name=repo["fullName"],
                url=url,
                description=repo.get("description") or "",
                source="github",
            )
    return list(candidates.values())


def fetch_gitlab_candidates(fetcher: Callable[[str], Any] = get_json) -> list[Candidate]:
    projects = fetcher(
        f"https://gitlab.com/api/v4/projects?topic={GITLAB_TOPIC}&order_by=last_activity_at&per_page=100"
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


def fetch_codeberg_candidates(fetcher: Callable[[str], Any] = get_json) -> list[Candidate]:
    result = fetcher(f"https://codeberg.org/api/v1/repos/search?q={CODEBERG_QUERY}&limit=50")
    return [
        Candidate(
            name=r["full_name"],
            url=r["html_url"],
            description=r.get("description") or "",
            source="codeberg",
        )
        for r in result.get("data", [])
    ]


def fetch_crates_candidates(fetcher: Callable[[str], Any] = get_json) -> list[Candidate]:
    result = fetcher(f"https://crates.io/api/v1/crates/{CRATES_RDEP_CRATE}/reverse_dependencies")
    candidates = []
    for dep in result.get("versions", result.get("dependencies", [])):
        crate_id = dep.get("crate") or dep.get("crate_id")
        if not crate_id:
            continue
        candidates.append(
            Candidate(
                name=crate_id,
                url=f"https://crates.io/crates/{crate_id}",
                description="",
                source="crates.io",
            )
        )
    return candidates


def load_seen_candidates(path: Path = DEFAULT_SEEN_CANDIDATES_PATH) -> set[str]:
    if not path.exists():
        return set()
    return set(json.loads(path.read_text(encoding="utf-8")))


def save_seen_candidates(urls: set[str], path: Path = DEFAULT_SEEN_CANDIDATES_PATH) -> None:
    path.write_text(json.dumps(sorted(urls), indent=2) + "\n", encoding="utf-8")


def filter_new_candidates(
    candidates: list[Candidate], known_urls: set[str], seen_urls: set[str]
) -> list[Candidate]:
    """Candidates not already in entries.yaml and not already reported before."""
    seen = {u.rstrip("/") for u in known_urls | seen_urls}
    return [c for c in candidates if c.url.rstrip("/") not in seen]


def check_staleness(
    repo_refs: list[GitHubRepoRef],
    fetcher: Callable[[str, str], dict[str, Any]] = gh_repo_info,
    now: datetime | None = None,
) -> list[StaleEntry]:
    now = now or datetime.now(UTC)
    stale = []
    for ref in repo_refs:
        info = fetcher(ref.owner, ref.repo)
        if info.get("archived"):
            stale.append(StaleEntry(name=ref.entry_name, url=ref.url, reason="archived"))
            continue
        pushed_at = info.get("pushed_at")
        if pushed_at:
            pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            if now - pushed > STALE_AFTER:
                stale.append(
                    StaleEntry(
                        name=ref.entry_name,
                        url=ref.url,
                        reason=f"no push since {pushed.date().isoformat()}",
                    )
                )
    return stale


def render_report(new_candidates: list[Candidate], stale_entries: list[StaleEntry]) -> str:
    lines = ["## Discovery report", ""]

    lines.append("### New candidates")
    lines.append("")
    if new_candidates:
        by_source: dict[str, list[Candidate]] = {}
        for c in new_candidates:
            by_source.setdefault(c.source, []).append(c)
        for source, items in sorted(by_source.items()):
            lines.append(f"#### {source}")
            lines.append("")
            for c in sorted(items, key=lambda c: c.name.lower()):
                desc = f" — {c.description}" if c.description else ""
                lines.append(f"- [{c.name}]({c.url}){desc}")
            lines.append("")
    else:
        lines.append("No new candidates this run.")
        lines.append("")

    lines.append("### Possibly stale, consider removing")
    lines.append("")
    if stale_entries:
        for s in stale_entries:
            lines.append(f"- [{s.name}]({s.url}) — {s.reason}")
    else:
        lines.append("No existing entries flagged as stale this run.")
    lines.append("")

    return "\n".join(lines)


def run(
    entries_path: Path = DEFAULT_ENTRIES_PATH, seen_path: Path = DEFAULT_SEEN_CANDIDATES_PATH
) -> str:
    data = load_entries(entries_path)
    known_urls = all_urls(data)
    seen_urls = load_seen_candidates(seen_path)

    all_candidates: list[Candidate] = []
    all_candidates.extend(fetch_github_candidates())
    all_candidates.extend(fetch_gitlab_candidates())
    all_candidates.extend(fetch_codeberg_candidates())
    all_candidates.extend(fetch_crates_candidates())

    new_candidates = filter_new_candidates(all_candidates, known_urls, seen_urls)
    save_seen_candidates(seen_urls | {c.url for c in new_candidates}, seen_path)

    stale_entries = check_staleness(github_repos(data))

    return render_report(new_candidates, stale_entries)
