from awesome_jj_tools.redirects import (
    Redirect,
    diff_redirects,
    extract_redirects,
    load_accepted_redirects,
    render_report,
    run,
)

SAMPLE_REPORT = {
    "redirect_map": {
        "README.md": [
            {
                "origin": "https://www.revset.dev/",
                "redirects": [{"url": "https://revset.dev/", "code": 308}],
            },
            {
                "origin": "https://awesome.re/",
                "redirects": [{"url": "https://github.com/sindresorhus/awesome", "code": 302}],
            },
        ]
    }
}


def test_extract_redirects_flattens_redirect_map():
    redirects = extract_redirects(SAMPLE_REPORT)
    assert redirects == [
        Redirect(
            source_file="README.md",
            url="https://www.revset.dev/",
            target="https://revset.dev/",
            code=308,
        ),
        Redirect(
            source_file="README.md",
            url="https://awesome.re/",
            target="https://github.com/sindresorhus/awesome",
            code=302,
        ),
    ]


def test_extract_redirects_empty_map():
    assert extract_redirects({"redirect_map": {}}) == []


def test_load_accepted_redirects_reads_entry_field():
    data = {
        "section": [
            {"name": "a", "url": "https://a.example/", "accepted_redirect": "https://a.example/x"},
            {"name": "b", "url": "https://b.example/"},
        ]
    }
    assert load_accepted_redirects(data) == {("https://a.example/", "https://a.example/x")}


def _redirect(url="https://a.example/", target="https://a.example/x", code=301):
    return Redirect(source_file="README.md", url=url, target=target, code=code)


def test_diff_redirects_new_only():
    current = [_redirect()]
    new, stale = diff_redirects(current, known=set())
    assert new == current
    assert stale == []


def test_diff_redirects_known_not_reported_as_new():
    r = _redirect()
    new, stale = diff_redirects([r], known={(r.url, r.target)})
    assert new == []
    assert stale == []


def test_diff_redirects_stale_only():
    known = {("https://gone.example/", "https://gone.example/x")}
    new, stale = diff_redirects([], known=known)
    assert new == []
    assert stale == [("https://gone.example/", "https://gone.example/x")]


def test_diff_redirects_same_url_different_target_counts_as_new():
    known = {("https://a.example/", "https://a.example/old")}
    r = _redirect(url="https://a.example/", target="https://a.example/new")
    new, stale = diff_redirects([r], known=known)
    assert new == [r]
    assert stale == [("https://a.example/", "https://a.example/old")]


def test_render_report_empty():
    output = render_report([], [])
    assert "No new or stale redirects" in output


def test_render_report_lists_new_and_stale():
    new = [_redirect(url="https://new.example/", target="https://new.example/x")]
    stale = [("https://gone.example/", "https://gone.example/x")]
    output = render_report(new, stale)
    assert "new.example" in output
    assert "gone.example" in output


def test_run_reports_new_redirect_and_has_findings(tmp_path):
    entries_path = tmp_path / "entries.yaml"
    entries_path.write_text("section: []\n", encoding="utf-8")
    exceptions_path = tmp_path / "redirect-exceptions.yaml"

    def fake_runner(inputs):
        return SAMPLE_REPORT

    report, has_findings = run(
        inputs=["README.md"],
        entries_path=entries_path,
        exceptions_path=exceptions_path,
        lychee_runner=fake_runner,
    )
    assert has_findings is True
    assert "revset.dev" in report


def test_run_reports_no_findings_when_entries_and_exceptions_cover_everything(tmp_path):
    entries_path = tmp_path / "entries.yaml"
    entries_path.write_text(
        "section:\n"
        "  - name: Revset\n"
        "    url: https://www.revset.dev/\n"
        "    accepted_redirect: https://revset.dev/\n",
        encoding="utf-8",
    )
    exceptions_path = tmp_path / "redirect-exceptions.yaml"
    exceptions_path.write_text(
        "redirects:\n"
        "  - url: https://awesome.re/\n"
        "    target: https://github.com/sindresorhus/awesome\n"
        "    reason: test\n",
        encoding="utf-8",
    )

    def fake_runner(inputs):
        return SAMPLE_REPORT

    report, has_findings = run(
        inputs=["README.md"],
        entries_path=entries_path,
        exceptions_path=exceptions_path,
        lychee_runner=fake_runner,
    )
    assert has_findings is False
    assert "No new or stale redirects" in report
