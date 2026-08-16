from test_generate import MINIMAL

from awesome_jj_tools.site import generate, render


def render_page(data, updated_at, filename="index.html"):
    return render(data, updated_at)[filename]


def test_renders_doctype_and_title():
    output = render_page(MINIMAL, "2026-01-01")
    assert output.startswith("<!doctype html>")
    assert "<title>Awesome JJ</title>" in output


def test_non_index_page_title_includes_section():
    output = render_page(MINIMAL, "2026-01-01", "books.html")
    assert "<title>Books — Awesome JJ</title>" in output


def test_index_page_heading_is_bare_site_title():
    output = render_page(MINIMAL, "2026-01-01")
    assert '<h1 id="tools">Awesome JJ</h1>' in output


def test_non_index_page_heading_includes_section():
    output = render_page(MINIMAL, "2026-01-01", "books.html")
    assert '<h1 id="books">Awesome JJ - Books</h1>' in output


def test_pagefind_hooks_present():
    output = render_page(MINIMAL, "2026-01-01", "books.html")
    assert "data-pagefind-body" in output
    assert "<pagefind-modal-trigger>" in output
    assert "<pagefind-modal>" in output
    assert "pagefind-component-ui.js" in output
    assert "pagefind-component-ui.css" in output


def test_pagefind_body_absent_on_tools_hub():
    # The hub duplicates every Tools entry (grouped under its subsection
    # heading) so visitors can scan everything at a glance, but each entry
    # is already indexed — with a filterable category — on its own
    # subsection page. Indexing the hub too would just double every result.
    output = render_page(MINIMAL, "2026-01-01")
    assert "data-pagefind-body" not in output


def test_pagefind_bundle_path_explicit():
    # type="module" scripts don't set document.currentScript, so the
    # Component UI can't auto-detect its own location and falls back to
    # the absolute "/pagefind/" — 404s once served under a subpath (e.g.
    # GitHub Pages' /awesome-jj/). Must be set explicitly, and:
    # - needs a leading "./" — the bundle path also feeds a dynamic
    #   import() inside the Component UI, where a bare "pagefind/" (no
    #   leading dot/slash) is parsed as a bare module specifier rather
    #   than a relative URL and fails to resolve.
    # - is relative to pagefind-component-ui.js's own location (which is
    #   already inside pagefind/), not the page — "./" not "./pagefind/",
    #   which would double up to .../pagefind/pagefind/pagefind.js.
    output = render_page(MINIMAL, "2026-01-01")
    assert '<pagefind-config bundle-path="./">' in output


def test_pagefind_modal_closes_on_result_click():
    # pagefind-modal has no built-in auto-close on result selection, and a
    # result linking to a same-page anchor (a Pagefind sub-result) doesn't
    # trigger a full page navigation, so the modal would otherwise stay
    # open over the scrolled-to content.
    output = render_page(MINIMAL, "2026-01-01")
    assert 'closest("pagefind-results a")' in output
    assert 'querySelector("pagefind-modal")?.close()' in output


def test_pagefind_asset_paths_are_relative():
    # Absolute (leading-slash) paths resolve to the domain root, not the
    # /awesome-jj/ project-site subpath GitHub Pages serves this under —
    # that mismatch is what left PagefindUI undefined on the live site.
    output = render_page(MINIMAL, "2026-01-01")
    assert 'href="pagefind/pagefind-component-ui.css"' in output
    assert 'src="pagefind/pagefind-component-ui.js"' in output
    assert 'href="/pagefind' not in output
    assert 'src="/pagefind' not in output


def test_pagefind_category_filter_present_on_top_level_sections():
    # Now that Tools is split into one page per subsection, every page has
    # exactly one category, so Pagefind's filter-pane (which only gates
    # whole pages, not sub-result fragments) can filter by it site-wide.
    output = render_page(MINIMAL, "2026-01-01", "books.html")
    assert 'data-pagefind-filter="category">Books' in output


