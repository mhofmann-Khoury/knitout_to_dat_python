"""Module for generating the startup and ending sequences on all Dat files.

This module provides functions for creating the standardized startup and finishing sequences that are required at the beginning and end of all DAT files.
These sequences ensure proper initialization and termination of knitting operations on the machine.
"""
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.needle_instructions import (
    Knit_Instruction,
    Miss_Instruction,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)


def finish_knit_sequence(pattern_width: int) -> list[Carriage_Pass]:
    """Generate the sequence of carriage passes needed to finish a knitting process.

    Creates a standardized ending sequence consisting of three carriage passes: a leftward front bed pass, a rightward back bed pass, and a leftward all-needle pass.
    This sequence ensures proper completion of the knitting process and prepares the machine for pattern termination.

    Args:
        pattern_width (int): The width of the knitting process at the widest carriage pass.

    Returns:
        list[Carriage_Pass]: The List of carriage passes of knitout operations needed to finish a knitting process with the specified width.
    """
    front_pass = Carriage_Pass(Knit_Instruction(Needle(is_front=True, position=pattern_width - 1), Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set([])), rack=0, all_needle_rack=False)
    for p in range(pattern_width - 2, -1, -1):
        front_pass.add_instruction(Knit_Instruction(Needle(is_front=True, position=p), Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set([])), rack=0, all_needle_rack=False)
    back_pass = Carriage_Pass(Knit_Instruction(Needle(is_front=False, position=0), Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set([])), rack=0, all_needle_rack=False)
    for p in range(1, pattern_width):
        back_pass.add_instruction(Knit_Instruction(Needle(is_front=False, position=p), Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set([])), rack=0, all_needle_rack=False)
    all_pass = Carriage_Pass(Knit_Instruction(Needle(is_front=True, position=pattern_width - 1), Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set([])), rack=0, all_needle_rack=True)
    all_pass.add_instruction(Knit_Instruction(Needle(is_front=False, position=pattern_width - 1), Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set([])), rack=0, all_needle_rack=True)
    for p in range(pattern_width - 2, -1, -1):
        all_pass.add_instruction(Knit_Instruction(Needle(is_front=True, position=p), Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set([])), rack=0, all_needle_rack=True)
        all_pass.add_instruction(Knit_Instruction(Needle(is_front=False, position=p), Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set([])), rack=0, all_needle_rack=True)
    return [front_pass, back_pass, all_pass]


def startup_knit_sequence(pattern_width: int) -> list[Carriage_Pass]:
    """Generate the sequence of carriage passes needed to start up a knitting process.

    Creates a standardized startup sequence consisting of three carriage passes:
    * A rightward miss pass on the front bed
    * A leftward knit pass on the front bed
    * A rightward knit pass on the back bed.

    This sequence ensures proper initialization of the knitting process and prepares the machine for pattern execution.

    Args:
        pattern_width (int): The width of the knitting process at the widest carriage pass.

    Returns:
        list[Carriage_Pass]: The list of carriage passes of knitout operations needed to start up a knitting process of the specified width.
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
