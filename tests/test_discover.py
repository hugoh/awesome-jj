from datetime import UTC, datetime

from awesome_jj_tools.discover import (
    Candidate,
    check_staleness,
    fetch_codeberg_candidates,
    fetch_crates_candidates,
    fetch_github_candidates,
    fetch_gitlab_candidates,
    filter_low_signal,
    filter_missing,
    load_ignored_urls,
    render_report,
    split_new_vs_outstanding,
)
from awesome_jj_tools.entries import GitHubRepoRef


def test_load_ignored_urls_reads_real_file():
    urls = load_ignored_urls()
    assert "https://github.com/chawyehsu/awesome-jj" in urls


def test_load_ignored_urls_returns_empty_set_when_file_missing(tmp_path):
    assert load_ignored_urls(tmp_path / "does-not-exist.yaml") == set()


def test_load_ignored_urls_parses_yaml(tmp_path):
    path = tmp_path / "ignored.yaml"
    path.write_text(
        "ignored:\n  - url: https://github.com/x/y\n    reason: test\n", encoding="utf-8"
    )
    assert load_ignored_urls(path) == {"https://github.com/x/y"}


def test_filter_missing_excludes_known_urls():
    candidates = [
        Candidate(name="a", url="https://github.com/x/a", description="", source="github"),
        Candidate(name="b", url="https://github.com/x/b", description="", source="github"),
    ]
    result = filter_missing(candidates, excluded_urls={"https://github.com/x/a"})
    assert [c.name for c in result] == ["b"]


def test_filter_missing_ignores_trailing_slash_differences():
    candidates = [
        Candidate(name="a", url="https://github.com/x/a/", description="", source="github")
    ]
    result = filter_missing(candidates, excluded_urls={"https://github.com/x/a"})
    assert result == []


def test_split_new_vs_outstanding_new_candidate_not_in_previous_snapshot():
    candidates = [
        Candidate(name="a", url="https://github.com/x/a", description="", source="github")
    ]
    new, outstanding = split_new_vs_outstanding(candidates, previous_snapshot_urls=set())
    assert [c.name for c in new] == ["a"]
    assert outstanding == []


def test_split_new_vs_outstanding_candidate_in_previous_snapshot_is_outstanding():
    candidates = [
        Candidate(name="a", url="https://github.com/x/a", description="", source="github")
    ]
    new, outstanding = split_new_vs_outstanding(
        candidates, previous_snapshot_urls={"https://github.com/x/a"}
    )
    assert new == []
    assert [c.name for c in outstanding] == ["a"]


def test_split_new_vs_outstanding_never_drops_a_candidate_across_repeated_runs():
    """A candidate mentioned once must keep appearing (as outstanding) every run after,
    not silently vanish — that's the whole point of dropping the old permanent-suppress list."""
    candidate = Candidate(name="a", url="https://github.com/x/a", description="", source="github")
    previous_urls: set[str] = set()

    for _ in range(5):
        new, outstanding = split_new_vs_outstanding([candidate], previous_urls)
        assert new or outstanding  # always shows up somewhere
        previous_urls = {candidate.url}

    # after the first run it should always land in "outstanding," never disappear
    new, outstanding = split_new_vs_outstanding([candidate], previous_urls)
    assert [c.name for c in outstanding] == ["a"]


def test_split_new_vs_outstanding_ignores_trailing_slash_differences():
    candidates = [
        Candidate(name="a", url="https://github.com/x/a/", description="", source="github")
    ]
    new, outstanding = split_new_vs_outstanding(
        candidates, previous_snapshot_urls={"https://github.com/x/a"}
    )
    assert new == []
    assert [c.name for c in outstanding] == ["a"]


async def test_fetch_github_candidates_dedups_across_topics(client):
    calls = []

    async def fake_fetcher(client, topic):
        calls.append(topic)
        return [
            {
                "fullName": "x/a",
                "url": "https://github.com/x/a",
                "description": "desc",
                "pushedAt": "2026-01-01T00:00:00Z",
                "stargazersCount": 5,
            }
        ]

    result = await fetch_github_candidates(client, fake_fetcher)
    assert len(calls) == 2  # jujutsu + jj-vcs
    assert len(result) == 1
    assert result[0].source == "github"
    assert result[0].stars == 5


