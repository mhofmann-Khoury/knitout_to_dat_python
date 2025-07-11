"""Module for getting a startup sequence in knitout for a dat file."""

from knit_script.interpret_knit_script import knit_script_to_knitout
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from knitout_interpreter.knitout_operations.needle_instructions import Needle_Instruction, Tuck_Instruction, Miss_Instruction
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_to_dat_python.dat_file_structure.dat_sequences.load_knit_script_sequence import get_knit_script_sequence, delete_generated_file


class Miss_Carriage_Pass(Carriage_Pass):

    def __init__(self, first_instruction: Miss_Instruction, rack: int, all_needle_rack: bool):
        super().__init__(first_instruction, rack, all_needle_rack)

    def compatible_with_pass_type(self, instruction: Needle_Instruction) -> bool:
        return isinstance(instruction, Miss_Instruction)


def startup_knit_sequence(pattern_width: int) -> list[Carriage_Pass]:
    """
    Args:
        pattern_width: The width of the knitting process at the widest carriage pass.

    Returns:
        The list of carriage passes of knitout operations needed to start up a knitting process of the specified width.
    """
    startup_sequence_ks = get_knit_script_sequence('dat_start_up.ks')
    startup_sequence_k_file = 'startup_sequence.k'
    _knit_graph, _machine_state = knit_script_to_knitout(startup_sequence_ks, startup_sequence_k_file, pattern_is_filename=False,
                                                         c=1, pattern_width=pattern_width)
    knitout_lines = parse_knitout(startup_sequence_k_file, pattern_is_file=True)
    # change knitout lines to have no carrier or inhooks
    carriage_passes = []
    current_carriage_pass = None
    for line in knitout_lines:
        if isinstance(line, Needle_Instruction):
            if isinstance(line, Tuck_Instruction):
                line = Miss_Instruction(line.needle, line.direction, Yarn_Carrier_Set([1]))
            line.carrier_set = None
            if current_carriage_pass is None:
                if isinstance(line, Miss_Instruction):
                    current_carriage_pass = Miss_Carriage_Pass(line, rack=0, all_needle_rack=False)
                else:
                    current_carriage_pass = Carriage_Pass(line, rack=0, all_needle_rack=False)
            elif current_carriage_pass.can_add_instruction(line, rack=0, all_needle_rack=False):
                current_carriage_pass.add_instruction(line, rack=0, all_needle_rack=False)
            else:
                carriage_passes.append(current_carriage_pass)
                if isinstance(line, Miss_Instruction):
                    current_carriage_pass = Miss_Carriage_Pass(line, rack=0, all_needle_rack=False)
                else:
                    current_carriage_pass = Carriage_Pass(line, rack=0, all_needle_rack=False)
    if current_carriage_pass is not None:
        carriage_passes.append(current_carriage_pass)

    delete_generated_file(startup_sequence_k_file)
    return carriage_passes
