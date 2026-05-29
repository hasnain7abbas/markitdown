"""Post-processing utilities for cleaning up converted Markdown.

These functions run offline (no network access) on the raw Markdown produced
by a converter, repairing common syntax issues, optionally stripping low-value
boilerplate, and normalizing tables.

Pipeline order (see ``fix_broken_markdown``)::

    raw output
       -> fix_markdown_tables()
       -> fix_broken_markdown()
       -> strip_boilerplate()   # only if explicitly requested
       -> final markdown
"""

import re
from collections import Counter
from typing import List

__all__ = [
    "fix_broken_markdown",
    "fix_markdown_tables",
    "strip_boilerplate",
]


# ---------------------------------------------------------------------------
# Improvement 3 — Table formatting accuracy
# ---------------------------------------------------------------------------

_SEPARATOR_CELL_RE = re.compile(r"^\s*:?-{1,}:?\s*$")


def _split_table_row(line: str) -> List[str]:
    """Split a single Markdown table row into its cell values.

    Leading/trailing pipes are treated as delimiters (not empty cells), and
    escaped pipes (``\\|``) inside cells are preserved.
    """
    # Temporarily protect escaped pipes so we don't split on them.
    placeholder = "\x00PIPE\x00"
    protected = line.replace("\\|", placeholder)

    stripped = protected.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]

    cells = stripped.split("|")
    return [c.replace(placeholder, "\\|").strip() for c in cells]


def _is_separator_row(cells: List[str]) -> bool:
    """Return True if every cell looks like a table separator (e.g. ``---``)."""
    if not cells:
        return False
    return all(_SEPARATOR_CELL_RE.match(c) for c in cells)


def _looks_like_table_row(line: str) -> bool:
    """A table row contains at least one pipe that is not escaped."""
    stripped = line.strip()
    if not stripped:
        return False
    # Remove escaped pipes before checking for a delimiter pipe.
    return "|" in stripped.replace("\\|", "")


def _format_table_block(rows: List[str]) -> List[str]:
    """Reformat a contiguous block of table rows into a clean Markdown table."""
    parsed: List[List[str]] = []
    has_separator = False

    for row in rows:
        cells = _split_table_row(row)
        if _is_separator_row(cells):
            has_separator = True
            continue
        parsed.append(cells)

    if not parsed:
        return rows  # Nothing usable; leave it untouched.

    # Handle merged cells: an empty cell that follows a non-empty one in the
    # same row is treated as a merged continuation and filled with a marker.
    for cells in parsed:
        for i in range(1, len(cells)):
            if cells[i] == "" and cells[i - 1] != "":
                # Only mark as merged if a later cell in the row has content,
                # otherwise it is just a trailing empty cell (padding).
                if any(c != "" for c in cells[i + 1 :]):
                    cells[i] = "[merged]"

    # Determine the column count from the widest row and pad the rest.
    num_cols = max(len(cells) for cells in parsed)
    for cells in parsed:
        while len(cells) < num_cols:
            cells.append("")

    # Remove duplicate header rows (rows identical to the header).
    header = parsed[0]
    body = [row for row in parsed[1:] if row != header]

    # Rebuild the table with a guaranteed separator row.
    out: List[str] = []
    out.append("| " + " | ".join(header) + " |")
    out.append("| " + " | ".join(["---"] * num_cols) + " |")
    for row in body:
        out.append("| " + " | ".join(row) + " |")

    _ = has_separator  # Computed for clarity; separator is always re-emitted.
    return out


def fix_markdown_tables(text: str) -> str:
    """Repair misaligned or broken Markdown tables.

    - Pads short rows so every row has the same number of columns.
    - Ensures a separator row (``| --- | --- |``) follows the header.
    - Removes duplicate header rows.
    - Trims excess whitespace inside cells.
    - Replaces merged (empty interior) cells with a ``[merged]`` placeholder.
    """
    if not text:
        return text

    lines = text.split("\n")
    out: List[str] = []
    block: List[str] = []

    def flush() -> None:
        if block:
            out.extend(_format_table_block(block))
            block.clear()

    for line in lines:
        if _looks_like_table_row(line):
            block.append(line)
        else:
            flush()
            out.append(line)
    flush()

    return "\n".join(out)


# ---------------------------------------------------------------------------
# Improvement 1 — Detect & fix broken Markdown
# ---------------------------------------------------------------------------

_HEADING_NO_SPACE_RE = re.compile(r"^(#{1,6})([^#\s].*)$")
_BROKEN_LINK_RE = re.compile(r"(\[[^\]]*\]\([^)\n]*?)(?=\n|$)")


def _fix_heading_spacing(line: str) -> str:
    """Insert a space after the leading ``#`` run of a heading if missing."""
    m = _HEADING_NO_SPACE_RE.match(line)
    if m:
        return f"{m.group(1)} {m.group(2)}"
    return line


def _fix_broken_links(line: str) -> str:
    """Close link targets that are missing their trailing ``)``.

    Matches ``[text](url`` with no closing paren before end of line and
    appends the missing ``)``.
    """

    def repl(m: re.Match) -> str:
        fragment = m.group(1)
        if ")" in fragment:  # Already balanced somewhere; leave alone.
            return fragment
        return fragment + ")"

    return _BROKEN_LINK_RE.sub(repl, line)


