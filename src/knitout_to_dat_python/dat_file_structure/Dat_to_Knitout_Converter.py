"""Module containing the Dat_to_Knitout_Converter class."""
import struct

from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.Header_Line import get_machine_header
from knitout_interpreter.knitout_operations.Rack_Instruction import Rack_Instruction
from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction
from knitout_interpreter.knitout_operations.carrier_instructions import Inhook_Instruction, Releasehook_Instruction
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_to_dat_python.dat_file_structure.dat_codes.dat_file_color_codes import WIDTH_SPECIFIER
from knitout_to_dat_python.dat_file_structure.raster_processes.Pixel_Carriage_Pass_Converter import Pixel_Carriage_Pass_Converter


class Dat_to_Knitout_Converter:
    """
    Class to convert a Shima Seiki Dat file to knitout instructions.
    """

    def __init__(self, dat_filename: str, pattern_buffer: int = 4):
        self.dat_filename: str = dat_filename
        self.pixels: list[list[int]] = []
        self._read_dat_file_to_pixels()
        self._trim_pixels_to_pattern()
        self.expected_pattern_width: int = -1
        self._set_expected_pattern_width(pattern_buffer)
        self._trim_startup_sequence()
        self._trim_end_sequence()
        self.rasters: list[Pixel_Carriage_Pass_Converter] = [Pixel_Carriage_Pass_Converter(row, pattern_buffer=pattern_buffer) for row in self.pixels]
        for raster in self.rasters:
            assert raster.pattern_width <= self.expected_pattern_width, f"Raster {raster} has width of {raster.pattern_width} but expected width <= {self.expected_pattern_width}"
        self.process: list[Knitout_Instruction | Carriage_Pass] = []
        self.executed_instructions: list[Knitout_Instruction] = []
        self._read_process()

    def _read_process(self) -> None:
        """
        Reads the Pixel rows into a knitout process and executed isntruction set.
        """
        self.process: list[Knitout_Instruction | Carriage_Pass] = []
        self.executed_instructions: list[Knitout_Instruction] = []

        carrier_on_gripper: None | int = None
        rack: int = 0
        all_needle_rack: bool = False

        def _add_to_process(e: Knitout_Instruction | Carriage_Pass | None) -> tuple[bool, None | int | tuple[int, bool]]:
            """

            Args:
                e: The executed instruction or carriage pass to add to the process.

            Returns:
                A tuple:
                    The first value is a boolean which is True if the executed process would update a local variable involving the knitting machine.
                    The second value is None if there are no local values to update.
                    Otherwise, the second value may be a tuple of an int and bool to set the new racking, or an integer to set the current carrier on the yarn-inserting-hook.

            """
            if e is None:
                return False, None
            elif isinstance(e, Rack_Instruction):
                if e.rack != rack or e.all_needle_rack != all_needle_rack:
                    self.process.append(e)
                    return True, (e.rack, e.all_needle_rack)
                else:
                    return False, None
            elif isinstance(e, Inhook_Instruction):
                self.process.append(e)
                return True, e.carrier_id
            elif isinstance(e, Releasehook_Instruction):
                self.process.append(e)
                return True, None
            else:  # outhook, pause instruction, or carriage pass
                self.process.append(e)
                return False, None

        for i, raster in enumerate(self.rasters):
            raster_process = raster.get_execution_process(carrier_on_gripper)
            for execution in raster_process:
                has_update, updated_value = _add_to_process(execution)
                if has_update:
                    if isinstance(updated_value, tuple):  # rack update
                        rack = updated_value[0]
                        all_needle_rack = updated_value[1]
                    else:
                        carrier_on_gripper = updated_value

        for execution in self.process:
            if isinstance(execution, Knitout_Instruction):
                self.executed_instructions.append(execution)
            else:
                assert isinstance(execution, Carriage_Pass)
                for instruction in execution:
                    if not isinstance(instruction, Kick_Instruction):  # skip kick instructions
                        self.executed_instructions.append(instruction)

    def _trim_startup_sequence(self, startup_length: int = 3) -> None:
        """
        Trim the starting sequence common to knitout files.
        Args:
            startup_length: The length of the expected startup sequence.
        """
        self.pixels = self.pixels[startup_length:]

    def _trim_end_sequence(self, end_length: int = 3) -> None:
        """
        Trim the end sequence common to knitout files.
        Args:
            end_length: The length of the expected end sequence.
        """
        self.pixels = self.pixels[:-1 * end_length]

    def _set_expected_pattern_width(self, pattern_buffer: int = 4) -> None:
        """
            Determines the expected pattern width by searching for the top pattern specifier row.
            Removes all rows above the pattern specifier row from pixels.
        """
        i = 0
        for i, row in enumerate(reversed(self.pixels)):
            if not any(p != WIDTH_SPECIFIER for p in row):  # True if the row only contains the color for a width specifier.
                self.expected_pattern_width = len(row) - (pattern_buffer * 2) - 2  # stopping marks and pattern buffer
                break
        self.pixels = self.pixels[:(-1 * i) - 1]

    def _trim_pixels_to_pattern(self) -> None:
        """
            Trims the pixel set of empty buffer rows and edges.
        """
        # Remove all empty rows from the pixels.
        self.pixels = [row for row in self.pixels if any(p != 0 for p in row)]

        def _trim_row(row: list[int]) -> list[int]:
            """
            Trims a row of the left and right empty value buffer.
            Args:
                row: The row to trim.

            Returns: The Trimmed row.
            """
            i = 0
            for i, x in enumerate(row):
                if x != 0:
                    if x == 20:  # First Option on Left side (0 value before had meaning)
                        i -= 1
                    break
            row = row[i:]
            for i, x in enumerate(reversed(row)):
                if x != 0:
                    if x == 20:  # First Option on Right side (0 value before had meaning)
                        i -= 1
                    break
            return row[:-1 * i]

        self.pixels = [_trim_row(row) for row in self.pixels]

    def _read_dat_file_to_pixels(self) -> None:
        """
        Read a DAT file and convert it to a list of lists of integers.
        Each inner list represents a row of pixels from top to bottom.

        Returns:
            List of lists where each inner list contains pixel color indices for one row
        """
        with open(self.dat_filename, 'rb') as f:
            # Read header (0x200 bytes)
            header_data = f.read(0x200)

            # Parse header using little-endian format
            x_min, y_min, x_max, y_max, magic1 = struct.unpack('<HHHHH', header_data[:10])
            magic2 = struct.unpack('<H', header_data[16:18])[0]

            # Validate magic numbers
            if magic1 != 1000 or magic2 != 1000:
                raise ValueError(f"Invalid DAT file: magic numbers are {magic1}, {magic2}, expected 1000, 1000")

            # Calculate dimensions
            width = x_max - x_min + 1
            height = y_max - y_min + 1

            print(f"DAT file dimensions: {width} x {height}")

            # Skip palette data (0x400 bytes = 3*256 RGB values)
            _palette_data = f.read(0x400)

            # Read run-length encoded data
            rle_data = f.read()

            # Decode run-length encoded data
            self.pixels = []
            current_row = []
            pixels_in_current_row = 0

            i = 0
            while i < len(rle_data):
                if i + 1 >= len(rle_data):
                    break

                color_index = rle_data[i]
                run_length = rle_data[i + 1]

                # Add pixels to current row
                for _ in range(run_length):
                    current_row.append(color_index)
                    pixels_in_current_row += 1

                    # If we've filled a complete row, start a new one
                    if pixels_in_current_row == width:
                        self.pixels.append(current_row)
                        current_row = []
                        pixels_in_current_row = 0

                i += 2

            # Add any remaining partial row
            if current_row:
                self.pixels.append(current_row)

            # Validate we got the expected number of rows
            assert len(self.pixels) == height, f"Expected {height} rows, got {len(self.pixels)} rows"

    def write_knitout(self, knitout_filename: str) -> None:
        """
        Writes the knitout gathered from the dat file to the given knitout filename.
        Args:
            knitout_filename: The name of the knitout file to write.
        """
        header_lines = get_machine_header(Knitting_Machine())
        with open(knitout_filename, 'w') as f:
            f.writelines([str(h) for h in header_lines])
            f.writelines([str(e) for e in self.executed_instructions])
