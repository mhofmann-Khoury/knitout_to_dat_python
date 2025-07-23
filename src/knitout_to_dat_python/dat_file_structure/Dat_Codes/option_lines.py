"""Module containing the enumerations of left and right option lines."""
from enum import Enum


class Left_Option_Lines(Enum):
    """Enumeration key of left-option lines to their line numbers."""
    Direction_Specification = 1
    Rack_Pitch = 2
    Rack_Alignment = 3
    Rack_Direction = 4
    Knit_Speed = 5
    Transfer_Speed = 6
    Pause_Option = 7
    AMiss_Split_Flag = 12
    Transfer_Type = 13

    def __str__(self) -> str:
        return f"L{self.value}"

    def __repr__(self) -> str:
        return f"{self.name}({str(self)})"

    def __int__(self) -> int:
        return self.value

    def __hash__(self) -> int:
        return int(self)


class Right_Option_Lines(Enum):
    """Enumeration key of right-option lines to their line numbers."""
    Direction_Specification = 1
    Yarn_Carrier_Number = 3
    Knit_Cancel_or_Carriage_Move = 5
    Stitch_Number = 6
    Drop_Sinker = 7
    Links_Process = 9
    Carrier_Gripper = 10
    Presser_Mode = 11
    Apply_Stitch_to_Transfer = 13
    Hook_Operation = 15

    def __str__(self) -> str:
        return f"R{self.value}"

    def __repr__(self) -> str:
        return f"{self.name}({str(self)})"

    def __int__(self) -> int:
        return self.value

    def __hash__(self) -> int:
        return int(self)
