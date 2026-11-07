from markupsafe import Markup

from awesome_jj_tools.templating import md_inline


def test_none_and_empty_pass_through():
    assert md_inline(None) is None
    assert md_inline("") == ""


def test_link_rendered():
    assert md_inline("See [docs](https://example.com/a).") == (
        'See <a href="https://example.com/a">docs</a>.'
    )


def test_code_and_emphasis_rendered():
    assert md_inline("Run `jj git push` *now*") == "Run <code>jj git push</code> <em>now</em>"


def test_no_wrapping_paragraph():
    assert not str(md_inline("plain")).startswith("<p>")


def test_raw_html_is_escaped():
    out = str(md_inline("<script>alert(1)</script> & more"))
    assert "<script>" not in out
    assert "&lt;script&gt;" in out
    assert "&amp;" in out


def test_link_with_parens_in_url():
    out = str(md_inline("[x](https://en.wikipedia.org/wiki/A_(b))"))
    assert 'href="https://en.wikipedia.org/wiki/A_(b)"' in out


def test_returns_markup_so_jinja_does_not_double_escape():
    assert isinstance(md_inline("a"), Markup)
