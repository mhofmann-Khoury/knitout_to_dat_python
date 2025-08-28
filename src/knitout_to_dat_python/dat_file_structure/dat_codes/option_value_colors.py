"""Module of Enumerations for common color codes to Option Lines.

This module provides enumerations for various option line color codes used in DAT files,
along with utility functions for converting between different representations and determining appropriate settings based on carriage pass characteristics.
"""
from __future__ import annotations

from enum import Enum

from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)

from knitout_to_dat_python.dat_file_structure.dat_codes.dat_file_color_codes import (
    NO_CARRIERS,
)


class Link_Process_Color(Enum):
    """Enumeration of the Links Process color options.

    This enumeration defines color codes for link process operations in DAT files.
    """
    Ignore_Link_Process = 1
    """int: Color code to ignore link process operations."""

    def __str__(self) -> str:
        """Return string representation of the link process color.

        Returns:
            str: The name of the link process color enumeration.
        """
        return self.name

    def __repr__(self) -> str:
        """Return detailed string representation of the link process color.

        Returns:
            str: String representation of the link process color.
        """
        return str(self)

    def __int__(self) -> int:
        """Return integer value of the link process color.

        Returns:
            int: The integer value associated with this link process color.
        """
        return self.value

    def __hash__(self) -> int:
        """Return hash value of the link process color.

        Returns:
            int: Hash value based on the integer value of the link process color.
        """
        return int(self)


class Drop_Sinker_Color(Enum):
    """Enumeration of color codes for the drop-sinker option line.

    This enumeration defines color codes that control drop-sinker functionality in knitting machine operations.
    """
    Standard = 0
    """int: Standard drop-sinker setting."""

    Drop_Sinker = 11
    """int: Active drop-sinker setting."""

    def __str__(self) -> str:
        """Return string representation of the drop sinker color.

        Returns:
            str: The name of the drop sinker color enumeration.
        """
        return self.name

    def __repr__(self) -> str:
        """Return detailed string representation of the drop sinker color.

        Returns:
            str: String representation of the drop sinker color.
        """
        return str(self)

    def __int__(self) -> int:
        """Return integer value of the drop sinker color.

        Returns:
            int: The integer value associated with this drop sinker color.
        """
        return self.value

    def __hash__(self) -> int:
        """Return hash value of the drop sinker color.

        Returns:
            int: Hash value based on the integer value of the drop sinker color.
        """
        return int(self)


class Amiss_Split_Hook_Color(Enum):
    """Enumeration of color codes for the Amiss_Split_Hook option line.

    This enumeration defines color codes for amiss split hook operations in knitting machine control.
    """
    Split_Hook = 10
    """int: Color code for split hook operation."""

    def __str__(self) -> str:
        """Return string representation of the amiss split hook color.

        Returns:
            str: The name of the amiss split hook color enumeration.
        """
        return self.name

    def __repr__(self) -> str:
        """Return detailed string representation of the amiss split hook color.

        Returns:
            str: String representation of the amiss split hook color.
        """
        return str(self)

    def __int__(self) -> int:
        """Return integer value of the amiss split hook color.

        Returns:
            int: The integer value associated with this amiss split hook color.
        """
        return self.value

    def __hash__(self) -> int:
        """Return hash value of the amiss split hook color.

        Returns:
            int: Hash value based on the integer value of the amiss split hook color.
        """
        return int(self)


class Pause_Color(Enum):
    """Enumeration of Pause Color Codes for pause/reset option Line.

    This enumeration defines color codes for pause and reset operations in knitting machine control sequences.
    """
    Pause = 20
    """int: Color code for pause operation."""

    def __str__(self) -> str:
        """Return string representation of the pause color.

        Returns:
            str: The name of the pause color enumeration.
        """
        return self.name

    def __repr__(self) -> str:
        """Return detailed string representation of the pause color.

        Returns:
            str: String representation of the pause color.
        """
        return str(self)

    def __int__(self) -> int:
        """Return integer value of the pause color.

        Returns:
            int: The integer value associated with this pause color.
        """
        return self.value

    def __hash__(self) -> int:
        """Return hash value of the pause color.

        Returns:
            int: Hash value based on the integer value of the pause color.
        """
        return int(self)


class Hook_Operation_Color(Enum):
    """Enumeration of yarn-inserting-hook operation colors.

    This enumeration defines color codes for different yarn-inserting-hook operations used in knitting machine control.
    """
    No_Hook_Operation = 0
    """int: No hook operation active."""

    In_Hook_Operation = 10
    """int: Hook insertion operation."""

    Out_Hook_Operation = 20
    """int: Hook extraction operation."""

    ReleaseHook_Operation = 90
    """int: Hook release operation."""

    def __str__(self) -> str:
        """Return string representation of the hook operation color.

        Returns:
            str: The name of the hook operation color enumeration.
        """
        return self.name

    def __repr__(self) -> str:
        """Return detailed string representation of the hook operation color.

        Returns:
            str: String representation of the hook operation color.
        """
        return str(self)

    def __int__(self) -> int:
        """Return integer value of the hook operation color.

        Returns:
            int: The integer value associated with this hook operation color.
        """
        return self.value

    def __hash__(self) -> int:
        """Return hash value of the hook operation color.

        Returns:
            int: Hash value based on the integer value of the hook operation color.
        """
        return int(self)


