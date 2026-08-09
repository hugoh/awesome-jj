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
from awesome_jj_tools.sections import build_context
from awesome_jj_tools.templating import env

SITE_DIR = DEFAULT_ENTRIES_PATH.parents[1] / "site"
INDEX_PATH = SITE_DIR / "index.html"


def render(data: dict[str, Any]) -> str:
    context = build_context(data)
    template = env.get_template("index.html.j2")
    return template.render(**context)


def generate(entries_path: Path = DEFAULT_ENTRIES_PATH, index_path: Path = INDEX_PATH) -> str:
    data = load_entries(entries_path)
    content = render(data)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(content, encoding="utf-8")
    return content
