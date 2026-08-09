"""The Jinja2 environment shared by every template (readme.md.j2, index.html.j2).

Centralized so both renderers stay in sync on the whitespace/undefined
behavior — see generate.py's module docstring for why `%` line statements
instead of `{% %}` blocks.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    line_statement_prefix="%",
    undefined=StrictUndefined,
    keep_trailing_newline=True,
)
