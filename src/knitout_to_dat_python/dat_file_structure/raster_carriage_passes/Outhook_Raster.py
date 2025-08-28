"""Module for the Outhook_Raster_Pass class.

This module provides the Outhook_Raster_Pass class, which creates a specialized soft-miss carriage pass specifically designed for outhook operations.
It extends the Soft_Miss_Raster_Pass to handle yarn carrier outhook functionality.
"""

from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction
from virtual_knitting_machine.Knitting_Machine_Specification import (
    Knitting_Machine_Specification,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)

from knitout_to_dat_python.dat_file_structure.dat_codes.option_value_colors import (
    Hook_Operation_Color,
    Presser_Setting_Color,
)
from knitout_to_dat_python.dat_file_structure.raster_carriage_passes.Raster_Soft_Miss_Pass import (
    Soft_Miss_Raster_Pass,
)


class Outhook_Raster_Pass(Soft_Miss_Raster_Pass):
    """Used to create a soft-miss carriage pass to outhook a carrier.

    This class creates a specialized raster pass for outhook operations, which are used to release yarn carriers from the knitting machine's yarn-inserting hook.
    The pass is implemented as a soft-miss operation with specific hook operation settings and always moves in the rightward direction.
    """

    def __init__(self, carrier_position: int, carrier_id: int, machine_specification: Knitting_Machine_Specification,
                 min_knitting_slot: int, max_knitting_slot: int,
                 stitch_number: int = 5, speed_number: int = 0, presser_setting: Presser_Setting_Color = Presser_Setting_Color.Off,
                 pause: bool = False):
        """Initialize an Outhook_Raster_Pass.

        Creates a raster pass that performs an outhook operation for a specific yarn carrier.
        The operation is implemented as a rightward-moving kickback instruction with outhook hook operation settings.

        Args:
            carrier_position (int): The position of the carrier to be outhooked.
            carrier_id (int): The ID of the carrier to be outhooked.
            machine_specification (Knitting_Machine_Specification): The machine specification for the knitout file specified in the knitout header.
            min_knitting_slot (int): The minimum slot of knitting operations in this file.
            max_knitting_slot (int): The maximum slot of knitting operations in this file.
            stitch_number (int, optional): Current stitch setting. Defaults to 5.
            speed_number (int, optional): Current speed setting. Defaults to 0.
            presser_setting (Presser_Setting_Color, optional): Current presser mode setting. Defaults to Presser_Setting_Color.Off.
            pause (bool, optional): Whether this pass should pause. Defaults to False.
        """
        self.carriage_position: int = carrier_position
        """int: The position of the carrier being outhooked."""

        self.carrier_id: int = carrier_id
        """int: The ID of the carrier being outhooked."""

        out_kick_instruction = Kick_Instruction(self.carriage_position, Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set([self.carrier_id]), comment="Kickback for outhook")
        super().__init__(out_kick_instruction, machine_specification, min_knitting_slot, max_knitting_slot, hook_operation=Hook_Operation_Color.Out_Hook_Operation, stitch_number=stitch_number,
                         speed_number=speed_number, presser_setting=presser_setting, pause=pause)
