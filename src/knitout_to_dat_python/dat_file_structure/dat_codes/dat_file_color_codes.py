"""Module containing the hard-coded dat file color codes associated with different operations and settings.

This module defines constants used throughout the DAT file processing system for
identifying specific operations, settings, and markers within DAT files used
for knitting machine control.

Attributes:
    OPTION_LINE_COUNT (int):
        Number of option lines expected on the left and right side of a DAT file.
        This constant defines the expected number of option lines that should appear on both the left and right sides of a DAT file structure.
    NO_CARRIERS (int):
        Number used to indicate that there are no carriers used in a carriage pass.
        This special value (255) is used as a marker to indicate the absence of yarn carriers in a particular carriage pass operation.
    WIDTH_SPECIFIER (int):
        The number used on Width Specification rows at the top of a DAT file. This constant identifies rows that contain width specification information at the beginning of DAT files.
    STOPPING_MARK (int):
        The number used to indicate the stopping left and right slot of needle operations in a carriage pass.
        This marker value is used to define the boundaries (left and right stopping positions) for needle operations during carriage pass execution.
"""

OPTION_LINE_COUNT: int = 20

NO_CARRIERS: int = 255

WIDTH_SPECIFIER: int = 1

STOPPING_MARK: int = 13
