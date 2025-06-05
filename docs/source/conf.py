"""Sphinx configuration for knitout-to-dat-python documentation."""

import os
import sys

# =============================================================================
# PATH CONFIGURATION
# =============================================================================
# Add the project source directory to Python path so Sphinx can import modules
# Using src/ layout, so we go up two levels from docs/source/ to project root,
# then into src/
sys.path.insert(0, os.path.abspath('../../src'))

# =============================================================================
# PROJECT INFORMATION
# =============================================================================
project = 'knitout-to-dat-python'
copyright = '2025, Megan Hofmann'
author = 'Megan Hofmann'
release = '0.1.0'  # Full version including alpha/beta/rc tags
version = '0.1.0'  # Short X.Y version for display

# =============================================================================
# SPHINX EXTENSIONS
# =============================================================================
extensions = [
    # Core Sphinx extensions
    'sphinx.ext.autodoc',  # Auto-generate docs from docstrings
    'sphinx.ext.napoleon',  # Support for Google/NumPy style docstrings
    'sphinx.ext.viewcode',  # Add [source] links to documentation
    'sphinx.ext.intersphinx',  # Link to other project documentation
    'sphinx.ext.githubpages',  # Publish HTML docs to GitHub Pages

    # Third-party extensions
    'sphinx_autodoc_typehints',  # Better rendering of type hints
    'myst_parser',  # Support for Markdown files alongside RST
]

# =============================================================================
# TEMPLATE AND STATIC FILE PATHS
# =============================================================================
# Paths for custom templates (relative to this configuration file)
templates_path = ['_templates']

# Paths for static files like custom CSS/JS (relative to this configuration file)
# Check if _static directory exists, if not, use empty list to avoid error
static_dir = os.path.join(os.path.dirname(__file__), '_static')
if os.path.exists(static_dir):
    html_static_path = ['_static']
else:
    html_static_path = []

# =============================================================================
# SOURCE FILE CONFIGURATION
# =============================================================================
# List of patterns to exclude when looking for source files
# These are relative to the source directory
exclude_patterns = [
    '_build',  # Sphinx build directory
    'Thumbs.db',  # Windows thumbnail cache
    '.DS_Store',  # macOS directory metadata
]

# =============================================================================
# HTML OUTPUT CONFIGURATION
# =============================================================================
# The theme to use for HTML and HTML Help pages
html_theme = 'sphinx_rtd_theme'

# Custom title for HTML pages (appears in browser tab and page header)
html_title = f"{project} v{version}"

# Additional options for the Read the Docs theme
html_theme_options = {
    'collapse_navigation': False,  # Keep navigation expanded
    'sticky_navigation': True,  # Keep navigation visible while scrolling
    'navigation_depth': 4,  # How deep to show navigation tree
    'includehidden': True,  # Include hidden toctree entries
    'titles_only': False,  # Show section titles in navigation
}

# =============================================================================
# NAPOLEON EXTENSION CONFIGURATION
# =============================================================================
# Configure how Google and NumPy style docstrings are parsed
napoleon_google_docstring = True  # Parse Google style docstrings
napoleon_numpy_docstring = True  # Parse NumPy style docstrings
napoleon_include_init_with_doc = False  # Don't include __init__ docstring with class docstring
napoleon_include_private_with_doc = False  # Don't document private members
napoleon_include_special_with_doc = True  # Document special members like __call__
napoleon_use_admonition_for_examples = False  # Use code blocks for examples, not admonitions
napoleon_use_admonition_for_notes = False  # Use simple paragraphs for notes
napoleon_use_admonition_for_references = False  # Use simple paragraphs for references
napoleon_use_ivar = False  # Use :ivar: for instance variables
napoleon_use_param = True  # Use :param: for parameters
napoleon_use_rtype = True  # Use :rtype: for return types
napoleon_preprocess_types = False  # Don't preprocess type annotations

# =============================================================================
# AUTODOC EXTENSION CONFIGURATION
# =============================================================================
# Default options for the autodoc extension
autodoc_default_options = {
    'members': True,  # Document all members
    'member-order': 'bysource',  # Order members as they appear in source
    'special-members': '__init__',  # Include __init__ method
    'undoc-members': True,  # Include members without docstrings
    'exclude-members': '__weakref__',  # Exclude this special attribute
    'show-inheritance': True,  # Show inheritance relationships
}

# Configure how type hints are handled in autodoc
autodoc_typehints = 'description'  # Show type hints in parameter descriptions
autodoc_typehints_description_target = 'documented'  # Only add type info for documented parameters

# =============================================================================
# TYPE HINTS CONFIGURATION
# =============================================================================
# Configuration for sphinx-autodoc-typehints extension
always_document_param_types = True  # Always document parameter types
typehints_fully_qualified = False  # Use short names for types when possible
typehints_document_rtype = True  # Document return types

# =============================================================================
# INTERSPHINX CONFIGURATION
# =============================================================================
# Mapping to other project documentation for cross-references
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    # Add more as your project dependencies grow
}

# Timeout for fetching intersphinx inventories (in seconds)
intersphinx_timeout = 10

# =============================================================================
# MYST PARSER CONFIGURATION (for Markdown support)
# =============================================================================
# Configure MyST parser for Markdown files
myst_enable_extensions = [
    "colon_fence",  # Enable ::: fenced code blocks
    "deflist",  # Enable definition lists
    "html_admonition",  # Enable HTML-style admonitions
    "html_image",  # Enable HTML img tags
    "linkify",  # Auto-convert URLs to links
    "replacements",  # Enable replacements like (c) -> ©
    "smartquotes",  # Enable smart quotes
    "substitution",  # Enable variable substitutions
    "tasklist",  # Enable task lists with checkboxes
]

# =============================================================================
# GITHUB PAGES CONFIGURATION
# =============================================================================
# Configuration for GitHub Pages deployment
# Creates a .nojekyll file to tell GitHub Pages not to process with Jekyll
html_copy_source = False  # Don't copy .rst source files to output
html_show_sourcelink = True  # Show "Show Source" links

# =============================================================================
# ADDITIONAL HTML OPTIONS
# =============================================================================
# Show "Edit on GitHub" links (if using GitHub)
html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "mhofmann-Khoury",  # Replace with your GitHub username
    "github_repo": "knitout_to_dat_python",  # Replace with your repo name
    "github_version": "main",  # Git branch
    "conf_py_path": "/docs/source/",  # Path to documentation source
}

# Custom CSS files (relative to html_static_path)
html_css_files = [
    # 'custom.css',  # Uncomment and create if you want custom styling
]

# Custom JavaScript files (relative to html_static_path)
html_js_files = [
    # 'custom.js',  # Uncomment and create if you want custom JavaScript
]
