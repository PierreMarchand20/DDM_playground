# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ddm_playground"
copyright = "2025, Pierre Marchand"
author = "Pierre Marchand"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # automatically document docstrings
    "sphinx.ext.napoleon",  # Google/NumPy style docstrings
    "sphinx_autodoc_typehints",  # shows type hints
]


sys.path.insert(0, os.path.abspath("../src"))

templates_path = ["_templates"]
exclude_patterns = []

# Avoid duplicate index entries when documenting classes multiple times
# Use :noindex: for repeated references
napoleon_include_private_with_doc = False
napoleon_numpy_docstring = True
napoleon_google_docstring = False


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
