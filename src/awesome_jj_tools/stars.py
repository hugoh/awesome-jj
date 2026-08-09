"""Snapshot star counts for listed repos and report notable relative growth."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from awesome_jj_tools.entries import DEFAULT_ENTRIES_PATH, GitHubRepoRef, github_repos, load_entries
from awesome_jj_tools.http import gh_repo_info

DEFAULT_STARS_SNAPSHOT_PATH = DEFAULT_ENTRIES_PATH.parent / "stars-snapshot.json"

GROWTH_THRESHOLD = 0.15


@dataclass(frozen=True)
class StarMover:
    name: str
    url: str
    previous: int
    current: int

    @property
    def relative_growth(self) -> float:
        if self.previous == 0:
            return float("inf") if self.current > 0 else 0.0
        return (self.current - self.previous) / self.previous


def load_snapshot(path: Path = DEFAULT_STARS_SNAPSHOT_PATH) -> dict[str, int]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_snapshot(data: dict[str, int], path: Path = DEFAULT_STARS_SNAPSHOT_PATH) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_current_stars(
    repo_refs: list[GitHubRepoRef], fetcher: Callable[[str, str], dict] = gh_repo_info
) -> dict[str, int]:
    return {ref.url: fetcher(ref.owner, ref.repo)["stargazers_count"] for ref in repo_refs}


def compute_movers(
    repo_refs: list[GitHubRepoRef],
    previous: dict[str, int],
    current: dict[str, int],
    threshold: float = GROWTH_THRESHOLD,
) -> list[StarMover]:
    name_by_url = {ref.url: ref.entry_name for ref in repo_refs}
    movers = []
    for url, current_count in current.items():
        previous_count = previous.get(url)
        if previous_count is None:
            continue  # first time we've seen this repo; nothing to compare against yet
        mover = StarMover(
            name=name_by_url.get(url, url), url=url, previous=previous_count, current=current_count
        )
        if mover.relative_growth >= threshold:
            movers.append(mover)
    return sorted(movers, key=lambda m: m.relative_growth, reverse=True)


def render_report(movers: list[StarMover]) -> str:
    lines = ["### Star movers", ""]
    if not movers:
        lines.append("No repos crossed the growth threshold this run.")
        return "\n".join(lines)

    for m in movers:
        growth_pct = "∞" if m.relative_growth == float("inf") else f"{m.relative_growth:.0%}"
        lines.append(f"- **{m.name}**: {m.previous} → {m.current} stars ({growth_pct})")
    return "\n".join(lines)


def run(
    entries_path: Path = DEFAULT_ENTRIES_PATH, snapshot_path: Path = DEFAULT_STARS_SNAPSHOT_PATH
) -> str:
    data = load_entries(entries_path)
    repo_refs = github_repos(data)
    previous = load_snapshot(snapshot_path)
    current = fetch_current_stars(repo_refs)
    movers = compute_movers(repo_refs, previous, current)
    save_snapshot(current, snapshot_path)
    return render_report(movers)
