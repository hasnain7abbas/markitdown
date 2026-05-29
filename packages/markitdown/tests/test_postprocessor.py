#!/usr/bin/env python3 -m pytest
"""Tests for the offline Markdown post-processor.

Covers the three improvements:
  1. fix_broken_markdown  -- syntax repair
  2. strip_boilerplate    -- noise removal (opt-in)
  3. fix_markdown_tables  -- table normalization
"""

from markitdown.postprocessor import (
    fix_broken_markdown,
    fix_markdown_tables,
    strip_boilerplate,
)


# ---------------------------------------------------------------------------
# Improvement 1 -- fix_broken_markdown
# ---------------------------------------------------------------------------


def test_heading_missing_space_is_fixed():
    assert fix_broken_markdown("##Title") == "## Title"
    assert fix_broken_markdown("###Sub heading") == "### Sub heading"


def test_well_formed_heading_is_untouched():
    assert fix_broken_markdown("## Title") == "## Title"


def test_unclosed_bold_is_closed():
    assert fix_broken_markdown("This is **bold text") == "This is **bold text**"


def test_balanced_bold_is_untouched():
    assert fix_broken_markdown("This is **bold** text") == "This is **bold** text"


def test_unclosed_italic_is_closed():
    assert fix_broken_markdown("an _italic word") == "an _italic word_"


def test_snake_case_underscores_are_not_treated_as_italic():
    text = "use the my_function_name helper"
    assert fix_broken_markdown(text) == text


def test_broken_link_is_closed():
    assert (
        fix_broken_markdown("see [docs](http://example.com")
        == "see [docs](http://example.com)"
    )


def test_complete_link_is_untouched():
    text = "see [docs](http://example.com)"
    assert fix_broken_markdown(text) == text


def test_consecutive_blank_lines_collapse_to_two():
    text = "a\n\n\n\n\nb"
    assert fix_broken_markdown(text) == "a\n\nb"


def test_two_blank_lines_are_preserved():
    text = "a\n\nb"
    assert fix_broken_markdown(text) == "a\n\nb"


def test_trailing_whitespace_is_stripped():
    assert fix_broken_markdown("hello   \nworld\t") == "hello\nworld"


def test_empty_input_returns_empty():
    assert fix_broken_markdown("") == ""


# ---------------------------------------------------------------------------
# Improvement 3 -- fix_markdown_tables
# ---------------------------------------------------------------------------


def test_missing_separator_row_is_added():
    text = "| A | B |\n| 1 | 2 |"
    out = fix_markdown_tables(text)
    lines = out.split("\n")
    assert lines[0] == "| A | B |"
    assert lines[1] == "| --- | --- |"
    assert lines[2] == "| 1 | 2 |"


def test_existing_separator_is_preserved_once():
    text = "| A | B |\n| --- | --- |\n| 1 | 2 |"
    out = fix_markdown_tables(text)
    assert out.split("\n").count("| --- | --- |") == 1


def test_short_rows_are_padded_to_column_count():
    text = "| A | B | C |\n| --- | --- | --- |\n| 1 | 2 |"
    out = fix_markdown_tables(text)
    last = out.split("\n")[-1]
    # Three columns -> two interior pipes plus the bounding pipes.
    assert last == "| 1 | 2 |  |"


def test_excess_whitespace_inside_cells_is_trimmed():
    text = "|   A    |   B   |\n| --- | --- |\n|   1   |   2   |"
    out = fix_markdown_tables(text)
    assert out.split("\n")[0] == "| A | B |"
    assert out.split("\n")[2] == "| 1 | 2 |"


def test_duplicate_header_rows_are_removed():
    text = "| A | B |\n| --- | --- |\n| A | B |\n| 1 | 2 |"
    out = fix_markdown_tables(text)
    # The header should appear only once (in position 0).
    assert out.split("\n").count("| A | B |") == 1


def test_merged_interior_cell_gets_placeholder():
    # Middle cell is empty but a later cell has content -> merged.
    text = "| A | B | C |\n| --- | --- | --- |\n| 1 |  | 3 |"
    out = fix_markdown_tables(text)
    assert "[merged]" in out


def test_malformed_table_full_repair():
    # No separator, ragged columns, extra whitespace, duplicate header.
    text = "|  A  | B |  C  |\n| A | B | C |\n|  1  | 2 |"
    out = fix_markdown_tables(text)
    lines = out.split("\n")
    assert lines[0] == "| A | B | C |"
    assert lines[1] == "| --- | --- | --- |"
    # Duplicate header removed; only the data row remains, padded to 3 cols.
    assert lines[2] == "| 1 | 2 |  |"
    assert len(lines) == 3


def test_non_table_text_is_untouched():
    text = "Just a paragraph.\nAnother line."
    assert fix_markdown_tables(text) == text


# ---------------------------------------------------------------------------
# Improvement 2 -- strip_boilerplate
# ---------------------------------------------------------------------------


def test_bare_page_number_line_is_removed():
    text = "Real content\n42\nMore content"
    out = strip_boilerplate(text)
    assert "42" not in out.split("\n")
    assert "Real content" in out
    assert "More content" in out


def test_page_label_lines_are_removed():
    text = "Body\nPage 2\n- 3 -\nPage 2 of 10\nMore"
    out = strip_boilerplate(text).split("\n")
    assert "Page 2" not in out
    assert "- 3 -" not in out
    assert "Page 2 of 10" not in out


def test_repeated_header_three_times_is_removed():
    header = "ACME CORP CONFIDENTIAL REPORT"
    text = "\n".join(
        [header, "intro", header, "middle", header, "conclusion"]
    )
    out = strip_boilerplate(text)
    assert header not in out.split("\n")
    assert "intro" in out
    assert "conclusion" in out


def test_header_repeated_only_twice_is_kept():
    header = "Section Title"
    text = "\n".join([header, "a", header, "b"])
    out = strip_boilerplate(text)
    # Appears fewer than 3 times, so it should be preserved.
    assert out.split("\n").count(header) == 2


def test_legal_boilerplate_is_removed():
    text = "Important text\nAll Rights Reserved\nConfidential\nKeep this"
    out = strip_boilerplate(text).split("\n")
    assert "All Rights Reserved" not in out
    assert "Confidential" not in out
    assert "Important text" in out
    assert "Keep this" in out


def test_punctuation_only_line_is_removed():
    text = "content\n=======\n****\nmore content"
    out = strip_boilerplate(text).split("\n")
    assert "=======" not in out
    assert "****" not in out
    assert "content" in out


def test_normal_content_is_preserved():
    text = "# Heading\n\nA normal paragraph with words.\n\n- a list item"
    out = strip_boilerplate(text)
    assert "# Heading" in out
    assert "A normal paragraph with words." in out
    assert "- a list item" in out


def test_strip_boilerplate_empty_input():
    assert strip_boilerplate("") == ""


def test_strip_boilerplate_preserves_table_separator_row():
    # A separator row is punctuation-only but is structural and must survive.
    text = "| A | B |\n| --- | --- |\n| 1 | 2 |"
    out = strip_boilerplate(text)
    assert "| --- | --- |" in out.split("\n")


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------


def test_fix_broken_markdown_runs_table_fix_internally():
    # A broken table plus a broken heading should both be repaired by the
    # single fix_broken_markdown entry point.
    text = "##Report\n\n| A | B |\n| 1 | 2 |"
    out = fix_broken_markdown(text)
    assert "## Report" in out
    assert "| --- | --- |" in out