class Knit_Cancel_Color(Enum):
    """Enumeration of color options for the knit cancel setting.

    This enumeration defines color codes for different knit cancel and carriage movement options in knitting operations.
    """
    Knit_Cancel = 1
    """int: Used in Transfers."""

    Carriage_Move = 2
    """int: Used if a carriage needs to repeat its last direction."""

    Standard = 0
    """int: Standard knit cancel setting."""

    def __str__(self) -> str:
        """Return string representation of the knit cancel color.

        Returns:
            str: The name of the knit cancel color enumeration.
        """
        return self.name

    def __repr__(self) -> str:
        """Return detailed string representation of the knit cancel color.

        Returns:
            str: String representation of the knit cancel color.
        """
        return str(self)

    def __int__(self) -> int:
        """Return integer value of the knit cancel color.

        Returns:
            int: The integer value associated with this knit cancel color.
        """
        return self.value

    def __hash__(self) -> int:
        """Return hash value of the knit cancel color.

        Returns:
            int: Hash value based on the integer value of the knit cancel color.
        """
        return int(self)


class Transfer_Type_Color(Enum):
    """Enumeration of transfer slider options.

    This enumeration defines color codes for different transfer slider configurations used in knitting machine operations.
    """
    To_Sliders = 1
    """int: Transfer operation to sliders."""

    From_Sliders = 3
    """int: Transfer operation from sliders."""

    No_Sliders = 0
    """int: No slider involvement in transfer."""

    def __str__(self) -> str:
        """Return string representation of the transfer type color.

        Returns:
            str: The name of the transfer type color enumeration.
        """
        return self.name

    def __repr__(self) -> str:
        """Return detailed string representation of the transfer type color.

        Returns:
            str: String representation of the transfer type color.
        """
        return str(self)

    def __int__(self) -> int:
        """Return integer value of the transfer type color.

        Returns:
            int: The integer value associated with this transfer type color.
        """
        return self.value

    def __hash__(self) -> int:
        """Return hash value of the transfer type color.

        Returns:
            int: Hash value based on the integer value of the transfer type color.
        """
        return int(self)


class Rack_Direction_Color(Enum):
    """Enumeration of the color codes to specify leftward or rightward racking.

    This enumeration defines color codes for controlling the direction of rack movement in knitting machine operations.
    """
    Left = 10
    """int: Leftward rack direction."""

    Right = 11
    """int: Rightward rack direction."""

    def __str__(self) -> str:
        """Return string representation of the rack direction color.

        Returns:
            str: The name of the rack direction color enumeration.
        """
        return self.name

    def __repr__(self) -> str:
        """Return detailed string representation of the rack direction color.

        Returns:
            str: String representation of the rack direction color.
        """
        return str(self)

    def __int__(self) -> int:
        """Return integer value of the rack direction color.

        Returns:
            int: The integer value associated with this rack direction color.
        """
        return self.value

    def __hash__(self) -> int:
        """Return hash value of the rack direction color.

        Returns:
            int: Hash value based on the integer value of the rack direction color.
        """
        return int(self)


class Rack_Pitch_Color(Enum):
    """Enumeration of the color codes to specify all-needle racking pitch.

    This enumeration defines color codes for controlling rack pitch settings in all-needle racking operations.
    """
    All_Needle = 1
    """int: All-needle racking pitch setting."""

    Standard = 0
    """int: Standard racking pitch setting."""

    def __str__(self) -> str:
        """Return string representation of the rack pitch color.

        Returns:
            str: The name of the rack pitch color enumeration.
        """
        return self.name

    def __repr__(self) -> str:
        """Return detailed string representation of the rack pitch color.

        Returns:
            str: String representation of the rack pitch color.
        """
        return str(self)

    def __int__(self) -> int:
        """Return integer value of the rack pitch color.

        Returns:
            int: The integer value associated with this rack pitch color.
        """
        return self.value

    def __hash__(self) -> int:
        """Return hash value of the rack pitch color.

        Returns:
            int: Hash value based on the integer value of the rack pitch color.
        """
        return int(self)


