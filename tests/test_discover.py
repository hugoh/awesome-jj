from datetime import UTC, datetime

from awesome_jj_tools.discover import (
    Candidate,
    check_staleness,
    fetch_codeberg_candidates,
    fetch_crates_candidates,
    fetch_github_candidates,
    fetch_gitlab_candidates,
    filter_new_candidates,
    render_report,
)
from awesome_jj_tools.entries import GitHubRepoRef


def test_filter_new_candidates_excludes_known_urls():
    candidates = [
        Candidate(name="a", url="https://github.com/x/a", description="", source="github"),
        Candidate(name="b", url="https://github.com/x/b", description="", source="github"),
    ]
    result = filter_new_candidates(
        candidates, known_urls={"https://github.com/x/a"}, seen_urls=set()
    )
    assert [c.name for c in result] == ["b"]


def test_filter_new_candidates_excludes_seen_urls():
    candidates = [
        Candidate(name="a", url="https://github.com/x/a", description="", source="github")
    ]
    result = filter_new_candidates(
        candidates, known_urls=set(), seen_urls={"https://github.com/x/a"}
    )
    assert result == []


def test_filter_new_candidates_ignores_trailing_slash_differences():
    candidates = [
        Candidate(name="a", url="https://github.com/x/a/", description="", source="github")
    ]
    result = filter_new_candidates(
        candidates, known_urls={"https://github.com/x/a"}, seen_urls=set()
    )
    assert result == []


def test_fetch_github_candidates_dedups_across_topics():
    calls = []

    def fake_fetcher(topic):
        calls.append(topic)
        return [
            {
                "fullName": "x/a",
                "url": "https://github.com/x/a",
                "description": "desc",
                "pushedAt": "2026-01-01T00:00:00Z",
            }
        ]

    result = fetch_github_candidates(fake_fetcher)
    assert len(calls) == 2  # jujutsu + jj-vcs
    assert len(result) == 1
    assert result[0].source == "github"


def test_fetch_gitlab_candidates():
    def fake_fetcher(url):
        assert "topic=jujutsu" in url
        return [{"name_with_namespace": "ns / proj", "web_url": "https://gitlab.com/ns/proj"}]

    result = fetch_gitlab_candidates(fake_fetcher)
    assert result[0].source == "gitlab"
    assert result[0].url == "https://gitlab.com/ns/proj"


def test_fetch_codeberg_candidates():
    def fake_fetcher(url):
        return {"data": [{"full_name": "ns/proj", "html_url": "https://codeberg.org/ns/proj"}]}

    result = fetch_codeberg_candidates(fake_fetcher)
    assert result[0].source == "codeberg"


def test_fetch_crates_candidates():
    def fake_fetcher(url):
        return {"versions": [{"crate": "some-jj-plugin"}]}

    result = fetch_crates_candidates(fake_fetcher)
    assert result[0].name == "some-jj-plugin"
    assert result[0].url == "https://crates.io/crates/some-jj-plugin"


def test_check_staleness_flags_archived():
    ref = GitHubRepoRef(
        owner="x", repo="a", url="https://github.com/x/a", entry_name="a", section_path=()
    )

    def fake_fetcher(owner, repo):
        return {"archived": True, "pushed_at": "2026-01-01T00:00:00Z"}

    stale = check_staleness([ref], fake_fetcher, now=datetime(2026, 6, 1, tzinfo=UTC))
    assert len(stale) == 1
    assert stale[0].reason == "archived"


def test_check_staleness_flags_no_push_in_a_year():
    ref = GitHubRepoRef(
        owner="x", repo="a", url="https://github.com/x/a", entry_name="a", section_path=()
    )

    def fake_fetcher(owner, repo):
        return {"archived": False, "pushed_at": "2024-01-01T00:00:00Z"}

    stale = check_staleness([ref], fake_fetcher, now=datetime(2026, 6, 1, tzinfo=UTC))
    assert len(stale) == 1
    assert "no push since" in stale[0].reason


def test_check_staleness_ignores_recently_active_repo():
    ref = GitHubRepoRef(
        owner="x", repo="a", url="https://github.com/x/a", entry_name="a", section_path=()
    )

    def fake_fetcher(owner, repo):
        return {"archived": False, "pushed_at": "2026-05-01T00:00:00Z"}

    stale = check_staleness([ref], fake_fetcher, now=datetime(2026, 6, 1, tzinfo=UTC))
    assert stale == []


def test_render_report_no_candidates_or_stale():
    output = render_report([], [])
    assert "No new candidates this run." in output
    assert "No existing entries flagged as stale this run." in output


def test_render_report_groups_by_source():
    candidates = [
        Candidate(name="b", url="https://github.com/x/b", description="", source="github"),
        Candidate(name="a", url="https://gitlab.com/x/a", description="", source="gitlab"),
    ]
    output = render_report(candidates, [])
    assert output.index("#### github") < output.index("#### gitlab")
