import subprocess
from unittest.mock import patch

import httpx
import pytest

from awesome_jj_tools.http import (
    gh_repo_info,
    gh_search_repos,
    github_headers,
    github_token,
    reddit_access_token,
)


@pytest.fixture(autouse=True)
def _reset_token_cache(monkeypatch):
    github_token.cache_clear()
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    yield
    github_token.cache_clear()


def test_github_token_prefers_github_token_env_var(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "from-env")
    with patch("subprocess.run") as mock_run:
        assert github_token() == "from-env"
    mock_run.assert_not_called()


def test_github_token_falls_back_to_gh_token_env_var(monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "from-gh-token")
    with patch("subprocess.run") as mock_run:
        assert github_token() == "from-gh-token"
    mock_run.assert_not_called()


def test_github_token_falls_back_to_gh_auth_token_when_no_env_var():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="from-gh-cli\n", stderr=""
        )
        assert github_token() == "from-gh-cli"
    mock_run.assert_called_once_with(
        ["gh", "auth", "token"], capture_output=True, text=True, check=True
    )


def test_github_token_is_cached(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "cached-value")
    assert github_token() == "cached-value"
    monkeypatch.setenv("GITHUB_TOKEN", "different-value")
    assert github_token() == "cached-value"  # still the cached one


def test_github_headers_include_bearer_token(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "secret-token")
    headers = github_headers()
    assert headers["Authorization"] == "Bearer secret-token"
    assert headers["Accept"] == "application/vnd.github+json"


def _mock_client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_gh_search_repos_maps_rest_api_fields_to_expected_names(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    seen_requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request)
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "full_name": "x/a",
                        "html_url": "https://github.com/x/a",
                        "description": "desc",
                        "pushed_at": "2026-01-01T00:00:00Z",
                        "created_at": "2025-01-01T00:00:00Z",
                        "stargazers_count": 42,
                    }
                ]
            },
        )

    async with _mock_client(handler) as client:
        result = await gh_search_repos(client, "jujutsu")

    assert result == [
        {
            "fullName": "x/a",
            "url": "https://github.com/x/a",
            "description": "desc",
            "pushedAt": "2026-01-01T00:00:00Z",
            "createdAt": "2025-01-01T00:00:00Z",
            "stargazersCount": 42,
        }
    ]
    assert seen_requests[0].headers["Authorization"] == "Bearer t"
    assert "topic%3Ajujutsu" in str(seen_requests[0].url)


async def test_gh_repo_info_sends_authenticated_request(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    seen_requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request)
        return httpx.Response(200, json={"archived": False, "pushed_at": "2026-01-01T00:00:00Z"})

    async with _mock_client(handler) as client:
        result = await gh_repo_info(client, "owner", "repo")

    assert result == {"archived": False, "pushed_at": "2026-01-01T00:00:00Z"}
    assert seen_requests[0].headers["Authorization"] == "Bearer t"
    assert str(seen_requests[0].url) == "https://api.github.com/repos/owner/repo"


async def test_reddit_access_token_sends_basic_auth_and_returns_token():
    seen_requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request)
        return httpx.Response(200, json={"access_token": "reddit-token", "expires_in": 3600})

    async with _mock_client(handler) as client:
        token = await reddit_access_token(client, "client-id", "client-secret")

    assert token == "reddit-token"
    request = seen_requests[0]
    assert str(request.url) == "https://www.reddit.com/api/v1/access_token"
    assert request.headers["Authorization"].startswith("Basic ")
    assert request.content == b"grant_type=client_credentials"
