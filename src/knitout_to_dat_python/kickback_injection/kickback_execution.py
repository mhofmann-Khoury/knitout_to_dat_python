"""Subclass of Knitout_Executer that introduces kickbacks for carrier management when creating Dat files.

This module provides enhanced knitout execution with automatic kickback injection for carrier management.
It prevents carrier conflicts by automatically inserting kick instructions to move carriers out of the way of incoming carriage passes, ensuring smooth operation during DAT file generation.
"""

from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line
from knitout_interpreter.knitout_operations.needle_instructions import (
    Needle_Instruction,
)
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import (
    Yarn_Carrier,
)
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)

from knitout_to_dat_python.kickback_injection.carriage_pass_with_kick import (
    Carriage_Pass_with_Kick,
)


class Negative_Kick_Instruction(Kick_Instruction):
    """A subclass of the Kick_Instruction used to undo the negative needle requirement
    TODO: Remove this requirement from the original Kick_Instruction class.
    """

    def __init__(self, position: int, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set | None = None, comment: None | str = None):
        """Initialize a kick instruction for a specific needle position.

        Args:
            position (int): The needle position for the kickback.
            direction: The direction of the carriage pass.
            cs: The yarn carrier set to use. Defaults to None.
            comment: Optional comment for the instruction. Defaults to None.
        """
        if isinstance(position, Needle):
            self._position: int = position.position
        else:
            self._position: int = position
        super().__init__(position=abs(position), direction=direction, cs=cs, comment=comment)
        self._needle = Needle(is_front=True, position=self._position)  # correct the position to the negative value.


