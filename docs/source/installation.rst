Installation
============

This guide covers different methods for installing this library depending on your use case.

📦 Standard Installation
------------------------

From PyPI (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to install KnitScript is from PyPI using pip:

.. code-block:: bash

   pip install knitout-to-dat-python

This installs the latest stable release with all required dependencies.

From Test-PyPI (Development Versions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to try unreleased features, you can install from Test-PyPI:

.. code-block:: bash

   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ knitout-to-dat-python

.. note::
   Development versions may be unstable and are not recommended for production use.

🛠️ Development Installation
---------------------------

From Source (Latest)
~~~~~~~~~~~~~~~~~~~~

To get the latest development version:

.. code-block:: bash

   git clone https://github.com/mhofmann-Khoury/knitout_to_dat_python.git
   cd knitout_to_dat_python
   pip install -e .

Development with All Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For contributing to KnitScript development:

.. code-block:: bash

   git clone https://github.com/mhofmann-Khoury/knitout_to_dat_python.git
   cd knitout_to_dat_python
   pip install -e ".[dev]"
   pre-commit install

This installs:
- All runtime dependencies
- Development tools (mypy, pytest, etc.)
- Documentation generation tools
- Pre-commit hooks for code quality

Next Steps
----------

After successful installation:

1. Read the :doc:`quickstart` guide for your first pattern
