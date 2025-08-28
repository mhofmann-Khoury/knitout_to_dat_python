"""Module containing the Soft Miss Raster Pass Class.

This module provides the Soft_Miss_Raster_Pass class, which extends the Raster_Carriage_Pass to create specialized carriage passes with miss/kick instructions.
These passes are used for carrier management operations where the carriage moves without performing knitting operations.
"""

from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction
from virtual_knitting_machine.Knitting_Machine_Specification import (
    Knitting_Machine_Specification,
)

from knitout_to_dat_python.dat_file_structure.dat_codes.dat_file_color_codes import (
    NO_CARRIERS,
)
from knitout_to_dat_python.dat_file_structure.dat_codes.option_lines import (
    Right_Option_Lines,
)
from knitout_to_dat_python.dat_file_structure.dat_codes.option_value_colors import (
    Hook_Operation_Color,
    Knit_Cancel_Color,
    Presser_Setting_Color,
    carriers_to_int,
)
from knitout_to_dat_python.dat_file_structure.raster_carriage_passes.Raster_Carriage_Pass import (
    Raster_Carriage_Pass,
)


class Soft_Miss_Raster_Pass(Raster_Carriage_Pass):
    """Class that extends the Raster Carriage pass Class to create a carriage pass with a miss/kick instruction.

    This class creates specialized raster passes for soft miss operations,
    which are carriage movements that don't perform knitting operations but are used for carrier positioning, hook operations, and other machine control functions.
    It handles the specific carrier option settings required for miss operations.
    """

    def __init__(self, kick_instruction: Kick_Instruction, machine_specification: Knitting_Machine_Specification, min_knitting_slot: int, max_knitting_slot: int,
                 hook_operation: Hook_Operation_Color = Hook_Operation_Color.No_Hook_Operation, knit_cancel: Knit_Cancel_Color = Knit_Cancel_Color.Standard, stitch_number: int = 5,
                 speed_number: int = 0, presser_setting: Presser_Setting_Color = Presser_Setting_Color.Off, pause: bool = False):
        """Initialize a Soft_Miss_Raster_Pass.

        Creates a raster pass based on a kick instruction for soft miss operations.
        The pass is configured with specific hook operation settings and carrier management.

        Args:
            kick_instruction (Kick_Instruction): The kick instruction that defines the soft miss operation.
            machine_specification (Knitting_Machine_Specification): The machine specification for the knitout file specified in the knitout header.
            min_knitting_slot (int): The minimum slot of knitting operations in this file.
            max_knitting_slot (int): The maximum slot of knitting operations in this file.
            hook_operation (Hook_Operation_Color, optional): The operation of the yarn-inserting hook for this carrier. Defaults to Hook_Operation_Color.No_Hook_Operation.
            knit_cancel (Knit_Cancel_Color, optional): Knit cancel mode setting. Defaults to Knit_Cancel_Color.Standard.
            stitch_number (int, optional): Current stitch setting. Defaults to 5.
            speed_number (int, optional): Current speed setting. Defaults to 0.
            presser_setting (Presser_Setting_Color, optional): Current presser mode setting. Defaults to Presser_Setting_Color.Off.
            pause (bool, optional): Whether this pass should pause. Defaults to False.

        Raises:
            AssertionError: If hook_operation is In_Hook_Operation, as inhook operations cannot be performed on soft-miss passes.
        """
        assert hook_operation is not Hook_Operation_Color.In_Hook_Operation, f"Cannot inhook on a soft-miss: {kick_instruction}"

        self.kick_instruction = kick_instruction
        """Kick_Instruction: The kick instruction that defines this soft miss operation."""

        miss_release_carriage_pass = Carriage_Pass(kick_instruction, rack=0, all_needle_rack=False)
        super().__init__(miss_release_carriage_pass, machine_specification, min_knitting_slot, max_knitting_slot, hook_operation=hook_operation, stitch_number=stitch_number, speed_number=speed_number,
                         presser_setting=presser_setting, pause=pause, knit_cancel=knit_cancel)

    def _set_carrier_options(self) -> None:
        """Set the carrier and yarn-inserting-hook option lines.

        Configures carrier-related option lines specifically for soft miss operations.
        Sets carrier gripper to 0 (no carrier on gripper) and handles special encoding for outhook operations with the 100 value offset.

        Note:
            Outhook carrier numbers are set with the 100 value offset.
        """
        self.right_option_line_settings[Right_Option_Lines.Carrier_Gripper] = 0  # No carrier on gripper
        self.right_option_line_settings[Right_Option_Lines.Hook_Operation] = int(self.hook_operation)
        if self.kick_instruction.no_carriers:
            self.right_option_line_settings[Right_Option_Lines.Yarn_Carrier_Number] = NO_CARRIERS
        else:
            carriers_int = carriers_to_int(self.carriage_pass.carrier_set)
            self.right_option_line_settings[Right_Option_Lines.Yarn_Carrier_Number] = carriers_int
            if self.hook_operation is Hook_Operation_Color.Out_Hook_Operation:
                self.right_option_line_settings[Right_Option_Lines.Carrier_Gripper] = 100 + carriers_int  # outhook carrier numbers are set with the 100 value.
