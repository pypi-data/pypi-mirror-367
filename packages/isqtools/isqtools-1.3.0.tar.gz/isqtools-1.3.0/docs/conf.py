import datetime
import importlib.metadata

project = "isqtools"
author = "Arclight Quantum"
copyright = f"{datetime.date.today().year}, {author}"
version = release = importlib.metadata.version(f"{project}")

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.todo",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "nbsphinx",
]

myst_enable_extensions = [
    "amsmath",
    "dollarmath",
    "deflist",
    "colon_fence",
]

todo_include_todos = True
source_suffix = [".rst", ".md"]
exclude_patterns = [
    "_build",
    "**.ipynb_checkpoints",
    "Thumbs.db",
    ".DS_Store",
    ".env",
    ".venv",
]

html_static_path = ["_static"]

pygments_style = "colorful"
add_module_names = False
numfig = True
numfig_format = {"table": "Table %s"}
language = "en"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

nitpick_ignore = [
    ("py:class", "_io.StringIO"),
    ("py:class", "_io.BytesIO"),
]
autoclass_content = "both"
always_document_param_types = True


html_title = "isqtools 1.3.0"
html_theme = "furo"
html_theme_options = {}
html_context = {"copyright": copyright}
html_last_updated_fmt = datetime.datetime.now().strftime("%b %d, %Y")
