from awesome_jj_tools.entries import GitHubRepoRef
from awesome_jj_tools.stars import StarMover, compute_movers, fetch_current_stars, render_report


def _ref(owner="x", repo="a", name="a"):
    return GitHubRepoRef(
        owner=owner,
        repo=repo,
        url=f"https://github.com/{owner}/{repo}",
        entry_name=name,
        section_path=(),
    )


def test_star_mover_relative_growth():
    mover = StarMover(name="a", url="u", previous=100, current=120)
    assert mover.relative_growth == 0.2


def test_star_mover_relative_growth_from_zero_previous():
    assert StarMover(name="a", url="u", previous=0, current=5).relative_growth == float("inf")
    assert StarMover(name="a", url="u", previous=0, current=0).relative_growth == 0.0


def test_compute_movers_skips_repo_with_no_prior_snapshot():
    ref = _ref()
    movers = compute_movers([ref], previous={}, current={ref.url: 100})
    assert movers == []


def test_compute_movers_includes_repo_at_threshold_boundary():
    ref = _ref()
    movers = compute_movers([ref], previous={ref.url: 100}, current={ref.url: 115}, threshold=0.15)
    assert len(movers) == 1
    assert movers[0].relative_growth == 0.15


def test_compute_movers_excludes_below_threshold():
    ref = _ref()
    movers = compute_movers([ref], previous={ref.url: 100}, current={ref.url: 110}, threshold=0.15)
    assert movers == []


def test_compute_movers_excludes_negative_growth():
    ref = _ref()
    movers = compute_movers([ref], previous={ref.url: 100}, current={ref.url: 50}, threshold=0.15)
    assert movers == []


def test_compute_movers_sorted_descending_by_growth():
    ref_a = _ref(owner="x", repo="a", name="a")
    ref_b = _ref(owner="x", repo="b", name="b")
    movers = compute_movers(
        [ref_a, ref_b],
        previous={ref_a.url: 100, ref_b.url: 100},
        current={ref_a.url: 150, ref_b.url: 300},
    )
    assert [m.name for m in movers] == ["b", "a"]


async def test_fetch_current_stars(client):
    async def fake_fetcher(client, owner, repo):
        return {"stargazers_count": 42}

    ref = _ref()
    assert await fetch_current_stars(client, [ref], fake_fetcher) == {ref.url: 42}


async def test_fetch_current_stars_handles_multiple_refs_concurrently(client):
    refs = [_ref(owner="x", repo=f"r{i}", name=f"r{i}") for i in range(5)]

    async def fake_fetcher(client, owner, repo):
        return {"stargazers_count": int(repo[1:])}

    result = await fetch_current_stars(client, refs, fake_fetcher)
    assert result == {r.url: i for i, r in enumerate(refs)}


def test_render_report_empty():
    assert "No repos crossed" in render_report([])


def test_render_report_lists_movers():
    mover = StarMover(name="a", url="u", previous=100, current=150)
    output = render_report([mover])
    assert "a" in output and "100" in output and "150" in output and "50%" in output
