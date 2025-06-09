"""Test suite for adding kickbacks to a knitout execution - converted to unittest."""
import unittest

from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction

from knitout_to_dat_python.kickback_injection.kickback_execution import Knitout_Executer_With_Kickbacks, Kick_Instruction


class TestKickbackExecution(unittest.TestCase):
    """Test class for kickback execution functionality."""

    @staticmethod
    def get_kickback_executer(knitout: str, pattern_is_file: bool = False) -> Knitout_Executer_With_Kickbacks:
        """Helper method to create a kickback executer from a knitout file.

        Args:
            pattern_is_file: If set to true, looks for a knitout file to parse instead of a test string with the knitout code.
            knitout: Filename of the knitout to process into the kickback executer.

        Returns:
            Configured kickback executer.
        """
        knitout_lines = parse_knitout(knitout, pattern_is_file=pattern_is_file)
        return Knitout_Executer_With_Kickbacks(knitout_lines, Knitting_Machine())

    @staticmethod
    def get_kicks(kickback_executer: Knitout_Executer_With_Kickbacks) -> list[Kick_Instruction]:
        """Helper method to extract kick instructions from executer.

        Args:
            kickback_executer: The kickback executer to collect from.

        Returns:
            The list of kick back instruction in the execution in the order that they are added.
        """
        return [i for i in kickback_executer.process if isinstance(i, Kick_Instruction)]

    def test_single_carrier_no_kicks(self) -> None:
        """
        Tests if any kickbacks are introduced with a simple tuck.
        """
        k = r"""
            inhook 1;
            tuck - f1 1;
            releasehook 1;
            outhook 1;
        """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 0, f"Expected no kicks. Got {kicks}")

    def test_sequential_carriers_no_kicks(self) -> None:
        """Test that two carriers operating at different positions don't conflict."""
        k = r"""
            inhook 1;
            tuck + f10 1;
            releasehook 1;
            outhook 1;
            inhook 2;
            tuck + f100 2;
            releasehook 2;
            outhook 2;
        """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 0, f"Expected no kicks. Got {kicks}")

    def test_distant_carriers_no_kicks(self) -> None:
        """Test that two carriers operating at different positions don't conflict."""
        k = r"""
            inhook 1;
            tuck + f10 1;
            releasehook 1;
            inhook 2;
            tuck + f100 2;
            releasehook 2;
            outhook 1;
            outhook 2;
        """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 0, f"Expected no kicks. Got {kicks}")

    def test_simple_pass_over_conflict(self) -> None:
        """Test that a carrier gets kicked when it would conflict with another carrier's operation."""
        k = r"""
        inhook 1;
        tuck - f50 1;
        releasehook 1;
        inhook 2;
        tuck - f60 2;
        tuck - f45 2;
        releasehook 2;
        outhook 1;
        outhook 2;
        """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 1, f"Expected exactly 1 kick to resolve conflict. Got {len(kicks)} kicks.")

    def test_conflict_with_stopping_distance(self) -> None:
        """Test that a carrier gets kicked when it would conflict with another carrier's stopping distance."""
        k = r"""
        inhook 1;
        tuck - f20 1;
        releasehook 1;
        inhook 2;
        tuck - f25 2;
        releasehook 2;
        outhook 1;
        outhook 2;
        """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 1, f"Expected exactly 1 kick to resolve conflict. Got {len(kicks)} kicks.")

    def test_kick_direction_closer_left_edge(self) -> None:
        """Test that a carrier gets kicked leftward when that is the shortest distance ouf of the conflict zone."""
        k = r"""
        inhook 1;
        tuck - f50 1;
        releasehook 1;
        inhook 2;
        tuck - f80 2;
        tuck - f45 2;
        releasehook 2;
        outhook 1;
        outhook 2;
        """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 1, f"Expected exactly 1 kick to resolve conflict. Got {len(kicks)} kicks.")
        self.assertEqual(kicks[0].direction, Carriage_Pass_Direction.Leftward, f"Expected to kick to closer left edge. Got {kicks}")

    def test_kick_direction_closer_right_edge(self) -> None:
        """Test that a carrier gets kicked rightward when that is the shortest distance out of the conflict zone."""
        k = r"""
        inhook 1;
        tuck - f50 1;
        releasehook 1;
        inhook 2;
        tuck - f55 2;
        tuck - f10 2;
        releasehook 2;
        outhook 1;
        outhook 2;
        """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 1, f"Expected exactly 1 kick to resolve conflict. Got {len(kicks)} kicks.")
        self.assertEqual(kicks[0].direction, Carriage_Pass_Direction.Rightward, f"Expected to kick to closer right edge. Got {kicks}")

    def test_kick_direction_left_equal_distance(self) -> None:
        """Test that a carrier gets kicked left when the distances out of the conflict zone are equal."""
        k = fr"""
        inhook 1;
        tuck - f50 1;
        releasehook 1;
        inhook 2;
        tuck - f{50 - 5 - Knitout_Executer_With_Kickbacks.STOPPING_DISTANCE} 2;
        tuck - f{50 + 5 + Knitout_Executer_With_Kickbacks.STOPPING_DISTANCE} 2;
        releasehook 2;
        outhook 1;
        outhook 2;
        """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 1, f"Expected exactly 1 kick to resolve conflict. Got {len(kicks)} kicks.")
        self.assertEqual(kicks[0].direction, Carriage_Pass_Direction.Leftward, f"Expected to kick to closer right edge. Got {kicks}")

    def test_multiple_carriers(self) -> None:
        """Test that multiple carriers get kicked out of conflict zone."""
        k = r"""
                inhook 1;
                tuck - f30 1;
                releasehook 1;
                inhook 2;
                tuck - f41 2; Out of conflict with
                releasehook 2;
                inhook 3;
                tuck - f50 3;
                tuck - f20 3;
                releasehook 3;
                outhook 1;
                outhook 2;
                outhook 3;
                """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 2, f"Expected 2 kicks for carrier 1 and carrier 2 kick to resolve conflict. Got {len(kicks)} kicks.")
        self.assertEqual(kicks[0].carrier_set.carrier_ids[0], 1, f"Expected carrier 1 to kick. Got {kicks}.")
        self.assertEqual(kicks[1].carrier_set.carrier_ids[0], 2, f"Expected carrier 2 to kick. Got {kicks}.")

    def test_previously_kicked_carrier(self) -> None:
        """Test that a carrier kicked into conflict range is kicked again to resolve the new conflict."""
        k = r"""
        inhook 1;
        tuck - f40 1;
        releasehook 1;
        inhook 2;
        ; Expect kickback - f29 1 out of conflict zone 30-50
        tuck - f50 2;
        tuck - f40 2;
        releasehook 2;
        inhook 3;
        tuck - f31 3;
        tuck - f28 3;
        releasehook 3;
        outhook 1;
        outhook 2;
        outhook 3;
        """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 3, f"Expected 3 kicks for carrier 1 for kickback conflicts. Got \n{kicks}")
        self.assertEqual(kicks[0].carrier_set.carrier_ids[0], 1, f"Expected carrier 1 to kick out of way of carrier 2. Got {kicks}.")
        self.assertEqual(kicks[1].carrier_set.carrier_ids[0], 2, f"Expected c2 to kick out of way of c1 kick. Got {kicks}.")
        self.assertEqual(kicks[2].carrier_set.carrier_ids[0], 1, f"Expected carrier 1 out of way of carrier 3. Got {kicks}.")

    def test_kicked_carrier_kicked_out_of_new_conflict(self) -> None:
        """Test that a carrier kicked into conflict range is kicked again to resolve the new conflict."""
        k = r"""
        inhook 1;
        tuck - f40 1;
        releasehook 1;
        inhook 2;
        tuck - f40 2;
        releasehook 2;
        inhook 3;
        tuck - f40 3;
        releasehook 3;
        outhook 1;
        outhook 2;
        outhook 3;
        """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 3, f"Expected 3 kicks. Got {len(kicks)} kicks.")
        self.assertEqual(kicks[0].carrier_set.carrier_ids[0], 1, f"Expected carrier 1 to kick out of way of carrier 2. Got {kicks}.")
        self.assertEqual(kicks[1].carrier_set.carrier_ids[0], 1, f"Expected carrier 1 to kick out of way of carrier 2's kickback. Got {kicks}.")
        self.assertEqual(kicks[2].carrier_set.carrier_ids[0], 2, f"Expected carrier 2 to kick out of way of carrier 3. Got {kicks}.")

    def test_kicked_carrier_remains_out_of_conflict(self) -> None:
        """Test that a carrier that has been kicked out of a conflict range stays kicked out of that range."""
        k = r"""
                inhook 1;
                tuck - f40 1;
                releasehook 1;
                inhook 2;
                tuck - f40 2;
                releasehook 2;
                inhook 3;
                tuck - f30 3;
                releasehook 3;
                outhook 1;
                outhook 2;
                outhook 3;
                """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 1, f"Expected only 1 kick. Got {len(kicks)} kicks.")
        self.assertEqual(kicks[0].carrier_set.carrier_ids[0], 1, f"Expected carrier 1 to kick out of way of carrier 2. Got {kicks}.")

    def test_kicked_carrier_uncertainty_conflicts(self) -> None:
        """Test that a carrier that has been kicked is kicked again because of a possible conflict zone."""
        k = r"""
            inhook 1;
            tuck - f40 1;
            releasehook 1;
            inhook 2;
            ;Expected kick: miss + f41 1 (conflict zone 41->51)
            tuck - f40 2;
            releasehook 2;
            inhook 3;
            tuck - f51 3;
            releasehook 3;
            outhook 1;
            outhook 2;
            outhook 3;
            """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 3, f"Expected 3 kicks. Got {kicks} kicks.")
        self.assertEqual(kicks[0].carrier_set.carrier_ids[0], 1, f"Expected carrier 1 to kick out of way of carrier 2. Got {kicks}")
        self.assertEqual(kicks[1].carrier_set.carrier_ids[0], 2, f"Expected carrier 2 to kick out of way of kicked carrier 1. Got {kicks}")
        self.assertEqual(kicks[2].carrier_set.carrier_ids[0], 1, f"Expected carrier 1 to kick out of uncertain conflict with carrier 3. Got {kicks}")

    def test_kicked_carrier_reused(self) -> None:
        """Test that knitting continues without additional kicks after a carrier is kicked"""
        k = r"""
            inhook 1;
            tuck - f40 1;
            releasehook 1;
            inhook 2;
            ;Expected kick: miss + f41 1 (conflict zone 41->51)
            tuck - f40 2;
            releasehook 2;
            tuck + f40 1;
            outhook 1;
            outhook 2;
            """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 2, f"Expected 2 kicks. Got {kicks} kicks.")
        self.assertEqual(kicks[0].carrier_set.carrier_ids[0], 1, f"Expected carrier 1 to kick out of way of carrier 2. Got {kicks}")
        self.assertEqual(kicks[1].carrier_set.carrier_ids[0], 2, f"Expected carrier 2 to kick out of way of carrier 1. Got {kicks}")

    def test_no_self_kicks(self) -> None:
        """Test that knitting multiple carriage passes causes no kicks of operating carrier"""
        k = r"""
            inhook 1;
            tuck - f40 1;
            releasehook 1;
            tuck + f40 1;
            tuck - f40 1;
            tuck + f40 1;
            outhook 1;
            """
        executer = self.get_kickback_executer(k)
        kicks = self.get_kicks(executer)
        self.assertEqual(len(kicks), 0, f"Expected 0 kicks. Got {kicks}")
