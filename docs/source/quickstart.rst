Quick Start Guide
=================

This guide will help you get started with knitout-to-dat-python.

Basic Usage
-----------

Import the main converter class::

    from knitout_to_dat import KnitoutConverter

Create a converter instance::

    converter = KnitoutConverter("input.knitout", "output.dat")

Convert the file::

    converter.convert_to_dat()

Complete Example
----------------

Here's a complete example::

    from knitout_to_dat import KnitoutConverter
    from pathlib import Path

    # Ensure input file exists
    input_file = Path("my_pattern.knitout")
    if not input_file.exists():
        raise FileNotFoundError(f"Input file {input_file} not found")

    # Convert to DAT format
    converter = KnitoutConverter(str(input_file), "my_pattern.dat")
    try:
        converter.convert_to_dat()
        print("Conversion successful!")
    except Exception as e:
        print(f"Conversion failed: {e}")
