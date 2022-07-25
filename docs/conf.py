"""Sphinx configuration."""
project = "Python SHT4X"
author = "Christopher Johnson"
copyright = "2022, Christopher Johnson"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
