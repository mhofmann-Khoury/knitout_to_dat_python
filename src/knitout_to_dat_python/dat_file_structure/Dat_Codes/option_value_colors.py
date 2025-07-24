"""Module of Enumerations for common color codes to Option Lines."""

from enum import Enum

from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_to_dat_python.dat_file_structure.Dat_Codes.dat_file_color_codes import NO_CARRIERS


class Link_Process_Color(Enum):
    """Enumeration of the Links Process color options."""
    Ignore_Link_Process = 1

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return self.value

    def __hash__(self) -> int:
        return int(self)


class Drop_Sinker_Color(Enum):
    """Enumeration of color codes for the drop-sinker option line."""
    Standard = 0
    Drop_Sinker = 11

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return self.value

    def __hash__(self) -> int:
        return int(self)


class Amiss_Split_Hook_Color(Enum):
    """Enumeration of color codes for the Amiss_Split_Hook option line."""
    Split_Hook = 10

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return self.value

    def __hash__(self) -> int:
        return int(self)


class Pause_Color(Enum):
    """Enumeration of Pause Color Codes for pause/reset option Line"""
    Pause = 20

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return self.value

    def __hash__(self) -> int:
        return int(self)


class Hook_Operation_Color(Enum):
    """Enumeration of yarn-inserting-hook operation colors."""
    No_Hook_Operation = 0
    In_Hook_Operation = 10
    Out_Hook_Operation = 20
    ReleaseHook_Operation = 90

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return self.value

    def __hash__(self) -> int:
        return int(self)


class Knit_Cancel_Color(Enum):
    """Enumeration of color options for the knit cancel setting."""
    Knit_Cancel = 1
    Carriage_Move = 2
    Standard = 0

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return self.value

    def __hash__(self) -> int:
        return int(self)


class Transfer_Type_Color(Enum):
    """Enumeration of transfer slider options."""
    To_Sliders = 1
    From_Sliders = 3
    No_Sliders = 0

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return self.value

    def __hash__(self) -> int:
        return int(self)


class Rack_Direction_Color(Enum):
    """ Enumeration of the color codes to specify leftward or rightward racking."""
    Left = 10
    Right = 11

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return self.value

    def __hash__(self) -> int:
        return int(self)


class Rack_Pitch_Color(Enum):
    """ Enumeration of the color codes to specify all-needle racking pitch."""
    All_Needle = 1
    Standard = 0

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return self.value

    def __hash__(self) -> int:
        return int(self)


class Carriage_Pass_Direction_Color(Enum):
    """ Enumeration of the color codes to specify carriage pass direction."""
    Leftward = 7
    Rightward = 6
    Unspecified = 1

    def get_direction(self) -> Carriage_Pass_Direction | None:
        """
        Returns:
            The corresponding carriage pass direction for the enumeration. None if the direction is unspecified.
        """
        if self is Carriage_Pass_Direction_Color.Leftward:
            return Carriage_Pass_Direction.Leftward
        elif self is Carriage_Pass_Direction_Color.Rightward:
            return Carriage_Pass_Direction.Rightward
        else:
            return None

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return self.value

    def __hash__(self) -> int:
        return int(self)


def get_carriage_pass_direction_color(carriage_pass: Carriage_Pass) -> Carriage_Pass_Direction_Color:
    """
    Args:
        carriage_pass: The carriage pass to determine the pass direction color from.

    Returns:
        The direction color corresponding to the given carriage pass direction.
    """
    if carriage_pass.xfer_pass:
        return Carriage_Pass_Direction_Color.Unspecified
    elif carriage_pass.direction is Carriage_Pass_Direction.Leftward:
        return Carriage_Pass_Direction_Color.Leftward  # Left direction marker
    elif carriage_pass.direction is Carriage_Pass_Direction.Rightward:
        return Carriage_Pass_Direction_Color.Rightward  # Right direction marker
    else:
        return Carriage_Pass_Direction_Color.Unspecified  # No direction marker


