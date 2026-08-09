from awesome_jj_tools.sections import build_context, slug, sort_key


def test_slug_strips_non_alnum_and_lowercases():
    assert slug("Diff and Merge Drivers") == "diff-and-merge-drivers"


def test_sort_key_strips_leading_quote():
    assert sort_key('"Quoted Title"') == 'quoted title"'


def test_sort_key_lowercases():
    assert sort_key("Zebra") == "zebra"


def test_build_context_every_section_has_uniform_shape():
    data = {"official_resources": [{"name": "x", "url": "https://example.com"}]}
    context = build_context(data)
    for section in context["sections"]:
        assert "subsections" in section
        assert "entries" in section


def test_build_context_tools_subsections_sorted():
    data = {
        "tools": {
            "gui": [
                {"name": "Zeta", "url": "https://example.com/z"},
                {"name": "alpha", "url": "https://example.com/a"},
            ]
        }
    }
    context = build_context(data)
    tools_section = next(s for s in context["sections"] if s["key"] == "tools")
    gui = next(sub for sub in tools_section["subsections"] if sub["key"] == "gui")
    assert [e["name"] for e in gui["entries"]] == ["alpha", "Zeta"]


def test_build_context_articles_entries_have_year_month():
    data = {
        "articles": [{"name": "x", "url": "https://example.com", "date": "2024-03", "author": "A"}]
    }
    context = build_context(data)
    articles = next(s for s in context["sections"] if s["key"] == "articles")
    assert articles["entries"][0]["year"] == "2024"
    assert articles["entries"][0]["month"] == "03"