class Carriage_Pass_Direction_Color(Enum):
    """Enumeration of the color codes to specify carriage pass direction.

    This enumeration defines color codes for controlling carriage pass direction
    in knitting machine operations, including leftward, rightward, and unspecified
    directions.
    """
    Leftward = 7
    """int: Leftward carriage pass direction."""

    Rightward = 6
    """int: Rightward carriage pass direction."""

    Unspecified = 1
    """int: Unspecified carriage pass direction."""

    def get_direction(self) -> Carriage_Pass_Direction | None:
        """Get the corresponding carriage pass direction.

        Returns:
            Carriage_Pass_Direction | None: The corresponding carriage pass direction for the enumeration.
                None if the direction is unspecified.
        """
        if self is Carriage_Pass_Direction_Color.Leftward:
            return Carriage_Pass_Direction.Leftward
        elif self is Carriage_Pass_Direction_Color.Rightward:
            return Carriage_Pass_Direction.Rightward
        else:
            return None

    def __str__(self) -> str:
        """Return string representation of the carriage pass direction color.

        Returns:
            str: The name of the carriage pass direction color enumeration.
        """
        return self.name

    def __repr__(self) -> str:
        """Return detailed string representation of the carriage pass direction color.

        Returns:
            str: String representation of the carriage pass direction color.
        """
        return str(self)

    def __int__(self) -> int:
        """Return integer value of the carriage pass direction color.

        Returns:
            int: The integer value associated with this carriage pass direction color.
        """
        return self.value

    def __hash__(self) -> int:
        """Return hash value of the carriage pass direction color.

        Returns:
            int: Hash value based on the integer value of the carriage pass direction color.
        """
        return int(self)

    @staticmethod
    def get_carriage_pass_direction_color(carriage_pass: Carriage_Pass) -> Carriage_Pass_Direction_Color:
        """Get the direction color corresponding to the given carriage pass direction.

        Args:
            carriage_pass (Carriage_Pass): The carriage pass to determine the pass direction color from.

        Returns:
            Carriage_Pass_Direction_Color: The direction color corresponding to the given carriage pass direction.
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
    """An enumeration of the possible presser mode settings for a carriage pass.

    This enumeration defines color codes for different presser mode settings that control presser behavior during carriage pass operations.
    """
    On = 101
    """int: Presser mode enabled."""

    Off = 0
    """int: Presser mode disabled."""

    Auto = 0
    """int: Automatic presser mode (same value as Off, determined dynamically)."""

    def __int__(self) -> int:
        """Return integer value of the presser setting color.

        Returns:
            int: The integer value associated with this presser setting color.
        """
        return self.value

    def __str__(self) -> str:
        """Return string representation of the presser setting color.

        Returns:
            str: The name of the presser setting color enumeration.
        """
        return self.name

    def __hash__(self) -> int:
        """Return hash value of the presser setting color.

        Returns:
            int: Hash value based on the presser setting color value.
        """
        return int(self)

    def __repr__(self) -> str:
        """Return detailed string representation of the presser setting color.

        Returns:
            str: String representation of the presser setting color.
        """
        return str(self)

    @staticmethod
    def should_use_presser_mode(carriage_pass: Carriage_Pass) -> bool:
        """Determine if presser mode should be used for a carriage pass.

        A presser mode should be used if the yarn-inserting-hook is not active and there are not mixed front/back needles operations in the carriage pass.

        Args:
            carriage_pass (Carriage_Pass): The carriage pass to interpret the need for presser mode.

        Returns:
            bool: True if the given carriage pass does not have mixed front/back needles and thus should use the presser.
        """
        has_front = any(needle.is_front for needle in carriage_pass.needles)
        has_back = any(not needle.is_front for needle in carriage_pass.needles)
        return not (has_front and has_back)  # Don't use presser for mixed front/back

    def presser_option(self, carriage_pass: Carriage_Pass) -> int:
        """Get the color-code for the presser mode based on carriage pass characteristics.

        Args:
            carriage_pass (Carriage_Pass): The carriage pass used to determine mode in Auto-Mode.

        Returns:
            int: The color-code for the presser mode. If auto-mode, this is dynamically determined by the carriage pass.
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
    """Convert a carrier set to an integer representation for DAT files.

    This function converts yarn carrier sets to integer values used in DAT files.
    It handles single carriers, dual carrier combinations, and special cases involving carrier 10.

    Args:
        carrier_set (Yarn_Carrier_Set | None): The carrier set to convert to an integer for a DAT file.

    Returns:
        int: The integer that represents the carrier set.
        * Returns NO_CARRIERS (255) if carrier_set is None or empty.
        * For single carriers, returns the carrier ID.
        * For dual carriers, returns concatenated numbers with special handling for carrier 10.
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
    """Convert a pixel value back to a yarn carrier set.

    This function mirrors the inverse logic of carriers_to_int() to decode pixel values from DAT files back into yarn carrier sets.
    It handles the special encoding used for carrier combinations, particularly the special cases involving carrier 10.

    Args:
        pixel_value (int): Integer pixel value from DAT file representing carrier information.

    Returns:
        Yarn_Carrier_Set | None: Yarn carrier set containing the decoded carrier numbers (each 1-10), or None if no carriers are specified (pixel_value is 0 or 255).

    Raises:
        ValueError: If the pixel value cannot be decoded to a valid carrier set.

    Note:
        Pixel value encoding rules:
        * NO_CARRIERS (0 or 255) -> None
        * Single carriers: pixel value = carrier number (1-10)
        * Two carriers: decode concatenated numbers with special handling for carrier 10
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
