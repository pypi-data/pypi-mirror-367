"""Configuration file for the Sphinx documentation builder.

Created from `sphinx-quickstart` template and various existing
HQS repositories.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

**NOTE**: We might move soon to a different framework to (auto-)generate
the API documentation for our Python packages.

Copyright © 2023-2023 HQS Quantum Simulations GmbH. All Rights Reserved.
"""

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = "qoqo-tket"
copyright = "2024, HQS Quantum Simulation GmbH"
author = "The qoqo developers"
description = (
    "Python package provided by HQS to use pytket backend on qoq Circuits and QuantumPrograms."
)
# extract version
try:
    from importlib.metadata import version as version_finder

    version = version_finder(f"{project}")

except Exception:
    version = "0.0.0"

version_tuple = tuple(version.split("."))
main_version = f"{version_tuple[0]}.{version_tuple[1]}"
# The full version, including alpha/beta/rc tags.
release = version
# The short X.Y version.
version = main_version
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "nbsphinx",
]
# automatically use sphinx-autogen
autosummary_generate = True
autosummary_imported_members = False
autoclass_content = "both"
# 'both': class and __init__ docstring are concatenated and inserted
# 'class': only class docstring inserted
# 'init': only init docstring inserted
# This value is a list of autodoc directive flags that should be automatically applied to
# all autodoc directives. The supported flags are 'members', 'undoc-members',
# 'private-members', 'special-members', 'inherited-members', 'show-inheritance',
# 'ignore-module-all' and 'exclude-members'.
# autodoc_default_flags = ['members']
# The default options for autodoc directives. They are applied to all autodoc directives
# automatically. It must be a dictionary which maps option names to the values.
autodoc_default_options = {
    "members": True,
    "special-members": "__init__",
    "private-members": True,
    "inherited-members": True,
    "undoc-members": True,
    "member-order": "bysource",
}
# This value controls the docstrings inheritance. If set to True the docstring for classes
# or methods, if not explicitly set, is inherited form parents.
autodoc_inherit_docstrings = True
# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}
# The master toctree document.
master_doc = "index"
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
# -- Options for HTMLHelp output ------------------------------------------
# Output file base name for HTML help builder.
htmlhelp_basename = f"{project}_doc"
# -- Options for LaTeX output ---------------------------------------------
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'a4paper',
    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '11pt',
    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',
    # Latex figure (float) alignment
    # 'figure_align': 'htbp',
}
# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, f"{project}.tex", f"{project} Documentation", author, "manual"),
]
# -- Options for manual page output ---------------------------------------
# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, f"{project}", f"{project} Documentation", author, 1)]
# -- Options for Texinfo output -------------------------------------------
# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        f"{project}",
        f"{project} Documentation",
        author,
        f"{project}",
        description,
        "Miscellaneous",
    ),
]
# Turning off executing notebooks when adding them to Documentation
nbsphinx_execute = "never"
