"""Sweep Hacker News/Reddit for jj-related articles, and YouTube for videos.

Lobste.rs was considered but dropped: there's no "jujutsu" tag to query
(confirmed via its tags.json), and /search.json 400s on any query params —
it has no working public full-text search API, only an HTML search page.

Unlike discover.py's tool-candidate sweep (report everything unlisted, let a
human triage volume), "popular jj content" has no natural cutoff — HN/Reddit
surface plenty of noise. Per-run output is capped to the top few, picked
round-robin across sources so one noisy source can't crowd the others out
(see `merge_top_n`) — raw scores (HN points, Reddit upvotes, YouTube views)
aren't comparable across sources, so ranking is by each source's own order,
not a merged score.

YouTube requires a Data API v3 key (`YOUTUBE_API_KEY`), and Reddit requires
a script app's `REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET` (Reddit blocks
anonymous requests to its public JSON endpoints from datacenter IPs, so
unauthenticated access isn't a viable fallback there) — both are things
only the repo owner can provision. Their fetchers return `[]` gracefully
when unset, so the sweep still runs everywhere else without them.
"""

from __future__ import annotations

import os
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx2

from awesome_jj_tools.candidates import (
    filter_missing,
    load_url_snapshot,
    save_url_snapshot,
    split_new_vs_outstanding,
)
from awesome_jj_tools.discover import DEFAULT_IGNORED_PATH, load_ignored_urls
from awesome_jj_tools.entries import DEFAULT_ENTRIES_PATH, all_urls, load_entries
from awesome_jj_tools.http import get_json, new_client, reddit_access_token
from awesome_jj_tools.progress import parallel_map

DEFAULT_ARTICLES_SNAPSHOT_PATH = DEFAULT_ENTRIES_PATH.parent / "media-articles-snapshot.json"
DEFAULT_VIDEOS_SNAPSHOT_PATH = DEFAULT_ENTRIES_PATH.parent / "media-videos-snapshot.json"

HN_SEARCH_API = "https://hn.algolia.com/api/v1/search"
REDDIT_OAUTH_SEARCH_URL = "https://oauth.reddit.com/search"
YOUTUBE_SEARCH_API = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_API = "https://www.googleapis.com/youtube/v3/videos"

# Wide enough to comfortably cover a biweekly run's gap without missing
# anything that landed near the previous run's cutoff.
LOOKBACK_DAYS = 35

# "Popular" has no natural threshold — cap output instead, round-robin
# across sources, so a slow month reports 0-1 rather than padding with
# mediocre content to hit a number.
TOP_N_ARTICLES_PER_RUN = 3
TOP_N_VIDEOS_PER_RUN = 2


@dataclass(frozen=True)
class MediaCandidate:
    name: str
    url: str
    source: str
    score: int
    published: str = ""


def _cutoff(now: datetime) -> datetime:
    return now - timedelta(days=LOOKBACK_DAYS)


async def fetch_hn_candidates(
    client: httpx2.AsyncClient,
    fetcher: Callable[[httpx2.AsyncClient, str], Awaitable[Any]] = get_json,
    now: datetime | None = None,
) -> list[MediaCandidate]:
    now = now or datetime.now(UTC)
    cutoff_ts = int(_cutoff(now).timestamp())
    url = f"{HN_SEARCH_API}?query=jujutsu&tags=story&numericFilters=created_at_i%3E{cutoff_ts}"
    data = await fetcher(client, url)
    candidates = [
        MediaCandidate(
            name=hit["title"],
            url=hit.get("url") or f"https://news.ycombinator.com/item?id={hit['objectID']}",
            source="hn",
            score=hit.get("points") or 0,
            published=hit.get("created_at", ""),
        )
        for hit in data.get("hits", [])
        if hit.get("title")
    ]
    return sorted(candidates, key=lambda c: c.score, reverse=True)


