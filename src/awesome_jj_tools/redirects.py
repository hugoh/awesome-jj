"""Diff lychee's redirects against known/accepted ones, flagging new ones for triage.

Known redirects come from two places:
- `entries.yaml`'s `accepted_redirect` field, colocated with the entry's own
  `url:` — covers the common case where the redirecting URL *is* an entry's
  url, so editing/removing the entry naturally keeps the exception in sync.
- `data/redirect-exceptions.yaml`, for redirects that don't live on any
  entry's `url:` field (template-hardcoded badges, or a link embedded in an
  entry's `description:` rather than its own `url:`).
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import yaml

from awesome_jj_tools.entries import DEFAULT_ENTRIES_PATH, all_entries, load_entries

DEFAULT_REDIRECT_EXCEPTIONS_PATH = DEFAULT_ENTRIES_PATH.parent / "redirect-exceptions.yaml"

LYCHEE_INPUTS = [
    "README.md",
    "SOURCES.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "AGENTS.md",
]


@dataclass(frozen=True)
class Redirect:
    source_file: str
    url: str
    target: str
    code: int


def load_accepted_redirects(entries_data: dict) -> set[tuple[str, str]]:
    """(url, target) pairs from entries.yaml items' `accepted_redirect` field."""
    return {
        (entry["url"], entry["accepted_redirect"])
        for _, entry in all_entries(entries_data)
        if "accepted_redirect" in entry
    }


def load_exceptions(path: Path = DEFAULT_REDIRECT_EXCEPTIONS_PATH) -> set[tuple[str, str]]:
    """(url, target) pairs recorded in redirect-exceptions.yaml — see its header comment."""
    if not path.exists():
        return set()
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {(item["url"], item["target"]) for item in data.get("redirects", [])}


def run_lychee_json(inputs: list[str]) -> dict:
    result = subprocess.run(
        [
            "lychee",
            "--no-progress",
            "-vv",
            "--format",
            "json",
            "--max-retries",
            "3",
            "--retry-wait-time",
            "5",
            "--accept",
            "100..=103,200..=299,403,429",
            *inputs,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return json.loads(result.stdout)


def extract_redirects(report: dict) -> list[Redirect]:
    redirects = []
    for source_file, entries in report.get("redirect_map", {}).items():
        for entry in entries:
            for redirect in entry["redirects"]:
                redirects.append(
                    Redirect(
                        source_file=source_file,
                        url=entry["origin"],
                        target=redirect["url"],
                        code=redirect["code"],
                    )
                )
    return redirects


def diff_redirects(
    current: list[Redirect], known: set[tuple[str, str]]
) -> tuple[list[Redirect], list[tuple[str, str]]]:
    """Returns (new, stale): new = current redirects not yet recorded; stale = recorded
    exceptions that no longer show up as a redirect (fixed upstream, or now failing outright)."""
    current_pairs = {(r.url, r.target) for r in current}
    new = [r for r in current if (r.url, r.target) not in known]
    stale = sorted(known - current_pairs)
    return new, stale


def render_report(new: list[Redirect], stale: list[tuple[str, str]]) -> str:
    lines = ["### Redirect exceptions", ""]
    if not new and not stale:
        lines.append("No new or stale redirects — all accounted for.")
        return "\n".join(lines)

    if new:
        lines.append("**New redirects, not yet recorded:**")
        for r in new:
            lines.append(f"- `{r.url}` --[{r.code}]--> `{r.target}` (in {r.source_file})")
        lines.append("")

    if stale:
        lines.append("**Recorded exceptions no longer occurring (safe to remove):**")
        for url, target in stale:
            lines.append(f"- `{url}` --> `{target}`")

    return "\n".join(lines)


def run(
    inputs: list[str] | None = None,
    entries_path: Path = DEFAULT_ENTRIES_PATH,
    exceptions_path: Path = DEFAULT_REDIRECT_EXCEPTIONS_PATH,
    lychee_runner: Callable[[list[str]], dict] = run_lychee_json,
) -> tuple[str, bool]:
    """Returns (report_text, has_findings)."""
    report = lychee_runner(inputs if inputs is not None else LYCHEE_INPUTS)
    current = extract_redirects(report)
    known = load_accepted_redirects(load_entries(entries_path)) | load_exceptions(exceptions_path)
    new, stale = diff_redirects(current, known)
    return render_report(new, stale), bool(new)
