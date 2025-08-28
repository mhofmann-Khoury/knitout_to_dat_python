"""A Module containing the Pixel Carriage Pass Converter Class.

This module provides functionality to convert pixel data from DAT files back into carriage pass objects and knitout instructions.
It serves as the inverse operation of the raster generation process, allowing DAT file data to be interpreted and converted back into knitting machine instructions.
"""
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.carrier_instructions import (
    Hook_Instruction,
    Inhook_Instruction,
    Outhook_Instruction,
    Releasehook_Instruction,
)
from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction
from knitout_interpreter.knitout_operations.knitout_instruction import (
    Knitout_Instruction,
)
from knitout_interpreter.knitout_operations.needle_instructions import (
    Drop_Instruction,
    Needle_Instruction,
    Split_Instruction,
    Xfer_Instruction,
)
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction
from knitout_interpreter.knitout_operations.Rack_Instruction import Rack_Instruction
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)

from knitout_to_dat_python.dat_file_structure.dat_codes.dat_file_color_codes import (
    OPTION_LINE_COUNT,
    STOPPING_MARK,
)
from knitout_to_dat_python.dat_file_structure.dat_codes.operation_colors import (
    Operation_Color,
)
from knitout_to_dat_python.dat_file_structure.dat_codes.option_lines import (
    Left_Option_Lines,
    Right_Option_Lines,
)
from knitout_to_dat_python.dat_file_structure.dat_codes.option_value_colors import (
    Amiss_Split_Hook_Color,
    Carriage_Pass_Direction_Color,
    Hook_Operation_Color,
    Pause_Color,
    Rack_Direction_Color,
    pixel_to_carriers,
)
from knitout_to_dat_python.kickback_injection.carriage_pass_with_kick import (
    Carriage_Pass_with_Kick,
)


