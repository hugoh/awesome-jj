import json

import yaml
from test_generate import MINIMAL

from awesome_jj_tools.last_updated import LastUpdatedSnapshot, save_snapshot
from awesome_jj_tools.site import export_site_data, site_data


def pages_by_filename(updated_at="2026-01-01"):
    return {p["filename"]: p for p in site_data(MINIMAL, updated_at)["pages"]}


def test_one_page_per_section_and_tools_subsection():
    pages = pages_by_filename()
    assert "index.html" in pages
    assert "books.html" in pages
    assert "official-resources.html" in pages
    assert "tools-gui.html" in pages
    assert "tools-misc-tools.html" in pages
    # 7 non-Tools top-level sections + 1 Tools hub + 9 Tools subsections
    assert len(pages) == 17


def test_site_level_fields():
    data = site_data(MINIMAL, "2026-01-01")
    assert data["title"] == "Awesome JJ"
    assert data["updated_at"] == "2026-01-01"
    assert data["url"].startswith("https://")


def test_index_page_title_is_bare_site_title():
    assert pages_by_filename()["index.html"]["page_title"] == "Awesome JJ"


def test_non_index_page_title_includes_section():
    assert pages_by_filename()["books.html"]["page_title"] == "Books — Awesome JJ"


def test_tools_nav_only_on_tools_pages():
    pages = pages_by_filename()
    assert pages["index.html"]["tools_nav"]
    assert pages["tools-gui.html"]["tools_nav"]
    assert pages["books.html"]["tools_nav"] == []


def test_description_markdown_rendered_to_html():
    data = {
        "official_resources": [
            {
                "name": "X",
                "url": "https://example.com",
                "description": "See [docs](https://example.com/d) & `code` <b>.",
            }
        ]
    }
    entry = site_data(data, "")["pages"][0]["section"]["entries"][0]
    html = entry["description_html"]
    assert '<a href="https://example.com/d">docs</a>' in html
    assert "<code>code</code>" in html
    assert "&amp;" in html
    assert "<b>" not in html


def test_entry_without_description_has_empty_html():
    entry = pages_by_filename()["official-resources.html"]["section"]["entries"][0]
    assert entry["description_html"] == ""


def test_hub_lists_every_tool_under_its_subsection():
    hub = pages_by_filename()["index.html"]["section"]
    assert hub["kind"] == "tools"
    assert [s["title"] for s in hub["subsections"]]
    assert sum(len(s["entries"]) for s in hub["subsections"]) > 0


def test_export_writes_json_with_recorded_date(tmp_path):
    entries_path = tmp_path / "entries.yaml"
    last_updated_path = tmp_path / "last-updated.json"
    output = tmp_path / "out" / "site.json"
    entries_path.write_text(yaml.safe_dump(MINIMAL), encoding="utf-8")
    save_snapshot(LastUpdatedSnapshot(hash="irrelevant", date="2026-08-09"), last_updated_path)

    export_site_data(output, entries_path, last_updated_path)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["updated_at"] == "2026-08-09"
    assert len(payload["pages"]) == 17


def test_export_uses_empty_date_when_no_snapshot_exists(tmp_path):
    entries_path = tmp_path / "entries.yaml"
    output = tmp_path / "site.json"
    entries_path.write_text(yaml.safe_dump(MINIMAL), encoding="utf-8")

    export_site_data(output, entries_path, tmp_path / "does-not-exist.json")

    assert json.loads(output.read_text(encoding="utf-8"))["updated_at"] == ""
