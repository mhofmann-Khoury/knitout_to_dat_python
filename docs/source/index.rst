knitout-to-dat-python
=====================

A Python library to convert Knitout files into Shima Seiki DAT files.

This library replicates the functionality of CMU Textile Lab's Knitout-to-DAT
Interpreter, originally implemented in JavaScript, but now available as a
Python package for easier integration into Python-based knitting workflows.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api
   examples
   changelog

Quick Start
-----------

Install the package::

    pip install knitout-to-dat-python

Basic usage::

    from knitout_to_dat import KnitoutConverter

    converter = KnitoutConverter("input.ko", "output.dat")
    converter.convert_to_dat()

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
