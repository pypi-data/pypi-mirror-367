#!/usr/bin/env python3
"""
Sphinx configuration file.
"""

# pylint: disable=invalid-name,redefined-builtin

import importlib
import pathlib
import sys

source_code = "../../src"
git_url = "https://gitlab.inria.fr/tanat/core/tanat"

this_path = pathlib.Path(__file__).resolve()
sys.path.insert(0, str((this_path.parent / source_code).resolve()))

author = "Arnaud Duvermy, Thomas Guyet"
copyright = "2024, Inria"
project = "TanaT"
html_theme = "pydata_sphinx_theme"
html_logo = "static/logo.png"

# Configuration du thème pydata-sphinx-theme - Version épurée
html_theme_options = {
    "logo": {
        "image_light": "static/logo.png",
        "image_dark": "static/logo.png",
    },
    "use_edit_page_button": False,
    "show_toc_level": 2,
    "navbar_align": "left",
    "navbar_center": ["navbar-nav"],
    "navbar_persistent": ["search-button"],
    "navbar_end": ["navbar-icon-links"],
    "primary_sidebar_end": ["sidebar-ethical-ads"],
    "secondary_sidebar_items": ["page-toc"],
    "footer_items": ["copyright", "sphinx-version"],
    # FORCER LE MODE LIGHT UNIQUEMENT
    "theme_switcher": {
        "json_url": "",  # Désactiver complètement le switcher
    },
    "default_mode": "light",
    "icon_links": [
        {
            "name": "GitLab",
            "url": "https://gitlab.inria.fr/tanat/core/tanat",
            "icon": "fa-brands fa-gitlab",
            "type": "fontawesome",
        }
    ],
}

html_static_path = ["static"]
html_css_files = [
    "css/custom.css",
]
html_js_files = [
    "js/force-light-theme.js",
]

autodoc_mock_imports = [
    "pandas",
    "numpy",
    "PyYAML",
    "sklearn",
]
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.linkcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "nbsphinx",
    "sphinxcontrib.mermaid",
    "sphinx_gallery.gen_gallery",
]
index_entries = []

# exclude_patterns = ['notebooks/*']
exclude_patterns = ["**.ipynb_checkpoints"]

# Configuration Sphinx-Gallery - Version simplifiée
sphinx_gallery_conf = {
    "examples_dirs": "user-guide/examples",
    "gallery_dirs": "user-guide/auto_examples",
    "ignore_pattern": r"__init__\.py",
    "download_all_examples": False,
    "show_memory": False,
    "plot_gallery": "True",
    "default_thumb_file": str(this_path.parent / "static" / "logo.png"),
    "thumbnail_size": (200, 200),
    "filename_pattern": r".*\.py$",
}

# Configuration nbsphinx pour les tutoriels
nbsphinx_execute = "always"  # ou 'never' si vous ne voulez pas ré-exécuter
nbsphinx_allow_errors = True


# Pour supporter les fichiers .py au format notebook
nbsphinx_custom_formats = {
    ".py": ["jupytext.reads", {"fmt": "py:percent"}],
}

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}


def skip(
    _app, _what, name, _obj, would_skip, _options
):  # pylint: disable=too-many-arguments
    """Customize autodoc member skipping."""
    if name == "__init__":
        return False
    return would_skip


def setup(app):
    """Connect the skip function."""
    app.connect("autodoc-skip-member", skip)


def linkcode_resolve(domain, info):
    """Get source links for the linkcode extension."""
    module = info["module"]
    if domain != "py" or not module:
        return None
    top_mod = importlib.import_module(module.split(".")[0])
    mod = importlib.import_module(module)
    top_mod_path = pathlib.Path(top_mod.__file__)
    mod_path = pathlib.Path(mod.__file__)
    subpath = str(mod_path.relative_to(top_mod_path.parent.parent))
    return f"{git_url}/-/blob/main/src/{subpath}"
