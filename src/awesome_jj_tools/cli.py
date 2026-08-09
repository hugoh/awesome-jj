"""Entry points: `awesome-jj generate|check|generate-site|discover|releases|stars`."""

from __future__ import annotations

import argparse
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

        print(run())
        return 0

    if args.command == "releases":
        from awesome_jj_tools.releases import run

        print(run())
        return 0

    if args.command == "stars":
        from awesome_jj_tools.stars import run

        print(run())
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
