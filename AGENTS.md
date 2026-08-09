# AGENTS.md

Instructions for coding agents maintaining this list. Read [CONTRIBUTING.md](CONTRIBUTING.md)
and [SOURCES.md](SOURCES.md) first — this file assumes both.

## `README.md` is generated — never hand-edit it

Entries live in [`data/entries.yaml`](data/entries.yaml). `README.md` is
rendered from it by `mise run generate`. Any change to the list —
whether you're adding a candidate from a discovery report or fixing a typo —
goes into `entries.yaml`, followed by regenerating. `hk`'s `readme_drift`
check (`mise run check-readme`) fails the build if the two ever diverge —
and only fails it: CI never regenerates or auto-commits `README.md` itself,
so the next step is always a local `mise run generate` + push, not waiting
on the pipeline to fix it.

## Discovery is automated — read the report, don't re-run the sweep by hand

`.github/workflows/discovery.yml` runs every two weeks (and on-demand via
`workflow_dispatch`), driven by `src/awesome_jj_tools/discover.py`,
`releases.py`, and `stars.py`. It opens or updates a single issue labeled
`discovery-report` with four sections:

1. **New candidates** — repos from GitHub/GitLab/Codeberg topic sweeps and
   crates.io's `jj-lib` reverse-dependencies that aren't in `entries.yaml`
   yet, and weren't in the previous run's sweep either. Grouped by source.
2. **Still outstanding** — candidates that showed up as "new" in some earlier
   run and *still* aren't in `entries.yaml`. This list only shrinks when a
   candidate is actually added (or genuinely drops out of the sweep, e.g.
   archived) — a candidate mentioned once and never triaged keeps
   reappearing here indefinitely, it never silently disappears.
3. **Possibly stale, consider removing** — existing entries whose GitHub repo
   is archived or hasn't been pushed to in 12+ months. This is separate from
   the dead-link check `lychee` already runs in CI — a repo can 404 (caught
   by `lychee`) or just go quiet while still resolving (caught here).
4. **New releases** / **Star movers** — informational, not
   inclusion/exclusion signals on their own.

When asked to update this list, or asked proactively to check it:

1. **Read the open `discovery-report` issue first** rather than re-running
   `gh search` by hand — that's what the workflow is for. If it's stale or
   you need a fresh read, trigger it: `gh workflow run discovery.yml`.
2. **Triage every candidate in both "New" and "Still outstanding"** against
   `CONTRIBUTING.md`'s bar (jj-specific, maintained, substantive — not a
   dotfiles repo or a vague WIP). Add ones that clear it to
   `data/entries.yaml`. Don't feel pressure to resolve "Still outstanding"
   in one pass — anything left untriaged simply reappears next run
   (`data/candidates-snapshot.json` is a last-run snapshot, not a permanent
   suppress list), so nothing gets lost by deferring a judgment call.
3. **Triage each staleness flag.** A rename just needs the URL updated in
   `entries.yaml`; a genuine abandonment means removing the entry. Don't
   remove solely because the workflow flagged it — skim the repo first (a
   stable, feature-complete tool can legitimately go quiet).
4. **Regenerate and record.** Run `mise run generate`, then append a
   dated note to `SOURCES.md` under "Re-sweeps" (create the section if this is
   the first one) — what you added, removed, and why. Append, don't overwrite
   `SOURCES.md`'s existing history.
5. **Verify before pushing.** Run `hk check --all` (covers `awesome-lint`,
   `lychee`, `readme_drift`, `ruff`/`ty`/`pytest` for the tooling itself, and
   the rest of the lint suite in `hk.pkl`). Don't `--fix` your way past a real
   failure without reading what it's flagging — `awesome-lint` in particular
   is strict about structural conventions, and a mechanical fix can silently
   mangle an entry.

## If the automation itself needs a fix

`src/awesome_jj_tools/` has a `pytest` suite (`tests/`) with every HTTP call
mocked — no network needed to run it. If `discover`/`releases`/`stars` are
misbehaving (wrong dedup, false staleness flags, a source that changed its
API), fix the logic there and add a test that would have caught it, the same
TDD expectation as any other code change in this repo.

## What NOT to do

- Don't invent a repo, URL, or star count you haven't actually looked up —
  every fact in this list should trace back to a real `gh api`/`gh search`
  call, a discovery report, or a page you fetched, the same way `SOURCES.md`
  was built. Filling in plausible-looking placeholders here is worse than
  leaving a gap.
- Don't add entries for projects that only tangentially mention jj (e.g. a
  general multi-VCS tool where jj support is one line in a changelog) unless
  jj support is a first-class, documented feature.
- Don't restructure sections or rewrite prose for style reasons alone —
  that's scope creep for a maintenance pass. Open that as its own PR.
- Don't hand-edit `README.md`. If you catch yourself doing it, you're editing
  the wrong file — go to `data/entries.yaml`.

## No established standard exists for this

There isn't a widely-adopted "LLM instructions for maintaining an
awesome-list" convention (nothing analogous to `llms.txt` for docs sites), and
no generic tool automates the discovery step either — the closest thing,
[trackawesomelist.com](https://www.trackawesomelist.com/), only tracks
changes *after* a maintainer commits them, it doesn't find candidates. This
file and the `discovery.yml` workflow are this repo's own answer to that gap
— extend them as patterns emerge, rather than assuming a canonical version
exists elsewhere to defer to.