async def test_fetch_github_candidates_defaults_stars_to_zero_when_missing(client):
    async def fake_fetcher(client, topic):
        return [{"fullName": "x/a", "url": "https://github.com/x/a", "description": ""}]

    result = await fetch_github_candidates(client, fake_fetcher)
    assert result[0].stars == 0


def test_filter_low_signal_drops_low_star_github_candidates():
    candidates = [
        Candidate(name="a", url="https://github.com/x/a", description="", source="github", stars=0),
        Candidate(name="b", url="https://github.com/x/b", description="", source="github", stars=5),
    ]
    result = filter_low_signal(candidates, min_github_stars=2)
    assert [c.name for c in result] == ["b"]


def test_filter_low_signal_keeps_candidates_at_exact_threshold():
    candidates = [
        Candidate(name="a", url="https://github.com/x/a", description="", source="github", stars=2)
    ]
    result = filter_low_signal(candidates, min_github_stars=2)
    assert len(result) == 1


def test_filter_low_signal_does_not_apply_star_filter_to_non_github_sources():
    candidates = [
        Candidate(name="a", url="https://gitlab.com/x/a", description="", source="gitlab", stars=0)
    ]
    result = filter_low_signal(candidates, min_github_stars=2)
    assert len(result) == 1


async def test_fetch_gitlab_candidates(client):
    async def fake_fetcher(client, url):
        assert "topic=jujutsu" in url
        return [{"name_with_namespace": "ns / proj", "web_url": "https://gitlab.com/ns/proj"}]

    result = await fetch_gitlab_candidates(client, fake_fetcher)
    assert result[0].source == "gitlab"
    assert result[0].url == "https://gitlab.com/ns/proj"


async def test_fetch_codeberg_candidates(client):
    async def fake_fetcher(client, url):
        return {"data": [{"full_name": "ns/proj", "html_url": "https://codeberg.org/ns/proj"}]}

    result = await fetch_codeberg_candidates(client, fake_fetcher)
    assert result[0].source == "codeberg"


async def test_fetch_crates_candidates_resolves_to_repository_url(client):
    async def fake_fetcher(client, url):
        if "reverse_dependencies" in url:
            return {"versions": [{"crate": "lumen"}]}
        assert url == "https://crates.io/api/v1/crates/lumen"
        return {
            "crate": {
                "repository": "https://github.com/jnsahaj/lumen",
                "homepage": None,
                "description": "A CLI tool for AI-generated commit messages",
            }
        }

    result = await fetch_crates_candidates(client, fake_fetcher)
    assert result[0].name == "lumen"
    assert result[0].url == "https://github.com/jnsahaj/lumen"
    assert result[0].description == "A CLI tool for AI-generated commit messages"


async def test_fetch_crates_candidates_collapses_multiline_description(client):
    async def fake_fetcher(client, url):
        if "reverse_dependencies" in url:
            return {"versions": [{"crate": "tmux-sessionizer"}]}
        return {
            "crate": {
                "repository": "https://github.com/jrmoulton/tmux-sessionizer",
                "homepage": None,
                "description": "Fuzzy find all git repositories in a list of\n"
                "specified folders and open them as a new tmux session. \n",
            }
        }

    result = await fetch_crates_candidates(client, fake_fetcher)
    assert result[0].description == (
        "Fuzzy find all git repositories in a list of "
        "specified folders and open them as a new tmux session."
    )


async def test_fetch_crates_candidates_falls_back_to_homepage(client):
    async def fake_fetcher(client, url):
        if "reverse_dependencies" in url:
            return {"versions": [{"crate": "some-plugin"}]}
        return {"crate": {"repository": None, "homepage": "https://example.com/some-plugin"}}

    result = await fetch_crates_candidates(client, fake_fetcher)
    assert result[0].url == "https://example.com/some-plugin"


async def test_fetch_crates_candidates_falls_back_to_crates_io_page_when_no_links(client):
    async def fake_fetcher(client, url):
        if "reverse_dependencies" in url:
            return {"versions": [{"crate": "some-plugin"}]}
        return {"crate": {"repository": None, "homepage": None}}

    result = await fetch_crates_candidates(client, fake_fetcher)
    assert result[0].url == "https://crates.io/crates/some-plugin"


