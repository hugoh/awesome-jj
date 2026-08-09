from datetime import UTC, datetime, timedelta

from awesome_jj_tools.media import (
    MediaCandidate,
    fetch_hn_candidates,
    fetch_reddit_candidates,
    fetch_youtube_candidates,
    merge_top_n,
    render_media_report,
)

NOW = datetime(2026, 8, 9, tzinfo=UTC)


async def test_fetch_hn_candidates_sorts_by_points_and_passes_lookback_cutoff(client):
    seen_urls = []

    async def fake_fetcher(client, url):
        seen_urls.append(url)
        return {
            "hits": [
                {
                    "title": "Low score",
                    "url": "https://example.com/low",
                    "points": 3,
                    "created_at": "2026-08-01T00:00:00.000Z",
                    "objectID": "2",
                },
                {
                    "title": "High score",
                    "url": "https://example.com/high",
                    "points": 80,
                    "created_at": "2026-08-05T00:00:00.000Z",
                    "objectID": "3",
                },
            ]
        }

    result = await fetch_hn_candidates(client, fake_fetcher, now=NOW)

    assert [c.name for c in result] == ["High score", "Low score"]
    assert result[0].source == "hn"
    # Lookback is enforced server-side via this param, not re-checked client-side.
    assert "numericFilters=created_at_i" in seen_urls[0]


async def test_fetch_hn_candidates_uses_discussion_url_when_missing(client):
    async def fake_fetcher(client, url):
        return {
            "hits": [
                {
                    "title": "Ask HN: jj tips?",
                    "url": None,
                    "points": 40,
                    "created_at": "2026-08-05T00:00:00.000Z",
                    "objectID": "42",
                }
            ]
        }

    result = await fetch_hn_candidates(client, fake_fetcher, now=NOW)
    assert result[0].url == "https://news.ycombinator.com/item?id=42"


async def _fake_reddit_token(client, client_id, client_secret):
    return "fake-token"


async def test_fetch_reddit_candidates_returns_empty_without_credentials(client):
    result = await fetch_reddit_candidates(
        client, now=NOW, client_id=None, client_secret=None, token_fetcher=_fake_reddit_token
    )
    assert result == []


async def test_fetch_reddit_candidates_uses_permalink_for_self_posts(client):
    async def fake_fetcher(client, url, headers=None):
        assert headers == {"Authorization": "Bearer fake-token"}
        return {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "A self post",
                            "is_self": True,
                            "permalink": "/r/jj/comments/abc/a_self_post/",
                            "ups": 12,
                            "created_utc": NOW.timestamp() - 1000,
                        }
                    }
                ]
            }
        }

    result = await fetch_reddit_candidates(
        client,
        fake_fetcher,
        now=NOW,
        client_id="id",
        client_secret="secret",
        token_fetcher=_fake_reddit_token,
    )
    assert result[0].url == "https://www.reddit.com/r/jj/comments/abc/a_self_post/"


async def test_fetch_reddit_candidates_filters_by_lookback(client):
    async def fake_fetcher(client, url, headers=None):
        return {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "Old",
                            "is_self": False,
                            "url": "https://example.com/old",
                            "ups": 99,
                            "created_utc": (NOW - timedelta(days=100)).timestamp(),
                        }
                    }
                ]
            }
        }

    result = await fetch_reddit_candidates(
        client,
        fake_fetcher,
        now=NOW,
        client_id="id",
        client_secret="secret",
        token_fetcher=_fake_reddit_token,
    )
    assert result == []


async def test_fetch_youtube_candidates_returns_empty_without_api_key(client):
    result = await fetch_youtube_candidates(client, now=NOW, api_key=None)
    assert result == []


async def test_fetch_youtube_candidates_ranks_by_view_count(client):
    async def fake_fetcher(client, url):
        if "youtube/v3/search" in url:
            return {
                "items": [
                    {
                        "id": {"videoId": "a"},
                        "snippet": {"title": "A", "publishedAt": "2026-08-01"},
                    },
                    {
                        "id": {"videoId": "b"},
                        "snippet": {"title": "B", "publishedAt": "2026-08-02"},
                    },
                ]
            }
        return {
            "items": [
                {"id": "a", "statistics": {"viewCount": "50"}},
                {"id": "b", "statistics": {"viewCount": "500"}},
            ]
        }

    result = await fetch_youtube_candidates(client, fake_fetcher, now=NOW, api_key="fake-key")
    assert [c.name for c in result] == ["B", "A"]
    assert result[0].score == 500


def test_merge_top_n_round_robins_across_sources():
    by_source = {
        "hn": [
            MediaCandidate("h1", "https://x/h1", "hn", 100),
            MediaCandidate("h2", "https://x/h2", "hn", 90),
        ],
        "reddit": [MediaCandidate("r1", "https://x/r1", "reddit", 5)],
    }
    result = merge_top_n(by_source, 2)
    assert [c.name for c in result] == ["h1", "r1"]


def test_merge_top_n_respects_cap():
    by_source = {
        "hn": [MediaCandidate(f"h{i}", f"https://x/h{i}", "hn", 100 - i) for i in range(5)]
    }
    result = merge_top_n(by_source, 3)
    assert len(result) == 3
    assert [c.name for c in result] == ["h0", "h1", "h2"]


def test_merge_top_n_handles_empty_sources():
    assert merge_top_n({}, 3) == []
    assert merge_top_n({"hn": []}, 3) == []


def test_render_media_report_nothing_found():
    output = render_media_report([], [], [], [], [])
    assert output.count("None since last run.") == 2
    assert output.count("Nothing outstanding.") == 2
    assert "Sources unavailable" not in output


def test_render_media_report_lists_unavailable_sources():
    output = render_media_report([], [], [], [], [("reddit", "429 rate limited")])
    assert "### Sources unavailable this run" in output
    assert "reddit: 429 rate limited" in output


def test_render_media_report_shows_score_and_source():
    candidate = MediaCandidate("Cool post", "https://x/cool", "hn", 42, "2026-08-01")
    output = render_media_report([candidate], [], [], [], [])
    assert "- [Cool post](https://x/cool) — hn, score 42 (2026-08-01)" in output


async def test_fetch_all_isolates_a_failing_source(client):
    from awesome_jj_tools.media import _fetch_all

    async def ok(client):
        return [MediaCandidate("ok", "https://x/ok", "good", 1)]

    async def broken(client):
        raise RuntimeError("503 unavailable")

    by_source, unavailable = await _fetch_all(
        client, {"good": ok, "bad": broken}, "Fetching test sources"
    )

    assert [c.name for c in by_source["good"]] == ["ok"]
    assert unavailable == [("bad", "503 unavailable")]
