# PDF documentation for the `krotov` package

This folder contains a PDF documentation of the [krotov Python package][package] for different releases.

For non-released development versions, a PDF of the documentation can be generated from a git checkout of the [`krotov`][package]. Run

    tox -e bootstrap
    tox -e docs -- _build/tex -b latex
    cp docs/krotovscheme.pdf docs/oct_decision_tree.pdf docs/_build/tex/
    tox -e run-cmd -- python docs/build_pdf.py

or simply `make docs-pdf` to create a file `docs/_build/tex/krotov.pdf`.

This assumes that you have `lualatex` (e.g. through [texlive][] on Linux/macOS or [MikTeX][] on Windows). You must also have the [DejaVu fonts][] installed on your system.


[package]: https://github.com/qucontrol/krotov
[texlive]: https://www.tug.org/texlive/
[MikTex]: https://miktex.org
[DejaVu fonts]: https://dejavu-fonts.github.io