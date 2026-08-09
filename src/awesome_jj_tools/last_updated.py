"""Tracks when data/entries.yaml's *content* last actually changed.

README.md/index.html show this as "last updated" — it must only advance when
there's something to show for it, not on every regeneration (a no-op
`generate` run shouldn't bump the date). Compares a hash of entries.yaml's
current bytes against the last-recorded hash in last-updated.json; only
writes a new date when they differ.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from awesome_jj_tools.entries import DEFAULT_ENTRIES_PATH

DEFAULT_LAST_UPDATED_PATH = DEFAULT_ENTRIES_PATH.parent / "last-updated.json"


@dataclass(frozen=True)
class LastUpdatedSnapshot:
    hash: str
    date: str


def _hash_entries(entries_path: Path) -> str:
    return hashlib.sha256(entries_path.read_bytes()).hexdigest()


def load_snapshot(path: Path = DEFAULT_LAST_UPDATED_PATH) -> LastUpdatedSnapshot | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return LastUpdatedSnapshot(hash=data["hash"], date=data["date"])


def save_snapshot(snapshot: LastUpdatedSnapshot, path: Path = DEFAULT_LAST_UPDATED_PATH) -> None:
    path.write_text(
        json.dumps({"hash": snapshot.hash, "date": snapshot.date}, indent=2) + "\n",
        encoding="utf-8",
    )


def sync(
    entries_path: Path = DEFAULT_ENTRIES_PATH,
    snapshot_path: Path = DEFAULT_LAST_UPDATED_PATH,
    today: str = "",
) -> str:
    """Return the "last updated" date, advancing it to `today` only if
    entries.yaml's content changed since the last recorded snapshot.
    """
    current_hash = _hash_entries(entries_path)
    previous = load_snapshot(snapshot_path)
    if previous is not None and previous.hash == current_hash:
        return previous.date
    save_snapshot(LastUpdatedSnapshot(hash=current_hash, date=today), snapshot_path)
    return today
