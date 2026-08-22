"""Entry points: generate, check, generate-site, discover, releases, stars, redirects,
discovery-report."""

from __future__ import annotations

import argparse
import asyncio
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="awesome-jj")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("generate", help="Render README.md from data/entries.yaml")
    subparsers.add_parser(
        "check", help="Exit non-zero if README.md is out of sync with entries.yaml"
    )
    subparsers.add_parser("generate-site", help="Render site/index.html from data/entries.yaml")
    subparsers.add_parser("discover", help="Sweep for new candidates and stale existing entries")
    subparsers.add_parser("releases", help="Check for new releases among listed repos")
    subparsers.add_parser("stars", help="Refresh star snapshot and report notable movers")
    subparsers.add_parser(
        "media", help="Sweep HN/Lobsters/Reddit/YouTube for popular new jj articles and videos"
    )
    redirects_parser = subparsers.add_parser(
        "redirects", help="Diff lychee's redirects against known/accepted ones"
    )
    redirects_parser.add_argument(
        "inputs", nargs="*", help="Files to check (default: the standard doc set)"
    )
    subparsers.add_parser(
        "discovery-report",
        help=(
            "Run discover+releases+stars+redirects, print the combined report. "
            "Exits 1 (like grep) if nothing was found, for CI to skip filing an issue."
        ),
    )

    args = parser.parse_args(argv)

    if args.command == "generate":
        from awesome_jj_tools.generate import generate

        generate()
        return 0

    if args.command == "check":
        from awesome_jj_tools.generate import check

        if check():
            return 0
        print(
            "README.md is out of sync with data/entries.yaml — run `awesome-jj generate`.",
            file=sys.stderr,
        )
        return 1

    if args.command == "generate-site":
        from awesome_jj_tools.site import generate as generate_site

        generate_site()
        return 0

    if args.command == "discover":
        from awesome_jj_tools.discover import run

        report, _has_findings = asyncio.run(run())
        print(report)
        return 0

    if args.command == "releases":
        from awesome_jj_tools.releases import run

        report, _has_findings = asyncio.run(run())
        print(report)
        return 0

    if args.command == "stars":
        from awesome_jj_tools.stars import run

        report, _has_findings = asyncio.run(run())
        print(report)
        return 0

    if args.command == "media":
        from awesome_jj_tools.media import run

        report, _has_findings = asyncio.run(run())
        print(report)
        return 0

    if args.command == "redirects":
        from awesome_jj_tools.redirects import run

        report, _has_findings = run(args.inputs or None)
        print(report)
        return 0

    if args.command == "discovery-report":
        return asyncio.run(_discovery_report())

    return 1


async def _discovery_report() -> int:
    from awesome_jj_tools.discover import run as discover_run
    from awesome_jj_tools.media import run as media_run
    from awesome_jj_tools.redirects import run as redirects_run
    from awesome_jj_tools.releases import run as releases_run
    from awesome_jj_tools.stars import run as stars_run

    discover_text, discover_found = await discover_run()
    media_text, media_found = await media_run()
    releases_text, releases_found = await releases_run()
    stars_text, stars_found = await stars_run()
    redirects_text, redirects_found = redirects_run()

    print("\n\n".join([discover_text, media_text, releases_text, stars_text, redirects_text]))
    return (
        0
        if (discover_found or media_found or releases_found or stars_found or redirects_found)
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
