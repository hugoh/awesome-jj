"""Thin HTTP helpers shared by discover/releases/stars, isolated here so tests mock one place."""

from __future__ import annotations

import subprocess
from typing import Any

import requests

USER_AGENT = "awesome-jj-tools (https://github.com/hugoh/awesome-jj)"


def get_json(url: str, params: dict[str, Any] | None = None) -> Any:
    response = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    return response.json()


def get_text(url: str) -> str:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    return response.text


def gh_search_repos(topic: str) -> list[dict[str, Any]]:
    """Wraps `gh search repos --topic <topic>` since gh handles auth/rate-limits for us."""
    result = subprocess.run(
        [
            "gh",
            "search",
            "repos",
            f"--topic={topic}",
            "--sort=updated",
            "--limit=100",
            "--json=fullName,url,description,pushedAt,createdAt,stargazersCount",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    import json

    return json.loads(result.stdout)


def gh_repo_info(owner: str, repo: str) -> dict[str, Any]:
    return get_json(f"https://api.github.com/repos/{owner}/{repo}")
