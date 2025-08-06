# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import pathlib
sys.path.insert(0, os.path.abspath('..'))

here = pathlib.Path(__file__).parent.resolve()
about = {}
version_file = here.parent / "DashML" / "__version__.py"
exec(version_file.read_text(), about)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'DashingTurtle'
copyright = '2025, J. White Bear'
author = 'J. White Bear'
version = release = about["__version__"]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",   # For Google/NumPy docstrings
    "sphinx.ext.viewcode",
]
html_theme = "furo"
templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
