"""Module containing the Releasehook Raster Pass Class"""
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction

from knitout_to_dat_python.dat_file_structure.dat_codes.dat_file_color_codes import NO_CARRIERS
from knitout_to_dat_python.dat_file_structure.dat_codes.option_value_colors import Hook_Operation_Color, Knit_Cancel_Color, Presser_Setting_Color
from knitout_to_dat_python.dat_file_structure.dat_codes.option_lines import Right_Option_Lines
from knitout_to_dat_python.dat_file_structure.raster_processes.raster_passes.Raster_Soft_Miss_Pass import Soft_Miss_Raster_Pass


class Releasehook_Raster_Pass(Soft_Miss_Raster_Pass):
    """
    Extension of Soft_Miss_Raster_Pass class for kickbacks for releasehook operations.
    """
    def __init__(self, carrier_position: int, release_direction: Carriage_Pass_Direction,
                 machine_specification: Knitting_Machine_Specification,
                 min_knitting_slot: int, max_knitting_slot: int, stitch_number: int = 5,
                 speed_number: int = 0, presser_setting: Presser_Setting_Color = Presser_Setting_Color.Off, pause: bool = False):
        self.carrier_position: int = carrier_position
        # Note, all releasehook operations must be in a leftward direction.
        release_kick = Kick_Instruction(self.carrier_position, release_direction, comment="Kickback for releasehook operation")
        super().__init__(release_kick, machine_specification, min_knitting_slot, max_knitting_slot, hook_operation=Hook_Operation_Color.ReleaseHook_Operation,
                         knit_cancel=Knit_Cancel_Color.Standard, stitch_number=stitch_number,
                         speed_number=speed_number, presser_setting=presser_setting, pause=pause)

    def _set_carrier_options(self) -> None:
        """
        Set the carrier and yarn-inserting-hook option lines.
        """
        self.right_option_line_settings[Right_Option_Lines.Yarn_Carrier_Number] = NO_CARRIERS
        self.right_option_line_settings[Right_Option_Lines.Hook_Operation] = int(Hook_Operation_Color.ReleaseHook_Operation)
        self.right_option_line_settings[Right_Option_Lines.Carrier_Gripper] = 0  # No carrier on gripper
