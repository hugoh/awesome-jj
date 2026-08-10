"""Async fan-out over a list of items with a `rich` progress bar.

Writes to stderr, never stdout — the CLI's report text goes to stdout and
gets captured verbatim (e.g. into a GitHub Actions output in discovery.yml);
progress-bar escape codes have no business ending up in there. `rich`
auto-disables the fancy rendering when stderr isn't a terminal (CI logs,
piped output), so this is a no-op noise-wise outside interactive use.

Concurrency itself is bounded twice over: httpx2.Limits caps connections
(see http.py), and the semaphore here caps how many `fn(item)` coroutines
are in flight at once — belt and suspenders against GitHub's abuse-detection
rate limit, and it's what makes the progress bar's "in progress" count mean
something.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable

from rich.console import Console
from rich.progress import Progress

from awesome_jj_tools.http import MAX_CONCURRENCY

_console = Console(stderr=True)


async def parallel_map[T, R](
    fn: Callable[[T], Awaitable[R]],
    items: Iterable[T],
    description: str,
    max_concurrency: int = MAX_CONCURRENCY,
) -> list[R]:
    """Await fn(item) for every item concurrently, preserving input order in the result."""
    items = list(items)
    if not items:
        return []

    results: dict[int, R] = {}
    semaphore = asyncio.Semaphore(max_concurrency)

    with Progress(console=_console, transient=True) as progress:
        task_id = progress.add_task(description, total=len(items))

        async def run_one(index: int, item: T) -> None:
            async with semaphore:
                results[index] = await fn(item)
            progress.advance(task_id)

        await asyncio.gather(*(run_one(i, item) for i, item in enumerate(items)))

    return [results[i] for i in range(len(items))]
