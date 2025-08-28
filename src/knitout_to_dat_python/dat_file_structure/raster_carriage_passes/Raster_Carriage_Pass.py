"""Raster_Pass class that wraps Carriage_Pass to extract DAT file generation information.

This module provides the Raster_Carriage_Pass class, which wraps Carriage_Pass objects to extract information needed for DAT raster generation.
It converts knitout operations into colored pixels and option line settings based on the original knitout-to-dat.js raster generation logic.
"""

from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.knitout_instruction import (
    Knitout_Instruction_Type,
)
from virtual_knitting_machine.Knitting_Machine_Specification import (
    Knitting_Machine_Specification,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.needles.Needle import Needle

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
    Drop_Sinker_Color,
    Hook_Operation_Color,
    Knit_Cancel_Color,
    Link_Process_Color,
    Pause_Color,
    Presser_Setting_Color,
    Rack_Direction_Color,
    Rack_Pitch_Color,
    carriers_to_int,
)


class Raster_Carriage_Pass:
    """Wrapper for Carriage_Pass that extracts information needed for DAT raster generation.

    This class converts knitout operations into colored pixels and option line settings that can be used to generate DAT file raster data.
    It processes carriage pass instructions and machine settings to create the appropriate pixel representation.
    """

    def __init__(self, carriage_pass: Carriage_Pass, machine_specification: Knitting_Machine_Specification, min_knitting_slot: int, max_knitting_slot: int,
                 hook_operation: Hook_Operation_Color = Hook_Operation_Color.No_Hook_Operation,
                 stitch_number: int = 5, speed_number: int = 0, presser_setting: Presser_Setting_Color = Presser_Setting_Color.Off,
                 pause: bool = False,
                 knit_cancel: Knit_Cancel_Color = Knit_Cancel_Color.Standard, drop_sinker: bool = False):
        """Initialize a Raster_Pass from a Carriage_Pass.

        Args:
            carriage_pass (Carriage_Pass): The carriage pass to wrap.
            machine_specification (Knitting_Machine_Specification): The machine specification for the knitout file specified in the knitout header.
            min_knitting_slot (int): The minimum slot of knitting operations in this file.
            max_knitting_slot (int): The maximum slot of knitting operations in this file.
            hook_operation (Hook_Operation_Color, optional): The operation of the yarn-inserting hook for this carrier. Defaults to Hook_Operation_Color.No_Hook_Operation.
            stitch_number (int, optional): Current stitch setting. Defaults to 5.
            speed_number (int, optional): Current speed setting. Defaults to 0.
            presser_setting (Presser_Setting_Color, optional): Current presser mode ('on', 'off', 'auto'). Defaults to Presser_Setting_Color.Off.
            pause (bool, optional): Whether this pass should pause. Defaults to False.
            knit_cancel (Knit_Cancel_Color, optional): Knit cancel mode setting. Will be reset to true for transfer carriage passes. Defaults to Knit_Cancel_Color.Standard.
            drop_sinker (bool, optional): Set to true to set "drop failure, sinker reset". Defaults to False.

        Raises:
            AssertionError: If inhook operation is attempted on a rightward knitting pass.
        """
        self.drop_sinker: bool = drop_sinker
        """bool: Whether drop sinker mode is enabled."""

        self.carriage_pass: Carriage_Pass = carriage_pass
        """Carriage_Pass: The wrapped carriage pass object."""

        self._knit_cancel: Knit_Cancel_Color = Knit_Cancel_Color.Standard
        """Knit_Cancel_Color: The knit cancel setting for this pass."""

        self._hook_operation: Hook_Operation_Color = hook_operation
        """Hook_Operation_Color: The hook operation setting for this pass."""

        if self.hook_operation is Hook_Operation_Color.In_Hook_Operation:
            assert self.carriage_pass.direction is Carriage_Pass_Direction.Leftward, f"Knitout Error: Cannot inhook on a rightward knitting pass."

        self.max_knitting_slot: int = max_knitting_slot
        """int: The maximum slot of knitting operations in this file."""

        self.min_knitting_slot: int = min_knitting_slot
        """int: The minimum slot of knitting operations in this file."""

        self.machine_specification: Knitting_Machine_Specification = machine_specification
        """Knitting_Machine_Specification: The machine specification for the knitout file."""

        self.stitch_number: int = stitch_number
        """int: Current stitch setting."""

        self.speed_number: int = speed_number
        """int: Current speed setting."""

        self.presser_setting: Presser_Setting_Color = presser_setting
        """Presser_Setting_Color: Current presser mode setting."""

        self._pause: bool = pause
        """bool: Whether this pass should pause."""

        # Process the carriage pass into raster data
        self.slot_colors: dict[int, Operation_Color] = {}  # slot_number -> color_code
        """dict[int, Operation_Color]: Dictionary mapping slot numbers to their operation color codes."""

        self.left_option_line_settings: dict[Left_Option_Lines, int] = {opt: 0 for opt in Left_Option_Lines}
        """dict[Left_Option_Lines, int]: Dictionary of left option line settings."""

        self.right_option_line_settings: dict[Right_Option_Lines, int] = {opt: 0 for opt in Right_Option_Lines}
        """dict[Right_Option_Lines, int]: Dictionary of right option line settings."""

        self._process_operations()
        self._set_option_lines()
        self.knit_cancel = knit_cancel

    @property
    def knit_cancel(self) -> Knit_Cancel_Color:
        """Get the value of the knit-cancel option.

        Returns:
            Knit_Cancel_Color: Value of the knit-cancel option.
        """
        return self._knit_cancel

    @knit_cancel.setter
    def knit_cancel(self, value: Knit_Cancel_Color) -> None:
        """Set the knit-cancel option value.

        Automatically sets knit cancel to Knit_Cancel for transfer passes.

        Args:
            value (Knit_Cancel_Color): The knit cancel setting to apply.
        """
        if self.carriage_pass.xfer_pass:
            self._knit_cancel = Knit_Cancel_Color.Knit_Cancel
        else:
            self._knit_cancel = value
        self._set_knit_cancel_option()

    def shift_slot_colors(self, shift: int) -> None:
        """Shift the slot numbers of the carriage pass by the given amount.

        Args:
            shift (int): The amount to shift the slots by.
        """
        if shift != 0:
            self.slot_colors = {s + shift: c for s, c in self.slot_colors.items()}

    @property
    def hook_operation(self) -> Hook_Operation_Color:
        """Get the hook operation for the given carriage pass.

        Returns:
            Hook_Operation_Color: The Hook operation for the given carriage pass.
        """
        return self._hook_operation

    @hook_operation.setter
    def hook_operation(self, hook_operation: Hook_Operation_Color) -> None:
        """Set the hook operation and update option lines.

        Args:
            hook_operation (Hook_Operation_Color): The hook operation to set.
        """
        self._hook_operation = hook_operation
        self._set_option_lines()

    @property
    def empty_pass(self) -> bool:
        """Check if there are no needle operations in this carriage pass.

        Returns:
            bool: True if there are no needle operations in this carriage pass.
        """
        return len(self.carriage_pass) == 0

    @property
    def min_slot(self) -> int | None:
        """Get the leftmost slot that operations will occur on.

        Returns:
            int | None: None if there are no needle operations in this carriage pass. Otherwise, return the leftmost slot that operations will occur on.
        """
        if self.empty_pass:
            return None
        return min(self.slot_colors)

    @property
    def max_slot(self) -> int | None:
        """Get the rightmost slot that operations will occur on.

        Returns:
            int | None: None if there are no needle operations in this carriage pass.  Otherwise, return the rightmost slot that operations will occur on.
        """
        if self.empty_pass:
            return None
        return max(self.slot_colors)

    def _process_operations(self) -> None:
        """Process carriage pass operations into colored pixels.

        Converts each needle instruction in the carriage pass to its corresponding operation color and maps it to the appropriate slot position.
        Handles all-needle operations by combining multiple operation colors.

        Raises:
            RuntimeError: If all-needle operations cannot be combined for a given slot.
        """
        rightward_order_needles = self.carriage_pass.rightward_sorted_needles()
        needle_instructions = self.carriage_pass.instructions_by_needles(rightward_order_needles)
        for instruction in needle_instructions:
            slot_number = self._needle_to_slot(instruction.needle)
            instruction_color = Operation_Color.get_operation_color(instruction)
            if slot_number in self.slot_colors:  # An instruction is already set for this slot
                assert self.carriage_pass.all_needle_rack, f"Cannot do two operations on slot {slot_number} unless all-needle-knitting."
                cur_instruction_color = self.slot_colors[slot_number]
                all_needle_color = instruction_color.get_all_needle(cur_instruction_color)
                if all_needle_color is None:
                    raise RuntimeError(f"Cannot all needle {cur_instruction_color} and {instruction_color} on slot {slot_number}")
                else:
                    assert isinstance(all_needle_color, Operation_Color)
                    instruction_color = all_needle_color
            self.slot_colors[slot_number] = instruction_color

    def _needle_to_slot(self, needle: Needle) -> int:
        """Convert needle to slot number (accounting for racking).

        Args:
            needle (Needle): The needle to convert to a slot number.

        Returns:
            int: The slot number corresponding to the needle position.
        """
        assert isinstance(needle.position, int)
        if needle.is_front:
            return needle.position
        else:
            assert isinstance(self.carriage_pass.rack, int)
            return needle.position + self.carriage_pass.rack

    def _set_option_lines(self) -> None:
        """Set all option lines based on carriage pass instructions and specified knitting parameters.

        Configures all left and right option line settings based on the carriage pass characteristics, machine settings, and operational parameters.
        """
        self._set_ignore_link_process_option()
        self._set_carrier_options()
        self._set_rack_options()
        self._set_stitch_number_option()
        self._set_speed_options()
        self._set_transfer_stitch_option()
        self._set_presser_mode_option()
        self._set_pause_option()
        self._set_direction_options()
        self._set_drop_sinker_option()
        self._set_knit_cancel_option()
        self._set_amiss_split_hook_options()

    @property
    def has_splits(self) -> bool:
        """Check if the carriage pass has split operations.

        Returns:
            bool: True if the carriage pass has splits. False otherwise.
        """
        return bool(self.carriage_pass.contains_instruction_type(Knitout_Instruction_Type.Split))

    def _set_amiss_split_hook_options(self) -> None:
        """Set the amiss_split_hook options based on carriage pass instruction types.

        Configures the split hook option line if the carriage pass contains split operations.
        """
        if self.has_splits:
            self.left_option_line_settings[Left_Option_Lines.AMiss_Split_Flag] = int(Amiss_Split_Hook_Color.Split_Hook)

    def _set_drop_sinker_option(self) -> None:
        """Set the drop-sinker option line.

        Configures the drop sinker option line based on the drop_sinker setting.
        """
        if self.drop_sinker:
            self.right_option_line_settings[Right_Option_Lines.Drop_Sinker] = int(Drop_Sinker_Color.Drop_Sinker)

    def _set_ignore_link_process_option(self) -> None:
        """Set the ignore_link_process_option flag to True.

        This option is always true for knitout processes and configures the link process option line accordingly.
        """
        self.right_option_line_settings[Right_Option_Lines.Links_Process] = int(Link_Process_Color.Ignore_Link_Process)

    def _set_carrier_options(self) -> None:
        """Set the carrier and yarn-inserting-hook option lines.

        Configures carrier-related option lines including yarn carrier numbers, hook operations, and carrier gripper settings based on the carriage pass characteristics and hook operation type.

        Raises:
            AssertionError: If hook operation is not No_Hook_Operation for transfer passes.
        """
        if self.carriage_pass.xfer_pass:
            self.right_option_line_settings[Right_Option_Lines.Yarn_Carrier_Number] = 0
            assert self.hook_operation is Hook_Operation_Color.No_Hook_Operation
        else:
            carriers_int = carriers_to_int(self.carriage_pass.carrier_set)
            self.right_option_line_settings[Right_Option_Lines.Yarn_Carrier_Number] = carriers_int
            self.right_option_line_settings[Right_Option_Lines.Hook_Operation] = int(self.hook_operation)
            if self.hook_operation is Hook_Operation_Color.In_Hook_Operation:
                self.right_option_line_settings[Right_Option_Lines.Carrier_Gripper] = carriers_int
            elif self.hook_operation is Hook_Operation_Color.Out_Hook_Operation:
                self.right_option_line_settings[Right_Option_Lines.Carrier_Gripper] = 100 + carriers_int  # outhook carrier numbers are set with the 100 value.

    def _set_rack_options(self) -> None:
        """Set the racking option lines.

        Configures rack direction, pitch, and alignment option lines based on the carriage pass rack settings and all-needle rack configuration.

        Raises:
            ValueError: If racking value exceeds the machine's maximum rack specification.
        """
        rack: int = self.carriage_pass.rack
        if abs(rack) > self.machine_specification.maximum_rack:
            raise ValueError(f"Knitout: Racking value ({rack}) is greater than maximum specified rack of {self.machine_specification.maximum_rack}")
        if rack >= 1.0:  # Rightward racking
            self.left_option_line_settings[Left_Option_Lines.Rack_Direction] = int(Rack_Direction_Color.Right)
            self.left_option_line_settings[Left_Option_Lines.Rack_Pitch] = rack - 1  # Rightward racking amount
        else:
            self.left_option_line_settings[Left_Option_Lines.Rack_Direction] = int(Rack_Direction_Color.Left)
            self.left_option_line_settings[Left_Option_Lines.Rack_Pitch] = abs(rack)  # Negative (leftward) racks are adjusted to be positive values.
        # Quarter pitch setting for All needle Racking
        self.left_option_line_settings[Left_Option_Lines.Rack_Alignment] = int(Rack_Pitch_Color.Standard if not self.carriage_pass.all_needle_rack else Rack_Pitch_Color.All_Needle)

    def _set_stitch_number_option(self) -> None:
        """Set the stitch number option line.

        Configures the stitch number option line with the current stitch setting.
        """
        self.right_option_line_settings[Right_Option_Lines.Stitch_Number] = self.stitch_number

    def _set_speed_options(self) -> None:
        """Set the speed option lines.

        Configures both knit speed and transfer speed option lines. Speed values are adjusted by adding 10 when non-zero (following original js-dat compiler logic).

        Note:
            10 is added to non-zero speed values in js-dat compiler. Reason unclear.
        """
        speed_value = 0 if self.speed_number == 0 else self.speed_number + 10  # Note: 10 added in js-dat compiler. Not sure why.
        self.left_option_line_settings[Left_Option_Lines.Knit_Speed] = speed_value
        self.left_option_line_settings[Left_Option_Lines.Transfer_Speed] = speed_value  # Transfer speed

    def _set_knit_cancel_option(self) -> None:
        """Set the option line for the knit cancel status.

        Configures the knit cancel or carriage move option line based on the current knit cancel setting.
        """
        self.right_option_line_settings[Right_Option_Lines.Knit_Cancel_or_Carriage_Move] = int(self.knit_cancel)

    def _set_transfer_stitch_option(self) -> None:
        """Set the stitch numbers for transfers.

        Note:
            How is this used in the JS compiler? This doesn't seem to apply in test samples.
        """
        pass  # Note: How is this used in the JS compiler? This doesn't seem to apply in test samples.

    def _set_presser_mode_option(self) -> None:
        """Set the presser mode option line.

        Configures the presser mode option line based on the presser setting and carriage pass characteristics.
        """
        self.right_option_line_settings[Right_Option_Lines.Presser_Mode] = self.presser_setting.presser_option(self.carriage_pass)

    def _set_pause_option(self) -> None:
        """Set the pause option line.

        Configures the pause option line if pause is enabled for this pass.
        """
        if self.pause:
            self.left_option_line_settings[Left_Option_Lines.Pause_Option] = int(Pause_Color.Pause)

    @property
    def pause(self) -> bool:
        """Check if this carriage pass will have a pause option.

        Returns:
            bool: True if this carriage pass will have a pause option.
        """
        return self._pause

    @pause.setter
    def pause(self, value: bool) -> None:
        """Set the pause option for this carriage pass.

        Args:
            value (bool): Whether this pass should pause.
        """
        self._pause = value
        self._set_pause_option()

    @property
    def direction_color(self) -> Carriage_Pass_Direction_Color:
        """Get the direction color for this raster Carriage Pass.

        Returns:
            Carriage_Pass_Direction_Color: The direction color of for this raster Carriage Pass.
        """
        return Carriage_Pass_Direction_Color.get_carriage_pass_direction_color(self.carriage_pass)

    def _set_direction_options(self) -> None:
        """Set the direction option lines based on the carriage pass's direction.

        Configures both left and right direction specification option lines with the same direction color value.
        """
        direction_color = self.direction_color
        self.left_option_line_settings[Left_Option_Lines.Direction_Specification] = int(direction_color)
        self.right_option_line_settings[Right_Option_Lines.Direction_Specification] = int(direction_color)

    def _should_use_presser(self) -> bool:
        """Determine if presser should be used when auto-mode is specified.

        A presser should be used if the hook is not active and there are not mixed front/back bed needle operations.

        Returns:
            bool: True if presser should be used when auto-mode is specified.
        """
        has_front = any(needle.is_front for needle in self.carriage_pass.needles)
        has_back = any(not needle.is_front for needle in self.carriage_pass.needles)
        return not (has_front and has_back)  # Don't use presser for mixed front/back

    def get_slot_range(self) -> tuple[int, int]:
        """Get the range of slots this pass operates on.

        Returns:
            tuple[int, int]: The range of slots this pass operates on. Returns (0, 0) for empty passes.
        """
        if self.empty_pass:
            return 0, 0
        assert self.min_slot is not None
        assert self.max_slot is not None
        return self.min_slot, self.max_slot

    def _get_stopping_marks(self) -> tuple[int, int]:
        """Get the stopping mark positions (before and after the pass).

        Returns:
            tuple[int, int]: The stopping mark positions (before and after the pass). Returns (0, 0) if no slot colors are defined.
        """
        if not self.slot_colors:
            return 0, 0
        min_slot, max_slot = self.get_slot_range()
        return min_slot - 1, max_slot + 1

    @staticmethod
    def raster_width(pattern_width: int, option_space: int = 10, pattern_space: int = 4) -> int:
        """Calculate the expected width of a raster row.

        Args:
            pattern_width (int): Width of the knitting pattern.
            option_space (int, optional): Spacing around the exterior of the option lines. Defaults to 10.
            pattern_space (int, optional): Spacing between option lines and the knitting pattern. Defaults to 4.

        Returns:
            int: The expected width of a raster row with the given width parameters.
        """
        return 2 * ((OPTION_LINE_COUNT * 2) + option_space + pattern_space) + pattern_width + 2

    def get_raster_row(self, pattern_width: int, option_space: int = 10, pattern_space: int = 4, offset_slots: int = 0) -> list[int]:
        """Generate the complete raster row for this carriage pass.

        Creates the full pixel representation of this carriage pass including
        left option lines, needle operations, and right option lines.

        Args:
            pattern_width (int): The width of the knitting pattern.
            option_space (int, optional): The spacing around the option lines. Defaults to 10.
            pattern_space (int, optional): The spacing between option lines and the pattern. Defaults to 4.
            offset_slots (int, optional): The amount to offset the slots. Used in patterns with no 0-needles, to offset everything 1 to left (-1 offset). Defaults to 0.

        Returns:
            list[int]: The list of color-codes that correspond to a row of the DAT raster for the given carriage pass.

        Raises:
            AssertionError: If the generated raster row length doesn't match the expected width.
        """
        raster_row = self._raster_left_option_raster(option_space)
        raster_row.extend(self._raster_needle_operations(pattern_width, offset_slots, pattern_space))
        raster_row.extend(self._raster_right_option_raster(option_space))
        assert len(raster_row) == self.raster_width(pattern_width, option_space, pattern_space)
        return raster_row

    def _raster_needle_operations(self, pattern_width: int, offset_slots: int, pattern_space: int = 4) -> list[int]:
        """Generate the needle operations portion of the raster row.

        Creates the central portion of the raster row containing needle operations, stopping marks, and pattern spacing.

        Args:
            pattern_width (int): The width of the knitting pattern.
            offset_slots (int): The amount to offset the slots.
            pattern_space (int, optional): Buffer space around the pattern. Defaults to 4.

        Returns:
            list[int]: The pixel values representing needle operations and spacing.
        """
        # initiate with left side pattern spacing
        pattern_raster = [0] * pattern_space
        left_stop_mark, right_stop_mark = self._get_stopping_marks()
        left_stop_mark += offset_slots
        right_stop_mark += offset_slots
        for slot_index in range(-1, pattern_width + 1):  # Add needle operations for each index.
            if slot_index == left_stop_mark or slot_index == right_stop_mark:  # A stopping mark index has been found.
                pattern_raster.append(STOPPING_MARK)
            elif (slot_index - offset_slots) in self.slot_colors:  # An operation is specified for this slot
                pattern_raster.append(int(self.slot_colors[slot_index - offset_slots]))
            else:  # No operation or stopping point specified. Fill with a no-op
                pattern_raster.append(0)
        # add right side pattern spacing
        pattern_raster.extend([0] * pattern_space)
        return pattern_raster

    @staticmethod
    def get_option_margin_width(option_buffer: int = 10) -> int:
        """Calculate the width of the option line margin.

        Args:
            option_buffer (int, optional): The amount of padding outside the option lines. Defaults to 10.

        Returns:
            int: The number of pixels of the option line margin width up to the beginning of the pattern's buffer.
        """
        return option_buffer + (2 * OPTION_LINE_COUNT)  # left buffer, space for left option lines

    def _raster_left_option_raster(self, left_space: int = 10) -> list[int]:
        """Generate the left option lines portion of the raster row.

        Creates the left side of the raster row containing option line numbers and their corresponding values, with appropriate spacing and reversal.

        Args:
            left_space (int, optional): Left side spacing buffer. Defaults to 10.

        Returns:
            list[int]: The pixel values representing left option lines and spacing.

        Note:
            The L1 option to specify carriage direction is set on the option line instead of beside it.
        """
        option_raster = []
        for option_index in range(1, OPTION_LINE_COUNT + 1):
            option_raster.append(option_index)  # make the option lines
            option_raster.append(0)  # add a placeholder 0 option
        for option_line, option_color in self.left_option_line_settings.items():
            option_line_position = (int(option_line) - 1) * 2  # adjust option line numbers to be 0 offset and multiply by 2 for spacing
            option_position = option_line_position + 1 if option_line is not Left_Option_Lines.Direction_Specification else option_line_position
            # The L1 option to specify carriage direction is set on the option line instead of beside it.
            option_raster[option_position] = option_color
        leftward_raster = [0 for _ in range(left_space)]
        leftward_raster.extend(reversed(option_raster))
        return leftward_raster

    def _raster_right_option_raster(self, right_space: int = 10) -> list[int]:
        """Generate the right option lines portion of the raster row.

        Creates the right side of the raster row containing option line numbers and their corresponding values, with appropriate spacing.

        Args:
            right_space (int, optional): Right side spacing buffer. Defaults to 10.

        Returns:
            list[int]: The pixel values representing right option lines and spacing.

        Note:
            The R1 option to specify carriage direction is set on the option line instead of beside it.
        """
        option_raster = []
        for option_index in range(1, OPTION_LINE_COUNT + 1):
            option_raster.append(option_index)  # make the option lines
            option_raster.append(0)  # add a placeholder 0 option
        for option_line, option_color in self.right_option_line_settings.items():
            option_line_position = (int(option_line) - 1) * 2  # adjust option line numbers to be 0 offset and multiply by 2 for spacing
            option_position = option_line_position + 1 if option_line is not Right_Option_Lines.Direction_Specification else option_line_position
            # The R1 option to specify carriage direction is set on the option line instead of beside it.
            option_raster[option_position] = option_color
        option_raster.extend(0 for _ in range(right_space))
        return option_raster

    def __str__(self) -> str:
        """Return string representation of the raster pass.

        Returns:
            str: String representation showing slot range, direction, carriers, and operation count.
        """
        slot_range = self.get_slot_range()
        direction = self.carriage_pass.direction.name if self.carriage_pass.direction else "None"
        carriers = self.carriage_pass.carrier_set.carrier_ids if self.carriage_pass.carrier_set else []

        return (f"Raster_Pass(slots={slot_range}, direction={direction}, "
                f"carriers={carriers}, operations={len(self.slot_colors)})")
