"""Module containing the Soft Miss Raster Pass Class"""

from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification
from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction

from knitout_to_dat_python.dat_file_structure.dat_codes.dat_file_color_codes import NO_CARRIERS
from knitout_to_dat_python.dat_file_structure.dat_codes.option_value_colors import Hook_Operation_Color, Knit_Cancel_Color, Presser_Setting_Color, carriers_to_int
from knitout_to_dat_python.dat_file_structure.dat_codes.option_lines import Right_Option_Lines
from knitout_to_dat_python.dat_file_structure.raster_processes.raster_passes.Raster_Carriage_Pass import Raster_Carriage_Pass


class Soft_Miss_Raster_Pass(Raster_Carriage_Pass):
    """
    Class that extends the Raster Carriage pass Class to create a carriage pass with a miss/kick instruction.
    """

    def __init__(self, kick_instruction: Kick_Instruction, machine_specification: Knitting_Machine_Specification, min_knitting_slot: int, max_knitting_slot: int,
                 hook_operation: Hook_Operation_Color = Hook_Operation_Color.No_Hook_Operation, knit_cancel: Knit_Cancel_Color = Knit_Cancel_Color.Standard, stitch_number: int = 5,
                 speed_number: int = 0, presser_setting: Presser_Setting_Color = Presser_Setting_Color.Off, pause: bool = False):
        assert hook_operation is not Hook_Operation_Color.In_Hook_Operation, f"Cannot inhook on a soft-miss: {kick_instruction}"
        self.kick_instruction = kick_instruction
        miss_release_carriage_pass = Carriage_Pass(kick_instruction, rack=0, all_needle_rack=False)
        super().__init__(miss_release_carriage_pass, machine_specification, min_knitting_slot, max_knitting_slot, hook_operation=hook_operation, stitch_number=stitch_number, speed_number=speed_number,
                         presser_setting=presser_setting, pause=pause, knit_cancel=knit_cancel)

    def _set_carrier_options(self) -> None:
        """
        Set the carrier and yarn-inserting-hook option lines.
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
