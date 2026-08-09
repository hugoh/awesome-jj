"""Async HTTP helpers shared by discover/releases/stars, isolated here so tests mock one place.

httpx.AsyncClient (not requests + a hand-rolled thread pool) is what actually
provides the concurrency discover/releases/stars need — one client, shared
across a run, with its connection pool capped via httpx.Limits so a sweep of
~150 repos doesn't burst past GitHub's abuse-detection secondary rate limit.
"""

from __future__ import annotations

import os
import subprocess
from functools import lru_cache
from typing import Any

import httpx

USER_AGENT = "awesome-jj-tools (https://github.com/hugoh/awesome-jj)"
GITHUB_API = "https://api.github.com"
REDDIT_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"

# Keep well under GitHub's secondary (abuse-detection) rate limit, which
# throttles bursts of concurrent requests independently of the 5000/hr quota.
MAX_CONCURRENCY = 8


def new_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT},
        limits=httpx.Limits(
            max_connections=MAX_CONCURRENCY, max_keepalive_connections=MAX_CONCURRENCY
        ),
        timeout=30,
    )


@lru_cache(maxsize=1)
def github_token() -> str:
    """The GitHub token to authenticate REST API calls with (5000/hr vs. 60/hr anonymous).

    In CI, discovery.yml exports GH_TOKEN/GITHUB_TOKEN from secrets.GITHUB_TOKEN. Locally,
    fall back to whatever `gh` is already authenticated as — one subprocess call, cached, not
    one per request.
    """
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token
    result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def github_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {github_token()}",
        "Accept": "application/vnd.github+json",
    }


async def get_json(
    client: httpx.AsyncClient,
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> Any:
    response = await client.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


async def get_text(client: httpx.AsyncClient, url: str) -> str:
    response = await client.get(url)
    response.raise_for_status()
    return response.text


async def gh_search_repos(client: httpx.AsyncClient, topic: str) -> list[dict[str, Any]]:
    """GitHub's REST search API, authenticated — same field names `gh search repos --json=...`
    produced, so callers (fetch_github_candidates) don't need to know this isn't `gh` anymore.
    """
    data = await get_json(
        client,
        f"{GITHUB_API}/search/repositories",
        params={"q": f"topic:{topic}", "sort": "updated", "per_page": 100},
        headers=github_headers(),
    )
    return [
        {
            "fullName": item["full_name"],
            "url": item["html_url"],
            "description": item["description"],
            "pushedAt": item["pushed_at"],
            "createdAt": item["created_at"],
            "stargazersCount": item["stargazers_count"],
        }
        for item in data["items"]
    ]


async def gh_repo_info(client: httpx.AsyncClient, owner: str, repo: str) -> dict[str, Any]:
    return await get_json(client, f"{GITHUB_API}/repos/{owner}/{repo}", headers=github_headers())


async def reddit_access_token(client: httpx.AsyncClient, client_id: str, client_secret: str) -> str:
    """Client-credentials OAuth token for oauth.reddit.com — Reddit blocks anonymous
    requests to www.reddit.com's public JSON endpoints from datacenter IPs (like CI
    runners) outright, so the unauthenticated path isn't a fallback, just broken there.
    """
    response = await client.post(
        REDDIT_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return response.json()["access_token"]
