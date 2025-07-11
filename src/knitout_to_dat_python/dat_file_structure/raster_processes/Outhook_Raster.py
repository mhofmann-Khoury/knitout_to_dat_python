"""Module for the Outhook_Raster_Pass class"""

from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_to_dat_python.dat_file_structure.Dat_Codes.option_value_colors import Hook_Operation_Color, Presser_Setting_Color
from knitout_to_dat_python.dat_file_structure.raster_processes.Raster_Soft_Miss_Pass import Soft_Miss_Raster_Pass
from knitout_to_dat_python.kickback_injection.kickback_execution import Kick_Instruction


class Outhook_Raster_Pass(Soft_Miss_Raster_Pass):
    """Used to create a soft-miss carriage pass to outhook a carrier."""
    def __init__(self, carrier_position: int, carrier_id: int, machine_specification: Knitting_Machine_Specification,
                 min_knitting_slot: int, max_knitting_slot: int,
                 stitch_number: int = 5, speed_number: int = 0, presser_setting: Presser_Setting_Color = Presser_Setting_Color.Off,
                 pause: bool = False):
        self.carriage_position: int = carrier_position
        self.carrier_id: int = carrier_id
        out_kick_instruction = Kick_Instruction(self.carriage_position, Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set([self.carrier_id]), comment="Kickback for outhook")
        super().__init__(out_kick_instruction, machine_specification, min_knitting_slot, max_knitting_slot, hook_operation=Hook_Operation_Color.Out_Hook_Operation, stitch_number=stitch_number,
                         speed_number=speed_number, presser_setting=presser_setting, pause=pause)
