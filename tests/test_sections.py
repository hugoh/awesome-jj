from awesome_jj_tools.sections import build_context, load_config, slug, sort_key

MINIMAL_CONFIG = {
    "title": "Test Title",
    "description": "Test description.",
    "intro": "Test intro sentence.",
    "url": "https://example.com/",
    "sections": [
        {"key": "official_resources", "title": "Official Resources", "kind": "list"},
        {"key": "articles", "title": "Articles", "kind": "dated"},
        {
            "key": "tools",
            "title": "Tools",
            "kind": "tools",
            "subsections": [{"key": "gui", "title": "GUI"}],
        },
        {
            "key": "forges",
            "title": "Forges",
            "kind": "list_sorted",
            "intro": "Forges intro text.",
        },
        {"key": "miscellaneous", "title": "Miscellaneous", "kind": "list"},
    ],
}


def test_slug_strips_non_alnum_and_lowercases():
    assert slug("Diff and Merge Drivers") == "diff-and-merge-drivers"


def test_sort_key_strips_leading_quote():
    assert sort_key('"Quoted Title"') == 'quoted title"'


def test_sort_key_lowercases():
    assert sort_key("Zebra") == "zebra"


def test_load_config_reads_real_config():
    config = load_config()
    assert config["title"]
    assert config["description"]
    assert config["intro"]
    keys = [s["key"] for s in config["sections"]]
    assert "official_resources" in keys
    assert "tools" in keys
    tools = next(s for s in config["sections"] if s["key"] == "tools")
    assert any(sub["key"] == "gui" for sub in tools["subsections"])


def test_build_context_every_section_has_uniform_shape():
    data = {"official_resources": [{"name": "x", "url": "https://example.com"}]}
    context = build_context(data, MINIMAL_CONFIG)
    for section in context["sections"]:
        assert "subsections" in section
        assert "entries" in section
        assert "intro" in section


def test_build_context_exposes_title_description_intro():
    context = build_context({}, MINIMAL_CONFIG)
    assert context["title"] == "Test Title"
    assert context["description"] == "Test description."
    assert context["intro"] == "Test intro sentence."
    assert context["url"] == "https://example.com/"


def test_build_context_uses_injected_config_not_real_file():
    data = {"official_resources": [{"name": "x", "url": "https://example.com"}]}
    context = build_context(data, MINIMAL_CONFIG)
    keys = [s["key"] for s in context["sections"]]
    assert keys == ["official_resources", "articles", "tools", "forges", "miscellaneous"]


def test_build_context_tools_subsections_sorted():
    data = {
        "tools": {
            "gui": [
                {"name": "Zeta", "url": "https://example.com/z"},
                {"name": "alpha", "url": "https://example.com/a"},
            ]
        }
    }
    context = build_context(data, MINIMAL_CONFIG)
    tools_section = next(s for s in context["sections"] if s["key"] == "tools")
    gui = next(sub for sub in tools_section["subsections"] if sub["key"] == "gui")
    assert [e["name"] for e in gui["entries"]] == ["alpha", "Zeta"]


def test_build_context_articles_entries_have_year_month():
    data = {
        "articles": [{"name": "x", "url": "https://example.com", "date": "2024-03", "author": "A"}]
    }
    context = build_context(data, MINIMAL_CONFIG)
    articles = next(s for s in context["sections"] if s["key"] == "articles")
    assert articles["entries"][0]["year"] == "2024"
    assert articles["entries"][0]["month"] == "03"


def test_build_context_entries_get_slug():
    data = {"official_resources": [{"name": "Jujutsu Homepage", "url": "https://example.com"}]}
    context = build_context(data, MINIMAL_CONFIG)
    resources = next(s for s in context["sections"] if s["key"] == "official_resources")
    assert resources["entries"][0]["slug"] == "jujutsu-homepage"


def test_build_context_duplicate_names_get_unique_slugs():
    data = {
        "miscellaneous": [
            {"name": "Same Name", "url": "https://example.com/1"},
            {"name": "Same Name", "url": "https://example.com/2"},
        ]
    }
    context = build_context(data, MINIMAL_CONFIG)
    misc = next(s for s in context["sections"] if s["key"] == "miscellaneous")
    slugs = [e["slug"] for e in misc["entries"]]
    assert slugs == ["same-name", "same-name-2"]
    assert len(set(slugs)) == 2


def test_build_context_section_intro_comes_from_config():
    context = build_context({}, MINIMAL_CONFIG)
    forges = next(s for s in context["sections"] if s["key"] == "forges")
    assert forges["intro"] == "Forges intro text."


def test_build_context_section_intro_defaults_to_none():
    context = build_context({}, MINIMAL_CONFIG)
    resources = next(s for s in context["sections"] if s["key"] == "official_resources")
    assert resources["intro"] is None


def test_build_context_defaults_to_real_config():
    context = build_context({})
    keys = [s["key"] for s in context["sections"]]
    assert "official_resources" in keys
    assert "community" in keys
    assert context["title"]
