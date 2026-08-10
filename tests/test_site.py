from test_generate import MINIMAL

from awesome_jj_tools.site import generate, render


def test_renders_doctype_and_title():
    output = render(MINIMAL, "2026-01-01")
    assert output.startswith("<!doctype html>")
    assert "<title>Awesome JJ</title>" in output


def test_pagefind_hooks_present():
    output = render(MINIMAL, "2026-01-01")
    assert "data-pagefind-body" in output
    assert '<div id="search">' in output
    assert "pagefind-ui.js" in output
    assert "pagefind-ui.css" in output


def test_pagefind_focus_on_slash_enabled():
    output = render(MINIMAL, "2026-01-01")
    assert "focusOnSlash: true" in output


def test_pagefind_asset_paths_are_relative():
    # Absolute (leading-slash) paths resolve to the domain root, not the
    # /awesome-jj/ project-site subpath GitHub Pages serves this under —
    # that mismatch is what left PagefindUI undefined on the live site.
    output = render(MINIMAL, "2026-01-01")
    assert 'href="pagefind/pagefind-ui.css"' in output
    assert 'src="pagefind/pagefind-ui.js"' in output
    assert 'href="/pagefind' not in output
    assert 'src="/pagefind' not in output


def test_seo_tags_present():
    output = render(MINIMAL, "2026-01-01")
    assert '<link rel="canonical" href="https://hugoh.github.io/awesome-jj/">' in output
    assert '<meta name="robots" content="index, follow">' in output
    assert 'property="og:title" content="Awesome JJ"' in output
    assert 'property="og:description"' in output
    assert 'property="og:url" content="https://hugoh.github.io/awesome-jj/"' in output
    assert 'name="twitter:card" content="summary"' in output


def test_entries_get_unique_anchor_ids():
    output = render(MINIMAL, "2026-01-01")
    assert 'id="jujutsu-homepage"' in output
    assert 'id="quoted-title"' in output


def test_entry_with_description_rendered():
    output = render(MINIMAL, "2026-01-01")
    assert (
        '<li id="quoted-title"><a href="https://example.com/q">Quoted title</a>'
        " &mdash; Has a description.</li>" in output
    )


def test_description_markdown_link_rendered_as_anchor():
    data = {
        **MINIMAL,
        "official_resources": [
            *MINIMAL["official_resources"],
            {
                "name": "Tangled",
                "url": "https://tangled.org/",
                "description": "Social coding ([announcement](https://blog.tangled.org/stacking)).",
            },
        ],
    }
    output = render(data, "2026-01-01")
    assert 'Social coding (<a href="https://blog.tangled.org/stacking">announcement</a>).' in output
    assert "[announcement]" not in output


def test_description_ampersand_escaped():
    data = {
        **MINIMAL,
        "official_resources": [
            *MINIMAL["official_resources"],
            {
                "name": "Multi",
                "url": "https://example.com/multi",
                "description": "TUI & CLI tool.",
            },
        ],
    }
    output = render(data, "2026-01-01")
    assert "TUI &amp; CLI tool." in output


def test_book_rendered_with_by_prefix():
    output = render(MINIMAL, "2026-01-01")
    assert "&mdash; By A Author." in output


def test_tools_subsections_have_headings():
    output = render(MINIMAL, "2026-01-01")
    assert '<h3 id="gui">GUI</h3>' in output


def test_section_anchors_match_toc_links():
    output = render(MINIMAL, "2026-01-01")
    assert '<h2 id="articles">Articles</h2>' in output
    assert '<a href="#articles">Articles</a>' in output


def test_generate_writes_index_html(tmp_path):
    import yaml

    from awesome_jj_tools.last_updated import LastUpdatedSnapshot, save_snapshot

    entries_path = tmp_path / "entries.yaml"
    index_path = tmp_path / "site" / "index.html"
    last_updated_path = tmp_path / "last-updated.json"
    entries_path.write_text(yaml.safe_dump(MINIMAL), encoding="utf-8")
    save_snapshot(LastUpdatedSnapshot(hash="irrelevant", date="2026-08-09"), last_updated_path)

    content = generate(entries_path, index_path, last_updated_path)

    assert index_path.read_text(encoding="utf-8") == content
    assert index_path.parent.is_dir()
    assert "2026-08-09" in content


def test_generate_uses_empty_string_when_no_snapshot_exists(tmp_path):
    import yaml

    entries_path = tmp_path / "entries.yaml"
    index_path = tmp_path / "site" / "index.html"
    entries_path.write_text(yaml.safe_dump(MINIMAL), encoding="utf-8")

    generate(entries_path, index_path, tmp_path / "does-not-exist.json")

    assert index_path.exists()
