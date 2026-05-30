"""PyInstaller entry point.

Wraps ``markitdown.__main__:main`` via the package namespace so the relative
imports inside ``__main__.py`` resolve correctly. Running the file directly
(which is what PyInstaller does) would otherwise hit
``ImportError: attempted relative import with no known parent package``.
"""

from markitdown.__main__ import main

if __name__ == "__main__":
    main()
