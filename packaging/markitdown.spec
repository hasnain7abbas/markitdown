# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for a one-file ``markitdown.exe`` CLI build.

Bundles the full ``[all]`` feature set so the resulting binary can handle
PDF, DOCX, XLSX, PPTX, audio, YouTube, etc. without a Python install on
the target machine.

Usage:
    pyinstaller packaging/markitdown.spec
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules

# Packages we collect fully because PyInstaller's static analysis misses
# their data files, dynamic submodules, or compiled C-extensions.
magika_datas, magika_binaries, magika_hidden = collect_all("magika")
numpy_datas, numpy_binaries, numpy_hidden = collect_all("numpy")
onnx_datas, onnx_binaries, onnx_hidden = collect_all("onnxruntime")

extra_datas = magika_datas + numpy_datas + onnx_datas
extra_binaries = magika_binaries + numpy_binaries + onnx_binaries

hiddenimports = list(set(
    magika_hidden
    + numpy_hidden
    + onnx_hidden
    + collect_submodules("markitdown")
    + collect_submodules("markitdown.converters")
    + collect_submodules("markitdown.converter_utils")
    + [
        # Optional converter backends — listed explicitly so PyInstaller
        # picks them up even though they are imported lazily.
        "pptx",
        "mammoth",
        "pandas",
        "openpyxl",
        "xlrd",
        "lxml",
        "pdfminer",
        "pdfminer.high_level",
        "pdfplumber",
        "olefile",
        "pydub",
        "speech_recognition",
        "youtube_transcript_api",
        "charset_normalizer",
        "defusedxml",
        "markdownify",
        "bs4",
    ]
))

a = Analysis(
    ["runner.py"],
    pathex=["..\\packages\\markitdown\\src"],
    binaries=extra_binaries,
    datas=extra_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # Heavy ML / Azure SDKs we don't need for the CLI build.
        "torch",
        "tensorflow",
        "azure.ai.documentintelligence",
        "azure.ai.contentunderstanding",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="markitdown",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
