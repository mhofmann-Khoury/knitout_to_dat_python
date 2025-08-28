"""Enumeration and supporting functions for converting needle operations to color codes.

This module provides the Operation_Color enumeration and utility functions for mapping knitting operations to their corresponding color codes used in DAT files.
The color codes represent different types of needle operations including knit, tuck, miss, transfer, and split operations on front and back needle beds.
"""
from __future__ import annotations

from enum import Enum

from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction
from knitout_interpreter.knitout_operations.knitout_instruction import (
    Knitout_Instruction_Type,
)
from knitout_interpreter.knitout_operations.needle_instructions import (
    Knit_Instruction,
    Miss_Instruction,
    Needle_Instruction,
    Split_Instruction,
    Tuck_Instruction,
    Xfer_Instruction,
)


class Operation_Color(Enum):
    """Color codes for different knitting operations (from original JS).

    This enumeration maps knitting operations to their corresponding color codes used in DAT file generation.
    Each color code represents a specific type of needle operation that can be performed on either the front bed, back bed, or both beds simultaneously.
    """
    # Miss operations
    SOFT_MISS = 16
    """int: A miss that does not specify a front or back needle. Used by kick-back operations."""

    MISS_FRONT = 216
    """int: Front miss (independent carrier movement)."""

    MISS_BACK = 217
    """int: Back miss (independent carrier movement)."""

    # Tuck operations
    TUCK_FRONT = 11
    """int: Indicates a tuck operation on the front bed needle."""

    TUCK_BACK = 12
    """int: Indicates a tuck operation on the back bed needle."""

    # Knit operations
    KNIT_FRONT = 51
    """int: Indicates a knit operation on the front bed needle."""

    KNIT_BACK = 52
    """int: Indicates a knit operation on the back bed needle."""

    # Combo operations (front + back)
    KNIT_FRONT_KNIT_BACK = 3
    """int: Indicates all needle knit on the front and back bed needles."""

    KNIT_FRONT_TUCK_BACK = 41
    """int: Indicates all needle knit on the front bed needle then tuck on the back bed needle."""

    TUCK_FRONT_KNIT_BACK = 42
    """int: Indicates all needle tuck on the front bed needle then knit on the back bed needle."""

    TUCK_FRONT_TUCK_BACK = 88
    """int: Indicates all needle tucks on the front and back bed needles."""

    # Transfer operations
    XFER_TO_BACK = 20
    """int: Indicates a transfer from the front bed needle to the aligned back bed needle."""

    XFER_TO_FRONT = 30
    """int: Indicates a transfer from the back bed needle to the aligned front bed needle."""

    # Split operations
    SPLIT_TO_BACK = 101
    """int: Indicates a split from the front bed needle to the aligned back bed needle."""

    SPLIT_TO_FRONT = 102
    """int: Indicates a split from the back bed needle to the aligned front bed needle."""

    @property
    def operation_types(self) -> tuple[type, None | type]:
        """Get the operation types associated with this color code.

        Returns:
            tuple[type, None | type]: A tuple of the front and back operation types for this operation color code.
                If this is an all needle operation, the first value is the front operation and the second value is the back operation.
                Otherwise, the first value is the operation type (regardless of position), and the second value is None.

        Raises:
            AssertionError: If the operation color code is not recognized or mapped to any operation type.
        """
        if self is Operation_Color.TUCK_FRONT or self is Operation_Color.TUCK_BACK:
            return Tuck_Instruction, None
        elif self is Operation_Color.KNIT_FRONT or self is Operation_Color.KNIT_BACK:
            return Knit_Instruction, None
        elif self is Operation_Color.XFER_TO_BACK or self is Operation_Color.XFER_TO_FRONT:
            return Xfer_Instruction, None
        elif self is Operation_Color.SPLIT_TO_BACK or self is Operation_Color.SPLIT_TO_FRONT:
            return Split_Instruction, None
        elif self is Operation_Color.MISS_FRONT or self is Operation_Color.MISS_BACK:
            return Miss_Instruction, None
        elif self is Operation_Color.SOFT_MISS:
            return Kick_Instruction, None
        elif self is Operation_Color.KNIT_FRONT_KNIT_BACK:
            return Knit_Instruction, Knit_Instruction
        elif self is Operation_Color.TUCK_FRONT_TUCK_BACK:
            return Tuck_Instruction, Tuck_Instruction
        elif self is Operation_Color.TUCK_FRONT_KNIT_BACK:
            return Tuck_Instruction, Knit_Instruction
        elif self is Operation_Color.KNIT_FRONT_TUCK_BACK:
            return Knit_Instruction, Tuck_Instruction
        assert False, f"Couldn't identify operation type for {self}"

    @property
    def is_front(self) -> bool:
        """Check if operation only occurs on front bed.

        Returns:
            bool: True if operation only occurs on front bed. False, otherwise.
        """
        return self in [Operation_Color.KNIT_FRONT, Operation_Color.TUCK_FRONT, Operation_Color.MISS_FRONT, Operation_Color.SPLIT_TO_BACK, Operation_Color.XFER_TO_BACK]

    @property
    def is_back(self) -> bool:
        """Check if operation only occurs on back bed.

        Returns:
            bool: True if operation only occurs on back bed. False, otherwise.
        """
        return self in [Operation_Color.KNIT_BACK, Operation_Color.TUCK_BACK, Operation_Color.MISS_BACK, Operation_Color.SPLIT_TO_FRONT, Operation_Color.XFER_TO_FRONT]

    @property
    def can_convert_to_all_needle(self) -> bool:
        """Check if this operation can be converted to an all needle operation.

        Returns:
            bool: True if this operation can be converted to an all needle operation. False, otherwise.
        """
        return self in [Operation_Color.KNIT_BACK, Operation_Color.KNIT_FRONT, Operation_Color.TUCK_BACK, Operation_Color.TUCK_FRONT]

    def can_be_opposite(self, other_color: Operation_Color) -> bool:
        """Check if two operations can be combined into an all needle operation.

        Args:
            other_color (Operation_Color): The other Operation_Color to test for all-needle combination with this operation.

        Returns:
            bool: True if the two operations can be combined into an all needle operation, otherwise False.
        """
        return (self.can_convert_to_all_needle and other_color.can_convert_to_all_needle and
                ((self.is_front and other_color.is_back) or (self.is_back and other_color.is_front)))

    def get_all_needle(self, other_color: Operation_Color) -> Operation_Color | None:
        """Get the all-needle merged operation color from two operation colors.

        Args:
            other_color (Operation_Color): The other Operation_Color to get the all-needle merged operation color.

        Returns:
            Operation_Color | None: None if the operations cannot be combined for all needle knitting.
                Otherwise, return a front-back knit/tuck operation for all-needle knitting.
        """
        if not self.can_be_opposite(other_color):
            return None
        if self.is_front:
            if self is Operation_Color.KNIT_FRONT:
                if other_color is Operation_Color.TUCK_BACK:
                    return Operation_Color.KNIT_FRONT_TUCK_BACK
                else:  # Other is knit back
                    return Operation_Color.KNIT_FRONT_KNIT_BACK
            else:  # Self is Tuck Front
                if other_color is Operation_Color.TUCK_BACK:
                    return Operation_Color.TUCK_FRONT_TUCK_BACK
                else:  # other is knit back
                    return Operation_Color.TUCK_FRONT_KNIT_BACK
        elif self is Operation_Color.KNIT_BACK:  # Self is a back operation
            if other_color is Operation_Color.TUCK_FRONT:
                return Operation_Color.TUCK_FRONT_KNIT_BACK
            else:  # other is Knit Front
                return Operation_Color.KNIT_FRONT_KNIT_BACK
        else:  # Self is Tuck Back
            if other_color is Operation_Color.TUCK_FRONT:
                return Operation_Color.TUCK_FRONT_TUCK_BACK
            else:  # other is Knit Front
                return Operation_Color.KNIT_FRONT_TUCK_BACK

    def __str__(self) -> str:
        """Return string representation of the operation color.

        Returns:
            str: The name of the operation color enumeration.
        """
        return self.name

    def __repr__(self) -> str:
        """Return detailed string representation of the operation color.

        Returns:
            str: String representation of the operation color.
        """
        return str(self)

    def __int__(self) -> int:
        """Return integer value of the operation color.

        Returns:
            int: The integer value associated with this operation color.
        """
        return self.value

    def __hash__(self) -> int:
        """Return hash value of the operation color.

        Returns:
            int: Hash value based on the integer value of the operation color.
        """
        return int(self)

    @staticmethod
    def get_operation_color(instruction: Needle_Instruction) -> Operation_Color:
        """Convert a needle instruction to its corresponding operation color.

        This function maps different types of needle instructions to their appropriate Operation_Color enumeration values based on the instruction type and needle position.

        Args:
            instruction (Needle_Instruction): The needle instruction to convert to a color.

        Returns:
            Operation_Color: The Operation_Color that corresponds to the given Needle instruction.

        Raises:
            ValueError: If no operation color corresponds to the given instruction type.
        """
        if instruction.instruction_type == Knitout_Instruction_Type.Knit:
            return Operation_Color.KNIT_FRONT if instruction.needle.is_front else Operation_Color.KNIT_BACK
        elif instruction.instruction_type == Knitout_Instruction_Type.Tuck:
            return Operation_Color.TUCK_FRONT if instruction.needle.is_front else Operation_Color.TUCK_BACK
        elif instruction.instruction_type == Knitout_Instruction_Type.Miss:
            if isinstance(instruction, Kick_Instruction):
                return Operation_Color.SOFT_MISS
            return Operation_Color.MISS_FRONT if instruction.needle.is_front else Operation_Color.MISS_BACK
        elif instruction.instruction_type == Knitout_Instruction_Type.Split:
            return Operation_Color.SPLIT_TO_BACK if instruction.needle.is_front else Operation_Color.SPLIT_TO_FRONT
        elif instruction.instruction_type == Knitout_Instruction_Type.Xfer:
            return Operation_Color.XFER_TO_BACK if instruction.needle.is_front else Operation_Color.XFER_TO_FRONT
        else:
            raise ValueError(f"No operation color corresponds to the instruction {instruction}.")
