<div align="center">

<img src="app/src-tauri/icons/icon.png" width="120" height="120" alt="markitdown-postproc logo" />

<h1 align="center">markitdown-postproc</h1>

**Drop a file. Get clean Markdown.**

A fork of [microsoft/markitdown](https://github.com/microsoft/markitdown) that ships an offline post-processing pipeline — syntax repair, table normalization, and opt-in boilerplate stripping — plus a Python library, CLI, a standalone Windows `.exe`, and a native desktop app for Windows / macOS / Linux.

[![License: MIT](https://img.shields.io/badge/license-MIT-ff7a59.svg?style=flat-square)](LICENSE)
[![PyPI](https://img.shields.io/badge/pypi-markitdown--postproc-7ee787.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/markitdown-postproc/)
[![Build desktop](https://img.shields.io/github/actions/workflow/status/hasnain7abbas/markitdown/build-desktop.yml?style=flat-square&label=desktop&logo=tauri)](https://github.com/hasnain7abbas/markitdown/actions/workflows/build-desktop.yml)
[![Build .exe](https://img.shields.io/github/actions/workflow/status/hasnain7abbas/markitdown/build-exe.yml?style=flat-square&label=.exe&logo=windows)](https://github.com/hasnain7abbas/markitdown/actions/workflows/build-exe.yml)
[![Pages](https://img.shields.io/github/actions/workflow/status/hasnain7abbas/markitdown/pages.yml?style=flat-square&label=pages&logo=githubpages)](https://hasnain7abbas.github.io/markitdown/)
[![Stars](https://img.shields.io/github/stars/hasnain7abbas/markitdown?style=flat-square&logo=github&color=ffd166)](https://github.com/hasnain7abbas/markitdown/stargazers)

<p>
  <a href="https://hasnain7abbas.github.io/markitdown/"><b>🌐 Website</b></a> &nbsp;·&nbsp;
  <a href="https://github.com/hasnain7abbas/markitdown/releases/latest"><b>⬇️ Download</b></a> &nbsp;·&nbsp;
  <a href="https://pypi.org/project/markitdown-postproc/"><b>🐍 pip install</b></a> &nbsp;·&nbsp;
  <a href="https://github.com/hasnain7abbas/markitdown/issues/new"><b>🐞 Report Bug</b></a> &nbsp;·&nbsp;
  <a href="https://github.com/microsoft/markitdown"><b>📤 Upstream</b></a>
</p>

[English](./README.md) ·  [中文 (placeholder)](./README.md)

</div>

---

<div align="center">

```text
┌─ markitdown ──────────────────────────────────────────────────┐
│                                                               │
│   ╔════════════════════════════════════════╗                  │
│   ║                                        ║                  │
│   ║     Drag & drop a file here, or        ║                  │
│   ║              [ Browse ]                ║                  │
│   ║                                        ║                  │
│   ║   PDF · DOCX · XLSX · PPTX · HTML      ║                  │
│   ║         images · audio · txt           ║                  │
│   ║                                        ║                  │
│   ╚════════════════════════════════════════╝                  │
│                                                               │
│   ☑ Strip boilerplate (page #s, headers, legal)               │
│                                                               │
│   ─── Result ─────────────────────  [Copy]  [Save as .md]     │
│   # Q4 Financial Report                                       │
│                                                               │
│   | Region | Revenue | YoY |                                  │
│   | ---    | ---     | --- |                                  │
│   | EMEA   | $12.4M  | +8% |                                  │
│   | APAC   | $9.1M   | +14%|                                  │
│   ...                                                         │
└───────────────────────────────────────────────────────────────┘
```

</div>

## 📚 Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [🖥️ Desktop App](#️-desktop-app)
- [📦 Standalone `.exe`](#-standalone-exe)
- [🛠️ The Post-Processing Pipeline](#️-the-post-processing-pipeline)
- [🔨 Build From Source](#-build-from-source)
- [🧪 Testing](#-testing)
- [🗺️ Project Layout](#️-project-layout)
- [🚢 Release Flow](#-release-flow)
- [🙏 Acknowledgements](#-acknowledgements)
- [📜 License](#-license)

---

## ✨ Features

- 🧼 **Auto-clean Markdown.** Every conversion is post-processed offline: unclosed `**bold**` / `_italic_` runs are closed, headings get their missing space, broken links are repaired, trailing whitespace is trimmed, and blank-line runs are collapsed.
- 📊 **Bullet-proof tables.** Ragged rows are padded, a separator row is guaranteed, duplicate headers are dropped, in-cell whitespace is trimmed, and merged cells are tagged with `[merged]` instead of vanishing.
- 🪒 **Opt-in boilerplate stripping.** A single `strip_boilerplate=True` flag (or the `--strip-boilerplate` CLI switch / `MARKITDOWN_STRIP_BOILERPLATE=1` env var) removes page numbers, headers/footers that repeat 3+ times, legal noise ("All rights reserved", "Confidential"), and punctuation-only lines.
- 🔌 **Drop-in compatible.** Import name stays `markitdown`. All upstream `convert_*` calls return identical-shape `DocumentConverterResult` objects — just cleaner. Existing scripts work unchanged.
- 🦀 **Native desktop app.** A Tauri 2 GUI: drag-and-drop a file, toggle stripping, copy or save as `.md`. Bundles to `.msi`, NSIS `.exe`, `.dmg`, `.deb`, and `.AppImage`.
- 📦 **Single-file Windows binary.** PyInstaller build produces one `markitdown.exe` (no Python required on the user's machine) with `[all]` extras bundled so PDF, DOCX, XLSX, PPTX, audio and YouTube all work out of the box.
- 🌐 **Static docs site.** Auto-deploys to GitHub Pages from `docs/` — landing page, install instructions, feature breakdown.
- ⚡ **Fully offline.** No external APIs, no telemetry, no network calls from the post-processor. What runs on your machine, stays on your machine.
- 🤖 **Automated release pipeline.** Tag `vX.Y.Z` → GitHub Actions builds the Python wheel, publishes to PyPI via Trusted Publishing, builds `markitdown.exe`, builds desktop installers on Windows/macOS/Linux, and attaches everything to a draft GitHub Release. Zero manual steps.

## 🚀 Quick Start

### 🐍 As a Python library

```bash
pip install markitdown-postproc
```

```python
from markitdown import MarkItDown

# default behavior — post-processing always on, boilerplate stripping off
md = MarkItDown()
result = md.convert("report.pdf")
print(result.markdown)

# turn on boilerplate stripping
md = MarkItDown(strip_boilerplate=True)
print(md.convert("messy_scan.pdf").markdown)
```

### 💻 As a CLI

```bash
# convert a file
markitdown example.pdf -o example.md

# or pipe via stdin
cat example.pdf | markitdown > example.md

# enable boilerplate stripping
markitdown report.pdf --strip-boilerplate -o report.md

# env-var equivalent (handy for scripts and the desktop app)
MARKITDOWN_STRIP_BOILERPLATE=1 markitdown report.pdf
```

### 🪟 As a one-file Windows `.exe`

Grab `markitdown.exe` from the latest [Release](https://github.com/hasnain7abbas/markitdown/releases/latest) — no Python install needed.

```bat
markitdown.exe report.pdf > report.md
```

## 🖥️ Desktop App

A native cross-platform GUI lives in [`app/`](app/) — built with [Tauri 2](https://tauri.app), vanilla JS + Vite frontend, Rust backend.

```text
Drag & drop  →  pick a file  →  ☑ strip boilerplate  →  Copy / Save .md
```

Installers are built on every push to `main` and attached to GitHub Releases on tag push:

| Platform | Installer |
| --- | --- |
| 🪟 Windows | `.msi` (WiX) · `.exe` (NSIS) |
| 🍎 macOS  | `.dmg` · `.app` (universal: Intel + Apple Silicon) |
| 🐧 Linux  | `.deb` · `.AppImage` |

Run locally:

```bash
cd app
npm install
npm run tauri dev      # development
npm run tauri build    # produces installers under src-tauri/target/release/bundle/
```

**Note:** the desktop app shells out to the `markitdown` CLI, so install the Python package (or drop `markitdown.exe` on PATH) before running.

## 📦 Standalone `.exe`

Built by [`.github/workflows/build-exe.yml`](.github/workflows/build-exe.yml) on every push to `main`. The PyInstaller spec at [`packaging/markitdown.spec`](packaging/markitdown.spec) bundles:

- 🐍 The full Python runtime
- 🔧 `markitdown[all]` extras (PDF, DOCX, XLSX, PPTX, audio, YouTube)
- 🧠 The `magika` ONNX model + JSON config
- 🚫 Excludes heavy ML and Azure SDKs to keep the binary slim

Build locally on Windows:

```powershell
pip install -e "packages/markitdown[all]"
pip install pyinstaller
cd packaging
pyinstaller --clean --noconfirm markitdown.spec
./dist/markitdown.exe --help
```

## 🛠️ The Post-Processing Pipeline

Lives in [`packages/markitdown/src/markitdown/postprocessor.py`](packages/markitdown/src/markitdown/postprocessor.py) and runs at the end of every `MarkItDown._convert()` call — automatically.

```text
raw converter output
   │
   ├─▶ 📊 fix_markdown_tables()    pad ragged rows · guarantee separator
   │                               · drop dup headers · mark merged cells
   │
   ├─▶ 🧼 fix_broken_markdown()    close **bold** / _italic_ · `##X → ## X`
   │                               · close [text](url · collapse blank runs
   │                               · strip trailing whitespace
   │
   ├─▶ 🪒 strip_boilerplate()      (only if strip_boilerplate=True)
   │                               page #s · 3x-repeated headers/footers
   │                               · legal boilerplate · punct-only lines
   │
   ▼
final Markdown — clean, structurally sound, table-safe
```

| Function | When it runs | What it fixes |
| --- | --- | --- |
| `fix_markdown_tables` | always | ragged rows, missing separator, duplicate header, merged cells (`[merged]`), in-cell whitespace |
| `fix_broken_markdown` | always | unclosed `**bold**` / `_italic_`, `##Heading`, broken links, trailing whitespace, blank-line runs |
| `strip_boilerplate` | opt-in | page numbers, repeated headers/footers, legal boilerplate, punctuation-only lines (table separators preserved) |

## 🔨 Build From Source

```bash
git clone https://github.com/hasnain7abbas/markitdown.git
cd markitdown
pip install -e "packages/markitdown[all]"
```

Optional extras you can install individually if you don't want the whole world:

```bash
pip install -e "packages/markitdown[pdf]"
pip install -e "packages/markitdown[docx]"
pip install -e "packages/markitdown[xlsx]"
pip install -e "packages/markitdown[pptx]"
pip install -e "packages/markitdown[audio-transcription]"
```

## 🧪 Testing

```bash
pytest packages/markitdown/tests/test_postprocessor.py -v
```

30 cases cover every fix rule (positive + negative), the table repair logic, boilerplate detection, and pipeline integration. The full upstream test suite also runs unchanged on supported Python versions (3.10 – 3.13).

## 🗺️ Project Layout

```text
markitdown/
├── 📁 packages/markitdown/      # Python package (library + CLI)
│   ├── src/markitdown/
│   │   ├── postprocessor.py     # 🆕 the three improvements
│   │   ├── _markitdown.py       # _convert() wires the pipeline in
│   │   ├── __main__.py          # CLI — adds --strip-boilerplate flag
│   │   └── converters/          # upstream converters (PDF, DOCX, ...)
│   └── tests/test_postprocessor.py  # 30 tests, all green
│
├── 📁 packaging/                # PyInstaller spec → markitdown.exe
│
├── 📁 app/                      # Tauri 2 desktop GUI
│   ├── src/                     # Vanilla JS + Vite frontend
│   ├── src-tauri/               # Rust backend + Cargo.toml
│   └── scripts/gen_icons.py     # icon generator
│
├── 📁 docs/                     # GitHub Pages static site
│
└── 📁 .github/workflows/
    ├── publish-pypi.yml         # 📦 sdist + wheel → PyPI on v* tag
    ├── build-exe.yml            # 🪟 markitdown.exe on every push to main
    ├── build-desktop.yml        # 🦀 .msi/.exe/.dmg/.deb/.AppImage
    └── pages.yml                # 🌐 deploy docs/ to GitHub Pages
```

## 🚢 Release Flow

```text
git tag v0.1.6-postproc.1
git push origin --tags
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│  GitHub Actions kicks off four pipelines in parallel:     │
│                                                          │
│   📦 publish-pypi.yml   →  PyPI (Trusted Publishing)     │
│   🪟 build-exe.yml      →  markitdown.exe attached       │
│   🦀 build-desktop.yml  →  .msi/.exe/.dmg/.deb/AppImage  │
│   🌐 pages.yml          →  docs site refreshed           │
│                                                          │
│  → draft GitHub Release with every artifact attached     │
└──────────────────────────────────────────────────────────┘
```

One-time setup:

- 📦 Register a PyPI Trusted Publisher at <https://pypi.org/manage/account/publishing/> pointing at this repo + `publish-pypi.yml` + environment `pypi`.
- 🌐 Pages is already enabled (workflow source) — site at <https://hasnain7abbas.github.io/markitdown/>.

## 🙏 Acknowledgements

- 🪟 [microsoft/markitdown](https://github.com/microsoft/markitdown) — the original project, by Adam Fourney and the AutoGen team. This fork stands on their shoulders; see [`README-upstream.md`](README-upstream.md) for their original docs.
- 🦀 [Tauri](https://tauri.app/) — for the tiny, fast, native desktop runtime.
- 🐍 [PyInstaller](https://pyinstaller.org/) — for the standalone Windows binary.
- 🎨 The icon set in [`app/src-tauri/icons/`](app/src-tauri/icons/) is generated by [`app/scripts/gen_icons.py`](app/scripts/gen_icons.py).

## 📜 License

[MIT](./LICENSE). Original copyright © Microsoft Corporation retained. Fork improvements © 2026 hasnain7abbas, also under MIT.

<div align="center">

— if this saved you an hour wrestling with broken Markdown, drop a ⭐ on the repo —

</div>
