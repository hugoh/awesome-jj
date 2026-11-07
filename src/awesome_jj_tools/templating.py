"""The Jinja2 environment shared by every template (readme.md.j2, index.html.j2).

Centralized so both renderers stay in sync on the whitespace/undefined
behavior — see generate.py's module docstring for why `%` line statements
instead of `{% %}` blocks.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markdown_it import MarkdownIt
from markupsafe import Markup

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

# Raw HTML in a description is escaped, not passed through: descriptions are
# data, not markup. Links, `code` and emphasis render normally.
_md = MarkdownIt("commonmark", {"html": False})


def md_inline(text: str | None) -> str | None:
    """Render an entry description's inline Markdown as HTML (no wrapping `<p>`).

    Descriptions in entries.yaml are written in Markdown (they're reused
    verbatim in README.md.j2), but index.html.j2 needs actual HTML.
    """
    if not text:
        return text
    return Markup(_md.renderInline(text))


env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    line_statement_prefix="%",
    undefined=StrictUndefined,
    keep_trailing_newline=True,
)
env.filters["md_inline"] = md_inline