async def fetch_reddit_candidates(
    client: httpx2.AsyncClient,
    fetcher: Callable[..., Awaitable[Any]] = get_json,
    now: datetime | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
    token_fetcher: Callable[[httpx2.AsyncClient, str, str], Awaitable[str]] = reddit_access_token,
) -> list[MediaCandidate]:
    client_id = client_id if client_id is not None else os.environ.get("REDDIT_CLIENT_ID")
    client_secret = (
        client_secret if client_secret is not None else os.environ.get("REDDIT_CLIENT_SECRET")
    )
    if not client_id or not client_secret:
        return []
    now = now or datetime.now(UTC)
    cutoff = _cutoff(now)
    token = await token_fetcher(client, client_id, client_secret)
    url = f"{REDDIT_OAUTH_SEARCH_URL}?q=jujutsu+vcs&sort=top&t=month&limit=25"
    data = await fetcher(client, url, headers={"Authorization": f"Bearer {token}"})
    candidates = []
    for child in data.get("data", {}).get("children", []):
        post = child.get("data", {})
        created = datetime.fromtimestamp(post.get("created_utc", 0), tz=UTC)
        if created < cutoff:
            continue
        link = (
            post.get("url")
            if not post.get("is_self")
            else f"https://www.reddit.com{post.get('permalink', '')}"
        )
        if not link:
            continue
        candidates.append(
            MediaCandidate(
                name=post.get("title", ""),
                url=link,
                source="reddit",
                score=post.get("ups") or 0,
                published=created.date().isoformat(),
            )
        )
    return sorted(candidates, key=lambda c: c.score, reverse=True)


async def fetch_youtube_candidates(
    client: httpx2.AsyncClient,
    fetcher: Callable[[httpx2.AsyncClient, str], Awaitable[Any]] = get_json,
    now: datetime | None = None,
    api_key: str | None = None,
) -> list[MediaCandidate]:
    api_key = api_key if api_key is not None else os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        return []
    now = now or datetime.now(UTC)
    published_after = _cutoff(now).strftime("%Y-%m-%dT%H:%M:%SZ")
    search_url = (
        f"{YOUTUBE_SEARCH_API}?part=snippet&type=video&order=viewCount"
        f"&q=jujutsu+vcs&publishedAfter={published_after}&maxResults=10&key={api_key}"
    )
    search_data = await fetcher(client, search_url)
    items = [item for item in search_data.get("items", []) if item.get("id", {}).get("videoId")]
    if not items:
        return []

    video_ids = [item["id"]["videoId"] for item in items]
    stats_url = f"{YOUTUBE_VIDEOS_API}?part=statistics&id={','.join(video_ids)}&key={api_key}"
    stats_data = await fetcher(client, stats_url)
    view_counts = {
        v["id"]: int(v.get("statistics", {}).get("viewCount", 0))
        for v in stats_data.get("items", [])
    }

    candidates = [
        MediaCandidate(
            name=item["snippet"]["title"],
            url=f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            source="youtube",
            score=view_counts.get(item["id"]["videoId"], 0),
            published=item["snippet"].get("publishedAt", ""),
        )
        for item in items
    ]
    return sorted(candidates, key=lambda c: c.score, reverse=True)


def merge_top_n(by_source: dict[str, list[MediaCandidate]], n: int) -> list[MediaCandidate]:
    """Round-robin merge, taking each source's highest-ranked item first, so no
    single source (however prolific) can crowd out the others within the cap.
    """
    queues = {source: list(items) for source, items in by_source.items() if items}
    merged: list[MediaCandidate] = []
    while queues and len(merged) < n:
        for source in sorted(queues.keys()):
            if len(merged) >= n:
                break
            items = queues[source]
            merged.append(items.pop(0))
            if not items:
                del queues[source]
    return merged


def _render_media_group(
    heading: str, candidates: list[MediaCandidate], empty_message: str
) -> list[str]:
    lines = [f"### {heading}", ""]
    if candidates:
        for c in candidates:
            when = f" ({c.published})" if c.published else ""
            lines.append(f"- [{c.name}]({c.url}) — {c.source}, score {c.score}{when}")
        lines.append("")
    else:
        lines.append(empty_message)
        lines.append("")
    return lines


