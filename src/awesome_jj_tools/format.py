"""Normalize generated markdown by piping it through `rumdl fmt`.

Rather than each renderer hand-crafting exact blank-line counts (a real
whitespace-control fight, especially in the Jinja template), let the
renderers be a little sloppy about spacing and let `rumdl` — already a
project dependency, already enforced on the committed README.md via
hk.pkl's `rumdl`/`rumdl_format` steps — normalize it as the final pass. This
means the renderer output and the linter's opinion of "correctly formatted"
can never drift apart.
"""

from __future__ import annotations

import subprocess


def format_markdown(content: str, filename: str = "README.md") -> str:
    result = subprocess.run(
        ["rumdl", "fmt", "--stdin", "--silent", "--stdin-filename", filename],
        input=content,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout
