from awesome_jj_tools.format import format_markdown


def test_format_markdown_collapses_multiple_blank_lines():
    result = format_markdown("# Title\n\n\n\n- a\n- b\n")
    assert "\n\n\n" not in result


def test_format_markdown_ends_with_single_trailing_newline():
    result = format_markdown("# Title\n\ncontent")
    assert result.endswith("content\n")
    assert not result.endswith("\n\n")
