# Sources

This repo was seeded on 2026-08-09 by merging prior "awesome jj" lists and
sweeping GitHub for active Jujutsu-related projects that neither list had
picked up. Recorded here so future maintainers know what went into the first
version and can judge what's worth re-sweeping for.

## Lists merged

- [chawyehsu/awesome-jj](https://github.com/chawyehsu/awesome-jj) — used as
  the base structure (categories, `awesome.re` badge, dated articles). At
  merge time: 8 stars, last commit 2026-07-10, 2 open issues.
- [Necior/awesome-jj](https://github.com/Necior/awesome-jj) — folded in the
  handful of entries not already covered by chawyehsu's list (the
  [jj-workshop](https://github.com/jkoppel/jj-workshop) tutorial, the
  [list of popular Jujutsu aliases](https://www.lysator.liu.se/~axl/jj-aliases/)).
  At merge time: 151 stars, last commit 2026-02-08 (~6 months stale).

## Lists considered and excluded

- [KANE-99/awesome-jj](https://github.com/KANE-99/awesome-jj) — despite the
  name, this is a personal jj workflow guide/script repo, not a curated
  awesome-list. Not a merge candidate.
- `jianzi123/awesomeJJ`, `gwongibeom/awesome-jjambbong` — unrelated to
  Jujutsu VCS (name collision only).

## Active-project sweep

Searched GitHub's `jujutsu` topic sorted by most-recently-pushed (2026-08-09)
to find projects missing from both source lists. Most of what surfaced was
already covered by chawyehsu's list; the genuinely new, substantive additions
folded into `README.md` were:

`jjq`, `jjx`, `jujutsu.nvim`, `jjwsm.nvim`, `juju` (Helix), `zsh-jj`, `jip`,
`jx`, `jj-navi`, `jif`, `blazingjj`, `jutsu`, `jujutsu-gi`, `jj-commit`,
`sesh`, `weiff`, `renri`, `vcs-toolkit-rs`, `garami`, and the maintainer's own
[`hrd`](https://github.com/hugoh/hrd) and
[`jj-trim`](https://github.com/hugoh/jj-trim).

Repos surfaced by the sweep but deliberately left out as too early-stage,
vague, or not actually jj-specific (dotfiles repos, single-purpose forks,
unrelated tools that merely mention jj in passing): `treq-dev/treq`,
`netresearch/jujutsu-workflow-skill`, `swissgrammie/jjhouse`,
`Divyxnk44x/jjtask`, `sjawhar/knives`, `MachineWisdomAI/fava-trails`, and
assorted personal dotfiles repos. Revisit these if they mature.

## Re-sweeping (automated as of 2026-08-09)

The jj ecosystem moves fast — the sweep above found ~50 pushes to jj-tagged
repos in the preceding two weeks alone. The one-time manual sweep this file
documents has been superseded by an automated one: `.github/workflows/discovery.yml`
runs `src/awesome_jj_tools/discover.py` (GitHub + GitLab + Codeberg topic
search, crates.io's `jj-lib` reverse-dependencies, plus a staleness check on
existing entries) every two weeks and files a `discovery-report` issue. See
[AGENTS.md](AGENTS.md) for how that report gets triaged into `data/entries.yaml`.

This section stays as historical record of what shipped in the first version;
new discoveries are logged below under "Re-sweeps" as they're triaged, not
folded back into the "Active-project sweep" section above.

### Re-sweeps
