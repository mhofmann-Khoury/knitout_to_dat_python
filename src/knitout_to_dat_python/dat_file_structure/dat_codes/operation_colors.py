"""Enumeration and supporting functions for converting needle operations to color codes."""

from enum import Enum

from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction_Type
from knitout_interpreter.knitout_operations.needle_instructions import Needle_Instruction, Tuck_Instruction, Knit_Instruction, Xfer_Instruction, Split_Instruction, Miss_Instruction


from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction


class Operation_Color(Enum):
    """Color codes for different knitting operations (from original JS)."""
    # Miss operations
    SOFT_MISS = 16
    MISS_FRONT = 216  # Front miss (independent carrier movement)
    MISS_BACK = 217  # Back miss (independent carrier movement)

    # Tuck operations
    TUCK_FRONT = 11
    TUCK_BACK = 12

    # Knit operations
    KNIT_FRONT = 51
    KNIT_BACK = 52

    # Combo operations (front + back)
    KNIT_FRONT_KNIT_BACK = 3
    KNIT_FRONT_TUCK_BACK = 41
    TUCK_FRONT_KNIT_BACK = 42
    TUCK_FRONT_TUCK_BACK = 88

    # Transfer operations
    XFER_TO_BACK = 20
    XFER_TO_FRONT = 30

    # Split operations
    SPLIT_TO_BACK = 101
    SPLIT_TO_FRONT = 102

    @property
    def operation_types(self) -> tuple[type, None | type]:
        """
        Returns:
            A tuple of the front and back operation types for this operation color code.
            If this is an all needle operation, the first value is the front operation and the second value is the back operation.
            Otherwise, the first value is the operation type (regardless of position), and the second value is None.
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
        """
        Returns:
            True if operation only occurs on front bed. False, otherwise.
        """
        return self in [Operation_Color.KNIT_FRONT, Operation_Color.TUCK_FRONT, Operation_Color.MISS_FRONT, Operation_Color.SPLIT_TO_BACK, Operation_Color.XFER_TO_BACK]

    @property
    def is_back(self) -> bool:
        """
        Returns:
            True if operation only occurs on back bed. False, otherwise.
        """
        return self in [Operation_Color.KNIT_BACK, Operation_Color.TUCK_BACK, Operation_Color.MISS_BACK, Operation_Color.SPLIT_TO_FRONT, Operation_Color.XFER_TO_FRONT]

    @property
    def can_convert_to_all_needle(self) -> bool:
        """
        Returns:
            True if this operation can be converted to an all needle operation. False, otherwise.
        """
        return self in [Operation_Color.KNIT_BACK, Operation_Color.KNIT_FRONT, Operation_Color.TUCK_BACK, Operation_Color.TUCK_FRONT]

    def can_be_opposite(self, other_color: Enum) -> bool:
        """
        Args:
            other_color: The other Operation_Color to test for all-needle combination with this operation.

        Returns:
            True if the two operations can be combined into an all needle operation, otherwise False.
        """
        assert isinstance(other_color, Operation_Color)
        return (self.can_convert_to_all_needle and other_color.can_convert_to_all_needle and
                ((self.is_front and other_color.is_back) or (self.is_back and other_color.is_front)))

    def get_all_needle(self, other_color: Enum) -> Enum | None:
        """
        Args:
            other_color: The other Operation_Color to get the all-needle merged operation color.

        Returns:
            None if the operations cannot be combined for all needle knitting.
            Otherwise, return a front-back knit/tuck operation for all-needle knitting.
        """
        assert isinstance(other_color, Operation_Color)
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
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return self.value

    def __hash__(self) -> int:
        return int(self)


def get_operation_color(instruction: Needle_Instruction) -> Operation_Color:
    """
    Args:
        instruction: The needle instruction to convert to a color.

    Returns:
        The Operation_Color that corresponds to the given Needle instruction.
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
        assert False, f"No operation color corresponds to the instruction {instruction}."