async def test_fetch_crates_candidates_falls_back_when_metadata_fetch_fails(client):
    async def fake_fetcher(client, url):
        if "reverse_dependencies" in url:
            return {"versions": [{"crate": "some-plugin"}]}
        raise Exception("404")

    result = await fetch_crates_candidates(client, fake_fetcher)
    assert result[0].url == "https://crates.io/crates/some-plugin"


async def test_fetch_crates_candidates_dedups_crate_names(client):
    async def fake_fetcher(client, url):
        if "reverse_dependencies" in url:
            return {"versions": [{"crate": "dup"}, {"crate": "dup"}]}
        return {"crate": {}}

    result = await fetch_crates_candidates(client, fake_fetcher)
    assert len(result) == 1


async def test_check_staleness_flags_archived(client):
    ref = GitHubRepoRef(
        owner="x", repo="a", url="https://github.com/x/a", entry_name="a", section_path=()
    )

    async def fake_fetcher(client, owner, repo):
        return {"archived": True, "pushed_at": "2026-01-01T00:00:00Z"}

    stale = await check_staleness(client, [ref], fake_fetcher, now=datetime(2026, 6, 1, tzinfo=UTC))
    assert len(stale) == 1
    assert stale[0].reason == "archived"


async def test_check_staleness_flags_no_push_in_a_year(client):
    ref = GitHubRepoRef(
        owner="x", repo="a", url="https://github.com/x/a", entry_name="a", section_path=()
    )

    async def fake_fetcher(client, owner, repo):
        return {"archived": False, "pushed_at": "2024-01-01T00:00:00Z"}

    stale = await check_staleness(client, [ref], fake_fetcher, now=datetime(2026, 6, 1, tzinfo=UTC))
    assert len(stale) == 1
    assert "no push since" in stale[0].reason


async def test_check_staleness_ignores_recently_active_repo(client):
    ref = GitHubRepoRef(
        owner="x", repo="a", url="https://github.com/x/a", entry_name="a", section_path=()
    )

    async def fake_fetcher(client, owner, repo):
        return {"archived": False, "pushed_at": "2026-05-01T00:00:00Z"}

    stale = await check_staleness(client, [ref], fake_fetcher, now=datetime(2026, 6, 1, tzinfo=UTC))
    assert stale == []


async def test_check_staleness_handles_multiple_refs_concurrently(client):
    refs = [
        GitHubRepoRef(
            owner="x",
            repo=f"r{i}",
            url=f"https://github.com/x/r{i}",
            entry_name=f"r{i}",
            section_path=(),
        )
        for i in range(5)
    ]

    async def fake_fetcher(client, owner, repo):
        return {"archived": repo == "r2", "pushed_at": "2026-05-01T00:00:00Z"}

    stale = await check_staleness(client, refs, fake_fetcher, now=datetime(2026, 6, 1, tzinfo=UTC))
    assert [s.name for s in stale] == ["r2"]


def test_render_report_nothing_found():
    output = render_report([], [], [])
    assert "None since last run." in output
    assert "Nothing outstanding." in output
    assert "No existing entries flagged as stale this run." in output


def test_render_report_groups_new_by_source():
    candidates = [
        Candidate(name="b", url="https://github.com/x/b", description="", source="github"),
        Candidate(name="a", url="https://gitlab.com/x/a", description="", source="gitlab"),
    ]
    output = render_report(candidates, [], [])
    assert output.index("#### github") < output.index("#### gitlab")


def test_render_report_shows_outstanding_separately_from_new():
    new = [
        Candidate(name="new-one", url="https://github.com/x/new", description="", source="github")
    ]
    outstanding = [
        Candidate(name="old-one", url="https://github.com/x/old", description="", source="github")
    ]
    output = render_report(new, outstanding, [])
    assert output.index("### New candidates") < output.index("new-one")
    assert output.index("### Still outstanding") < output.index("old-one")
    assert output.index("new-one") < output.index("### Still outstanding")
