"""Module containing the Carriage_Pass_with_Kick class.

This module provides a wrapper class for Carriage_Pass that allows kickback instructions to be integrated with regular knit-tuck passes.
This enables carrier management operations to be combined with knitting operations in a single carriage pass.
"""
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction
from knitout_interpreter.knitout_operations.needle_instructions import (
    Needle_Instruction,
)


class Carriage_Pass_with_Kick(Carriage_Pass):
    """Wrapper class for Carriage Pass that allows for kickbacks to be added to knit-tuck passes.

    This class extends the standard Carriage_Pass to support the integration of kick instructions (kickbacks) with regular knitting operations.
    It combines all instructions into a properly sorted execution order based on needle positions and carriage direction.
    """

    def __init__(self, carriage_pass: Carriage_Pass, kicks: list[Kick_Instruction]):
        """Initialize a Carriage_Pass_with_Kick.

        Creates a new carriage pass that combines the original carriage pass instructions with the provided kick instructions.
        Sorts them according to the carriage direction and needle positions for proper execution order.

        Args:
            carriage_pass (Carriage_Pass): The original carriage pass to extend with kick instructions.
            kicks (list[Kick_Instruction]): The list of kick instructions to integrate with the carriage pass.

        Raises:
            AssertionError: If any instruction cannot be added to the carriage pass.
        """
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
        """Check if an instruction is compatible with this carriage pass type.

        Extends the parent class compatibility check to allow kick instructions in addition to the standard compatible instruction types.

        Args:
            instruction (Needle_Instruction): The instruction to check for compatibility.

        Returns:
            bool: True if the instruction is compatible with this carriage pass type, False otherwise.
        """
        if isinstance(instruction, Kick_Instruction):
            return True
        else:
            super_pass = super().compatible_with_pass_type(instruction)
            assert isinstance(super_pass, bool)
            return super_pass