def test_pagefind_category_filter_present_on_tools_subsection():
    output = render_page(MINIMAL, "2026-01-01", "tools-gui.html")
    assert 'data-pagefind-filter="category">GUI' in output


def test_pagefind_category_filter_absent_on_tools_hub():
    # The hub page links to every subsection rather than belonging to a
    # single category itself.
    output = render_page(MINIMAL, "2026-01-01")
    assert "data-pagefind-filter" not in output


def test_pagefind_filter_pane_present():
    output = render_page(MINIMAL, "2026-01-01")
    assert '<pagefind-filter-pane label="Category">' in output


def test_pagefind_meta_title_overridden_per_section():
    output = render_page(MINIMAL, "2026-01-01", "books.html")
    assert 'data-pagefind-meta="title">Books — Awesome JJ' in output


def test_pagefind_entry_name_weighted():
    output = render_page(MINIMAL, "2026-01-01", "books.html")
    assert 'data-pagefind-weight="2"' in output


def test_seo_tags_present():
    output = render_page(MINIMAL, "2026-01-01")
    assert '<link rel="canonical" href="https://awesome-jj.larve.net/">' in output
    assert '<meta name="robots" content="index, follow">' in output
    assert 'property="og:title" content="Awesome JJ"' in output
    assert 'property="og:description"' in output
    assert 'property="og:url" content="https://awesome-jj.larve.net/"' in output
    assert 'name="twitter:card" content="summary"' in output


def test_seo_tags_present_on_non_index_page():
    output = render_page(MINIMAL, "2026-01-01", "books.html")
    assert '<link rel="canonical" href="https://awesome-jj.larve.net/books.html">' in output
    assert 'property="og:title" content="Books — Awesome JJ"' in output
    assert 'property="og:url" content="https://awesome-jj.larve.net/books.html"' in output


def test_sitemap_lists_every_page():
    pages = render(MINIMAL, "2026-01-01")
    sitemap = pages["sitemap.xml"]
    assert sitemap.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert "<loc>https://awesome-jj.larve.net/</loc>" in sitemap
    assert "<loc>https://awesome-jj.larve.net/books.html</loc>" in sitemap
    assert "<loc>https://awesome-jj.larve.net/tools-gui.html</loc>" in sitemap
    assert "sitemap.xml</loc>" not in sitemap
    assert "robots.txt</loc>" not in sitemap
    assert "<lastmod>2026-01-01</lastmod>" in sitemap


def test_sitemap_omits_lastmod_when_no_snapshot():
    sitemap = render(MINIMAL, "")["sitemap.xml"]
    assert "<lastmod>" not in sitemap


def test_robots_txt_points_at_sitemap():
    robots = render(MINIMAL, "2026-01-01")["robots.txt"]
    assert "Allow: /" in robots
    assert "Sitemap: https://awesome-jj.larve.net/sitemap.xml" in robots


def test_entries_get_unique_anchor_ids():
    output = render_page(MINIMAL, "2026-01-01")
    assert 'id="jujutsu-homepage"' not in output  # official_resources isn't on the tools page
    official_output = render_page(MINIMAL, "2026-01-01", "official-resources.html")
    assert 'id="jujutsu-homepage"' in official_output
    assert 'id="quoted-title"' in official_output


