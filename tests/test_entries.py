from awesome_jj_tools.entries import all_entries, all_urls, github_repos

SAMPLE = {
    "official_resources": [
        {"name": "Jujutsu homepage", "url": "https://www.jj-vcs.dev"},
    ],
    "tools": {
        "gui": [
            {"name": "gg", "url": "https://github.com/gulbanana/gg", "description": "GUI for jj."},
        ],
        "tui": [
            {
                "name": "jjewel",
                "url": "https://checksimsoftware.com/jjewel",
                "description": "Mac client.",
            },
        ],
    },
}


def test_all_entries_walks_nested_and_flat_sections():
    entries = all_entries(SAMPLE)
    names = {e["name"] for _, e in entries}
    assert names == {"Jujutsu homepage", "gg", "jjewel"}


def test_all_entries_records_section_path():
    entries = all_entries(SAMPLE)
    paths = {path for path, _ in entries}
    assert ("official_resources",) in paths
    assert ("tools", "gui") in paths
    assert ("tools", "tui") in paths


def test_all_urls():
    assert all_urls(SAMPLE) == {
        "https://www.jj-vcs.dev",
        "https://github.com/gulbanana/gg",
        "https://checksimsoftware.com/jjewel",
    }


def test_github_repos_only_matches_bare_owner_repo_urls():
    refs = github_repos(SAMPLE)
    assert len(refs) == 1
    assert refs[0].owner == "gulbanana"
    assert refs[0].repo == "gg"
    assert refs[0].entry_name == "gg"
    assert refs[0].section_path == ("tools", "gui")


def test_github_repos_ignores_non_repo_github_urls():
    data = {"x": [{"name": "discussions", "url": "https://github.com/jj-vcs/jj/discussions"}]}
    assert github_repos(data) == []


def test_load_save_round_trip(tmp_path):
    from awesome_jj_tools.entries import load_entries, save_entries

    path = tmp_path / "entries.yaml"
    save_entries(SAMPLE, path)
    loaded = load_entries(path)
    assert loaded == SAMPLE
