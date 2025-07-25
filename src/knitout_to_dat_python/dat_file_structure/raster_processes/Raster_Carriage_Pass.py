"""
Raster_Pass class that wraps Carriage_Pass to extract DAT file generation information.
Based on the original knitout-to-dat.js raster generation logic.
"""

from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction_Type
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle

from knitout_to_dat_python.dat_file_structure.Dat_Codes.operation_colors import Operation_Color, get_operation_color
from knitout_to_dat_python.dat_file_structure.Dat_Codes.option_lines import Left_Option_Lines, Right_Option_Lines
from knitout_to_dat_python.dat_file_structure.Dat_Codes.option_value_colors import Drop_Sinker_Color, Hook_Operation_Color, Knit_Cancel_Color, Rack_Direction_Color, Rack_Pitch_Color, \
    get_carriage_pass_direction_color, Presser_Setting_Color, carriers_to_int, Amiss_Split_Hook_Color, Pause_Color, Link_Process_Color
from knitout_to_dat_python.dat_file_structure.Dat_Codes.dat_file_color_codes import STOPPING_MARK, OPTION_LINE_COUNT


class Raster_Carriage_Pass:
    """
    Wrapper for Carriage_Pass that extracts information needed for DAT raster generation.
    Converts knitout operations into colored pixels and option line settings.
    """

    def __init__(self, carriage_pass: Carriage_Pass, machine_specification: Knitting_Machine_Specification, min_knitting_slot: int, max_knitting_slot: int,
                 hook_operation: Hook_Operation_Color = Hook_Operation_Color.No_Hook_Operation,
                 stitch_number: int = 5, speed_number: int = 0, presser_setting: Presser_Setting_Color = Presser_Setting_Color.Off,
                 pause: bool = False,
                 knit_cancel: Knit_Cancel_Color = Knit_Cancel_Color.Standard, drop_sinker: bool = False):
        """
        Initialize a Raster_Pass from a Carriage_Pass.

        Args:
            drop_sinker: Set to true to set "drop failure, sinker reset".
            knit_cancel: Set to true if knit-cancel mode is enabled. Will be reset to true for transfer carriage passes.
            hook_operation: The operation of the yarn-inserting hook for this carrier. Defaults to no operation.
            carriage_pass: The carriage pass to wrap.
            machine_specification: The machine specification for the knitout file specified in the knitout header.
            min_knitting_slot: The minimum slot of knitting operations in this file.
            max_knitting_slot: The maximum slot of knitting operations in this file.
            stitch_number: Current stitch setting.
            speed_number: Current speed setting.
            presser_setting: Current presser mode ('on', 'off', 'auto').
            pause: Whether this pass should pause.
        """
        self.drop_sinker: bool = drop_sinker
        self.carriage_pass: Carriage_Pass = carriage_pass
        if self.carriage_pass.xfer_pass:
            knit_cancel = Knit_Cancel_Color.Knit_Cancel  # Transfer passes always set to knit cancel
            stitch_number = 0  # Transfers have a 0 stitch number
        self.knit_cancel: Knit_Cancel_Color = knit_cancel
        self._hook_operation: Hook_Operation_Color = hook_operation
        if self.hook_operation is Hook_Operation_Color.In_Hook_Operation:
            # Todo: Bring this validation into knitscript and knitout interpreter.
            assert self.carriage_pass.direction is Carriage_Pass_Direction.Leftward, f"Knitout Error: Cannot inhook on a rightward knitting pass."
        self.max_knitting_slot: int = max_knitting_slot
        self.min_knitting_slot: int = min_knitting_slot
        self.machine_specification: Knitting_Machine_Specification = machine_specification
        self.stitch_number: int = stitch_number
        self.speed_number: int = speed_number
        self.presser_setting: Presser_Setting_Color = presser_setting
        self._pause: bool = pause

        # Process the carriage pass into raster data
        self.slot_colors: dict[int, Operation_Color] = {}  # slot_number -> color_code
        self.left_option_line_settings: dict[Left_Option_Lines, int] = {opt: 0 for opt in Left_Option_Lines}
        self.right_option_line_settings: dict[Right_Option_Lines, int] = {opt: 0 for opt in Right_Option_Lines}
        self._process_operations()
        self._set_option_lines()

    def shift_slot_colors(self, shift: int) -> None:
        """
        Shifts the slot numbers of the carriage pass by the given amount.
        Args:
            shift: The amount to shift the slots by.
        """
        if shift != 0:
            self.slot_colors = {s + shift: c for s, c in self.slot_colors.items()}

    @property
    def hook_operation(self) -> Hook_Operation_Color:
        """
        Returns:
            The Hook operation for the given carriage pass.
        """
        return self._hook_operation

    @hook_operation.setter
    def hook_operation(self, hook_operation: Hook_Operation_Color) -> None:
        self._hook_operation = hook_operation
        self._set_option_lines()

    @property
    def empty_pass(self) -> bool:
        """
        Returns:
            True if there are no needle operations in this carriage pass.
        """
        return len(self.carriage_pass) == 0

    @property
    def min_slot(self) -> int | None:
        """
        Returns:
            None if there are no needle operations in this carriage pass.
            Otherwise, return the leftmost slot that operations will occur on.
        """
        if self.empty_pass:
            return None
        return min(self.slot_colors)

    @property
    def max_slot(self) -> int | None:
        """
        Returns:
            None if there are no needle operations in this carriage pass.
            Otherwise, return the rightmost slot that operations will occur on.
        """
        if self.empty_pass:
            return None
        return max(self.slot_colors)

    def _process_operations(self) -> None:
        """Process carriage pass operations into colored pixels."""
        rightward_order_needles = self.carriage_pass.rightward_sorted_needles()
        needle_instructions = self.carriage_pass.instructions_by_needles(rightward_order_needles)
        for instruction in needle_instructions:
            slot_number = self._needle_to_slot(instruction.needle)
            instruction_color = get_operation_color(instruction)
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
        """Convert needle to slot number (accounting for racking)."""
        assert isinstance(needle.position, int)
        if needle.is_front:
            return needle.position
        else:
            assert isinstance(self.carriage_pass.rack, int)
            return needle.position + self.carriage_pass.rack

    def _set_option_lines(self) -> None:
        """Set all option lines based on carriage pass instructions and specified knitting parameters."""
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
        """
        Returns: True if the carriage pass has splits. False otherwise.
        """
        return bool(self.carriage_pass.contains_instruction_type(Knitout_Instruction_Type.Split))

    def _set_amiss_split_hook_options(self) -> None:
        """
        Sets the amiss_split_hook options based on carriage pass instruction types.
        """
        if self.has_splits:
            self.left_option_line_settings[Left_Option_Lines.AMiss_Split_Flag] = int(Amiss_Split_Hook_Color.Split_Hook)

    def _set_drop_sinker_option(self) -> None:
        """
        Sets the drop-sinker option line.
        """
        if self.drop_sinker:
            self.right_option_line_settings[Right_Option_Lines.Drop_Sinker] = int(Drop_Sinker_Color.Drop_Sinker)

    def _set_ignore_link_process_option(self) -> None:
        """
        Sets the ignore_link_process_option flag to True.
        This option is always true for knitout processes.
        """
        self.right_option_line_settings[Right_Option_Lines.Links_Process] = int(Link_Process_Color.Ignore_Link_Process)

    def _set_carrier_options(self) -> None:
        """
        Set the carrier and yarn-inserting-hook option lines.
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
        """
        Sets the racking option lines.
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
        """
        Sets the stitch number option line.
        """
        self.right_option_line_settings[Right_Option_Lines.Stitch_Number] = self.stitch_number

    def _set_speed_options(self) -> None:
        """
        Sets the speed option lines.
        """
        speed_value = 0 if self.speed_number == 0 else self.speed_number + 10  # Todo: why adding 10 to larger speed values.
        self.left_option_line_settings[Left_Option_Lines.Knit_Speed] = speed_value
        self.left_option_line_settings[Left_Option_Lines.Transfer_Speed] = speed_value  # Transfer speed

    def _set_knit_cancel_option(self) -> None:
        """
        Set the option line for the knit cancel status.
        """
        self.right_option_line_settings[Right_Option_Lines.Knit_Cancel_or_Carriage_Move] = int(self.knit_cancel)

    def _set_transfer_stitch_option(self) -> None:
        """
        Set the stitch numbers for transfers.
        """
        pass  # Todo: How is this used in the JS compiler? This doesn't seem to apply in test samples.
        # if self.carriage_pass.xfer_pass and self.stitch_number != 0:
        #     self.right_option_line_settings[Right_Option_Lines.Apply_Stitch_to_Transfer] = TRANSFER_STITCH_NUMBER  # Apply stitch number to transfer

    def _set_presser_mode_option(self) -> None:
        """
        Sets the presser mode option line.
        """
        self.right_option_line_settings[Right_Option_Lines.Presser_Mode] = self.presser_setting.presser_option(self.carriage_pass)

    def _set_pause_option(self) -> None:
        """
        Sets the pause option line.
        """
        if self.pause:
            self.left_option_line_settings[Left_Option_Lines.Pause_Option] = int(Pause_Color.Pause)

    @property
    def pause(self) -> bool:
        """
        Returns: True if this carriage pass will have a pause option.
        """
        return self._pause

    @pause.setter
    def pause(self, value: bool) -> None:
        self._pause = value
        self._set_pause_option()

    def _set_direction_options(self) -> None:
        """
        Sets the direction option lines based on the carriage pass's direction.
        """
        direction_color = get_carriage_pass_direction_color(self.carriage_pass)
        self.left_option_line_settings[Left_Option_Lines.Direction_Specification] = int(direction_color)
        self.right_option_line_settings[Right_Option_Lines.Direction_Specification] = int(direction_color)

    def _should_use_presser(self) -> bool:
        """
        Returns
            True if presser should be used whe auto-mode is specified.
            A presser should if the hook is not active and there are not mixed front/back bed needle operations."""
        has_front = any(needle.is_front for needle in self.carriage_pass.needles)
        has_back = any(not needle.is_front for needle in self.carriage_pass.needles)
        return not (has_front and has_back)  # Don't use presser for mixed front/back

    def get_slot_range(self) -> tuple[int, int]:
        """
        Returns:
            The range of slots this pass operates on."""
        if self.empty_pass:
            return 0, 0
        assert self.min_slot is not None
        assert self.max_slot is not None
        return self.min_slot, self.max_slot

    def _get_stopping_marks(self) -> tuple[int, int]:
        """
        Returns:
            The stopping mark positions (before and after the pass)."""
        if not self.slot_colors:
            return 0, 0
        min_slot, max_slot = self.get_slot_range()
        return min_slot - 1, max_slot + 1

    @staticmethod
    def raster_width(pattern_width: int, option_space: int = 10, pattern_space: int = 4) -> int:
        """
        Args:
            pattern_width: Width of the knitting pattern.
            option_space: Spacing around the exterior of the option lines.
            pattern_space: Spacing between option lines and the knitting pattern.

        Returns:
            The expected width of a raster row with the given width parameters.
        """
        return 2 * ((OPTION_LINE_COUNT * 2) + option_space + pattern_space) + pattern_width + 2

    def get_raster_row(self, pattern_width: int, option_space: int = 10, pattern_space: int = 4, offset_slots: int = 0) -> list[int]:
        """
        Args:
            offset_slots: The amount to offset the slots. Used in patterns with no 0-needles, to offset everything 1 to left (-1 offset).
            pattern_space: The spacing between option lines and the patter. Defaults to 4.
            pattern_width: The width of the knitting pattern.
            option_space: The spacing around the option lines. Defaults to 10.
        Returns:
            The list of color-codes that correspond to a row of the DAT raster for the given carriage pass.
        """
        raster_row = self._raster_left_option_raster(option_space)
        raster_row.extend(self._raster_needle_operations(pattern_width, offset_slots, pattern_space))
        raster_row.extend(self._raster_right_option_raster(option_space))
        assert len(raster_row) == self.raster_width(pattern_width, option_space, pattern_space)
        return raster_row

    def _raster_needle_operations(self, pattern_width: int, offset_slots: int, pattern_space: int = 4) -> list[int]:
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
        """
        Args:
            option_buffer: The amount of padding outside the option lines. Defaults to 10.

        Returns:
            The number of pixels of the option line margin width up to the beginning of the pattern's buffer.
        """
        return option_buffer + (2 * OPTION_LINE_COUNT)  # left buffer, space for left option lines

    def _raster_left_option_raster(self, left_space: int = 10) -> list[int]:
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
        """String representation of the raster pass."""
        slot_range = self.get_slot_range()
        direction = self.carriage_pass.direction.name if self.carriage_pass.direction else "None"
        carriers = self.carriage_pass.carrier_set.carrier_ids if self.carriage_pass.carrier_set else []

        return (f"Raster_Pass(slots={slot_range}, direction={direction}, "
                f"carriers={carriers}, operations={len(self.slot_colors)})")
