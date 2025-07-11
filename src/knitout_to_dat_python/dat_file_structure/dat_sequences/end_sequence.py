"""Module for getting a startup sequence in knitout for a dat file."""

from knit_script.interpret_knit_script import knit_script_to_knitout
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from knitout_interpreter.knitout_operations.needle_instructions import Needle_Instruction
from virtual_knitting_machine.machine_components.needles.Needle import Needle

from knitout_to_dat_python.dat_file_structure.dat_sequences.load_knit_script_sequence import get_knit_script_sequence, delete_generated_file


class All_Needle_Pass(Carriage_Pass):

    def __init__(self, first_instruction: Needle_Instruction, rack: int):
        assert first_instruction.has_direction, f"Cannot all-needle-knit without a direction."
        assert not first_instruction.has_second_needle, f"Cannot all-needle-knit with 2-needle (split, xfer) instructions."
        super().__init__(first_instruction, rack, all_needle_rack=True)

    def can_add_instruction(self, instruction: Needle_Instruction, rack: int, all_needle_rack: bool) -> bool:
        if rack != self.rack:
            return False
        elif all_needle_rack != self.all_needle_rack:
            return False
        elif instruction.direction != self._direction:
            return False
        elif instruction.carrier_set != self.carrier_set:
            return False
        elif not self.compatible_with_pass_type(instruction):
            return False
        opposite_needle = Needle(is_front=not instruction.needle.is_front, position=instruction.needle.position)
        if opposite_needle in self._needles_to_instruction and instruction.needle not in self._needles_to_instruction:  # All Needle knitting is available.
            return True
        elif not self._direction.needles_are_in_pass_direction(self.last_needle, instruction.needle):
            return False
        return True


def finish_knit_sequence(pattern_width: int) -> list[Carriage_Pass]:
    """
    Args:
        pattern_width: The width of the knitting process at the widest carriage pass.

    Returns:
        The List of carriage passes of knitout operations needed to finish a knitting process with the specified width
    """
    sequence_ks = get_knit_script_sequence('dat_finish.ks')
    sequence_k_file = 'end_sequence.k'
    _knit_graph, _machine_state = knit_script_to_knitout(sequence_ks, sequence_k_file, pattern_is_filename=False,
                                                         c=1, pattern_width=pattern_width)
    knitout_lines = parse_knitout(sequence_k_file, pattern_is_file=True)
    # change knitout lines to have no carrier or inhooks
    carriage_passes = []
    current_carriage_pass = None
    all_needle = False
    for line in knitout_lines:
        if isinstance(line, Needle_Instruction):
            line.carrier_set = None
            if current_carriage_pass is None:
                current_carriage_pass = Carriage_Pass(line, rack=0, all_needle_rack=all_needle)
            elif current_carriage_pass.can_add_instruction(line, rack=0, all_needle_rack=all_needle):
                current_carriage_pass.add_instruction(line, rack=0, all_needle_rack=all_needle)
            else:
                carriage_passes.append(current_carriage_pass)
                if len(carriage_passes) == 2:  # Next carriage pass is all_needle
                    all_needle = True
                    current_carriage_pass = All_Needle_Pass(line, rack=0)
                else:
                    current_carriage_pass = Carriage_Pass(line, rack=0, all_needle_rack=all_needle)
    if current_carriage_pass is not None:
        carriage_passes.append(current_carriage_pass)

    delete_generated_file(sequence_k_file)
    return carriage_passes
