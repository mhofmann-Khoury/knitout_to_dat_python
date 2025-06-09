"""
Subclass of Knitout_Executer that introduces kickbacks for carrier management when creating Dat files.
"""
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line
from knitout_interpreter.knitout_operations.carrier_instructions import Knitout_Instruction, Yarn_Carrier_Instruction, Releasehook_Instruction
from knitout_interpreter.knitout_operations.needle_instructions import Miss_Instruction
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_to_dat_python.kickback_injection.fixed_knitout_execution import Knitout_Executer


class Kick_Instruction(Miss_Instruction):
    """
        A subclass of the Miss_Instruction used to mark kickbacks added in dat-complication process.
    """

    def __init__(self, position: int, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set, comment: None | str = None):
        super().__init__(needle=Needle(is_front=True, position=position), direction=direction, cs=cs, comment=comment)


class Knitout_Executer_With_Kickbacks(Knitout_Executer):
    """
        Subclass of the Knitout_Executer that introduces kickback logic for carrier management before each carriage pass.
    """
    STOPPING_DISTANCE: int = 10

    def __init__(self, instructions: list[Knitout_Line], knitting_machine: Knitting_Machine, accepted_error_types: list | None = None):
        self.process: list[Knitout_Line | Carriage_Pass] = []
        self.executed_instructions: list[Knitout_Line] = []
        super().__init__(instructions, knitting_machine, accepted_error_types)
        # track the last kicking direction of each carrier. None implies that a carrier has not been kicked since it was last used.
        self._kicked_carriers: dict[int, Carriage_Pass_Direction | None] = {carrier.carrier_id: None for carrier in self.knitting_machine.carrier_system.carriers}
        self.add_kickbacks_to_process()

    def _get_carrier_position_range(self, cid: int, knitting_machine: Knitting_Machine) -> None | int | tuple[int, int]:
        """
        Args:
            cid: The id of the carrier to identify the position of.
            knitting_machine: The current state of the knitting machine to reference.

        Returns:
            None if the carrier is not active.
            An integer for the exact needle position of the carrier if it has not been kicked.
            A tuple of integers for the leftmost and rightmost possible positions of the carrier if it has been kicked.
        """
        carrier = knitting_machine.carrier_system[cid]
        if carrier.position is None:
            return None  # inactive carrier
        elif self._kicked_carriers[cid] is None:  # not kicked, return a precise position
            assert isinstance(carrier.position, int)
            return carrier.position
        elif self._kicked_carriers[cid] is Carriage_Pass_Direction.Leftward:  # Kicked leftward:
            return carrier.position - self.STOPPING_DISTANCE, carrier.position
        else:  # Kicked rightward
            return carrier.position, carrier.position + self.STOPPING_DISTANCE

    def _carriage_pass_conflict_zone(self, carriage_pass: Carriage_Pass, knitting_machine: Knitting_Machine) -> tuple[int, int] | None:
        """

        Args:
            carriage_pass: The carriage pass to identify the carrier-conflict zone of.
            knitting_machine: The current state of the knitting machine prior to the carriage_pass.

        Returns: None if there is no conflict zone for the carriage pass. Otherwise, return the leftmost and rightmost positions that carriers will move in this action.

        """
        if carriage_pass.carrier_set is None or len(carriage_pass.carrier_set) == 0:
            return None  # No carriers involved in the carriage pass, thus no conflicts.
        leftmost_position, rightmost_position = carriage_pass.carriage_pass_range()
        if carriage_pass.direction is Carriage_Pass_Direction.Leftward:
            leftmost_position -= self.STOPPING_DISTANCE
        else:  # Rightward carriage pass
            rightmost_position += self.STOPPING_DISTANCE
        for cid in carriage_pass.carrier_set.carrier_ids:
            carrier_position = self._get_carrier_position_range(cid, knitting_machine)
            if isinstance(carrier_position, int):  # Specific position, no kickbacks
                leftmost_position = min(carrier_position, leftmost_position)
                rightmost_position = max(carrier_position, rightmost_position)
            elif isinstance(carrier_position, tuple):  # kicked carrier, add stopping distance buffer from prior kicks to the conflict zone.
                leftmost_position = min(carrier_position[0], leftmost_position)
                rightmost_position = max(carrier_position[1], rightmost_position)
        return leftmost_position, rightmost_position

    def _get_kicks_before_carriage_pass(self, carriage_pass: Carriage_Pass, knitting_machine: Knitting_Machine) -> list[Kick_Instruction]:
        conflict_zone = self._carriage_pass_conflict_zone(carriage_pass, knitting_machine)
        if conflict_zone is None:
            return []
        leftmost_conflict = conflict_zone[0]
        rightmost_conflict = conflict_zone[1]
        exempt_carriers = set()
        if carriage_pass.carrier_set is not None:
            exempt_carriers.update(carriage_pass.carrier_set.carrier_ids)
        return self._kicks_out_of_conflict_zone(leftmost_conflict, rightmost_conflict, exempt_carriers=exempt_carriers, knitting_machine=knitting_machine)

    def _kicks_out_of_conflict_zone(self, leftmost_conflict: int, rightmost_conflict: int, exempt_carriers: set[int], knitting_machine: Knitting_Machine,
                                    allow_leftward_movement: bool = True, allow_rightward_movement: bool = True) -> list[Kick_Instruction]:
        assert allow_leftward_movement or allow_rightward_movement, f"Must have at least leftward or rightward options for kickbacks"
        kicks: list[Kick_Instruction] = []
        conflict_carriers = self._carriers_in_conflict_zone(leftmost_conflict, rightmost_conflict, exempt_carriers, knitting_machine)
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
            leftward_conflict_zone_extension = 1 + (len(leftward_positions_to_carriers) * self.STOPPING_DISTANCE)
            kicks = self._kicks_out_of_conflict_zone(leftmost_conflict=leftmost_conflict - leftward_conflict_zone_extension, rightmost_conflict=leftmost_conflict,
                                                     exempt_carriers=conflicting_kickback_exemptions, knitting_machine=knitting_machine,
                                                     allow_leftward_movement=True, allow_rightward_movement=False)
            kick_insert_index = len(kicks)
            for push_group, pos in enumerate(sorted(leftward_positions_to_carriers, reverse=True)):
                carriers = leftward_positions_to_carriers[pos]
                kick_position = leftmost_conflict - 1 - (push_group * self.STOPPING_DISTANCE)
                kick = Kick_Instruction(kick_position, Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set(list(carriers)),
                                        comment=f"Move out of conflict zone {leftmost_conflict} to {rightmost_conflict} of carriers {exempt_carriers}")
                kicks.insert(kick_insert_index, kick)  # add kick to front of kicks because we want the order to move the leftmost carriers first.

        # Set rightward kickbacks moving right to leftmost carrier sets
        if len(rightward_positions_to_carriers) > 0:
            rightward_conflict_zone_extension = 1 + (len(rightward_positions_to_carriers) * self.STOPPING_DISTANCE)
            conflict_kicks = self._kicks_out_of_conflict_zone(leftmost_conflict=rightmost_conflict, rightmost_conflict=rightmost_conflict + rightward_conflict_zone_extension,
                                                              exempt_carriers=conflicting_kickback_exemptions, knitting_machine=knitting_machine,
                                                              allow_leftward_movement=False, allow_rightward_movement=True)
            kicks.extend(conflict_kicks)
            kick_insert_index = len(kicks)
            for push_group, pos in enumerate(sorted(rightward_positions_to_carriers)):
                carriers = rightward_positions_to_carriers[pos]
                kick_position = rightmost_conflict + 1 + (push_group * self.STOPPING_DISTANCE)
                kick = Kick_Instruction(kick_position, Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set(list(carriers)),
                                        comment=f"Move out of conflict zone {leftmost_conflict} to {rightmost_conflict} of carriers {exempt_carriers}")
                kicks.insert(kick_insert_index, kick)  # add to front of rightmost kicks because we want the order to move the rightmost carriers first.

        return kicks

    @staticmethod
    def _carriers_in_conflict_zone(leftmost_conflict: int, rightmost_conflict: int, exempt_carriers: set[int], knitting_machine: Knitting_Machine) -> dict[int, int]:
        """
        Args:
            leftmost_conflict: The leftmost slot of the conflict zone.
            rightmost_conflict:  The rightmost slot of the conflict zone.
            exempt_carriers: The set of carriers that are exempts from conflicts since they are involved in the operation already.
            knitting_machine: The current state of the knitting machine.

        Returns:
            Dictionary of carrier ids keyed to carrier's current position. The dictionary will contain an entry for every carrier in the conflict zone.

        """
        conflict_carriers: dict[int, int] = {}  # carrier ids keyed to current conflicting position.
        for carrier in knitting_machine.carrier_system.active_carriers:  # check only the active carriers for conflicts
            if carrier.carrier_id not in exempt_carriers:
                assert carrier.position is not None
                if leftmost_conflict <= carrier.position <= rightmost_conflict:
                    conflict_carriers[carrier.carrier_id] = carrier.position
        return conflict_carriers

    def add_kickbacks_to_process(self) -> None:
        """
            Reruns the executor's process but adds kickback logic to form a new kickback program.
        """
        kickback_process: list[Knitout_Line | Carriage_Pass] = []
        kickback_executed_instructions: list[Knitout_Line] = []
        kickback_machine = Knitting_Machine(self.knitting_machine.machine_specification)
        for instruction in self.process:
            if isinstance(instruction, Knitout_Instruction):
                updated = instruction.execute(kickback_machine)
                if updated:
                    kickback_process.append(instruction)
                    kickback_executed_instructions.append(instruction)
                if isinstance(instruction, Yarn_Carrier_Instruction) and not isinstance(instruction, Releasehook_Instruction):  # reset kickback direction for carriers after carrier operations
                    self._kicked_carriers[instruction.carrier_id] = None
            elif isinstance(instruction, Knitout_Line):
                kickback_process.append(instruction)
                kickback_executed_instructions.append(instruction)
            else:  # Carriage pass that may need kickbacks before proceeding.
                assert isinstance(instruction, Carriage_Pass), f"Expected Carriage pass, got {instruction}"
                carriage_pass = instruction
                kicks = self._get_kicks_before_carriage_pass(carriage_pass, kickback_machine)
                for kick in kicks:
                    kick.execute(kickback_machine)
                    kickback_process.append(kick)
                    kickback_executed_instructions.append(kick)
                    for cid in kick.carrier_set.carrier_ids:
                        self._kicked_carriers[cid] = kick.direction
                executed_pass = carriage_pass.execute(kickback_machine)
                kickback_process.append(carriage_pass)
                kickback_executed_instructions.extend(executed_pass)
                if carriage_pass.carrier_set is not None:
                    for cid in carriage_pass.carrier_set.carrier_ids:  # reset kickback direction for any carriers involved in the carriage pass.
                        self._kicked_carriers[cid] = None
        self.process = kickback_process
        self.executed_instructions = kickback_executed_instructions
        self.knitting_machine = kickback_machine
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
