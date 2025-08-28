"""Module containing functions wrapping the main functionality of this library.

This module provides high-level utility functions for converting between knitout and DAT file formats.
It serves as the primary interface for users of the knitout-to-dat-python library, offering simple function calls for both forward and reverse conversion operations.
"""
from knitout_to_dat_python.dat_file_structure.Dat_to_Knitout_Converter import (
    Dat_to_Knitout_Converter,
)
from knitout_to_dat_python.dat_file_structure.knitout_to_dat_converter import (
    Knitout_to_Dat_Converter,
)


def knitout_to_dat(knitout_program: str, dat_filename: str | None = None, knitout_in_file: bool = True) -> str:
    """Convert a knitout program into a Shima Seiki DAT file.

    This is the main utility function of this package. It converts the given knitout program into a Shima Seiki DAT file suitable for use with knitting machines.
    The function handles the complete conversion pipeline including parsing, raster generation, and file creation.

    Args:
        knitout_program (str): The string containing the knitout program or a path to the file containing the knitout program.
        dat_filename (str | None, optional): The string containing the name of the output dat file. If None, defaults to the same name as the knitout file with .dat extension. Defaults to None.
        knitout_in_file (bool, optional): If true, looks for the knitout program inside a given knitout file. Defaults to True.

    Returns:
        str: The name of the dat file that contains the resulting dat program.

    Raises:
        ValueError: Raised if no dat_filename and no knitout filename are specified.
    """
    if dat_filename is None:
        if not knitout_in_file:
            raise ValueError('A knitout file must be specified if dat_filename is not specified')
        dat_filename = knitout_program.split('.')[0] + '.dat'
    converter = Knitout_to_Dat_Converter(knitout_program, dat_filename, knitout_in_file=knitout_in_file)
    converter.process_knitout_to_dat()
    return dat_filename


def dat_to_knitout(dat_file: str, knitout_file: str | None = None) -> str:
    """Convert a DAT file into a knitout file.

    This utility function provides access to the dat to knitout converter functionality.
    This method converts the given dat file into a knitout file of the corresponding instructions, enabling reverse conversion from machine-specific DAT format back to the universal knitout format.

    Args:
        dat_file (str): The path to the dat file to convert.
        knitout_file (str | None, optional): The path to the knitout file to convert. If None, the knitout file will share the name of the dat file with the .k extension. Defaults to None.

    Returns:
        str: The name of resulting knitout file.
    """
    if knitout_file is None:
        knitout_file = dat_file.split('.')[0] + '.k'
    converter = Dat_to_Knitout_Converter(dat_file)
    converter.write_knitout(knitout_file)
    return knitout_file
