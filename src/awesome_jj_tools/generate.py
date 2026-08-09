"""Render README.md deterministically from data/entries.yaml, using a Jinja2 template.

Header/footer/section-intro prose lives in templates/readme.md.j2 itself,
not passed in from Python — the template owns all of its own text, not just
the entries.

The template uses `%`-prefixed line statements instead of `{% %}` blocks —
Jinja's block-tag whitespace control (trim_blocks/lstrip_blocks) was built
for HTML, where stray whitespace mostly doesn't matter, and fighting it for
line-oriented markdown output was real friction. Line statements sidestep
that entirely: a `%`-prefixed line is consumed whole, no trailing-newline
accounting needed. `#` was the more obvious prefix choice but collides with
markdown's own heading syntax, which this template outputs literally.

Final output is piped through `rumdl fmt` (format.py) rather than the
renderer hand-crafting exact blank-line counts — see format.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from awesome_jj_tools.entries import DEFAULT_ENTRIES_PATH, load_entries
from awesome_jj_tools.format import format_markdown
from awesome_jj_tools.sections import build_context

README_PATH = DEFAULT_ENTRIES_PATH.parents[1] / "README.md"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    line_statement_prefix="%",
    undefined=StrictUndefined,
    keep_trailing_newline=True,
)


def render(data: dict[str, Any]) -> str:
    context = build_context(data)
    template = _env.get_template("readme.md.j2")
    content = template.render(sections=context["sections"])
    return format_markdown(content)


def generate(entries_path: Path = DEFAULT_ENTRIES_PATH, readme_path: Path = README_PATH) -> str:
    data = load_entries(entries_path)
    content = render(data)
    readme_path.write_text(content, encoding="utf-8")
    return content


def check(entries_path: Path = DEFAULT_ENTRIES_PATH, readme_path: Path = README_PATH) -> bool:
    """Return True if README.md matches what would be generated from entries_path."""
    data = load_entries(entries_path)
    expected = render(data)
    actual = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    return expected == actual
