# MarkItDown Improvements — Claude Code Instructions

## Context
This is a fork of [microsoft/markitdown](https://github.com/microsoft/markitdown) — a Python tool that converts files and office documents to Markdown.
We are adding 3 targeted improvements on top of the existing codebase without breaking any existing functionality.

---

## Setup
```bash
git clone https://github.com/microsoft/markitdown.git
cd markitdown
pip install -e 'packages/markitdown[all]'
```

---

## Improvement 1 — Detect & Fix Broken Markdown

### Goal
After conversion, automatically scan and repair common Markdown syntax issues.

### What to fix
- Unclosed `**bold**` or `_italic_` spans
- Headings missing a space after `#` (e.g. `##Title` → `## Title`)
- Broken links `[text](` with no closing `)`
- Consecutive blank lines (collapse to max 2)
- Trailing whitespace on every line

### Where to add it
- Create a new file: `packages/markitdown/src/markitdown/postprocessor.py`
- Add a function: `fix_broken_markdown(text: str) -> str`
- Call it at the end of every `convert_*` method in `_markitdown.py` before returning the result

### Tests
- Add `tests/test_postprocessor.py`
- Cover each fix rule with at least one passing and one failing case

---

## Improvement 2 — Strip Boilerplate & Noise Content

### Goal
Remove repetitive, low-value content that pollutes Markdown output — especially from PDFs and DOCX files.

### What to strip
- Page numbers (e.g. lines that are just `1`, `Page 2`, `- 3 -`)
- Repeated headers/footers (detect lines that appear 3+ times across the document)
- Common legal boilerplate patterns (e.g. "All rights reserved", "Confidential")
- Lines that are only whitespace or punctuation

### Where to add it
- Add a function `strip_boilerplate(text: str) -> str` inside `postprocessor.py`
- Make it **opt-in** via a flag: `MarkItDown(strip_boilerplate=True)`
- Wire the flag through `_markitdown.py`

### Tests
- Add test cases in `tests/test_postprocessor.py`
- Use a sample string with fake repeated headers and page numbers

---

## Improvement 3 — Preserve Table Formatting Accuracy

### Goal
Fix misaligned or broken Markdown tables that result from converted XLSX, DOCX, or PDF files.

### What to fix
- Ensure every row has the same number of columns (pad missing cells with empty string)
- Ensure separator row (`| --- | --- |`) is always present after the header
- Remove duplicate header rows
- Trim excess whitespace inside cells
- Handle merged cells gracefully (fill with `[merged]` placeholder)

### Where to add it
- Add a function `fix_markdown_tables(text: str) -> str` inside `postprocessor.py`
- Use regex to locate Markdown table blocks, then reformat each one
- Call this inside `fix_broken_markdown()` so it runs as part of the same pipeline

### Tests
- Add test cases in `tests/test_postprocessor.py`
- Include a malformed table with missing cells, no separator row, and extra whitespace

---

## Pipeline Order
All three improvements should run in this order at the end of every conversion:

```
raw output
   → fix_markdown_tables()
   → fix_broken_markdown()
   → strip_boilerplate()  ← only if flag is set
   → return final markdown
```

---

## PR Checklist (before pushing)
- [ ] All existing tests still pass (`pytest`)
- [ ] New tests added and passing
- [ ] No external API calls — fully offline
- [ ] `strip_boilerplate` defaults to `False` (non-breaking)
- [ ] Update `README.md` with new flag and postprocessor mention

---

## Attribution
Fork of [microsoft/markitdown](https://github.com/microsoft/markitdown) — MIT License.
Original copyright retained. Improvements authored separately.