def test_entry_with_description_rendered():
    output = render_page(MINIMAL, "2026-01-01", "official-resources.html")
    assert (
        '<li id="quoted-title"><a href="https://example.com/q" data-pagefind-weight="2">'
        "Quoted title</a> &mdash; Has a description.</li>" in output
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
    output = render_page(data, "2026-01-01", "official-resources.html")
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
    output = render_page(data, "2026-01-01", "official-resources.html")
    assert "TUI &amp; CLI tool." in output


def test_book_rendered_with_by_prefix():
    output = render_page(MINIMAL, "2026-01-01", "books.html")
    assert "&mdash; By A Author." in output


def test_tools_hub_links_to_subsections():
    output = render_page(MINIMAL, "2026-01-01")
    assert '<a href="tools-gui.html">GUI</a>' in output
    assert '<a href="tools-tui.html">TUI</a>' in output


def test_tools_hub_lists_all_entries_grouped_by_subsection():
    output = render_page(MINIMAL, "2026-01-01")
    assert '<h3 id="gui">GUI</h3>' in output
    assert output.index("alpha") < output.index("Zeta")


def test_tools_subsection_page_has_heading_and_entries():
    output = render_page(MINIMAL, "2026-01-01", "tools-gui.html")
    assert '<h1 id="gui">Awesome JJ - GUI</h1>' in output
    assert output.index("alpha") < output.index("Zeta")


def test_nav_links_to_other_pages():
    output = render_page(MINIMAL, "2026-01-01")
    assert '<a href="books.html">Books</a>' in output
    assert '<a href="./" aria-current="page">Tools</a>' in output


def test_nav_marks_tools_current_on_subsection_pages():
    output = render_page(MINIMAL, "2026-01-01", "tools-gui.html")
    assert '<a href="./" aria-current="page">Tools</a>' in output


def test_tools_subnav_present_on_hub_and_subsection_pages():
    hub_output = render_page(MINIMAL, "2026-01-01")
    assert '<div class="tools-subnav-box">' in hub_output
    assert '<nav class="tools-subnav">' in hub_output
    assert "Tools categories" in hub_output
    assert '<a href="tools-tui.html">TUI</a>' in hub_output

    gui_output = render_page(MINIMAL, "2026-01-01", "tools-gui.html")
    assert '<nav class="tools-subnav">' in gui_output
    assert '<a href="tools-gui.html" aria-current="page">GUI</a>' in gui_output


def test_tools_subnav_absent_on_non_tools_pages():
    output = render_page(MINIMAL, "2026-01-01", "books.html")
    assert 'class="tools-subnav"' not in output
    assert 'class="tools-subnav-box"' not in output


def test_nav_sections_are_labeled():
    output = render_page(MINIMAL, "2026-01-01")
    assert '<span class="nav-label">Sections</span>' in output


def test_generate_writes_one_file_per_section(tmp_path):
    import yaml

    from awesome_jj_tools.last_updated import LastUpdatedSnapshot, save_snapshot

    entries_path = tmp_path / "entries.yaml"
    index_path = tmp_path / "site" / "index.html"
    last_updated_path = tmp_path / "last-updated.json"
    entries_path.write_text(yaml.safe_dump(MINIMAL), encoding="utf-8")
    save_snapshot(LastUpdatedSnapshot(hash="irrelevant", date="2026-08-09"), last_updated_path)

    pages = generate(entries_path, index_path, last_updated_path)

    site_dir = index_path.parent
    assert site_dir.is_dir()
    for filename, content in pages.items():
        assert (site_dir / filename).read_text(encoding="utf-8") == content
    assert "2026-08-09" in pages["index.html"]
    assert "books.html" in pages
    assert "official-resources.html" in pages
    assert "tools-gui.html" in pages
    assert "tools-misc-tools.html" in pages
    assert "sitemap.xml" in pages
    assert "robots.txt" in pages
    # 7 non-Tools top-level sections + 1 Tools hub + 9 Tools subsections + sitemap.xml + robots.txt
    assert len(pages) == 19


def test_generate_uses_empty_string_when_no_snapshot_exists(tmp_path):
    import yaml

    entries_path = tmp_path / "entries.yaml"
    index_path = tmp_path / "site" / "index.html"
    entries_path.write_text(yaml.safe_dump(MINIMAL), encoding="utf-8")

    generate(entries_path, index_path, tmp_path / "does-not-exist.json")

    assert index_path.exists()