class Presser_Setting_Color(Enum):
    """ An enumeration of the possible presser mode settings for a carriage pass."""
    On = 101
    Off = 0
    Auto = 0

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(str(self))

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def should_use_presser_mode(carriage_pass: Carriage_Pass) -> bool:
        """
        A presser mode should be used if the yarn-inserting-hook is not active
            and there are not mixed front/back needles operations in the carriage pass
        Args:
            carriage_pass: The carriage pass to interpret the need for presser mode.
        Returns:
            True if the given carriage pass does not have mixed front/back needles and thus should use the presser.
        """
        has_front = any(needle.is_front for needle in carriage_pass.needles)
        has_back = any(not needle.is_front for needle in carriage_pass.needles)
        return not (has_front and has_back)  # Don't use presser for mixed front/back

    def presser_option(self, carriage_pass: Carriage_Pass) -> int:
        """
        Args:
            carriage_pass: The carriage pass used to determine mode in Auto-Mode.

        Returns:
            The color-code for the presser mode.
            If auto-mode, this is dynamically determined by the carriage pass.
        """
        if self is Presser_Setting_Color.On or self is Presser_Setting_Color.Off:
            value = self.value
            assert isinstance(value, int)
            return value
        elif self.should_use_presser_mode(carriage_pass):  # Auto, carriage pass suggests need for presser
            return int(Presser_Setting_Color.On)
        else:  # Auto, carriage pass does not need presser.
            return int(Presser_Setting_Color.Off)


def carriers_to_int(carrier_set: Yarn_Carrier_Set | None) -> int:
    """
    Args:
        carrier_set: The carrier set to convert to an integer for a DAT file.

    Returns:
        The integer that represents the carrier set.
    """
    if carrier_set is None or len(carrier_set) == 0:
        return NO_CARRIERS
    if len(carrier_set.carrier_ids) == 1:
        cid = carrier_set.carrier_ids[0]
        assert isinstance(cid, int)
        return cid
    elif len(carrier_set.carrier_ids) == 2:
        # Concatenate numbers with leading carrier first
        if carrier_set.carrier_ids[0] == 10:
            return int(f"10{carrier_set.carrier_ids[1]}")
        elif carrier_set.carrier_ids[1] == 10 and carrier_set.carrier_ids[0] != 1:
            return int(f"{carrier_set.carrier_ids[0]}0")
        else:
            return int(f"{carrier_set.carrier_ids[0]}{carrier_set.carrier_ids[1]}")
    else:
        # Default to first carrier for complex combinations
        cid = carrier_set.carrier_ids[0]
        assert isinstance(cid, int)
        return cid


def pixel_to_carriers(pixel_value: int) -> Yarn_Carrier_Set | None:
    """
    Convert a pixel value back to a list of carrier numbers.

    This mirrors the inverse logic of carriers_to_int():
    - NO_CARRIERS (0 or 255) -> empty list
    - Single carriers: pixel value = carrier number (1-10)
    - Two carriers: decode concatenated numbers with special handling for carrier 10

    Args:
        pixel_value: Integer pixel value from DAT file

    Returns:
        List of carrier numbers (each 1-10)
    """
    # Handle no carriers case
    if pixel_value == 0 or pixel_value == 255:  # NO_CARRIERS
        return None

    # Handle single carriers (1-10)
    if 1 <= pixel_value <= 10:
        return Yarn_Carrier_Set([pixel_value])

    # Handle two-carrier combinations
    pixel_str = str(pixel_value)

    # Case: carrier 10 is leading (format: "10X" where X is 1-9)
    if pixel_str.startswith('10') and len(pixel_str) == 3:
        second_carrier = int(pixel_str[2])
        if 1 <= second_carrier <= 9:
            return Yarn_Carrier_Set([10, second_carrier])

    # Case: carrier 10 is following (format: "X0" where X is 2-9, not 1)
    if pixel_str.endswith('0') and len(pixel_str) == 2:
        first_carrier = int(pixel_str[0])
        if 2 <= first_carrier <= 9:  # carrier_ids[0] != 1
            return Yarn_Carrier_Set([first_carrier, 10])

    # Case: regular two single-digit carriers (format: "XY" where X,Y are 1-9)
    if len(pixel_str) == 2:
        first_carrier = int(pixel_str[0])
        second_carrier = int(pixel_str[1])
        if 1 <= first_carrier <= 9 and 1 <= second_carrier <= 9:
            return Yarn_Carrier_Set([first_carrier, second_carrier])

    # If we can't decode it, return empty list and warn
    raise ValueError(f"Could not decode carrier value {pixel_value} to carrier set")
