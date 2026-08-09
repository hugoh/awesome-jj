"""Render a browsable index.html from data/entries.yaml, for GitHub Pages.

Same data model as generate.py's README.md renderer (sections.build_context),
different template (templates/index.html.j2) and no rumdl pass — that's a
markdown-specific formatter, HTML doesn't need it. Search is added at deploy
time by running Pagefind over the built site/ directory (see
.github/workflows/pages.yml) — this module only renders the page itself.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from awesome_jj_tools.entries import DEFAULT_ENTRIES_PATH, load_entries
from awesome_jj_tools.last_updated import DEFAULT_LAST_UPDATED_PATH, load_snapshot
from awesome_jj_tools.sections import build_context
from awesome_jj_tools.templating import env

SITE_DIR = DEFAULT_ENTRIES_PATH.parents[1] / "site"
INDEX_PATH = SITE_DIR / "index.html"


def render(data: dict[str, Any], updated_at: str) -> str:
    context = build_context(data) | {"updated_at": updated_at}
    template = env.get_template("index.html.j2")
    return template.render(**context)


def generate(
    entries_path: Path = DEFAULT_ENTRIES_PATH,
    index_path: Path = INDEX_PATH,
    last_updated_path: Path = DEFAULT_LAST_UPDATED_PATH,
) -> str:
    """Reads whatever date `generate.py`'s README pass already recorded — the
    site build never mints its own date, it's a pure read of committed state.
    """
    data = load_entries(entries_path)
    snapshot = load_snapshot(last_updated_path)
    updated_at = snapshot.date if snapshot else ""
    content = render(data, updated_at)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(content, encoding="utf-8")
    return content