def _balance_inline_marker(line: str, marker: str) -> str:
    """If a line has an odd number of ``marker`` runs, append a closing marker.

    Handles ``**bold**`` and ``_italic_`` style spans on a per-line basis.
    """
    # Count standalone occurrences of the marker.
    count = line.count(marker)
    if marker == "_":
        # Avoid counting underscores inside words (snake_case); only count
        # underscores at a word boundary.
        count = len(re.findall(r"(?<![A-Za-z0-9_])_|_(?![A-Za-z0-9_])", line))
        if count % 2 == 1:
            return line + "_"
        return line

    if count % 2 == 1:
        return line + marker
    return line


def fix_broken_markdown(text: str) -> str:
    """Scan and repair common Markdown syntax issues.

    Repairs performed:
    - Runs :func:`fix_markdown_tables` first (per the pipeline contract).
    - Adds a space after ``#`` in headings missing one (``##Title`` -> ``## Title``).
    - Closes broken links ``[text](url`` by appending ``)``.
    - Balances unclosed ``**bold**`` and ``_italic_`` spans per line.
    - Strips trailing whitespace from every line.
    - Collapses 3+ consecutive blank lines down to 2.
    """
    if not text:
        return text

    # Tables first, as mandated by the pipeline order.
    text = fix_markdown_tables(text)

    fixed_lines: List[str] = []
    for raw_line in text.split("\n"):
        line = _fix_heading_spacing(raw_line)
        line = _fix_broken_links(line)
        line = _balance_inline_marker(line, "**")
        line = _balance_inline_marker(line, "_")
        line = line.rstrip()
        fixed_lines.append(line)

    result = "\n".join(fixed_lines)

    # Collapse runs of 3+ blank lines into exactly 2 (one empty line between).
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result


# ---------------------------------------------------------------------------
# Improvement 2 — Strip boilerplate & noise
# ---------------------------------------------------------------------------

_PAGE_NUMBER_RES = [
    re.compile(r"^\s*\d+\s*$"),               # bare number:        42
    re.compile(r"^\s*[Pp]age\s+\d+\s*$"),     # "Page 2"
    re.compile(r"^\s*[Pp]age\s+\d+\s+of\s+\d+\s*$"),  # "Page 2 of 10"
    re.compile(r"^\s*-\s*\d+\s*-\s*$"),       # "- 3 -"
]

_BOILERPLATE_RES = [
    re.compile(r"all rights reserved", re.IGNORECASE),
    re.compile(r"\bconfidential\b", re.IGNORECASE),
    re.compile(r"\bproprietary\b", re.IGNORECASE),
    re.compile(r"\bdo not distribute\b", re.IGNORECASE),
]

# A line that is only whitespace and/or punctuation (no letters or digits).
_PUNCT_ONLY_RE = re.compile(r"^[\s\W_]*$", re.UNICODE)
_ALNUM_RE = re.compile(r"[A-Za-z0-9]")


def _is_page_number(line: str) -> bool:
    return any(r.match(line) for r in _PAGE_NUMBER_RES)


def _is_boilerplate(line: str) -> bool:
    return any(r.search(line) for r in _BOILERPLATE_RES)


def _is_punct_only(line: str) -> bool:
    """True if the line has no alphanumeric characters (whitespace/punct only)."""
    if line.strip() == "":
        return False  # Preserve blank lines; handled elsewhere.
    return _ALNUM_RE.search(line) is None


def strip_boilerplate(text: str) -> str:
    """Remove repetitive, low-value content from converted Markdown.

    Opt-in (wired through ``MarkItDown(strip_boilerplate=True)``). Removes:
    - Page-number lines (``1``, ``Page 2``, ``- 3 -``, ``Page 2 of 10``).
    - Headers/footers that repeat 3+ times across the document.
    - Common legal boilerplate ("All rights reserved", "Confidential", ...).
    - Lines containing only whitespace or punctuation.

    Blank lines are preserved here; final blank-line collapsing is left to
    :func:`fix_broken_markdown`.
    """
    if not text:
        return text

    lines = text.split("\n")

    # Identify repeated header/footer lines (appear 3+ times). We only treat
    # non-blank, reasonably short lines as candidate headers/footers so we do
    # not accidentally drop repeated body content.
    counts = Counter(
        ln.strip()
        for ln in lines
        if ln.strip() and len(ln.strip()) <= 80
    )
    repeated = {ln for ln, c in counts.items() if c >= 3}

    out: List[str] = []
    for line in lines:
        stripped = line.strip()

        if stripped == "":
            out.append(line)
            continue
        if _is_page_number(line):
            continue
        if stripped in repeated:
            continue
        if _is_boilerplate(line):
            continue
        # Preserve table rows/separators: a pipe-bearing line is structural and
        # must not be dropped by the punctuation-only rule (e.g. ``| --- | --- |``).
        if "|" not in stripped and _is_punct_only(line):
            continue

        out.append(line)

    return "\n".join(out)
