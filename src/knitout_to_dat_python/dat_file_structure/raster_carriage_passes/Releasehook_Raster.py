"""Module containing the Releasehook Raster Pass Class.

This module provides the Releasehook_Raster_Pass class, which extends the Soft_Miss_Raster_Pass to create specialized carriage passes for releasehook operations.
These passes are used to release yarn carriers from the knitting machine's yarn-inserting hook system.
"""
from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction
from virtual_knitting_machine.Knitting_Machine_Specification import (
    Knitting_Machine_Specification,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
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
)
from knitout_to_dat_python.dat_file_structure.raster_carriage_passes.Raster_Soft_Miss_Pass import (
    Soft_Miss_Raster_Pass,
)


class Releasehook_Raster_Pass(Soft_Miss_Raster_Pass):
    """Extension of Soft_Miss_Raster_Pass class for kickbacks for releasehook operations.

    This class creates specialized raster passes for releasehook operations, which are used to release yarn carriers from the knitting machine's yarn-inserting hook.
    All releasehook operations must move in the leftward direction and use specific hook operation settings.
    """

    def __init__(self, carrier_position: int, machine_specification: Knitting_Machine_Specification,
                 min_knitting_slot: int, max_knitting_slot: int, stitch_number: int = 5,
                 speed_number: int = 0, presser_setting: Presser_Setting_Color = Presser_Setting_Color.Off, pause: bool = False):
        """Initialize a Releasehook_Raster_Pass.

        Creates a raster pass that performs a releasehook operation at the specified carrier position.
        The operation is implemented as a leftward-moving kickback instruction with releasehook hook operation settings.

        Args:
            carrier_position (int): The position of the carrier to be released from the hook.
            machine_specification (Knitting_Machine_Specification): The machine specification for the knitout file specified in the knitout header.
            min_knitting_slot (int): The minimum slot of knitting operations in this file.
            max_knitting_slot (int): The maximum slot of knitting operations in this file.
            stitch_number (int, optional): Current stitch setting. Defaults to 5.
            speed_number (int, optional): Current speed setting. Defaults to 0.
            presser_setting (Presser_Setting_Color, optional): Current presser mode setting. Defaults to Presser_Setting_Color.Off.
            pause (bool, optional): Whether this pass should pause. Defaults to False.

        Note:
            All releasehook operations must be in a leftward direction.
        """
        self.carrier_position: int = carrier_position
        """int: The position of the carrier being released from the hook."""

        # Note, all releasehook operations must be in a leftward direction.
        release_kick = Kick_Instruction(self.carrier_position, Carriage_Pass_Direction.Leftward, comment="Kickback for releasehook operation")
        super().__init__(release_kick, machine_specification, min_knitting_slot, max_knitting_slot, hook_operation=Hook_Operation_Color.ReleaseHook_Operation,
                         knit_cancel=Knit_Cancel_Color.Standard, stitch_number=stitch_number,
                         speed_number=speed_number, presser_setting=presser_setting, pause=pause)

    def _set_carrier_options(self) -> None:
        """Set the carrier and yarn-inserting-hook option lines.

        Configures carrier-related option lines specifically for releasehook operations.
        Sets yarn carrier number to NO_CARRIERS, hook operation to ReleaseHook_Operation, and carrier gripper to 0 (no carrier on gripper).
        """
        self.right_option_line_settings[Right_Option_Lines.Yarn_Carrier_Number] = NO_CARRIERS
        self.right_option_line_settings[Right_Option_Lines.Hook_Operation] = int(Hook_Operation_Color.ReleaseHook_Operation)
        self.right_option_line_settings[Right_Option_Lines.Carrier_Gripper] = 0  # No carrier on gripper