class Knitout_Executer_With_Kickbacks(Knitout_Executer):
    """Subclass of the Knitout_Executer that introduces kickback logic for carrier management before each carriage pass.

    This class extends the standard Knitout_Executer to automatically inject kick instructions that prevent carrier conflicts during knitting operations.
    It tracks carrier positions, manages carrier buffers, and generates appropriate kickback sequences to ensure carriers don't interfere with carriage pass execution.

    Attributes:
        process (list[Knitout_Line | Carriage_Pass]): The processed instruction list including injected kickbacks.
        executed_instructions (list[Knitout_Line]): The list of executed instruction lines.
        kickback_machine (Knitting_Machine): Separate machine instance for tracking kickback state.
        _last_carrier_movement (Carriage_Pass | None): The most recent carriage pass that involved carrier movement.
    """

    def __init__(self, instructions: list[Knitout_Line], knitting_machine: Knitting_Machine):
        """Initialize a Knitout_Executer_With_Kickbacks.

        Creates an enhanced knitout executor that automatically manages carrier conflicts through kickback injection.
        Sets up carrier tracking systems and processes the instruction list with automatic conflict resolution.

        Args:
            instructions (list[Knitout_Line]): The list of knitout instructions to execute.
            knitting_machine (Knitting_Machine): The knitting machine to execute instructions on.
        """
        self.process: list[Knitout_Line | Carriage_Pass] = []
        self._kickback_process: list[Knitout_Line | Carriage_Pass] = []
        self.executed_instructions: list[Knitout_Line] = []
        self._kickback_executed_instructions: list[Knitout_Line] = []
        super().__init__(instructions, knitting_machine)
        self.kickback_machine: Knitting_Machine = Knitting_Machine(self.knitting_machine.machine_specification)
        self._last_carrier_movement: None | Carriage_Pass = None
        self.add_kickbacks_to_process()

    def _get_carrier_position(self, cid: int) -> None | int:
        """Get the exact position with buffer for the given carrier.

        Args:
            cid (int): The id of the carrier to find the position of.

        Returns:
            int | None: The exact position of the given carrier. None if carrier is inactive.
        """
        carrier = self.kickback_machine.carrier_system[cid]
        assert isinstance(carrier, Yarn_Carrier)
        if carrier.position is None:
            return None
        else:
            return int(carrier.position)

    def get_carriers(self, carrier_set: Yarn_Carrier_Set | None) -> set[Yarn_Carrier]:
        """
        Args:
            carrier_set (Yarn_Carrier_Set | None): Yarn carrier set to get carriers from. If this is None, the empty set is returned.

        Returns:
            set[Yarn_Carrier]: The set of yarn carriers from the kickback machine involved in the given carrier set.
        """
        if carrier_set is None:
            return set()
        return set(carrier_set.get_carriers(self.kickback_machine.carrier_system))

    def _get_carrier_position_range(self, carrier: int | Yarn_Carrier) -> None | int:
        """Get the position range for a carrier.

        Args:
            carrier (int | Yarn_Carrier): The id of the carrier to identify the position of.

        Returns:
            None | int: None if the carrier is not active or the needle-slot of the carrier is currently positioned at.
        """
        if isinstance(carrier, int):
            carrier = self.kickback_machine.carrier_system[carrier]
        assert isinstance(carrier, Yarn_Carrier)
        if carrier.position is None:
            return None
        return int(carrier.position)

    def _carriage_pass_conflict_zone(self, carriage_pass: Carriage_Pass) -> tuple[int, int]:
        """Identify the carrier-conflict zone for a carriage pass.

        Args:
            carriage_pass (Carriage_Pass): The carriage pass to identify the carrier-conflict zone of.

        Returns:
            tuple[int, int]: The leftmost and rightmost positions that carriers will move in this action.
        """
        leftmost_position, rightmost_position = carriage_pass.carriage_pass_range()
        # for carrier in self.get_carriers(carriage_pass.carrier_set):  # Include movements of involved carriers to the starting position of the carriage pass.
        #     carrier_position = self._get_carrier_position_range(carrier)
        #     if isinstance(carrier_position, int):  # Specific position, no kickbacks
        #         leftmost_position = min(carrier_position, leftmost_position)
        #         rightmost_position = max(carrier_position, rightmost_position)
        return leftmost_position, rightmost_position

    def _kicks_out_of_conflict_zone(self, leftmost_conflict: int, rightmost_conflict: int, exempt_carriers: set[Yarn_Carrier],
                                    allow_leftward_movement: bool = True, allow_rightward_movement: bool = True) -> list[Kick_Instruction]:
        """Generate kick instructions to move carriers out of a conflict zone.

        Args:
            leftmost_conflict (int): The left most position where carriers conflict.
            rightmost_conflict (int): The rightmost position where carriers conflict.
            exempt_carriers (set[Yarn_Carrier]): The set of carriers that are exempt from conflict consideration.
            allow_leftward_movement (bool, optional): If set to True, kickbacks may send carriers to the left. Defaults to True.
            allow_rightward_movement (bool, optional): If set to True, kickbacks may send carriers to the right. Defaults to True.

        Returns:
            list[Kick_Instruction]: The list of kickback instructions that will resolve the conflicts in the given conflict zone.

        Raises:
            ValueError: If both leftward and rightward movement are disallowed but conflicts are detected.
        """
        kicks: list[Kick_Instruction] = []
        conflict_carriers = self._carriers_in_conflict_zone(leftmost_conflict, rightmost_conflict, exempt_carriers)
        if len(conflict_carriers) == 0:
            return []  # No conflicts, so no kicks.
        elif not (allow_leftward_movement or allow_rightward_movement):
            raise ValueError(f"Must have at least leftward or rightward options  to kick {conflict_carriers}")
        exempt_carriers.update(conflict_carriers)

        if allow_leftward_movement and allow_rightward_movement:
            conflict_split = leftmost_conflict + (rightmost_conflict - leftmost_conflict) // 2
            leftward_carriers = set(carrier for carrier in conflict_carriers if carrier.position <= conflict_split)  # Carriers that should tend to push leftward
            rightward_carriers = set(carrier for carrier in conflict_carriers if carrier.position > conflict_split)  # Carriers that should tend to push rightward
        elif allow_leftward_movement:  # allow only leftward movements
            leftward_carriers = conflict_carriers
            rightward_carriers = set()
        else:  # allow only rightward movements
            rightward_carriers = conflict_carriers
            leftward_carriers = set()

        # associate carriers by current position for outward pushing to exterior of carriage pass
        leftward_positions_to_carriers: dict[int, set[Yarn_Carrier]] = {}
        for carrier in leftward_carriers:
            if carrier.position not in leftward_positions_to_carriers:
                leftward_positions_to_carriers[carrier.position] = set()
            leftward_positions_to_carriers[carrier.position].add(carrier)
        rightward_positions_to_carriers: dict[int, set[Yarn_Carrier]] = {}
        for carrier in rightward_carriers:
            if carrier.position not in rightward_positions_to_carriers:
                rightward_positions_to_carriers[carrier.position] = set()
            rightward_positions_to_carriers[carrier.position].add(carrier)

        # Set leftward kickbacks moving left most to rightmost carrier sets
        if len(leftward_positions_to_carriers) > 0:
            kicks = self._kicks_out_of_conflict_zone(leftmost_conflict=leftmost_conflict - len(leftward_positions_to_carriers),
                                                     rightmost_conflict=leftmost_conflict,
                                                     exempt_carriers=exempt_carriers, allow_leftward_movement=True, allow_rightward_movement=False)
            kick_insert_index = len(kicks)
            for push_group, pos in enumerate(sorted(leftward_positions_to_carriers, reverse=True)):
                carriers = leftward_positions_to_carriers[pos]
                kick_position = leftmost_conflict - 1 - push_group
                if kick_position < 0:
                    kick = Negative_Kick_Instruction(kick_position, Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set(list(carriers)),
                                                     comment=f"Move out of conflict zone {leftmost_conflict} to {rightmost_conflict} of carriers {exempt_carriers}")
                else:
                    kick = Kick_Instruction(kick_position, Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set(list(carriers)),
                                            comment=f"Move out of conflict zone {leftmost_conflict} to {rightmost_conflict} of carriers {exempt_carriers}")
                kicks.insert(kick_insert_index, kick)  # add kick to front of kicks because we want the order to move the leftmost carriers first.

        # Set rightward kickbacks moving right to leftmost carrier sets
        if len(rightward_positions_to_carriers) > 0:
            conflict_kicks = self._kicks_out_of_conflict_zone(leftmost_conflict=rightmost_conflict,
                                                              rightmost_conflict=rightmost_conflict + len(rightward_positions_to_carriers),
                                                              exempt_carriers=exempt_carriers, allow_leftward_movement=False, allow_rightward_movement=True)
            kicks.extend(conflict_kicks)
            kick_insert_index = len(kicks)
            for push_group, pos in enumerate(sorted(rightward_positions_to_carriers)):
                carriers = rightward_positions_to_carriers[pos]
                kick_position = rightmost_conflict + 1+ push_group
                if kick_position < 0:
                    kick = Negative_Kick_Instruction(kick_position, Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set(list(carriers)),
                                                     comment=f"Move out of conflict zone {leftmost_conflict} to {rightmost_conflict} of carriers {exempt_carriers}")
                else:
                    kick = Kick_Instruction(kick_position, Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set(list(carriers)),
                                            comment=f"Move out of conflict zone {leftmost_conflict} to {rightmost_conflict} of carriers {exempt_carriers}")
                kicks.insert(kick_insert_index, kick)  # add to front of rightmost kicks because we want the order to move the rightmost carriers first.

        return kicks

    def _carriers_in_conflict_zone(self, leftmost_conflict: int, rightmost_conflict: int, exempt_carriers: set[Yarn_Carrier]) -> set[Yarn_Carrier]:
        """
        Args:
            leftmost_conflict (int): The leftmost slot of the conflict zone.
            rightmost_conflict (int): The rightmost slot of the conflict zone.
            exempt_carriers (set[Yarn_Carrier]): The set of carriers that are exempt from conflicts since they are involved in the operation already.

        Returns:
            set[Yarn_Carrier]: The yarn carriers currently positioned within the given conflict zone.
        """
        return set(c for c in self.kickback_machine.carrier_system.active_carriers
                   if c not in exempt_carriers and c.position is not None and leftmost_conflict <= c.conflicting_needle_slot <= rightmost_conflict)

    def _kickback_to_align_carriers(self, carriage_pass: Carriage_Pass) -> Kick_Instruction | None:
        """Generate kick instructions to align carriers for the next carriage pass.

        Args:
            carriage_pass (Carriage_Pass): The next carriage pass to execute and kick to align carriers with.

        Returns:
            Kick_Instruction | None: The kickback instruction needed before the carriage pass that will align the carriers for the next movement or None if the carriers are aligned.
        """
        if carriage_pass.carrier_set is None or carriage_pass.direction is None:
            return None
        needle_position = carriage_pass.first_instruction.needle.position
        if carriage_pass.direction is Carriage_Pass_Direction.Leftward:
            carriers_to_kick = [c for c in carriage_pass.carrier_set.get_carriers(self.kickback_machine.carrier_system) if c.position is not None and needle_position >= c.conflicting_needle_slot]
            if len(carriers_to_kick) > 0:
                return Kick_Instruction(needle_position, Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set(carriers_to_kick), comment="Align carriers for next pass")
        else:
            carriers_to_kick = [c for c in carriage_pass.carrier_set.get_carriers(self.kickback_machine.carrier_system) if c.position is not None and c.conflicting_needle_slot >= needle_position]
            if len(carriers_to_kick) > 0:
                return Kick_Instruction(needle_position, Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set(carriers_to_kick), comment="Align carriers for next pass")

    def _can_add_kick_to_last_pass(self, kick: Kick_Instruction) -> bool:
        """Check if a kick instruction can be added to the last carriage pass.

        Args:
            kick (Kick_Instruction): The kick instruction to consider adding to the end of the last carriage pass.

        Returns:
            bool: True if the last carriage pass can receive the kick without causing any new conflicts. False otherwise.
        """
        if self._last_carrier_movement is None:
            return False
        last_movement_position = self._last_carrier_movement.last_needle.position
        if ((self._last_carrier_movement.direction is Carriage_Pass_Direction.Leftward and last_movement_position <= kick.needle.position)
                or (self._last_carrier_movement.direction is Carriage_Pass_Direction.Rightward and last_movement_position >= kick.needle.position)):
            return False
        if kick.carrier_set == self._last_carrier_movement.carrier_set:
            left_conflict, right_conflict = self._carriage_pass_conflict_zone(self._last_carrier_movement)
            for carrier in self.get_carriers(kick.carrier_set):  # Add the kick's movement to the range of the conflict zone
                left_conflict = min(left_conflict, carrier.conflicting_needle_slot)
                left_conflict = min(left_conflict, kick.position)
                right_conflict = max(right_conflict, carrier.conflicting_needle_slot)
                right_conflict = max(right_conflict, kick.position)
            conflicting_carriers = self._carriers_in_conflict_zone(left_conflict, right_conflict,
                                                                   exempt_carriers=self.get_carriers(kick.carrier_set))
            return len(conflicting_carriers) == 0  # No conflict with adding the carrier to the last carrier movement
        return False

    def _split_kicks_to_extend_last_pass(self, kicks: list[Kick_Instruction]) -> tuple[None | Kick_Instruction, list[Kick_Instruction]]:
        """Split kicks into those that can extend the last pass and those that cannot.

        Args:
            kicks (list[Kick_Instruction]): The list of kick instructions to evaluate.

        Returns:
            tuple[Kick_Instruction | None, list[Kick_Instruction]]: A tuple containing:
            * The kick that can be added to the last pass (or None)
            * The list of remaining kicks that must be executed separately.
        """
        extras = []
        add_on = None
        i = 0
        for i, kick in enumerate(kicks):
            if self._can_add_kick_to_last_pass(kick):
                add_on = kick
                break
            else:
                extras.append(kick)
        if add_on is not None:
            extras.extend(kicks[i + 1:])
        return add_on, extras

    def _add_carrier_movement(self, execution: Carriage_Pass | Knitout_Line) -> None:
        """Add a carrier movement operation to the process and update machine state.

        Args:
            execution (Carriage_Pass | Knitout_Line): The instruction or carriage pass to add and execute.
        """
        if isinstance(execution, Carriage_Pass):
            executed_pass = execution.execute(self.kickback_machine)
            updated = len(executed_pass) > 0
            if updated:
                self._kickback_executed_instructions.extend(executed_pass)
                self._kickback_process.append(execution)
            if execution.xfer_pass:
                self._last_carrier_movement = None  # Xfers may cause conflicts with the current carrier positions.
            elif execution.carrier_set is not None:
                self._last_carrier_movement = execution
        else:
            updated = execution.execute(self.kickback_machine)
            if updated or isinstance(execution, Pause_Instruction):
                self._kickback_executed_instructions.append(execution)
                self._kickback_process.append(execution)

    def _update_last_carriage_pass(self, updated_carriage_pass: Carriage_Pass) -> None:
        """Update the last carriage pass in the process.

        Args:
            updated_carriage_pass (Carriage_Pass): The updated carriage pass to replace the last one.
        """
        for update_cp_index in range(len(self._kickback_process) - 1, -1, -1):  # iterate back through the process until the last carriage pass is found.
            if isinstance(self._kickback_process[update_cp_index], Carriage_Pass):
                self._kickback_process[update_cp_index] = updated_carriage_pass
                return

    def _update_last_executed_instruction(self, added_kick: Kick_Instruction) -> None:
        """Update the executed instructions list by adding a kick instruction.

        Args:
            added_kick (Kick_Instruction): The kick instruction to add to the executed instructions.
        """
        for update_index in range(len(self._kickback_executed_instructions), -1, -1):
            if isinstance(self._kickback_executed_instructions[update_index - 1], Needle_Instruction):
                self._kickback_executed_instructions.insert(update_index, added_kick)
                return

    def _kick_conflicting_carriers(self, carriage_pass: Carriage_Pass) -> None:
        leftmost_conflict, rightmost_conflict = self._carriage_pass_conflict_zone(carriage_pass)
        conflict_kicks = self._kicks_out_of_conflict_zone(leftmost_conflict, rightmost_conflict, exempt_carriers=self.get_carriers(carriage_pass.carrier_set))
        add_on, kicks_before_cp = self._split_kicks_to_extend_last_pass(conflict_kicks)
        if isinstance(add_on, Kick_Instruction):  # there is a kickback that can extend the last carriage pass without causing new conflicts
            assert isinstance(self._last_carrier_movement, Carriage_Pass)
            add_on_cp = Carriage_Pass_with_Kick(self._last_carrier_movement, [add_on])
            add_on.execute(self.kickback_machine)
            self._update_last_carriage_pass(add_on_cp)
            self._update_last_executed_instruction(add_on)
        for kick in kicks_before_cp:
            kick_cp = Carriage_Pass(kick, rack=0, all_needle_rack=False)
            self._add_carrier_movement(kick_cp)

    def _kick_to_align_carriers(self, carriage_pass: Carriage_Pass) -> None:
        alignment_kick = self._kickback_to_align_carriers(carriage_pass)
        if isinstance(alignment_kick, Kick_Instruction):
            add_on, kicks_before_cp = self._split_kicks_to_extend_last_pass([alignment_kick])
            if isinstance(add_on, Kick_Instruction):  # there is a kickback that can extend the last carriage pass without causing new conflicts
                assert isinstance(self._last_carrier_movement, Carriage_Pass)
                add_on_cp = Carriage_Pass_with_Kick(self._last_carrier_movement, [add_on])
                add_on.execute(self.kickback_machine)
                self._update_last_carriage_pass(add_on_cp)
                self._update_last_executed_instruction(add_on)
            for kick in kicks_before_cp:
                kick_cp = Carriage_Pass(kick, rack=0, all_needle_rack=False)
                self._add_carrier_movement(kick_cp)

    def add_kickbacks_to_process(self) -> None:
        """Rerun the executor's process but add kickback logic to form a new kickback program.

        Processes the original instruction list and automatically injects kick instructions to prevent carrier conflicts.
        Manages carrier state tracking, conflict detection, and kickback generation throughout the execution process.
        """
        for instruction in self.process:
            if isinstance(instruction, Knitout_Line):
                self._add_carrier_movement(instruction)
            else:  # Carriage pass that may need kickbacks before proceeding.
                assert isinstance(instruction, Carriage_Pass), f"Expected Carriage pass, got {instruction}"
                carriage_pass = instruction
                self._kick_conflicting_carriers(carriage_pass)
                self._kick_to_align_carriers(carriage_pass)
                self._add_carrier_movement(carriage_pass)
        self.process = self._kickback_process
        self.executed_instructions = self._kickback_executed_instructions
        self.knitting_machine = self.kickback_machine
        self._carriage_passes = [cp for cp in self.process if isinstance(cp, Carriage_Pass)]
        self._left_most_position = None
        self._right_most_position = None
        for cp in self._carriage_passes:
            left, right = cp.carriage_pass_range()
            if self._left_most_position is None:
                self._left_most_position = left
            elif left is not None:
                self._left_most_position = min(self._left_most_position, left)
            if self._right_most_position is None:
                self._right_most_position = right
            elif right is not None:
                self._right_most_position = max(self._right_most_position, right)
