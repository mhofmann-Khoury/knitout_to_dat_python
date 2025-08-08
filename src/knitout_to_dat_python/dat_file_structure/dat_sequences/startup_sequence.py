"""Module for getting a startup sequence in knitout for a dat file."""

from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.needle_instructions import Miss_Instruction, Knit_Instruction
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set


def startup_knit_sequence(pattern_width: int) -> list[Carriage_Pass]:
    """
    Args:
        pattern_width: The width of the knitting process at the widest carriage pass.

    Returns:
        The list of carriage passes of knitout operations needed to start up a knitting process of the specified width.
    """
    miss_pass = Carriage_Pass(Miss_Instruction(Needle(is_front=True, position=0), Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set([])), rack=0, all_needle_rack=False)
    for p in range(1, pattern_width):
        miss_pass.add_instruction(Miss_Instruction(Needle(is_front=True, position=p), Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set([])), rack=0, all_needle_rack=False)
    front_pass = Carriage_Pass(Knit_Instruction(Needle(is_front=True, position=pattern_width - 1), Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set([])), rack=0, all_needle_rack=False)
    for p in range(pattern_width - 2, -1, -1):
        front_pass.add_instruction(Knit_Instruction(Needle(is_front=True, position=p), Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set([])), rack=0, all_needle_rack=False)
    back_pass = Carriage_Pass(Knit_Instruction(Needle(is_front=False, position=0), Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set([])), rack=0, all_needle_rack=False)
    for p in range(1, pattern_width):
        back_pass.add_instruction(Knit_Instruction(Needle(is_front=False, position=p), Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set([])), rack=0, all_needle_rack=False)

    return [miss_pass, front_pass, back_pass]
