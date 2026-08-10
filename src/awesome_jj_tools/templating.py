"""The Jinja2 environment shared by every template (readme.md.j2, index.html.j2).

Centralized so both renderers stay in sync on the whitespace/undefined
behavior — see generate.py's module docstring for why `%` line statements
instead of `{% %}` blocks.
"""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup, escape

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def md_links(text: str | None) -> str | None:
    """Render `[text](url)` Markdown links in `text` as HTML `<a>` tags.

    Entry descriptions in entries.yaml are written in Markdown (they're reused
    verbatim in README.md.j2), but index.html.j2 needs actual HTML links.
    """
    if not text:
        return text
    escaped = str(escape(text))
    return Markup(_MD_LINK_RE.sub(r'<a href="\2">\1</a>', escaped))


env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    line_statement_prefix="%",
    undefined=StrictUndefined,
    keep_trailing_newline=True,
)
env.filters["md_links"] = md_links
