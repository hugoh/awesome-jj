from awesome_jj_tools.generate import check, generate, render

MINIMAL = {
    "official_resources": [
        {"name": "Jujutsu homepage", "url": "https://www.jj-vcs.dev"},
        {
            "name": "Quoted title",
            "url": "https://example.com/q",
            "description": "Has a description.",
        },
    ],
    "articles": [
        {
            "name": "Second",
            "url": "https://example.com/2",
            "date": "2024-02",
            "author": "B Author",
        },
        {
            "name": "First",
            "url": "https://example.com/1",
            "date": "2024-01",
            "author": "A Author",
        },
    ],
    "books": [
        {"name": "Zebra Book", "url": "https://example.com/z", "author": "Z Author"},
        {"name": "Apple Book", "url": "https://example.com/a", "author": "A Author"},
    ],
    "videos": [
        {"name": "Later video", "url": "https://example.com/v2", "date": "2024-02"},
        {
            "name": "Earlier video",
            "url": "https://example.com/v1",
            "date": "2024-01",
            "suffix": "(playlist)",
        },
    ],
    "tools": {
        "gui": [
            {"name": "Zeta", "url": "https://example.com/zeta", "description": "Z tool."},
            {"name": "alpha", "url": "https://example.com/alpha", "description": "A tool."},
        ],
        "tui": [],
        "editor_integration": [],
        "diff_merge_drivers": [],
        "workflows": [],
        "shell_integration": [],
        "misc_tools": [],
    },
    "forges": [
        {"name": "Zeta Forge", "url": "https://example.com/zf", "description": "Z forge."},
        {"name": "Alpha Forge", "url": "https://example.com/af", "description": "A forge."},
    ],
    "miscellaneous": [
        {"name": "Misc one", "url": "https://example.com/m1"},
    ],
    "community": [
        {"name": "Zeta Community", "url": "https://example.com/zc", "description": "Z place."},
        {"name": "Alpha Community", "url": "https://example.com/ac", "description": "A place."},
    ],
}


def test_articles_sorted_by_date_ascending():
    output = render(MINIMAL, "2026-01-01")
    assert output.index("First") < output.index("Second")


def test_books_sorted_alphabetically():
    output = render(MINIMAL, "2026-01-01")
    assert output.index("Apple Book") < output.index("Zebra Book")


def test_videos_sorted_by_date_and_suffix_rendered():
    output = render(MINIMAL, "2026-01-01")
    assert output.index("Earlier video") < output.index("Later video")
    assert "- 01/2024 [Earlier video](https://example.com/v1) (playlist)" in output


def test_tools_subsection_sorted_case_insensitively():
    output = render(MINIMAL, "2026-01-01")
    assert output.index("alpha") < output.index("Zeta")


def test_forges_and_community_sorted_alphabetically():
    output = render(MINIMAL, "2026-01-01")
    assert output.index("Alpha Forge") < output.index("Zeta Forge")
    assert output.index("Alpha Community") < output.index("Zeta Community")


def test_official_resources_and_miscellaneous_preserve_declared_order():
    output = render(MINIMAL, "2026-01-01")
    assert output.index("Jujutsu homepage") < output.index("Quoted title")


def test_entry_with_description_uses_dash_separator():
    output = render(MINIMAL, "2026-01-01")
    assert "- [Quoted title](https://example.com/q) - Has a description." in output


def test_entry_without_description_has_no_trailing_dash():
    output = render(MINIMAL, "2026-01-01")
    assert "- [Jujutsu homepage](https://www.jj-vcs.dev)\n" in output


def test_book_rendered_with_by_prefix_and_period():
    output = render(MINIMAL, "2026-01-01")
    assert "- [Apple Book](https://example.com/a) - By A Author.\n" in output


def test_article_rendered_with_month_year_and_by():
    output = render(MINIMAL, "2026-01-01")
    assert "- 01/2024 [First](https://example.com/1) by A Author\n" in output


def test_contents_toc_lists_tools_subsections():
    output = render(MINIMAL, "2026-01-01")
    assert "  - [GUI](#gui)" in output


def test_badge_is_inline_with_h1():
    output = render(MINIMAL, "2026-01-01")
    first_line = output.splitlines()[0]
    assert first_line.startswith("# Awesome JJ [![Awesome]")


def test_no_license_heading():
    output = render(MINIMAL, "2026-01-01")
    assert "## License" not in output


def test_generate_writes_readme(tmp_path):
    import yaml

    entries_path = tmp_path / "entries.yaml"
    readme_path = tmp_path / "README.md"
    last_updated_path = tmp_path / "last-updated.json"
    entries_path.write_text(yaml.safe_dump(MINIMAL), encoding="utf-8")

    content = generate(entries_path, readme_path, last_updated_path, today="2026-08-09")

    assert readme_path.read_text(encoding="utf-8") == content
    assert "2026-08-09" in content
    assert check(entries_path, readme_path, last_updated_path) is True


def test_generate_does_not_advance_date_on_unchanged_rerun(tmp_path):
    import yaml

    entries_path = tmp_path / "entries.yaml"
    readme_path = tmp_path / "README.md"
    last_updated_path = tmp_path / "last-updated.json"
    entries_path.write_text(yaml.safe_dump(MINIMAL), encoding="utf-8")
    generate(entries_path, readme_path, last_updated_path, today="2026-08-01")

    content = generate(entries_path, readme_path, last_updated_path, today="2026-08-09")

    assert "2026-08-01" in content
    assert "2026-08-09" not in content


def test_check_detects_drift(tmp_path):
    import yaml

    entries_path = tmp_path / "entries.yaml"
    readme_path = tmp_path / "README.md"
    last_updated_path = tmp_path / "last-updated.json"
    entries_path.write_text(yaml.safe_dump(MINIMAL), encoding="utf-8")
    generate(entries_path, readme_path, last_updated_path, today="2026-08-09")

    readme_path.write_text("stale content", encoding="utf-8")

    assert check(entries_path, readme_path, last_updated_path) is False


def test_check_false_when_readme_missing(tmp_path):
    import yaml

    entries_path = tmp_path / "entries.yaml"
    readme_path = tmp_path / "README.md"
    last_updated_path = tmp_path / "last-updated.json"
    entries_path.write_text(yaml.safe_dump(MINIMAL), encoding="utf-8")

    assert check(entries_path, readme_path, last_updated_path) is False
