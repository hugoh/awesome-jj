from awesome_jj_tools.last_updated import (
    LastUpdatedSnapshot,
    load_snapshot,
    save_snapshot,
    sync,
)


def test_sync_seeds_today_when_no_snapshot_exists(tmp_path):
    entries_path = tmp_path / "entries.yaml"
    entries_path.write_text("official_resources: []\n", encoding="utf-8")
    snapshot_path = tmp_path / "last-updated.json"

    result = sync(entries_path, snapshot_path, today="2026-08-09")

    assert result == "2026-08-09"
    snapshot = load_snapshot(snapshot_path)
    assert snapshot is not None
    assert snapshot.date == "2026-08-09"


def test_sync_keeps_old_date_when_entries_content_unchanged(tmp_path):
    entries_path = tmp_path / "entries.yaml"
    entries_path.write_text("official_resources: []\n", encoding="utf-8")
    snapshot_path = tmp_path / "last-updated.json"
    sync(entries_path, snapshot_path, today="2026-08-01")

    result = sync(entries_path, snapshot_path, today="2026-08-09")

    assert result == "2026-08-01"


def test_sync_advances_date_when_entries_content_changes(tmp_path):
    entries_path = tmp_path / "entries.yaml"
    entries_path.write_text("official_resources: []\n", encoding="utf-8")
    snapshot_path = tmp_path / "last-updated.json"
    sync(entries_path, snapshot_path, today="2026-08-01")

    entries_path.write_text("official_resources: [{name: x, url: y}]\n", encoding="utf-8")
    result = sync(entries_path, snapshot_path, today="2026-08-09")

    assert result == "2026-08-09"
    snapshot = load_snapshot(snapshot_path)
    assert snapshot is not None
    assert snapshot.date == "2026-08-09"


def test_load_snapshot_returns_none_when_missing(tmp_path):
    assert load_snapshot(tmp_path / "does-not-exist.json") is None


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "last-updated.json"
    save_snapshot(LastUpdatedSnapshot(hash="abc", date="2026-08-09"), path)

    loaded = load_snapshot(path)

    assert loaded == LastUpdatedSnapshot(hash="abc", date="2026-08-09")
