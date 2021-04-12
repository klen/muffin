# -*- coding: utf-8 -*-

"""Setup Muffin documentation."""

import sys
import os
import pkg_resources

sys.path.append(os.path.abspath('_themes'))
sys.path.append(os.path.abspath('.'))

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Muffin'
copyright = u'2015, Kirill Klenov'  # noqa

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
try:
    release = pkg_resources.get_distribution('Muffin').version
except pkg_resources.DistributionNotFound:
    print('To build the documentation, The distribution information of Muffin')
    print('Has to be available.  Either install the package into your')
    print('development environment or run "setup.py develop" to setup the')
    print('metadata.  A virtualenv is recommended!')
    sys.exit(1)
del pkg_resources

version = release

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The theme to use for HTML and HTML Help pages.  Major themes that come with
# Sphinx are currently 'default' and 'sphinxdoc'.
html_theme = 'pydata_sphinx_theme'
#  html_theme = 'sphinx_rtd_theme'
#  html_theme = 'aiohttp_theme'
html_logo = 'static/logo.png'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    #  'logo_link': 'https://github.com/klen/muffin',
    'github_url': 'https://github.com/klen/muffin',
    'icon_links': [
        {
            'name': 'PyPI',
            'url': 'https://pypi.org/project/muffin',
            'icon': 'fas fa-box',
        }
    ],
    #  'logo_only': True,
    #  'canonical_url': "https://klen.github.io/muffin/",
}

html_sidebars = {
    "**": ["search-field.html", "sidebar-nav-bs.html", "custom-sidebar.html"],
}

# Add any paths that contain custom themes here, relative to this directory.
#  html_theme_path = ['_themes']

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#  html_favicon = "muffin-favicon.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#  html_static_path = ['static']
#  html_css_files = ['theme.css']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = True

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
html_use_modindex = False

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# If nonempty, this is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = ''

# Output file base name for HTML help builder.
htmlhelp_basename = 'Muffindoc'


# -- Options for LaTeX output --------------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
    ('latexindex', 'Muffin.tex', u'Muffin Documentation', u'Kirill Klenov', 'manual'),
]

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
latex_use_modindex = False

latex_elements = {
    'fontpkg':      r'\usepackage{mathpazo}',
    'papersize':    'a4paper',
    'pointsize':    '12pt',
    'preamble':     r'\usepackage{flaskstyle}'
}
latex_use_parts = True

latex_additional_files = [
    # 'muffinstyle.sty',
    'static/logo.png'
]


# -- Options for Epub output ---------------------------------------------------

# Bibliographic Dublin Core info.
# epub_title = ''
# epub_author = ''
# epub_publisher = ''
# epub_copyright = ''

# The language of the text. It defaults to the language option
# or en if the language is not set.
# epub_language = ''

# The scheme of the identifier. Typical schemes are ISBN or URL.
# epub_scheme = ''

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
# epub_identifier = ''

# A unique identification for the text.
# epub_uid = ''

# HTML files that should be inserted before the pages created by sphinx.
# The format is a list of tuples containing the path and title.
# epub_pre_files = []

# HTML files shat should be inserted after the pages created by sphinx.
# The format is a list of tuples containing the path and title.
# epub_post_files = []

# A list of files that should not be packed into the epub file.
# epub_exclude_files = []

# The depth of the table of contents in toc.ncx.
# epub_tocdepth = 3

intersphinx_mapping = {
    "python": ("http://docs.python.org/3", None),
    "multidict": ("https://multidict.readthedocs.io/en/stable/", None),
    "yarl": ("https://yarl.readthedocs.io/en/stable/", None),
    "asgi_tools": ("https://klen.github.io/asgi-tools/", None),
}

#  pygments_style = 'tango'

autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
