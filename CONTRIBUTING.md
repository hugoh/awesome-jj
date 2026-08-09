# Contributing

Contributions are welcome, whether it's fixing a typo, re-categorizing an
entry, or adding a new one.

**`README.md` is generated — don't edit it directly.** It's rendered from
[`data/entries.yaml`](data/entries.yaml), the source of record. Edits to
`README.md` itself will be overwritten and won't pass CI (see Checks below).

## Adding an entry

- Make sure the resource is about [Jujutsu](https://www.jj-vcs.dev) (jj)
  specifically, not Git in general.
- Add it to the most specific relevant list in `data/entries.yaml`, matching
  the fields already used by its neighbors (`name`, `url`, and usually
  `description`; `date`/`author` for Articles/Videos/Books). You don't need
  to worry about ordering — the generator sorts each section deterministically
  (alphabetically for tools/forges/miscellaneous/community, chronologically
  for articles/videos, alphabetically for books).
- Descriptions should be one factual sentence ending in a period, matching
  `awesome-lint`'s formatting rules — see existing entries for the exact
  style.
- Prefer a project that is maintained: has commits or releases within the
  last ~12 months, or is stable and complete enough not to need them. Dead
  links or archived/abandoned projects will be removed.
- Run `uv run awesome-jj generate` (or `mise run test` / `hk fix`, which do
  this for you) to render `README.md` from your `entries.yaml` change before
  committing both files together.
- One entry per pull request makes review easier, but batching a few related
  additions is fine.

## Removing an entry

If you notice a dead link, an archived repo, or a project that's been
abandoned, remove its entry from `data/entries.yaml`, regenerate, and open a
PR (or an issue flagging it). The automated discovery workflow
(`.github/workflows/discovery.yml`) also surfaces stale-looking entries on its
own schedule — see [AGENTS.md](AGENTS.md) for how that report gets triaged.

## Checks

This repo runs [`awesome-lint`](https://github.com/sindresorhus/awesome-lint),
a link checker, and a Python test suite in CI. Run `hk check --all` locally
before opening a PR — see the repo's `mise.toml`/`hk.pkl` for the tool
versions used. In particular, `hk` runs a `readme_drift` check that fails if
`README.md` doesn't match what `data/entries.yaml` would generate — running
`hk fix` (or `uv run awesome-jj generate`) resolves it.

## Code of Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).
