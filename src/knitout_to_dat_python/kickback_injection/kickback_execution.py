"""Subclass of Knitout_Executer that introduces kickbacks for carrier management when creating Dat files.

This module provides enhanced knitout execution with automatic kickback injection for carrier management.
It prevents carrier conflicts by automatically inserting kick instructions to move carriers out of the way of incoming carriage passes, ensuring smooth operation during DAT file generation.
"""
from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.carrier_instructions import (
    Knitout_Instruction,
    Releasehook_Instruction,
    Yarn_Carrier_Instruction,
)
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
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)

from knitout_to_dat_python.kickback_injection.carriage_pass_with_kick import (
    Carriage_Pass_with_Kick,
)


class Knitout_Executer_With_Kickbacks(Knitout_Executer):
    """Subclass of the Knitout_Executer that introduces kickback logic for carrier management before each carriage pass.

    This class extends the standard Knitout_Executer to automatically inject kick instructions that prevent carrier conflicts during knitting operations.
    It tracks carrier positions, manages carrier buffers, and generates appropriate kickback sequences to ensure carriers don't interfere with carriage pass execution.
    """

    STOPPING_DISTANCE: int = 10
    """int: The distance carriers are moved when kicked to avoid conflicts."""

    def __init__(self, instructions: list[Knitout_Line], knitting_machine: Knitting_Machine):
        """Initialize a Knitout_Executer_With_Kickbacks.

        Creates an enhanced knitout executor that automatically manages carrier conflicts through kickback injection.
        Sets up carrier tracking systems and processes the instruction list with automatic conflict resolution.

        Args:
            instructions (list[Knitout_Line]): The list of knitout instructions to execute.
            knitting_machine (Knitting_Machine): The knitting machine to execute instructions on.
        """
        self.process: list[Knitout_Line | Carriage_Pass] = []
        """list[Knitout_Line | Carriage_Pass]: The processed instruction list including injected kickbacks."""

        self.executed_instructions: list[Knitout_Line] = []
        """list[Knitout_Line]: The list of executed instruction lines."""

        super().__init__(instructions, knitting_machine)

        self.kickback_machine: Knitting_Machine = Knitting_Machine(self.knitting_machine.machine_specification)
        """Knitting_Machine: Separate machine instance for tracking kickback state."""

        # track the last kicking direction of each carrier. None implies that a carrier has not been kicked since it was last used.
        self._kicked_carriers: dict[int, Carriage_Pass_Direction | None] = {carrier.carrier_id: None for carrier in self.knitting_machine.carrier_system.carriers}
        """dict[int, Carriage_Pass_Direction | None]: Tracks the last kicking direction of each carrier. None implies that a carrier has not been kicked since it was last used."""

        # track the buffered position of each carrier based on the direction of the last movement.
        self._carrier_buffers: dict[int, float] = {carrier.carrier_id: 0 for carrier in self.knitting_machine.carrier_system.carriers}
        """dict[int, float]: Tracks the buffered position of each carrier based on the direction of the last movement."""

        self._last_carrier_movement: None | Carriage_Pass = None
        """Carriage_Pass | None: The most recent carriage pass that involved carrier movement."""

        self.add_kickbacks_to_process()

    def _get_carrier_position(self, cid: int) -> None | float:
        """Get the exact position with buffer for the given carrier.

        Args:
            cid (int): The id of the carrier to find the position of.

        Returns:
            float | None: The exact position with a small needle buffer for the given carrier. None if carrier is inactive.
        """
        carrier = self.kickback_machine.carrier_system[cid]
        if carrier.position is None:
            return None  # inactive carrier
        else:
            assert isinstance(carrier.position, int)
            return carrier.position + self._carrier_buffers[carrier.carrier_id]

    def _get_carrier_position_range(self, cid: int) -> None | float | tuple[int, int]:
        """Get the position or position range for a carrier.

        Args:
            cid (int): The id of the carrier to identify the position of.

        Returns:
            None | float | tuple[int, int]:
            * None if the carrier is not active.
            * A float for the exact needle position of the carrier if it has not been kicked.
            * A tuple of integers for the leftmost and rightmost possible positions of the carrier if it has been kicked.
        """
        carrier = self.kickback_machine.carrier_system[cid]
        if carrier.position is None:
            return None  # inactive carrier
        elif self._kicked_carriers[cid] is None:  # not kicked, return a precise position
            assert isinstance(carrier.position, int)
            return carrier.position
        elif self._kicked_carriers[cid] is Carriage_Pass_Direction.Leftward:  # Kicked leftward:
            return carrier.position - self.STOPPING_DISTANCE, carrier.position
        else:  # Kicked rightward
            return carrier.position, carrier.position + self.STOPPING_DISTANCE

    @staticmethod
    def _kick_conflict_zone(kick_instruction: Kick_Instruction) -> tuple[int, int]:
        """Get the conflict zone of executing a kickback instruction.

        Args:
            kick_instruction (Kick_Instruction): The kickback instruction to find the conflict zone of.

        Returns:
            tuple[int, int]: The conflict zone of executing this kickback as the leftmost and rightmost positions.
        """
        if kick_instruction.direction == Carriage_Pass_Direction.Leftward:
            return kick_instruction.needle.position - Knitout_Executer_With_Kickbacks.STOPPING_DISTANCE, kick_instruction.needle.position
        else:
            return kick_instruction.needle.position, kick_instruction.needle.position + Knitout_Executer_With_Kickbacks.STOPPING_DISTANCE

    @staticmethod
    def _kicks_conflict_zone(kicks: list[Kick_Instruction]) -> tuple[int, int] | tuple[None, None]:
        """Get the bounds of the conflict zone for a list of kick instructions.

        Args:
            kicks (list[Kick_Instruction]): The list of kicks to consider the conflict zone of.

        Returns:
            tuple[int, int] | tuple[None, None]: The bounds of the conflict zone of the given kicks. None boundaries if no kicks are given.
        """
        if len(kicks) == 0:
            return None, None
        leftmost = 1000  # a very large number.
        rightmost = -1
        for kick in kicks:
            left, right = Knitout_Executer_With_Kickbacks._kick_conflict_zone(kick)
            leftmost = min(leftmost, left)
            rightmost = max(rightmost, right)
        return leftmost, rightmost

    def _carriage_pass_conflict_zone(self, carriage_pass: Carriage_Pass) -> tuple[int, int] | None:
        """Identify the carrier-conflict zone for a carriage pass.

        Args:
            carriage_pass (Carriage_Pass): The carriage pass to identify the carrier-conflict zone of.

        Returns:
            tuple[int, int] | None:
            * None if there is no conflict zone for the carriage pass.
            * Otherwise, return the leftmost and rightmost positions that carriers will move in this action.
        """
        if carriage_pass.carrier_set is None or len(carriage_pass.carrier_set) == 0:
            return None  # No carriers involved in the carriage pass, thus no conflicts.
        leftmost_position, rightmost_position = carriage_pass.carriage_pass_range()
        for cid in carriage_pass.carrier_set.carrier_ids:
            carrier_position = self._get_carrier_position_range(cid)
            if isinstance(carrier_position, float):  # Specific position, no kickbacks
                leftmost_position = min(carrier_position, leftmost_position)
                rightmost_position = max(carrier_position, rightmost_position)
            elif isinstance(carrier_position, tuple):  # kicked carrier, add stopping distance buffer from prior kicks to the conflict zone.
                leftmost_position = min(carrier_position[0], leftmost_position)
                rightmost_position = max(carrier_position[1], rightmost_position)
        return leftmost_position, rightmost_position

    def _kicks_for_conflicting_carriers(self, carriage_pass: Carriage_Pass,
                                        prior_left_conflict: None | int = None, prior_right_conflict: None | int = None) -> list[Kick_Instruction]:
        """Generate kickback instructions to resolve carrier conflicts.

        Args:
            carriage_pass (Carriage_Pass): The carriage pass that may conflict with current carrier positions.
            prior_left_conflict (int | None, optional): Prior left conflict boundary to consider. Defaults to None.
            prior_right_conflict (int | None, optional): Prior right conflict boundary to consider. Defaults to None.

        Returns:
            list[Kick_Instruction]: A list of kickback instructions that will kick all conflicting carriers out of the way of an incoming carriage pass.
        """
        conflict_zone = self._carriage_pass_conflict_zone(carriage_pass)
        if conflict_zone is None:
            return []
        leftmost_conflict = conflict_zone[0]
        if prior_left_conflict is not None:
            leftmost_conflict = min(leftmost_conflict, prior_left_conflict)
        rightmost_conflict = conflict_zone[1]
        if prior_right_conflict is not None:
            rightmost_conflict = max(rightmost_conflict, prior_right_conflict)
        exempt_carriers = set()
        if carriage_pass.carrier_set is not None:
            exempt_carriers.update(carriage_pass.carrier_set.carrier_ids)
        return self._kicks_out_of_conflict_zone(leftmost_conflict, rightmost_conflict, exempt_carriers=exempt_carriers)

    def _kicks_out_of_conflict_zone(self, leftmost_conflict: int, rightmost_conflict: int, exempt_carriers: set[int],
                                    allow_leftward_movement: bool = True, allow_rightward_movement: bool = True) -> list[Kick_Instruction]:
        """Generate kick instructions to move carriers out of a conflict zone.

        Args:
            leftmost_conflict (int): The left most position where carriers conflict.
            rightmost_conflict (int): The rightmost position where carriers conflict.
            exempt_carriers (set[int]): The set of carriers that are exempt from conflict consideration.
            allow_leftward_movement (bool, optional): If set to True, kickbacks may send carriers to the left. Defaults to True.
            allow_rightward_movement (bool, optional): If set to True, kickbacks may send carriers to the right. Defaults to True.

        Returns:
            list[Kick_Instruction]: The list of kickback instructions that will resolve the conflicts in the given conflict zone.

        Raises:
            AssertionError: If both leftward and rightward movement are disallowed.
        """
        assert allow_leftward_movement or allow_rightward_movement, f"Must have at least leftward or rightward options for kickbacks"
        kicks: list[Kick_Instruction] = []
        conflict_carriers = self._carriers_in_conflict_zone(leftmost_conflict, rightmost_conflict, exempt_carriers)
        conflicting_kickback_exemptions = set(conflict_carriers.keys())
        conflicting_kickback_exemptions.update(exempt_carriers)

        if allow_leftward_movement and allow_rightward_movement:
            conflict_split = leftmost_conflict + (rightmost_conflict - leftmost_conflict) // 2
            leftward_carriers = {cid: pos for cid, pos in conflict_carriers.items() if pos <= conflict_split}  # Carriers that should tend to push leftward
            rightward_carriers = {cid: pos for cid, pos in conflict_carriers.items() if pos > conflict_split}  # Carriers that should tend to push rightward
        elif allow_leftward_movement:  # allow only leftward movements
            leftward_carriers = conflict_carriers
            rightward_carriers = {}
        else:  # allow only rightward movements
            rightward_carriers = conflict_carriers
            leftward_carriers = {}

        # associate carriers by current position for outward pushing to exterior of carriage pass
        leftward_positions_to_carriers: dict[int, set[int]] = {}
        for cid, pos in leftward_carriers.items():
            if pos not in leftward_positions_to_carriers:
                leftward_positions_to_carriers[pos] = set()
            leftward_positions_to_carriers[pos].add(cid)
        rightward_positions_to_carriers: dict[int, set[int]] = {}
        for cid, pos in rightward_carriers.items():
            if pos not in rightward_positions_to_carriers:
                rightward_positions_to_carriers[pos] = set()
            rightward_positions_to_carriers[pos].add(cid)

        # Set leftward kickbacks moving left most to rightmost carrier sets
        if len(leftward_positions_to_carriers) > 0:
            leftward_conflict_zone_extension = 1 + (len(leftward_positions_to_carriers) * Knitout_Executer_With_Kickbacks.STOPPING_DISTANCE)
            kicks = self._kicks_out_of_conflict_zone(leftmost_conflict=leftmost_conflict - leftward_conflict_zone_extension,
                                                     rightmost_conflict=leftmost_conflict,
                                                     exempt_carriers=conflicting_kickback_exemptions, allow_leftward_movement=True, allow_rightward_movement=False)
            kick_insert_index = len(kicks)
            for push_group, pos in enumerate(sorted(leftward_positions_to_carriers, reverse=True)):
                carriers = leftward_positions_to_carriers[pos]
                kick_position = leftmost_conflict - (push_group * Knitout_Executer_With_Kickbacks.STOPPING_DISTANCE)
                kick = Kick_Instruction(kick_position, Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set(list(carriers)),
                                        comment=f"Move out of conflict zone {leftmost_conflict} to {rightmost_conflict} of carriers {exempt_carriers}")
                kicks.insert(kick_insert_index, kick)  # add kick to front of kicks because we want the order to move the leftmost carriers first.

        # Set rightward kickbacks moving right to leftmost carrier sets
        if len(rightward_positions_to_carriers) > 0:
            rightward_conflict_zone_extension = 1 + (len(rightward_positions_to_carriers) * Knitout_Executer_With_Kickbacks.STOPPING_DISTANCE)
            conflict_kicks = self._kicks_out_of_conflict_zone(leftmost_conflict=rightmost_conflict,
                                                              rightmost_conflict=rightmost_conflict + rightward_conflict_zone_extension,
                                                              exempt_carriers=conflicting_kickback_exemptions, allow_leftward_movement=False, allow_rightward_movement=True)
            kicks.extend(conflict_kicks)
            kick_insert_index = len(kicks)
            for push_group, pos in enumerate(sorted(rightward_positions_to_carriers)):
                carriers = rightward_positions_to_carriers[pos]
                kick_position = rightmost_conflict + (push_group * Knitout_Executer_With_Kickbacks.STOPPING_DISTANCE)
                kick = Kick_Instruction(kick_position, Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set(list(carriers)),
                                        comment=f"Move out of conflict zone {leftmost_conflict} to {rightmost_conflict} of carriers {exempt_carriers}")
                kicks.insert(kick_insert_index, kick)  # add to front of rightmost kicks because we want the order to move the rightmost carriers first.

        return kicks

    def _carriers_in_conflict_zone(self, leftmost_conflict: int, rightmost_conflict: int, exempt_carriers: set[int]) -> dict[int, int]:
        """Find carriers currently positioned within a conflict zone.

        Args:
            leftmost_conflict (int): The leftmost slot of the conflict zone.
            rightmost_conflict (int): The rightmost slot of the conflict zone.
            exempt_carriers (set[int]): The set of carriers that are exempt from conflicts since they are involved in the operation already.

        Returns:
            dict[int, int]: Dictionary of carrier ids keyed to carrier's current position. The dictionary will contain an entry for every carrier in the conflict zone.
        """
        conflict_carriers: dict[int, int] = {}  # carrier ids keyed to current conflicting position.
        for carrier in self.kickback_machine.carrier_system.active_carriers:  # check only the active carriers for conflicts
            if carrier.carrier_id not in exempt_carriers and carrier.position is not None:
                if leftmost_conflict < carrier.position < rightmost_conflict:
                    conflict_carriers[carrier.carrier_id] = carrier.position
        return conflict_carriers

    def _kicks_to_align_carriers(self, carriage_pass: Carriage_Pass) -> list[Kick_Instruction]:
        """Generate kick instructions to align carriers for the next carriage pass.

        Args:
            carriage_pass (Carriage_Pass): The next carriage pass to execute and kick to align carriers with.

        Returns:
            list[Kick_Instruction]: The kickback instructions needed before the carriage pass that will align the carriers for the next movement.
        """
        if carriage_pass.carrier_set is None:
            return []
        carriers_cur_positions: dict[float, list[int]] = {}
        for cid in carriage_pass.carrier_set.carrier_ids:
            position = self._get_carrier_position(cid)
            if position is not None:
                if position not in carriers_cur_positions:
                    carriers_cur_positions[position] = []
                carriers_cur_positions[position].append(cid)
        if len(carriers_cur_positions) == 0:
            return []
        start_position = carriage_pass.first_instruction.needle.position
        kick_carriers = {}
        if carriage_pass.direction is Carriage_Pass_Direction.Leftward:
            start_position += .75
            for p, carrier_ids in carriers_cur_positions.items():
                if p < start_position:
                    kick_carriers[int(start_position)] = carrier_ids
                elif p == start_position:
                    kick_carriers[int(start_position) + 1] = carrier_ids
        else:  # Rightward carriage pass
            for p, carrier_ids in carriers_cur_positions.items():
                if start_position + .25 == p:
                    kick_carriers[start_position - 1] = carrier_ids
                elif start_position < p:
                    kick_carriers[start_position] = carrier_ids
        return [Kick_Instruction(p, carriage_pass.direction.opposite(), Yarn_Carrier_Set(cids), comment="Align carriers for next pass")
                for p, cids in kick_carriers.items()]

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
        left_conflict, right_conflict = self._kick_conflict_zone(kick)
        if kick.carrier_set == self._last_carrier_movement.carrier_set:
            conflicting_carriers = self._carriers_in_conflict_zone(left_conflict, right_conflict,
                                                                   exempt_carriers=set(kick.carrier_set))
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

    def add_kickbacks_to_process(self) -> None:
        """Rerun the executor's process but add kickback logic to form a new kickback program.

        Processes the original instruction list and automatically injects kick instructions to prevent carrier conflicts.
        Manages carrier state tracking, conflict detection, and kickback generation throughout the execution process.
        """
        kickback_process: list[Knitout_Line | Carriage_Pass] = []
        kickback_executed_instructions: list[Knitout_Line] = []

        def _add_carrier_movement(execution: Carriage_Pass | Knitout_Line) -> None:
            """Add a carrier movement operation to the process and update machine state.

            Args:
                execution (Carriage_Pass | Knitout_Line): The instruction or carriage pass to add and execute.
            """
            if isinstance(execution, Carriage_Pass):
                executed_pass = execution.execute(self.kickback_machine)
                updated = len(executed_pass) > 0
                kickback_executed_instructions.extend(executed_pass)
            else:
                updated = execution.execute(self.kickback_machine)
                if updated or isinstance(instruction, Pause_Instruction):
                    kickback_executed_instructions.append(execution)
            if updated or isinstance(instruction, Pause_Instruction):
                kickback_process.append(execution)
            if isinstance(execution, Carriage_Pass):
                if execution.xfer_pass:
                    self._last_carrier_movement = None  # Xfers may cause conflicts with the current carrier positions.
                elif execution.carrier_set is not None:
                    self._last_carrier_movement = execution
                    if execution.direction is None:
                        carrier_position_mod = 0.0
                    elif execution.direction is Carriage_Pass_Direction.Rightward:
                        carrier_position_mod = 1.25
                    else:
                        carrier_position_mod = -.25
                    for carrier_id in execution.carrier_set.carrier_ids:
                        self._carrier_buffers[carrier_id] = carrier_position_mod

        def _update_last_carriage_pass(updated_carriage_pass: Carriage_Pass) -> None:
            """Update the last carriage pass in the process.

            Args:
                updated_carriage_pass (Carriage_Pass): The updated carriage pass to replace the last one.
            """
            for update_cp_index in range(len(kickback_process) - 1, -1, -1):
                if isinstance(kickback_process[update_cp_index], Carriage_Pass):
                    kickback_process[update_cp_index] = updated_carriage_pass
                    return

        def _update_last_executed_instruction(added_miss: Kick_Instruction) -> None:
            """Update the executed instructions list by adding a kick instruction.

            Args:
                added_miss (Kick_Instruction): The kick instruction to add to the executed instructions.
            """
            for update_index in range(len(kickback_executed_instructions), -1, -1):
                if isinstance(kickback_executed_instructions[update_index - 1], Needle_Instruction):
                    kickback_executed_instructions.insert(update_index, added_miss)
                    return

        for instruction in self.process:
            if isinstance(instruction, Knitout_Line):
                _add_carrier_movement(instruction)
                if isinstance(instruction, Knitout_Instruction):
                    if isinstance(instruction, Yarn_Carrier_Instruction) and not isinstance(instruction, Releasehook_Instruction):  # reset kickback direction for carriers after carrier operations
                        self._kicked_carriers[instruction.carrier_id] = None
            else:  # Carriage pass that may need kickbacks before proceeding.
                assert isinstance(instruction, Carriage_Pass), f"Expected Carriage pass, got {instruction}"
                carriage_pass = instruction
                kicks_to_align_for_cp = self._kicks_to_align_carriers(carriage_pass)
                alignment_left_conflict, alignment_right_conflict = self._kicks_conflict_zone(kicks_to_align_for_cp)
                conflict_kicks = self._kicks_for_conflicting_carriers(carriage_pass, prior_left_conflict=alignment_left_conflict, prior_right_conflict=alignment_right_conflict)
                kicks_before_cp = kicks_to_align_for_cp
                kicks_before_cp.extend(conflict_kicks)
                add_on, kicks_before_cp = self._split_kicks_to_extend_last_pass(kicks_before_cp)
                if add_on is not None:  # there is a kickback that can extend the last carriage pass without causing new conflicts
                    assert isinstance(self._last_carrier_movement, Carriage_Pass)
                    add_on_cp = Carriage_Pass_with_Kick(self._last_carrier_movement, [add_on])
                    _updated = add_on.execute(self.kickback_machine)
                    _update_last_carriage_pass(add_on_cp)
                    _update_last_executed_instruction(add_on)
                for kick in kicks_before_cp:
                    kick_cp = Carriage_Pass(kick, rack=0, all_needle_rack=False)
                    _add_carrier_movement(kick_cp)
                    for cid in kick.carrier_set.carrier_ids:
                        self._kicked_carriers[cid] = kick.direction
                _add_carrier_movement(carriage_pass)
                if carriage_pass.carrier_set is not None:
                    for cid in carriage_pass.carrier_set.carrier_ids:  # reset kickback direction for any carriers involved in the carriage pass.
                        self._kicked_carriers[cid] = None
        self.process = kickback_process
        self.executed_instructions = kickback_executed_instructions
        self.knitting_machine = self.kickback_machine
        self._carriage_passes: list[Carriage_Pass] = [cp for cp in self.process if isinstance(cp, Carriage_Pass)]
        self._left_most_position: int | None = None
        self._right_most_position: int | None = None
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
