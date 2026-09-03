# Awesome JJ [![Awesome](https://awesome.re/badge-flat.svg)](https://awesome.re)

> A curated, actively-maintained list of awesome Jujutsu (jj) VCS resources.

Jujutsu (also known as jj) is a Git-compatible version control system.

Last updated: 2026-09-03

This list merges the various out-of-date awesome-jj lists — see [SOURCES.md](SOURCES.md) for provenance and what was merged.

## Contents

- [Official Resources](#official-resources)
- [Tools](#tools)
  - [GUI](#gui)
  - [TUI](#tui)
  - [Editor Integration](#editor-integration)
  - [Diff and Merge Drivers](#diff-and-merge-drivers)
  - [Workflows](#workflows)
  - [Multi-repo & Workspace Management](#multi-repo--workspace-management)
  - [Shell Integration](#shell-integration)
  - [AI & Agent Tooling](#ai--agent-tooling)
  - [Misc Tools](#misc-tools)
- [Articles](#articles)
- [Books](#books)
- [Videos](#videos)
- [Forges](#forges)
- [Miscellaneous](#miscellaneous)
- [Community](#community)

## Official Resources

- [Jujutsu homepage](https://www.jj-vcs.dev)
- [GitHub repository](https://github.com/jj-vcs/jj)
- [Official tutorial](https://docs.jj-vcs.dev/latest/tutorial)
- [Official documentation](https://docs.jj-vcs.dev/latest)
- [Frequently Asked Questions](https://docs.jj-vcs.dev/latest/FAQ/)
- ["The jj workshop: A Zero-to-Hero Speedrun"](https://github.com/jkoppel/jj-workshop) - A hands-on workshop repo.

## Tools

### GUI

- [gg](https://github.com/gulbanana/gg) - GUI for jj.
- [jayjay](https://github.com/hewigovens/jayjay) - A native macOS GUI for Jujutsu (jj).
- [jjewel](https://checksimsoftware.com/jjewel) - A native Mac client for the Jujutsu version control system.
- [lightjj](https://github.com/chronologos/lightjj) - A fast, powerful, single-binary Jujutsu client.
- [weiff](https://github.com/isgj/weiff) - A local web interface for exploring and managing Jujutsu repositories: revision graphs, diffs, files, bookmarks, workspaces, and operation history.

### TUI

- [blazingjj](https://github.com/blazingjj/blazingjj) - TUI for Jujutsu/jj.
- [gojo](https://github.com/0xhckr/gojo) - A fullscreen terminal UI for Jujutsu with commit graph, diff viewing, conflict resolution, and AI-generated commit messages.
- [jif](https://github.com/jrpat/jif) - A moldable Jujutsu TUI.
- [jj-fzf](https://github.com/tim-janik/jj-fzf) - Text UI for Jujutsu based on fzf.
- [jj-tui](https://github.com/madicen/jj-tui) - A TUI for Jujutsu that incorporates some light PR and ticket support.
- [jj_tui](https://github.com/faldor20/jj_tui) - A TUI for the Jujutsu version control system.
- [jjui](https://github.com/idursun/jjui) - TUI designed for interacting with the Jujutsu version control system.
- [jk](https://github.com/joshka/jk) - A jj-native terminal UI for Jujutsu.
- [jujutsu-gi](https://github.com/daeh/jujutsu-gi) - TUI and CLI for creating, managing, and merging Jujutsu workspaces.
- [jutsu](https://github.com/AliQ80/jutsu) - A TUI command composer for Jujutsu that teaches you the CLI instead of hiding it.
- [lazyjj](https://github.com/Cretezy/lazyjj) - TUI for Jujutsu/jj, built in Rust with Ratatui.
- [majjit](https://github.com/anthrofract/majjit) - A TUI to manipulate the Jujutsu DAG.

### Editor Integration

- [doprz/jujutsu.nvim](https://github.com/doprz/jujutsu.nvim) - A Neovim plugin for jujutsu integration, inspired by lazygit.nvim.
- [jiejie.nvim](https://github.com/jceb/jiejie.nvim) - Neovim frontend for Jujutsu in the style of vim-fugitive.
- [JJ View](https://github.com/brychanrobot/jj-view) - Integrates Jujutsu (jj) version control into VS Code.
- [jj-idea](https://github.com/kkkev/jj-idea) - Jujutsu VCS Plugin for IntelliJ IDEA.
- [jj-mode.el](https://github.com/bolivier/jj-mode.el) - Jujutsu version control mode for Emacs inspired by Magit.
- [jj.hx](https://github.com/icorbrey/jj.hx) - A Steel plugin that provides Jujutsu integration for the Helix editor.
- [jj.nvim](https://github.com/NicolasGB/jj.nvim) - Drive Jujutsu (jj) VCS from Neovim.
- [jjwsm.nvim](https://github.com/vapourismo/jjwsm.nvim) - Neovim Jujutsu Workspace Manager.
- [jjx](https://github.com/Christoph-D/jjx) - Jujutsu (jj) VCS support for VS Code.
- [juju](https://github.com/waddie/juju) - A Git/jj interface for the Helix editor.
- [Jujutsu Kaizen (jjk)](https://github.com/keanemind/jjk) - Jujutsu (jj) VCS support for VS Code.
- [Majutsu](https://github.com/0WD0/majutsu) - Magit-inspired Emacs interface for the Jujutsu.
- [mistweaverco/jujutsu.nvim](https://github.com/mistweaverco/jujutsu.nvim) - A Magit-style Jujutsu interface for Neovim.
- [neojj](https://github.com/krisajenkins/neojj) - A Magit/Neogit-style plugin for the Jujutsu version control system.
- [Selvejj](https://selvejj.com/) - JetBrains IDEs plugin for integrating Jujutsu as a first-class VCS.
- [vcsigns.nvim](https://github.com/algmyr/vcsigns.nvim) - Neovim sign gutter, designed to be mostly VCS-agnostic (works with Jujutsu).
- [VisualJJ](https://www.visualjj.com/) - Visual interface for Jujutsu and Git inside VS Code.

### Diff and Merge Drivers

- [0xferrous/jj-conflict.nvim](https://github.com/0xferrous/jj-conflict.nvim) - Neovim plugin for highlighting and resolving Jujutsu (jj) file conflicts, with multi-sided conflict support.
- [diffedit3](https://github.com/ilyagr/diffedit3) - Edit diffs in a 3-pane view.
- [hunk.nvim](https://github.com/julienvincent/hunk.nvim) - A tool for splitting diffs in Neovim.
- [jj-diffconflicts](https://github.com/rafikdraoui/jj-diffconflicts) - A conflict resolution merge tool for Jujutsu VCS that runs in Neovim.
- [larpios/jj-conflict.nvim](https://github.com/larpios/jj-conflict.nvim) - Neovim plugin for resolving and visualizing Jujutsu conflicts.
- [Meld](https://meldmerge.org/) - Visual diff and merge tool.
- [Mergiraf](https://mergiraf.org/) - A syntax-aware merge driver.
- [Oyui](https://github.com/emilien-jegou/oyui) - A modern TUI merge tool and staging interface for Jujutsu and Git.
- [scm-record](https://github.com/arxanas/scm-record) - The built-in diff editor for Jujutsu.
- [Weave](https://github.com/Ataraxy-Labs/weave) - Entity-level semantic merge driver.

### Workflows

- [jip](https://github.com/omarkohl/jip) - Tool for managing pull requests with jj.
- [jj-gh](https://github.com/mrjones2014/jj-gh) - GitHub PR tools for jj, usable from your terminal.
- [jj-navi](https://github.com/eersnington/jj-navi) - Workspace navigation and management for Jujutsu.
- [jj-ryu](https://github.com/dmmulroy/jj-ryu) - Stacked PRs for Jujutsu. Push bookmark stacks to GitHub and GitLab as chained pull requests.
- [jj-spr](https://github.com/jennings/jj-spr) - Super Pull Requests (SPR) is the power tool for Jujutsu + GitHub workflows.
- [jj-stack](https://github.com/keanemind/jj-stack) - Stacked PRs on GitHub for Jujutsu.
- [jj-vine](https://codeberg.org/abrenneke/jj-vine) - A tool for submitting stacked Pull/Merge Requests from Jujutsu bookmarks.
- [jx](https://github.com/solodov/jx) - Opinionated Jujutsu companion for GitHub PR workflows, safe syncing, and layout-aware multi-repository work.
- [kata](https://github.com/martint/kata) - Code review for jj workflows: revset-defined reviews, patchset-anchored comments that survive branch movement, with web, HTTP, and MCP surfaces.
- [stakk](https://github.com/glennib/stakk) - A tool that bridges Jujutsu bookmarks to GitHub stacked pull requests.

### Multi-repo & Workspace Management

- [hrd](https://github.com/hugoh/hrd) - Multi-repo manager (TUI & CLI) for Git and jj with parallel dispatch and live status.
- [renri](https://github.com/yukimemi/renri) - Unified manager for Git worktrees and Jujutsu workspaces.
- [smth](https://github.com/amnn/smth) - A tmux-native session switcher for navigating between and opening new sessions based on Jujutsu repositories and workspaces.
- [vcs-toolkit-rs](https://github.com/ZelAnton/vcs-toolkit-rs) - A Rust toolkit for automating Git, Jujutsu, and GitHub through CLI process execution.

### Shell Integration

- [fish_jj_prompt](https://github.com/nertzy/fish_jj_prompt) - A Fish shell prompt segment for Jujutsu repositories, installable via Fisher.
- [jj-starship](https://github.com/dmmulroy/jj-starship) - Unified Starship prompt module for Git and Jujutsu.
- [starship-jj](https://gitlab.com/lanastara_foss/starship-jj) - A Starship plugin that shows bookmarks and other Jujutsu commit state in your terminal prompt.
- [tide-item-jj](https://github.com/lucasadelino/tide-item-jj) - A Tide prompt item that displays Jujutsu change ID, bookmarks, commit status, and file statistics.
- [zsh-jj](https://github.com/rkh/zsh-jj) - Jujutsu support for Z Shell.

### AI & Agent Tooling

- [claude-plugins](https://github.com/muloka/claude-plugins) - Jujutsu plugins for Claude Code covering Git enforcement, project setup, parallel workspace orchestration, commit workflows, and peer review.
- [jujutsu-workflow-skill](https://github.com/netresearch/jujutsu-workflow-skill) - An agent skill for agent-safe version control with Jujutsu, using jj for local change management and Git as the canonical remote/PR/CI interface.

### Misc Tools

- [diffsoup](https://github.com/junglerobba/diffsoup) - A Gerrit-style patchset diff viewer for pull requests, using Jujutsu.
- [hunk](https://github.com/modem-dev/hunk) - A review-first terminal diff viewer for agent-authored changesets.
- [jj-commit](https://github.com/Odonno/jj-commit) - Simplify the `jj commit` experience.
- [jj-hunk](https://github.com/laulauland/jj-hunk) - Programmatic hunk selection for Jujutsu.
- [jj-pre-push](https://github.com/acarapetis/jj-pre-push) - Run pre-commit before `jj git push`.
- [jj-run](https://github.com/neongreen/mono/tree/main/jj-run) - A tool to execute shell commands across multiple repository changes in isolated workspaces using jj.
- [jj-trim](https://github.com/hugoh/jj-trim) - Clean up merged bookmarks and abandoned anonymous commits in a jj repository.
- [jjq](https://github.com/paulsmith/jjq) - A local merge queue for jj.
- [lumen](https://github.com/jnsahaj/lumen) - A diff viewer and code review TUI and CLI to generate commit messages with AI.

## Articles

- 07/2023 [jj init](https://v5.chriskrycho.com/essays/jj-init/) by Chris Krycho
- 01/2024 [Jujutsu: a new, Git-compatible version control system](https://lwn.net/Articles/958468/) by Daroc Alden
- 04/2024 [A Better Merge Workflow with Jujutsu](https://ofcr.se/jujutsu-merge-workflow) by Benjamin Tan
- 05/2024 [Jujutsu Strategies](https://reasonablypolymorphic.com/blog/jj-strategy/) by Sandy Maguire
- 06/2024 [Basic jj workflows](https://blog.chay.dev/basic-jj-workflows/) by Chay Choong
- 08/2024 [Understanding Revsets for a Better JJ Log Output](https://willhbr.net/2024/08/18/understanding-revsets-for-a-better-jj-log-output/) by Will Richardson
- 11/2024 [Jujutsu: A Haven for Mercurial Users at Mozilla](https://ahal.ca/blog/2024/jujutsu-mercurial-haven/) by Andrew Halberstadt
- 12/2024 [Jujutsu Megamerges and `jj absorb`](https://v5.chriskrycho.com/journal/jujutsu-megamerges-and-jj-absorb/) by Chris Krycho
- 01/2025 [Jujutsu VCS Introduction and Patterns](https://kubamartin.com/posts/introduction-to-the-jujutsu-vcs/) by Kuba Martin
- 02/2025 [Why are Jujutsu's ID Prefixes So Short?](https://jonathan-frere.com/posts/jujutsu-shortest-ids/) by Jonathan Frere
- 05/2025 [jj tips and tricks](https://zerowidth.com/2025/jj-tips-and-tricks/) by Nathan Witmer
- 05/2025 [Overengineering PR create with jj](https://crespo.business/posts/overeng-pr-create-jj/) by David Crespo
- 05/2025 [Configuring Jujutsu](https://oppi.li/posts/configuring_jujutsu/) by Akshay
- 06/2025 [Jujutsu on Tangled](https://blog.tangled.org/stacking/) by Akshay
- 07/2025 [Jujutsu For Busy Devs](https://maddie.wtf/posts/2025-07-21-jujutsu-for-busy-devs) by Madeleine Mortensen
- 08/2025 [Jujutsu with Radicle](https://radicle.dev/2025/08/14/jujutsu-with-radicle) by Fintan Halpenny
- 08/2025 [Understanding Jujutsu bookmarks](https://neugierig.org/software/blog/2025/08/jj-bookmarks.html) by Evan Martin
- 10/2025 [Switch to Jujutsu already: a tutorial](https://www.stavros.io/posts/switch-to-jujutsu-already-a-tutorial/) by Stavros
- 10/2025 [I see a future in jj](https://steveklabnik.com/writing/i-see-a-future-in-jj/) by Steve Klabnik
- 11/2025 [More Commands in the JJ Toolbox](https://willhbr.net/2025/11/22/more-commands-in-the-jj-toolbox/) by Will Richardson
- 12/2025 [why i think jj-vcs is worth your time](https://schpet.com/note/why-i-think-jj-vcs-is-worth-your-time) by Peter Schilling
- 01/2026 [How I use Jujutsu](https://abhinavsarkar.net/posts/jj-usage/) by Abhinav Sarkar
- 02/2026 [Jujutsu: Managing workspaces](https://pksunkara.com/tech-notes/jujutsu-managing-workspaces/) by Pavan Sunkara
- 03/2026 [Reviewing large changes with Jujutsu](https://ben.gesoff.uk/posts/reviewing-large-changes-with-jj/) by Ben Gesoff
- 04/2026 [Jujutsu megamerges for fun and profit](https://isaaccorbrey.com/notes/jujutsu-megamerges-for-fun-and-profit) by Isaac Corbrey
- 06/2026 [Jujutsu: The Git Upgrade You Didn't Know You Needed](https://www.git-tower.com/blog/jujutsu) by Bruno Brito

## Books

- [Evan's Jujutsu Tutorial](https://evmar.github.io/jjtut/) - By Evan Martin.
- [Ju! Ju! Tsu!](https://arialdo.codeberg.page/ju-ju-tsu/) - By Arialdo Martini.
- [Juju-chu! — Starting Your Jujutsu × AI Workflow with `jj new`](https://leanpub.com/juju-chu) - By Yuka Ooka.
- [Jujutsu for Everyone](https://jj-for-everyone.github.io/) - By Remo Senekowitsch.
- [Steve's Jujutsu tutorial](https://steveklabnik.github.io/jujutsu-tutorial/) - By Steve Klabnik.

## Videos

- 10/2022 [Jujutsu: A Git-Compatible VCS - Git Merge 2022](https://www.youtube.com/watch?v=bx_LGilOuE4)
- 03/2024 [What if version control was AWESOME?](https://www.youtube.com/watch?v=2otjrTzRfVk)
- 10/2024 [Jujutsu - A Git-compatible VCS - Martin von Zweigbergk | GitMerge 2024](https://www.youtube.com/watch?v=LV0JzI8IcCY)
- 11/2024 [Jujutsu | Ep. 5 Bits and Booze](https://www.youtube.com/watch?v=dwyMlLYIrPk)
- 06/2025 [JJ With Git is My New Favorite Workflow](https://www.youtube.com/watch?v=ou4ZNRFXkO0)
- 10/2025 [How Jujutsu Uses Git - Martin von Zweigbergk](https://www.youtube.com/watch?v=XPtvvfGX3UQ)
- 10/2025 [Solving Git's Pain Points with Jujutsu (with Martin von Zweigbergk)](https://www.youtube.com/watch?v=ulJ_Pw8qqsE)
- 10/2025 [JJ Con 2025](https://www.youtube.com/playlist?list=PLOU2XLYxmsILM5cRwAK6yKdtKnCK6Y4Oh) (playlist)
- 10/2025 [JJ and How to Evolve an Open Source Ecosystem](https://www.youtube.com/watch?v=JGAszo6Ud-U)
- 11/2025 [Goodbye Git? Why JJ Might Be the Future of Version Control](https://www.youtube.com/watch?v=J2f3Pj58wTg)
- 12/2025 [Jujutsu Megamerges & Git History Preview | Ep. 23 Bits and Booze](https://www.youtube.com/watch?v=PsiXflgIC8Q)
- 12/2025 [Stacked Diffs with Git and Jujutsu](https://www.youtube.com/watch?v=Er3dqH-lloY)
- 01/2026 [Hands-on Introduction to jujutsu (jj) | Rawkode Live](https://www.youtube.com/watch?v=bECcod9ZMl0)
- 01/2026 [Jujutsu Version Control Explained](https://www.youtube.com/watch?v=mM4nrhDenC8)
- 02/2026 [Make code changes without committing. Better than Git?](https://www.youtube.com/watch?v=ZiqFGZASSKs)
- 05/2026 [TokioConf 2026 - jj: Simpler and More Powerful Than Git by Steve Klabnik](https://www.youtube.com/watch?v=n8KzCUyId_Y)
- 07/2026 [JJ Version Control System | Simpler Git Alternative](https://www.youtube.com/watch?v=LPQJEyr4El8)

## Forges

While Jujutsu works with Git compatible forges like GitHub, there are also some new forges/platforms worth mentioning, and some of them are exploring/offering a better integration and support for Jujutsu.

- [ERSC](https://ersc.io/) - Source control that scales as you grow ([Early Access](https://ersc.io/blog/ersc-availability)).
- [garami](https://github.com/garami-vcs/garami) - Experimental native hosting and collaboration infrastructure for Jujutsu repositories (early-stage).
- [Jujubi](https://juju.bi/) - Modern code forge built for speed (Early Access).
- [Radicle](https://radicle.dev/) - The sovereign forge.
- [Revset](https://www.revset.dev/) - Commit First Code Forge (Early Access).
- [Tangled](https://tangled.org/) - The next-generation social coding platform ([announcement](https://blog.tangled.org/stacking)).

## Miscellaneous

- [JJ Cheat Sheet](https://justinpombrio.net/2025/02/11/jj-cheat-sheet.html)
- [List of popular Jujutsu aliases](https://www.lysator.liu.se/~axl/jj-aliases/)

## Community

- [Bluesky](https://bsky.app/profile/jj-vcs.dev) - Official Jujutsu account.
- [Discord](https://discord.gg/dkmfj3aGQN) - Community chat server.
- [GitHub Discussions](https://github.com/jj-vcs/jj/discussions) - Q&A and design discussions.
- [Libera Chat](https://web.libera.chat/?channel=#jujutsu) - IRC channel `#jujutsu`.
- [Reddit](https://www.reddit.com/r/jjvcs/) - Community subreddit.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Please read the [Code of Conduct](CODE_OF_CONDUCT.md) first.

[![CC0](https://i.creativecommons.org/p/zero/1.0/88x31.png)](https://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, the authors have waived all copyright and related or neighboring rights to this work under the license in [LICENSE](LICENSE).