class Pixel_Carriage_Pass_Converter:
    """A class to convert a row of pixels into a Raster Carriage Pass.

    This class takes pixel data from a DAT file row and converts it back into the corresponding carriage pass operations and instructions.
    It parses option lines, needle operations, and machine settings from the pixel representation.
    """

    def __init__(self, pixels: list[int], pattern_buffer: int = 4):
        """Initialize the Pixel_Carriage_Pass_Converter.

        Args:
            pixels (list[int]): The list of pixel values representing a row of DAT file data.
            pattern_buffer (int, optional): Buffer space around the pattern. Defaults to 4.
        """
        self.pixels: list[int] = pixels
        """list[int]: The pixel values from the DAT file row."""

        self.left_option_line_settings: dict[Left_Option_Lines, int] = {opt: 0 for opt in Left_Option_Lines}
        """dict[Left_Option_Lines, int]: Dictionary mapping left option lines to their values."""

        self._read_left_options()

        self.right_option_line_settings: dict[Right_Option_Lines, int] = {opt: 0 for opt in Right_Option_Lines}
        """dict[Right_Option_Lines, int]: Dictionary mapping right option lines to their values."""

        self._read_right_options()

        self.slot_colors: dict[int, Operation_Color] = {}
        """dict[int, Operation_Color]: Dictionary mapping slot numbers to their operation colors."""

        self.leftmost_slot = len(pixels)  # dummy maximum placeholder value
        """int: The leftmost slot with operations (initialized to maximum placeholder)."""

        self.rightmost_slot = 0  # dummy minimum placeholder value.
        """int: The rightmost slot with operations (initialized to minimum placeholder)."""

        self._read_needle_slots(pattern_buffer)

        self.direction: Carriage_Pass_Direction | None = None
        """Carriage_Pass_Direction | None: The direction of the carriage pass."""

        self._read_direction()

    def __repr__(self) -> str:
        """Return detailed string representation of the converter.

        Returns:
            str: String representation of the converter.
        """
        return str(self)

    def __str__(self) -> str:
        """Return string representation of the converter showing options and slots.

        Returns:
            str: String representation showing option settings and slot operations.
        """
        options = {o.name: v for o, v in self.left_option_line_settings.items()}
        options.update({o.name: v for o, v in self.right_option_line_settings.items()})
        slots = {s: o.name for s, o in self.slot_colors.items()}
        return f"{options}: {slots}"

    def _add_slot(self, slot: int, color: Operation_Color) -> None:
        """Add a slot operation and update the slot range bounds.

        Args:
            slot (int): The slot number to add.
            color (Operation_Color): The operation color for this slot.
        """
        self.slot_colors[slot] = color
        self.leftmost_slot = min(slot, self.leftmost_slot)
        self.rightmost_slot = max(slot, self.rightmost_slot)

    @property
    def pattern_width(self) -> int:
        """Get the width of the pattern from leftmost to rightmost operations.

        Returns:
            int: Width of the pattern from the leftmost to rightmost operations.
        """
        return self.rightmost_slot - self.leftmost_slot

    def _read_direction(self, check_both_left_and_right: bool = True) -> None:
        """Read and validate the carriage pass direction from pixels.

        Args:
            check_both_left_and_right (bool, optional): Whether to validate that left and right direction pixels match. Defaults to True.

        Raises:
            AssertionError: If check_both_left_and_right is True and left and right direction pixels don't match.
        """
        left_direction_pixel = self.pixels[(OPTION_LINE_COUNT * 2) - 1]
        if check_both_left_and_right:
            right_direction_pixel = self.pixels[-2 * OPTION_LINE_COUNT]
            assert left_direction_pixel == right_direction_pixel, f"Left and right direction pixels don't match: L={left_direction_pixel}, R={right_direction_pixel}"
        direction_color = Carriage_Pass_Direction_Color(left_direction_pixel)
        self.direction = direction_color.get_direction()

    def _read_left_options(self) -> None:
        """Read the option values from the left option line portion of the pattern.

        Raises:
            ValueError: If an unknown left option is encountered with a non-zero option value.
        """
        options_before_direction = OPTION_LINE_COUNT - 1
        option_area_width = 2 * options_before_direction
        for option_value, option in zip(self.pixels[0:option_area_width:2], self.pixels[1:option_area_width:2]):
            try:
                option_enum = Left_Option_Lines(option)
                self.left_option_line_settings[option_enum] = option_value
            except ValueError as e:  # Option  is not a known option_line value.
                if option_value != 0:
                    raise ValueError(f"Cannot set option value of {option_value} for unknown left option {option}") from e
                else:
                    continue

    def _read_right_options(self) -> None:
        """Read the option values from the right option line portion of the pattern.

        Raises:
            ValueError: If an unknown right option is encountered with a non-zero option value.
        """
        options_before_direction = OPTION_LINE_COUNT - 1
        option_area_width = -2 * options_before_direction
        for option, option_value in zip(self.pixels[option_area_width::2], self.pixels[option_area_width + 1::2]):
            try:
                self.right_option_line_settings[Right_Option_Lines(option)] = option_value
            except ValueError as e:  # Option  is not a known option_line value.
                if option_value != 0:
                    raise ValueError(f"Cannot set option value of {option_value} for unknown right option {option}") from e
                else:
                    continue

    def _read_needle_slots(self, buffer: int = 4) -> None:
        """Read needle slot operations from the pixel pattern.

        Parses the central portion of the pixel array to identify needle operations between stopping marks.
        Operations are identified by their color codes and mapped to slot positions.

        Args:
            buffer (int, optional): Buffer space around the pattern. Defaults to 4.
        """
        # Trim pixels of the option line boundaries, the left and right buffer, and a possible index of the right stop mark at the maximum width (i.e., -1)
        pattern = self.pixels[(2 * OPTION_LINE_COUNT) + buffer: (-2 * OPTION_LINE_COUNT) - buffer - 1]
        found_left_stop = pattern[0] == STOPPING_MARK
        pattern = pattern[1:]
        for slot, pixel in enumerate(pattern):
            if pixel == STOPPING_MARK:
                if not found_left_stop:
                    found_left_stop = True
                else:  # Found right stop
                    break
            elif found_left_stop:  # Inside pattern
                try:
                    self._add_slot(slot, Operation_Color(pixel))
                except ValueError as _e:
                    continue

    @property
    def hook_operation(self) -> Hook_Operation_Color | None:
        """Get the hook operation for the carriage pass.

        Returns:
            Hook_Operation_Color | None: The Hook operation for the carriage pass or None if the yarn-inserting hook is not in operation.
        """
        op_color = Hook_Operation_Color(self.right_option_line_settings[Right_Option_Lines.Hook_Operation])
        if op_color is Hook_Operation_Color.No_Hook_Operation:
            return None
        else:
            return op_color

    @property
    def stitch_number(self) -> int:
        """Get the specified stitch number for the operation.

        Returns:
            int: The specified stitch number for the operation.
        """
        return self.right_option_line_settings[Right_Option_Lines.Stitch_Number]

    @property
    def carrier_set(self) -> Yarn_Carrier_Set | None:
        """Get the carrier set to be used in this carriage pass.

        Returns:
            Yarn_Carrier_Set | None: The carrier set to be used in this carriage pass or None if no carrier is used.
        """
        carrier_number = self.right_option_line_settings[Right_Option_Lines.Yarn_Carrier_Number]
        return pixel_to_carriers(carrier_number)

    @property
    def is_all_needle_rack(self) -> bool:
        """Check if carriage pass is racked for all-needle racking.

        Returns:
            bool: True if carriage pass is racked for all-needle racking. False, otherwise.
        """
        offset = self.left_option_line_settings[Left_Option_Lines.Rack_Alignment]
        return offset != 0

    @property
    def rack(self) -> int:
        """Get the racking value for the carriage pass.

        Returns:
            int: The racking value (excluding all-needle-offset) for the given carriage pass.

        Raises:
            AssertionError: If rack amount is negative for rightward rack direction.
        """
        rack_amount = self.left_option_line_settings[Left_Option_Lines.Rack_Pitch]
        rack_direction = Rack_Direction_Color(self.left_option_line_settings[Left_Option_Lines.Rack_Direction])
        if rack_direction is Rack_Direction_Color.Right:
            assert rack_amount >= 0, f"Expected positive rack amount for rightward rack, got {rack_amount}"
            return rack_amount + 1
        elif rack_amount == 0:
            return rack_amount
        else:
            assert rack_direction is Rack_Direction_Color.Left
            return -1 * abs(rack_amount)

    @property
    def knit_speed(self) -> int:
        """Get the specified speed for the carriage pass.

        Returns:
            int: The specified speed for the carriage pass.
        """
        return self.left_option_line_settings[Left_Option_Lines.Knit_Speed]

    @property
    def holding_hook_carrier(self) -> None | int:
        """Get the yarn-inserting-hook's carrier value.

        Returns:
            int | None: The yarn-inserting-hook's carrier value (or None if no carrier is on the gripper).

        Raises:
            AssertionError: If outhook carrier expectations are not met (carrier 10 not first in set, or hook operation is not outhook).
        """
        carrier_number = self.right_option_line_settings[Right_Option_Lines.Carrier_Gripper]
        carrier_set = pixel_to_carriers(carrier_number)
        if carrier_set is None:
            return None
        elif len(carrier_set) == 1:
            cid = carrier_set.carrier_ids[0]
            assert isinstance(cid, int)
            return cid
        elif len(carrier_set) == 2:
            assert carrier_set.carrier_ids[0] == 10, f"Expected outhook carrier but got long carrier set of {carrier_set}"
            assert self.hook_operation is Hook_Operation_Color.Out_Hook_Operation, f"Got outhook carrier on gripper but hook operation is {self.hook_operation}"
            cid = carrier_set.carrier_ids[1]
            assert isinstance(cid, int)
            return cid

    def get_instructions_of_slot(self, slot: int, comment: str | None = None) -> list[Needle_Instruction]:
        """Get the knitout instructions for a specified slot.

        Converts the operation color at a given slot into the corresponding list of needle instructions,
        handling various operation types including single needle, all-needle, transfer, split, and drop operations.

        Args:
            slot (int): The slot to translate to knitout operations.
            comment (str | None, optional): An optional comment for the instruction. Defaults to None.

        Returns:
            list[Needle_Instruction]: The list of Knitout Instructions for the specified operation at the given slot.

        Raises:
            AssertionError:
                * If all-needle operation color is used without all-needle rack setting.
                * If all-needle operations are attempted without specified direction.
                * If split operations are attempted without proper split option line setting.
        """
        if comment is None:
            comment = ''

        def _rack_aligned_needle(n: Needle) -> Needle:
            """Find the needle aligned to the given needle at current racking.

            Note from Knitout Specification on Racking:
            Number indicating the offset of the front bed relative to the back bed.
            That is, at racking R, back needle index B is aligned to front needle index B+R.
            Needles are considered aligned if they can transfer.
            That is, at racking 2, it is possible to transfer from f3 to b1.
            F = B + R.
            R = F - B.
            B = F - R.

            Args:
                n (Needle): The needle to find the aligned needle at the current racking.

            Returns:
                Needle: The needle that is opposite the given needle at the current racking alignment.
            """
            if n.is_front:  # aligned position is on the back bed
                return Needle(is_front=False, position=n.position - self.rack)
            else:  # aligned position is on the front bed.
                return Needle(is_front=True, position=n.position + self.rack)

        def _get_single_needle_instruction(instruction_type: type, n: Needle) -> Needle_Instruction:
            """Create a needle instruction for a given type and needle.

            Args:
                instruction_type (type): The type of instruction to instantiate.
                n (Needle): The needle to instantiate the needle at.

            Returns:
                Needle_Instruction: A needle instruction based on the carriage pass values, instruction type, and given needle.
            """
            return instruction_type(n, self.direction, self.carrier_set, comment)

        operation_color = self.slot_colors[slot]
        first_operation, second_operation = operation_color.operation_types
        if second_operation is not None:
            assert self.is_all_needle_rack, f"Got all-needle operation color {operation_color} but not set for all needle rack"
            assert self.direction is not None, f"Cannot do all-needle operations without a specified direction."
            front_needle = Needle(is_front=True, position=slot)
            back_needle = _rack_aligned_needle(front_needle)
            if self.carrier_set is None:  # Convert to Drop operations
                return [Drop_Instruction(front_needle, comment), Drop_Instruction(back_needle, comment)]
            else:
                return [_get_single_needle_instruction(first_operation, front_needle),
                        _get_single_needle_instruction(second_operation, back_needle)]
        elif first_operation is Kick_Instruction:
            return [Kick_Instruction(slot, self.direction, self.carrier_set, comment)]
        elif first_operation == Xfer_Instruction or first_operation == Split_Instruction:  # 2 needle operations, need to check racking

            if operation_color.is_front:  # split or xfer from front to back
                needle = Needle(is_front=True, position=slot)
                needle_2 = _rack_aligned_needle(needle)
            else:
                assert operation_color.is_back
                needle_2 = Needle(is_front=True, position=slot)
                needle = _rack_aligned_needle(needle_2)
            if first_operation is Xfer_Instruction:
                return [Xfer_Instruction(needle, needle_2, comment)]
            else:  # Split operation
                assert self.left_option_line_settings[Left_Option_Lines.AMiss_Split_Flag] == Amiss_Split_Hook_Color.Split_Hook.value, f"Can't split without split option line set."
                return [Split_Instruction(needle, self.direction, needle_2, self.carrier_set, comment)]
        elif self.carrier_set is None:  # Drop Operation
            if operation_color.is_front:
                return [Drop_Instruction(Needle(is_front=True, position=slot), comment)]
            else:
                return [Drop_Instruction(Needle(is_front=False, position=slot-self.rack), comment)]
        elif operation_color.is_front:  # single operation with single needle
            return [_get_single_needle_instruction(first_operation, Needle(is_front=True, position=slot))]
        else:
            return [_get_single_needle_instruction(first_operation, Needle(is_front=False, position=slot-self.rack))]

    @property
    def has_prior_pause(self) -> bool:
        """Check if the carriage pass is set to pause.

        Returns:
            bool: True if the carriage pass is set to pause. False otherwise.
        """
        return self.left_option_line_settings[Left_Option_Lines.Pause_Option] == Pause_Color.Pause.value

    def get_prior_pause(self) -> None | Pause_Instruction:
        """Get a pause instruction if the carriage pass is set to pause.

        Returns:
            Pause_Instruction | None: A Pause_Instruction if the carriage pass is set to pause. None otherwise.
        """
        if self.has_prior_pause:
            return Pause_Instruction()
        else:
            return None

    def get_carriage_pass(self) -> Carriage_Pass:
        """Get the carriage pass that results from this row of pixels.

        Converts the parsed pixel data into a complete Carriage_Pass object with all instructions in the correct execution order based on direction.

        Returns:
            Carriage_Pass: The carriage pass that results from this row of pixels.

        Raises:
            AssertionError: If an instruction cannot be added to the carriage pass.
        """
        direction = self.direction
        if direction is None or direction is Carriage_Pass_Direction.Rightward:
            slots_in_operation_order: list[int] = [s for s in sorted(self.slot_colors.keys())]
        else:  # leftward direction:
            slots_in_operation_order: list[int] = [s for s in sorted(self.slot_colors.keys(), reverse=True)]
        instructions_in_order = []
        for slot in slots_in_operation_order:
            slot_instructions = self.get_instructions_of_slot(slot)
            instructions_in_order.extend(slot_instructions)
        if self.is_all_needle_rack and direction is not None:
            carriage_pass = Carriage_Pass(instructions_in_order[0], self.rack, all_needle_rack=True)
        else:
            carriage_pass = Carriage_Pass(instructions_in_order[0], self.rack, all_needle_rack=False)
        for instruction in instructions_in_order[1:]:
            if isinstance(instruction, Kick_Instruction) and not isinstance(carriage_pass, Carriage_Pass_with_Kick):  # convert to Kick carriage pass
                carriage_pass = Carriage_Pass_with_Kick(carriage_pass, kicks=[instruction])
            else:
                added = carriage_pass.add_instruction(instruction, rack=self.rack, all_needle_rack=self.is_all_needle_rack)
                assert added, f"Couldn't add {instruction} to {carriage_pass}"
        return carriage_pass

    def get_hook_instruction(self, release_carrier: int | None = None) -> None | Hook_Instruction:
        """Get the hook instruction associated with this carriage pass.

        Args:
            release_carrier (int | None, optional): The current carrier on the yarn-inserting hook to release. Defaults to None.

        Returns:
            Hook_Instruction | None: None if this carriage pass does not have a hook instruction. Otherwise, the hook instruction associated with the pass.

        Raises:
            AssertionError: If release_carrier is None when ReleaseHook_Operation is specified.
        """
        if self.hook_operation is None:
            return None
        elif self.hook_operation is Hook_Operation_Color.ReleaseHook_Operation:
            assert release_carrier is not None
            return Releasehook_Instruction(release_carrier)
        elif self.hook_operation is Hook_Operation_Color.In_Hook_Operation:
            return Inhook_Instruction(self.holding_hook_carrier)
        else:
            return Outhook_Instruction(self.holding_hook_carrier)

    def get_rack_instruction(self) -> Rack_Instruction:
        """Get the rack instruction that should precede this carriage pass.

        Returns:
            Rack_Instruction: The rack instruction that should proceed this carriage pass.
        """
        rack_value: float = float(self.rack)
        if self.is_all_needle_rack:
            rack_value += 0.25
        return Rack_Instruction(rack_value)

    def get_execution_process(self, release_carrier: int | None = None) -> list[Knitout_Instruction | Carriage_Pass | None]:
        """Get the complete execution process for this carriage pass.

        Returns a list of instructions and carriage passes in the correct execution order, including rack instructions, pause instructions, hook instructions, and the main carriage pass operation.

        Args:
            release_carrier (int | None, optional): The current carrier on the yarn-inserting hook to release. Defaults to None.

        Returns:
            list[Knitout_Instruction | Carriage_Pass | None]: A list of knitout instructions and the carriage pass used to execute this portion of the knitting process.
        """
        if self.hook_operation is Hook_Operation_Color.In_Hook_Operation or self.hook_operation is Hook_Operation_Color.ReleaseHook_Operation:
            return [self.get_rack_instruction(), self.get_prior_pause(), self.get_hook_instruction(release_carrier),  self.get_carriage_pass()]
        elif self.hook_operation is Hook_Operation_Color.Out_Hook_Operation:
            return [self.get_rack_instruction(), self.get_carriage_pass(),  self.get_prior_pause(), self.get_hook_instruction()]
        else:
            return [self.get_rack_instruction(), self.get_prior_pause(), self.get_carriage_pass()]
