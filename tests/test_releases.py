from awesome_jj_tools.entries import GitHubRepoRef
from awesome_jj_tools.releases import check_releases, parse_latest_release, render_report

SAMPLE_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>tag:github.com,2008:Repository/1/v1.2.0</id>
    <title>v1.2.0</title>
    <link href="https://github.com/x/a/releases/tag/v1.2.0" rel="alternate" type="text/html"/>
  </entry>
  <entry>
    <id>tag:github.com,2008:Repository/1/v1.1.0</id>
    <title>v1.1.0</title>
    <link href="https://github.com/x/a/releases/tag/v1.1.0" rel="alternate" type="text/html"/>
  </entry>
</feed>
"""

EMPTY_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"></feed>
"""


def test_parse_latest_release_returns_newest_entry():
    result = parse_latest_release(SAMPLE_ATOM)
    assert result is not None
    entry_id, title, link = result
    assert entry_id == "tag:github.com,2008:Repository/1/v1.2.0"
    assert title == "v1.2.0"
    assert link == "https://github.com/x/a/releases/tag/v1.2.0"


def test_parse_latest_release_returns_none_for_empty_feed():
    assert parse_latest_release(EMPTY_ATOM) is None


def _ref():
    return GitHubRepoRef(
        owner="x", repo="a", url="https://github.com/x/a", entry_name="a", section_path=()
    )


def test_check_releases_detects_new_release_when_none_seen_before():
    new_releases, updated = check_releases([_ref()], last_seen={}, fetcher=lambda url: SAMPLE_ATOM)
    assert len(new_releases) == 1
    assert new_releases[0].release_title == "v1.2.0"
    assert updated["https://github.com/x/a"] == "tag:github.com,2008:Repository/1/v1.2.0"


def test_check_releases_idempotent_on_second_run():
    last_seen = {"https://github.com/x/a": "tag:github.com,2008:Repository/1/v1.2.0"}
    new_releases, updated = check_releases(
        [_ref()], last_seen=last_seen, fetcher=lambda url: SAMPLE_ATOM
    )
    assert new_releases == []
    assert updated == last_seen


def test_check_releases_ignores_repo_with_no_releases_feed():
    def fetcher(url):
        raise Exception("404")

    new_releases, updated = check_releases([_ref()], last_seen={}, fetcher=fetcher)
    assert new_releases == []
    assert updated == {}


def test_check_releases_ignores_repo_with_empty_feed():
    new_releases, updated = check_releases([_ref()], last_seen={}, fetcher=lambda url: EMPTY_ATOM)
    assert new_releases == []
    assert updated == {}


def test_render_report_empty():
    assert "No new releases" in render_report([])


def test_render_report_lists_releases_sorted_by_repo_name():
    from awesome_jj_tools.releases import Release

    releases = [
        Release(
            repo_name="Zeta", repo_url="u", release_title="t", release_id="i", release_link="l"
        ),
        Release(
            repo_name="Alpha", repo_url="u", release_title="t", release_id="i", release_link="l"
        ),
    ]
    output = render_report(releases)
    assert output.index("Alpha") < output.index("Zeta")
