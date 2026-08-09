"""Render README.md deterministically from data/entries.yaml."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from awesome_jj_tools.entries import DEFAULT_ENTRIES_PATH, load_entries

README_PATH = DEFAULT_ENTRIES_PATH.parents[1] / "README.md"

HEADER = """# Awesome JJ [![Awesome](https://awesome.re/badge-flat.svg)](https://awesome.re)

> A curated, actively-maintained list of awesome Jujutsu (jj) VCS resources.

Jujutsu (also known as jj) is a Git-compatible version control system.

This list merges and supersedes the previously separate [Necior/awesome-jj](https://github.com/Necior/awesome-jj) and [chawyehsu/awesome-jj](https://github.com/chawyehsu/awesome-jj) lists — see [SOURCES.md](SOURCES.md) for provenance and what was merged.
"""

FOOTER = """## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Please read the [Code of Conduct](CODE_OF_CONDUCT.md) first.

[![CC0](https://i.creativecommons.org/p/zero/1.0/88x31.png)](https://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, the authors have waived all copyright and related or neighboring rights to this work under the license in [LICENSE](LICENSE).
"""

TOOLS_SUBSECTIONS = [
    ("gui", "GUI"),
    ("tui", "TUI"),
    ("editor_integration", "Editor Integration"),
    ("diff_merge_drivers", "Diff and Merge Drivers"),
    ("workflows", "Workflows"),
    ("shell_integration", "Shell Integration"),
    ("misc_tools", "Misc Tools"),
]

TOP_SECTIONS = [
    ("official_resources", "Official Resources", "list"),
    ("articles", "Articles", "dated"),
    ("books", "Books", "book"),
    ("videos", "Videos", "dated_video"),
    ("tools", "Tools", "tools"),
    ("forges", "Forges", "list_sorted"),
    ("miscellaneous", "Miscellaneous", "list"),
    ("community", "Community", "list_sorted"),
]


def _slug(title: str) -> str:
    return re.sub(r"[^a-z0-9- ]", "", title.lower()).replace(" ", "-")


def _sort_key(name: str) -> str:
    return re.sub(r'^["\'()]+', "", name).lower()


def _render_list_item(entry: dict[str, Any]) -> str:
    description = entry.get("description")
    if description:
        return f"- [{entry['name']}]({entry['url']}) - {description}"
    return f"- [{entry['name']}]({entry['url']})"


def _render_book(entry: dict[str, Any]) -> str:
    return f"- [{entry['name']}]({entry['url']}) - By {entry['author']}."


def _render_dated(entry: dict[str, Any]) -> str:
    year, month = entry["date"].split("-")
    return f"- {month}/{year} [{entry['name']}]({entry['url']}) by {entry['author']}"


def _render_dated_video(entry: dict[str, Any]) -> str:
    year, month = entry["date"].split("-")
    line = f"- {month}/{year} [{entry['name']}]({entry['url']})"
    suffix = entry.get("suffix")
    if suffix:
        line += f" {suffix}"
    return line


def _render_section_body(kind: str, items: list[dict[str, Any]]) -> list[str]:
    if kind == "list":
        entries = items
    elif kind == "list_sorted" or kind == "book":
        entries = sorted(items, key=lambda e: _sort_key(e["name"]))
    elif kind in ("dated", "dated_video"):
        entries = sorted(items, key=lambda e: e["date"])
    else:
        raise ValueError(f"unknown section kind: {kind}")

    renderer = {
        "list": _render_list_item,
        "list_sorted": _render_list_item,
        "book": _render_book,
        "dated": _render_dated,
        "dated_video": _render_dated_video,
    }[kind]
    return [renderer(e) for e in entries]


def _render_toc() -> list[str]:
    lines = ["## Contents", ""]
    for _key, title, kind in TOP_SECTIONS:
        lines.append(f"- [{title}](#{_slug(title)})")
        if kind == "tools":
            for _, sub_title in TOOLS_SUBSECTIONS:
                lines.append(f"  - [{sub_title}](#{_slug(sub_title)})")
    lines.append("")
    return lines


def render(data: dict[str, Any]) -> str:
    lines = [HEADER.rstrip("\n"), ""]
    lines.extend(_render_toc())

    for key, title, kind in TOP_SECTIONS:
        lines.append(f"## {title}")
        lines.append("")
        if kind == "tools":
            tools_data = data.get("tools", {})
            for sub_key, sub_title in TOOLS_SUBSECTIONS:
                lines.append(f"### {sub_title}")
                lines.append("")
                lines.extend(_render_section_body("list_sorted", tools_data.get(sub_key, [])))
                lines.append("")
        else:
            if key == "forges":
                lines.append(
                    "While Jujutsu works with Git compatible forges like GitHub, there are also "
                    "some new forges/platforms worth mentioning, and some of them are "
                    "exploring/offering a better integration and support for Jujutsu."
                )
                lines.append("")
            lines.extend(_render_section_body(kind, data.get(key, [])))
            lines.append("")

    lines.append(FOOTER.rstrip("\n"))
    lines.append("")

    return "\n".join(lines)


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
