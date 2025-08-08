from knitout_interpreter.knitout_execution_structures import Carriage_Pass
from knitout_interpreter.knitout_operations import Kick_Instruction, Needle_Instruction


class Carriage_Pass_with_Kick(Carriage_Pass):
    """Wrapper class for Carriage Pass that allows for kickbacks to be added to knit-tuck passes."""

    def __init__(self, carriage_pass: Carriage_Pass, kicks: list[Kick_Instruction]):
        all_instructions = list(carriage_pass.instruction_set())
        all_instructions.extend(kicks)
        needles_to_instruction = {i.needle: i for i in all_instructions}
        sorted_needles = carriage_pass.direction.sort_needles(needles_to_instruction, carriage_pass.rack)
        sorted_instructions = [needles_to_instruction[n] for n in sorted_needles]
        super().__init__(sorted_instructions[0], carriage_pass.rack, carriage_pass.all_needle_rack)
        for instruction in sorted_instructions[1:]:
            _added = self.add_instruction(instruction, self.rack, self.all_needle_rack)
            assert _added

    def compatible_with_pass_type(self, instruction: Needle_Instruction) -> bool:
        if isinstance(instruction, Kick_Instruction):
            return True
        else:
            super_pass = super().compatible_with_pass_type(instruction)
            assert isinstance(super_pass, bool)
            return super_pass