def render_media_report(
    new_articles: list[MediaCandidate],
    outstanding_articles: list[MediaCandidate],
    new_videos: list[MediaCandidate],
    outstanding_videos: list[MediaCandidate],
    unavailable_sources: list[tuple[str, str]],
) -> str:
    lines = ["## Media discovery report", ""]
    lines.extend(_render_media_group("New articles", new_articles, "None since last run."))
    lines.extend(
        _render_media_group(
            "Still outstanding articles", outstanding_articles, "Nothing outstanding."
        )
    )
    lines.extend(_render_media_group("New videos", new_videos, "None since last run."))
    lines.extend(
        _render_media_group("Still outstanding videos", outstanding_videos, "Nothing outstanding.")
    )
    if unavailable_sources:
        lines.append("### Sources unavailable this run")
        lines.append("")
        for name, reason in unavailable_sources:
            lines.append(f"- {name}: {reason}")
        lines.append("")
    return "\n".join(lines)


ARTICLE_FETCHERS: dict[str, Callable[[httpx2.AsyncClient], Awaitable[list[MediaCandidate]]]] = {
    "hn": fetch_hn_candidates,
    "reddit": fetch_reddit_candidates,
}
VIDEO_FETCHERS: dict[str, Callable[[httpx2.AsyncClient], Awaitable[list[MediaCandidate]]]] = {
    "youtube": fetch_youtube_candidates,
}


async def _fetch_one(
    client: httpx2.AsyncClient,
    name: str,
    fn: Callable[[httpx2.AsyncClient], Awaitable[list[MediaCandidate]]],
) -> tuple[str, list[MediaCandidate], str | None]:
    try:
        return name, await fn(client), None
    except Exception as e:  # noqa: BLE001 - isolate one flaky source from the rest of the sweep
        return name, [], str(e)


async def _fetch_all(
    client: httpx2.AsyncClient,
    fetchers: dict[str, Callable[[httpx2.AsyncClient], Awaitable[list[MediaCandidate]]]],
    description: str,
) -> tuple[dict[str, list[MediaCandidate]], list[tuple[str, str]]]:
    by_source: dict[str, list[MediaCandidate]] = {}
    unavailable: list[tuple[str, str]] = []
    results = await parallel_map(
        lambda name: _fetch_one(client, name, fetchers[name]),
        list(fetchers.keys()),
        description=description,
    )
    for name, items, error in results:
        if error is not None:
            unavailable.append((name, error))
        else:
            by_source[name] = items
    return by_source, unavailable


async def run(
    entries_path: Path = DEFAULT_ENTRIES_PATH,
    articles_snapshot_path: Path = DEFAULT_ARTICLES_SNAPSHOT_PATH,
    videos_snapshot_path: Path = DEFAULT_VIDEOS_SNAPSHOT_PATH,
    ignored_path: Path = DEFAULT_IGNORED_PATH,
) -> tuple[str, bool]:
    """Returns (report_text, has_findings)."""
    data = load_entries(entries_path)
    excluded_urls = all_urls(data) | load_ignored_urls(ignored_path)
    previous_article_urls = load_url_snapshot(articles_snapshot_path)
    previous_video_urls = load_url_snapshot(videos_snapshot_path)

    async with new_client() as client:
        article_by_source, article_failures = await _fetch_all(
            client, ARTICLE_FETCHERS, "Fetching articles"
        )
        video_by_source, video_failures = await _fetch_all(
            client, VIDEO_FETCHERS, "Fetching videos"
        )

    article_missing_by_source = {
        source: filter_missing(items, excluded_urls) for source, items in article_by_source.items()
    }
    video_missing_by_source = {
        source: filter_missing(items, excluded_urls) for source, items in video_by_source.items()
    }
    article_candidates = merge_top_n(article_missing_by_source, TOP_N_ARTICLES_PER_RUN)
    video_candidates = merge_top_n(video_missing_by_source, TOP_N_VIDEOS_PER_RUN)

    new_articles, outstanding_articles = split_new_vs_outstanding(
        article_candidates, previous_article_urls
    )
    new_videos, outstanding_videos = split_new_vs_outstanding(video_candidates, previous_video_urls)

    save_url_snapshot({c.url for c in article_candidates}, articles_snapshot_path)
    save_url_snapshot({c.url for c in video_candidates}, videos_snapshot_path)

    report = render_media_report(
        new_articles,
        outstanding_articles,
        new_videos,
        outstanding_videos,
        article_failures + video_failures,
    )
    has_findings = bool(new_articles or outstanding_articles or new_videos or outstanding_videos)
    return report, has_findings
