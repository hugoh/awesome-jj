from dataclasses import dataclass

from awesome_jj_tools.candidates import (
    filter_missing,
    load_url_snapshot,
    save_url_snapshot,
    split_new_vs_outstanding,
)


@dataclass(frozen=True)
class Item:
    url: str


def test_filter_missing_excludes_known_urls():
    result = filter_missing([Item("https://x/a"), Item("https://x/b")], {"https://x/a"})
    assert [i.url for i in result] == ["https://x/b"]


def test_filter_missing_ignores_trailing_slash_differences():
    result = filter_missing([Item("https://x/a/")], {"https://x/a"})
    assert result == []


def test_split_new_vs_outstanding_new_not_in_previous_snapshot():
    new, outstanding = split_new_vs_outstanding([Item("https://x/a")], set())
    assert [i.url for i in new] == ["https://x/a"]
    assert outstanding == []


def test_split_new_vs_outstanding_in_previous_snapshot_is_outstanding():
    new, outstanding = split_new_vs_outstanding([Item("https://x/a")], {"https://x/a"})
    assert new == []
    assert [i.url for i in outstanding] == ["https://x/a"]


def test_save_and_load_url_snapshot_round_trip(tmp_path):
    path = tmp_path / "snapshot.json"
    save_url_snapshot({"https://x/b", "https://x/a"}, path)

    assert load_url_snapshot(path) == {"https://x/a", "https://x/b"}


def test_load_url_snapshot_returns_empty_set_when_missing(tmp_path):
    assert load_url_snapshot(tmp_path / "does-not-exist.json") == set()
