"""Module containing the enumerations of left and right option lines.

This module defines enumerations that map option line names to their corresponding line numbers in DAT files.
Left and right option lines control different aspects of knitting machine operation and configuration.
"""
from enum import Enum


class Left_Option_Lines(Enum):
    """Enumeration key of left-option lines to their line numbers.

    Left option lines control various machine settings and operational parameters on the left side of the DAT file structure.
    Each enumeration value corresponds to a specific line number where that option is configured.
    """
    Direction_Specification = 1
    """int: Line number for direction specification settings."""

    Rack_Pitch = 2
    """int: Line number for rack pitch configuration."""

    Rack_Alignment = 3
    """int: Line number for rack alignment settings."""

    Rack_Direction = 4
    """int: Line number for rack direction specification."""

    Knit_Speed = 5
    """int: Line number for knit speed configuration."""

    Transfer_Speed = 6
    """int: Line number for transfer speed settings."""

    Pause_Option = 7
    """int: Line number for pause option configuration."""

    AMiss_Split_Flag = 12
    """int: Line number for AMiss split flag settings."""

    Transfer_Type = 13
    """int: Line number for transfer type specification."""

    def __str__(self) -> str:
        """Return string representation with 'L' prefix.

        Returns:
            str: String representation in format 'L{value}' where value is the line number.
        """
        return f"L{self.value}"

    def __repr__(self) -> str:
        """Return detailed string representation.

        Returns:
            str: String representation in format '{name}({str_representation})'.
        """
        return f"{self.name}({str(self)})"

    def __int__(self) -> int:
        """Return integer value of the option line.

        Returns:
            int: The line number associated with this left option.
        """
        return self.value

    def __hash__(self) -> int:
        """Return hash value of the option line.

        Returns:
            int: Hash value based on the integer value of the option line.
        """
        return int(self)


class Right_Option_Lines(Enum):
    """Enumeration key of right-option lines to their line numbers.

    Right option lines control various machine settings and operational parameters on the right side of the DAT file structure.
    Each enumeration value corresponds to a specific line number where that option is configured.
    """
    Direction_Specification = 1
    """int: Line number for direction specification settings."""

    Yarn_Carrier_Number = 3
    """int: Line number for yarn carrier number configuration."""

    Knit_Cancel_or_Carriage_Move = 5
    """int: Line number for knit cancel or carriage move settings."""

    Stitch_Number = 6
    """int: Line number for stitch number specification."""

    Drop_Sinker = 7
    """int: Line number for drop sinker configuration."""

    Links_Process = 9
    """int: Line number for links process settings."""

    Carrier_Gripper = 10
    """int: Line number for carrier gripper configuration."""

    Presser_Mode = 11
    """int: Line number for presser mode settings."""

    Apply_Stitch_to_Transfer = 13
    """int: Line number for apply stitch to transfer configuration."""

    Hook_Operation = 15
    """int: Line number for hook operation settings."""

    def __str__(self) -> str:
        """Return string representation with 'R' prefix.

        Returns:
            str: String representation in format 'R{value}' where value is the line number.
        """
        return f"R{self.value}"

    def __repr__(self) -> str:
        """Return detailed string representation.

        Returns:
            str: String representation in format '{name}({str_representation})'.
        """
        return f"{self.name}({str(self)})"

    def __int__(self) -> int:
        """Return integer value of the option line.

        Returns:
            int: The line number associated with this right option.
        """
        return self.value

    def __hash__(self) -> int:
        """Return hash value of the option line.

        Returns:
            int: Hash value based on the integer value of the option line.
        """
        return int(self)
