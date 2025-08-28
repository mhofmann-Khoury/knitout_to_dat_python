"""Dat_File class for creating Shima Seiki DAT files from knitout files.

This module provides comprehensive functionality for converting knitout files to Shima Seiki DAT format.
It handles the complete conversion pipeline including knitout parsing, raster generation, run-length encoding, and DAT file creation.
The implementation is based on the CMU Textile Lab's knitout-to-dat.js functionality.
"""

import os
import struct

from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from knitout_interpreter.knitout_operations.carrier_instructions import (
    Inhook_Instruction,
    Outhook_Instruction,
    Releasehook_Instruction,
)
from knitout_interpreter.knitout_operations.Header_Line import Knitting_Machine_Header
from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction
from knitout_interpreter.knitout_operations.knitout_instruction import (
    Knitout_Instruction,
)
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.Knitting_Machine_Specification import (
    Knitting_Machine_Specification,
    Knitting_Position,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)

from knitout_to_dat_python.dat_file_structure.dat_bookend_sequences import (
    finish_knit_sequence,
    startup_knit_sequence,
)
from knitout_to_dat_python.dat_file_structure.dat_codes.dat_file_color_codes import (
    WIDTH_SPECIFIER,
)
from knitout_to_dat_python.dat_file_structure.dat_codes.option_value_colors import (
    Carriage_Pass_Direction_Color,
    Hook_Operation_Color,
    Knit_Cancel_Color,
)
from knitout_to_dat_python.dat_file_structure.raster_carriage_passes.Outhook_Raster import (
    Outhook_Raster_Pass,
)
from knitout_to_dat_python.dat_file_structure.raster_carriage_passes.Raster_Carriage_Pass import (
    Raster_Carriage_Pass,
)
from knitout_to_dat_python.dat_file_structure.raster_carriage_passes.Raster_Soft_Miss_Pass import (
    Soft_Miss_Raster_Pass,
)
from knitout_to_dat_python.dat_file_structure.raster_carriage_passes.Releasehook_Raster import (
    Releasehook_Raster_Pass,
)
from knitout_to_dat_python.kickback_injection.kickback_execution import (
    Knitout_Executer_With_Kickbacks,
)


class Knitout_to_Dat_Converter:
    """A class for creating Shima Seiki DAT files from knitout files.

    DAT files are encoded raster images containing knitting patterns and machine instructions.
    The format consists of a header, color palette, and run-length encoded pixel data.
    This class handles the complete conversion pipeline from knitout parsing through DAT file generation.
    """

    # Class constants - palette data that's the same for all DAT files
    PALETTE_STR: str = ("ff 00 ff 00 ff 00 ff 00 6c 4a ff b4 99 90 80 cf 52 51 eb 00 fc b2 fc fc fc fc "
                        "64 d8 eb a0 90 73 9d 73 d8 eb ff b4 ac d7 d8 7f d8 90 ca d8 ae bc 80 9f ff dc "
                        "fc c0 d8 fc 90 ff fd b4 00 a0 32 32 00 35 d8 d8 a8 c0 ff 99 b7 00 e2 c5 90 c0 "
                        "90 90 4a 00 90 6d 00 00 66 33 85 99 78 ca b4 90 7d ff ff ff 7f 69 fa 81 fc ac "
                        "7f b2 b4 b4 b4 d4 ff 90 ff c0 c0 73 d8 a9 bf b4 ff 90 d8 b2 aa 00 d8 00 fb 90 "
                        "81 9d 37 ac dd bf b9 3f ef d7 de fd fe 73 2f 8d fb ff fe ed 06 f5 ea ed ad 3d fc "
                        "fa ef fd 66 8d 7f 7a 5f 79 9b 71 ff ee a8 ff 9f db f5 ff cd f3 e0 fe c8 79 73 1f "
                        "bf e5 f3 f6 e0 de f0 cc 4b 64 40 a1 f7 1a e0 67 ff 64 f5 3f 97 ef 14 96 d7 67 "
                        "b7 ee ba ea 6c bd 26 4e 64 2f bf 9f 7f f3 aa ff e6 bf 57 eb 06 fe 4f ed 6a ef "
                        "62 b7 dd cf 66 6b b2 7a 5a f7 9c 4c 96 9d 00 00 6e c8 00 64 00 00 ff ff 00 00 "
                        "ff ff 24 89 67 b4 99 6c 80 90 91 ff eb 7c b4 76 6c 94 b4 d8 c8 90 ac 66 d8 73 "
                        "7f b2 d8 eb 00 b4 ac c3 48 00 d8 6c a7 b4 8d 9a 60 7f 90 76 fc ff fc fc ff 90 "
                        "eb 90 ff ff ca e9 d5 af 6c 6c 54 60 ff 66 bc a0 c5 ae cf ff b4 d8 89 70 c0 a5 "
                        "99 66 c1 ad 7a d6 30 28 6c 48 8f 00 99 66 00 3f a3 64 d8 eb 7f b2 6c 90 d8 95 "
                        "bf 6c cf cf 90 b2 d8 e5 6a d8 dd d8 b4 73 00 00 9d 96 fd 65 df 5a 9d ac f3 df "
                        "f7 6e ff db ff fb fb ab 31 c7 fa af 6a af 03 9d fe ea 0c 9f de a7 f5 7d 00 c7 ff "
                        "67 bf 7f 7f 87 fc ce bf 2f 6f be ba fd f2 5f 2d df c8 7f 5b b5 77 6f 8f db 92 7e "
                        "f0 5f ff 9d 40 ba f7 ec 6d fb 64 64 96 e3 c7 f7 d3 ff af 7f f5 f6 73 f7 b2 5a "
                        "5f 88 89 b7 bc fd 7f e9 7f 7e 2f fa 7c f7 03 a5 c7 ea fb 8d ff ff 79 5b 00 e7 "
                        "8d 67 b9 ec 59 f7 00 bd 96 af 00 00 7d 64 00 00 00 00 ff ff ff ff 90 99 bd d8 "
                        "99 b4 ff c0 db de 24 91 6c b2 48 63 fc fc c8 fc eb 00 48 b2 01 73 48 ac a0 6c "
                        "eb e1 90 7f fc d8 e1 d8 f5 46 ff ff 90 75 b4 90 48 90 c0 cf c7 90 ff ff e9 e9 "
                        "00 ed b4 d8 b4 b4 ff ff bc a0 b2 b7 c0 cf fc fc 99 99 cf b4 ff ff ff ff 03 ff "
                        "9c 91 d8 b4 a5 8f d2 bb 00 24 b9 0c 6c ac 00 73 6c 48 d8 95 bf 6c 90 90 cf b2 "
                        "b4 e7 69 90 ad fc 6c 73 00 7f 49 00 fe fd a5 6f 7f ff 7b be ab 11 67 ff b9 55 "
                        "9d 7f fb de 7f 7f 7f fb f0 93 fe fb eb bf ef 5d f7 fc 8a de ff 96 3a bd df bb f8 "
                        "3d b0 cf 9e fe 5f fd f3 d9 ff 93 c8 bd aa 37 fd 81 7f be ff 7f f0 91 4b 4c 40 "
                        "4b 67 ce ff a9 7d ff 64 d3 6f f7 b4 f7 ad cf fc e9 cd 7f 81 af 64 f7 51 f5 a4 "
                        "7d df 3f cf f7 fd f9 7f df f0 4d 5f fb ff fb 4f df a9 f0 8a 45 ba 96 fc bd 09 "
                        "b7 00 f2 00 00 00 00 00 64")
    """str: Hexadecimal string representation of the standard DAT file color palette."""

    # Convert palette string to bytes (computed once as class constant)
    PALETTE_BYTES = bytes.fromhex(PALETTE_STR.replace(' ', ''))
    """bytes: Binary representation of the DAT file color palette."""

    # DAT file structure constants
    HEADER_SIZE = 0x200
    """int: Size of the DAT file header in bytes."""

    PALETTE_SIZE = 0x400  # 768 bytes palette + padding to 1024 bytes
    """int: Size of the palette section in bytes (768 bytes palette + padding to 1024 bytes)."""

    DATA_OFFSET = 0x600
    """int: Offset where the run-length encoded data begins in the DAT file."""

    def __init__(self, knitout: str, dat_filename: str, knitout_in_file: bool = True):
        """Initialize a Dat_File instance.

        Args:
            knitout (str): Path to the input knitout file or knitout content string.
            dat_filename (str): Name for the output DAT file.
            knitout_in_file (bool, optional): Whether knitout parameter is a file path (True) or content string (False). Defaults to True.

        Raises:
            ValueError: If palette data is not the expected 768 bytes.
            FileNotFoundError: If knitout file is specified but not found.
            RuntimeError: If knitting range is outside the specified needle bed range when using Keep position.
        """
        # Validate palette
        if len(self.PALETTE_BYTES) != 768:
            raise ValueError(f"Palette should be 768 bytes, got {len(self.PALETTE_BYTES)}")

        self.knitout: str = knitout
        """str: The knitout file path or content string."""

        self.knitout_is_file: bool = knitout_in_file
        """bool: Whether knitout parameter represents a file path."""

        if self.knitout_is_file and not os.path.exists(self.knitout):
            raise FileNotFoundError(f"Knitout file not found: {self.knitout}")

        self.dat_filename: str = dat_filename
        """str: Output DAT filename."""

        # Knitout parsing results
        self.knitout_lines: list[Knitout_Line] = parse_knitout(self.knitout, pattern_is_file=self.knitout_is_file)
        """list[Knitout_Line]: Parsed knitout lines from the input."""

        self.knitout_executer: Knitout_Executer_With_Kickbacks = Knitout_Executer_With_Kickbacks(self.knitout_lines, Knitting_Machine())
        """Knitout_Executer_With_Kickbacks: Executor for processing knitout instructions with kickback support."""

        self._leftmost_slot: int = 0
        """int: The leftmost needle slot used in the pattern."""

        self._rightmost_slot: int = 0
        """int: The rightmost needle slot used in the pattern."""

        self._set_slot_range()

        print(f"Needle bed specified as {self.specified_needle_bed_width} needles at gauge {self.specified_gauge} needles per inch.")

        # Pattern positioning info (derived from headers)
        self.position_offset: int = 0
        """int: Offset for positioning the pattern on the needle bed."""

        self._calculate_positioning()

        # Initialize properties that will be set during processing
        self.raster_data: list[list[int]] = []
        """list[list[int]]: 2D array of pixel values representing the complete DAT raster."""

    @property
    def dat_width(self) -> int:
        """Get the width in pixels of the dat file.

        Returns:
            int: The width in pixels of the dat file. Returns 0 if no raster data exists.
        """
        if len(self.raster_data) == 0:
            return 0
        else:
            return len(self.raster_data[0])

    @property
    def dat_height(self) -> int:
        """Get the height in pixels of the dat file.

        Returns:
            int: The height in pixels of the dat file.
        """
        return len(self.raster_data)

    def _set_slot_range(self) -> None:
        """Set the leftmost and rightmost slot ranges used in the knitout process.

        Analyzes all carriage passes to determine the minimum and maximum needle positions used, accounting for racking offsets to determine the effective slot range.
        """
        def _carriage_pass_range(carriage_pass: Carriage_Pass) -> tuple[int, int]:
            """Get the leftmost and rightmost needle positions in the carriage pass.

            Returns:
                tuple[int, int]: Left most and Right most needle positions in the carriage pass.
            """
            sorted_needles = carriage_pass.rightward_sorted_needles()
            return int(sorted_needles[0].racked_position_on_front(cp.rack)), int(sorted_needles[-1].racked_position_on_front(cp.rack))

        min_left, max_right = 1000, -1
        for cp in self.knitout_executer.process:
            if isinstance(cp, Carriage_Pass):
                left, right = _carriage_pass_range(cp)
                if left < min_left:
                    min_left = left
                if right > max_right:
                    max_right = right
        self._leftmost_slot = min_left
        self._rightmost_slot = max_right

    @property
    def leftmost_slot(self) -> int:
        """Get the minimum needle position of operations in the knitout code.

        Returns:
            int: The minimum needle position of operations in the knitout code. If the knitout never uses a needle position, this will be set to 0.
        """
        return self._leftmost_slot
        # return self.knitout_executer.left_most_position if self.knitout_executer.left_most_position is not None else 0

    @property
    def rightmost_slot(self) -> int:
        """Get the maximum needle position of operations in the knitout code.

        Returns:
            int: The maximum needle position of operations in the knitout code. If the knitout never uses a needle position, this will be set to 0.
        """
        return self._rightmost_slot
        # return self.knitout_executer.right_most_position if self.knitout_executer.right_most_position is not None else 0

    @property
    def slot_range(self) -> tuple[int, int]:
        """Get the leftmost and rightmost needle slots of the knitout process.

        Returns:
            tuple[int, int]: The leftmost and rightmost needle slots of the knitout process.
        """
        return self._leftmost_slot, self._rightmost_slot

    @property
    def knitout_header(self) -> Knitting_Machine_Header:
        """Get the Knitting Machine Header parsed from the given knitout.

        Returns:
            Knitting_Machine_Header: The Knitting Machine Header parsed from the given knitout. Default header values are set if a header value is not explicitly defined.
        """
        return self.knitout_executer.executed_header

    @property
    def machine_specification(self) -> Knitting_Machine_Specification:
        """Get the Knitting Machine Specification parsed from the given knitout header.

        Returns:
            Knitting_Machine_Specification: The Knitting Machine Specification parsed from the given knitout header.
        """
        return self.knitout_header.machine.machine_specification

    @property
    def specified_carrier_count(self) -> int:
        """Get the number of carriers specified for the machine.

        Returns:
            int: The number of carriers specified for the machine given the knitout file header or default values. Defaults to 10 carriers.
        """
        return int(self.machine_specification.carrier_count)

    @property
    def specified_position(self) -> Knitting_Position:
        """Get the position on the bed to knit on.

        Returns:
            Knitting_Position: The position on the bed to knit on given the knitout file header or default values. Defaults to Right side of bed.
        """
        position = self.machine_specification.position
        if isinstance(position, str):
            return Knitting_Position(position)
        return position

    @property
    def specified_needle_bed_width(self) -> int:
        """Get the count of needles on each bed.

        Returns:
            int: The count of needles on each bed given the knitout file header or default values. Defaults to 540 needles.
        """
        needle_count = self.machine_specification.needle_count
        assert isinstance(needle_count, int)
        return needle_count

    @property
    def specified_gauge(self) -> int:
        """Get the gauge of the knitting machine.

        Returns:
            int: The gauge of the knitting machine (needles per inch) given the knitout file header or default values. Defaults to 15 needles per inch.
        """
        gauge = self.machine_specification.gauge
        assert isinstance(gauge, int)
        return gauge

    def _calculate_positioning(self) -> None:
        """Calculate pattern positioning based on headers and needle usage.

        This determines where the pattern will be placed on the machine bed and sets the position_offset property based on the knitting width and specified position.

        Raises:
            RuntimeError: If knitting range is outside the specified needle bed range when using Keep position.
        """
        if self.specified_position is Knitting_Position.Center:
            self.position_offset = round((self.specified_needle_bed_width - (self.rightmost_slot - self.leftmost_slot + 1)) / 2)
        elif self.specified_position is Knitting_Position.Keep:
            if self.leftmost_slot > 0 and self.rightmost_slot <= self.specified_needle_bed_width:
                self.position_offset = self.leftmost_slot
            else:
                raise RuntimeError(f"Knitout: Knitting range ({self.leftmost_slot} -> {self.rightmost_slot} is outside of the range of needles from 0 to {self.specified_needle_bed_width}")
        elif self.specified_position is Knitting_Position.Right:  # Let knitPaint auto set for right edge
            self.position_offset = 0
        else:
            assert self.specified_position is Knitting_Position.Left
            self.position_offset = 1

    def get_dat_header_info(self) -> dict[str, int]:
        """Get current header information.

        Returns:
            dict[str, int]: Dictionary with header information including min_slot, max_slot, position_offset, and pattern_width.
        """
        return {
            'min_slot': self.leftmost_slot,
            'max_slot': self.rightmost_slot,
            'position_offset': self.position_offset,
            'pattern_width': self.knitting_width
        }

    @property
    def knitting_width(self) -> int:
        """Get the width of the range of needles used by the knitting operations.

        Returns:
            int: The width of the range of needles used in by the knitting operations. Returns 0 if rightmost_slot is not greater than leftmost_slot.
        """
        return self.rightmost_slot - self.leftmost_slot + 1 if self.rightmost_slot > self.leftmost_slot else 0

    def create_raster_from_knitout(self, pattern_vertical_buffer: int = 5, pattern_horizontal_buffer: int = 4, option_horizontal_buffer: int = 10) -> None:
        """Create raster data from the parsed knitout instructions.

        Generates the complete raster representation of the knitout pattern including startup sequences, main pattern operations, ending sequences, and appropriate spacing and buffers.

        Args:
            pattern_vertical_buffer (int, optional): Vertical spacing buffer around the pattern. Defaults to 5.
            pattern_horizontal_buffer (int, optional): Horizontal spacing buffer around the pattern. Defaults to 4.
            option_horizontal_buffer (int, optional): Horizontal spacing buffer around option lines. Defaults to 10.
        """
        # Create empty lower padding and startup sequence raster
        startup_sequence = self._get_startup_rasters()
        startup_rasters = [cp.get_raster_row(self.knitting_width, option_horizontal_buffer, pattern_horizontal_buffer) for cp in startup_sequence]
        dat_width = len(startup_rasters[0])
        base_spacer = [[0 for _ in range(dat_width)] for _ in range(pattern_vertical_buffer)]
        self.raster_data: list[list[int]] = base_spacer
        self._extend_raster_data(startup_rasters)

        # Add rasters for the knitout process.
        knitting_sequence = self._get_pattern_rasters()
        has_0_slot = False
        for cp in knitting_sequence:
            if 0 in cp.slot_colors:
                has_0_slot = True
                break
        if not has_0_slot:
            offset_slots = -1
        else:
            offset_slots = 0
        self._extend_raster_data([cp.get_raster_row(self.knitting_width, option_horizontal_buffer, pattern_horizontal_buffer, offset_slots=offset_slots) for cp in knitting_sequence])

        # Create ending sequence
        end_sequence = self._get_end_rasters()
        self._extend_raster_data([cp.get_raster_row(self.knitting_width, option_horizontal_buffer, pattern_horizontal_buffer) for cp in end_sequence])

        # Add pattern spacing buffer
        empty_line = [0] * self.dat_width
        self._append_to_raster_data(empty_line)
        width_line = self._get_knitting_width_raster(pattern_horizontal_buffer, option_horizontal_buffer)
        self._append_to_raster_data(width_line)

        # Add top buffer
        base_spacer = [[0 for _ in range(dat_width)] for _ in range(pattern_vertical_buffer + 1)]
        self._extend_raster_data(base_spacer)

    def _append_to_raster_data(self, row: list[int]) -> None:
        """Append a single row to the raster data.

        Args:
            row (list[int]): The row to append to the raster data.

        Raises:
            AssertionError: If the row length doesn't match the expected DAT width.
        """
        assert len(row) == self.dat_width
        self.raster_data.append(row)

    def _extend_raster_data(self, rows: list[list[int]]) -> None:
        """Extend the raster data with multiple rows.

        Args:
            rows (list[list[int]]): The rows to extend the raster data with.

        Raises:
            AssertionError: If any row length doesn't match the expected DAT width.
        """
        for row in rows:
            self._append_to_raster_data(row)

    def run_length_encode(self) -> list[int]:
        """Run-length encode the raster data into index-length pairs.

        Compresses the raster data using run-length encoding where consecutive pixels of the same color are represented as color-index and run-length pairs.
        This is the standard compression method used in DAT files.

        Returns:
            list[int]: List of alternating color indices and run lengths.

        Raises:
            ValueError: If no raster data exists to encode.
        """
        if not self.raster_data:
            raise ValueError("No raster data to encode. Call create_empty_raster() first.")

        index_length_pairs = []

        for y in range(self.dat_height):
            current_color = self.raster_data[y][0]
            run_length = 0
            assert len(self.raster_data[y]) == self.dat_width
            for x in range(self.dat_width):
                pixel = self.raster_data[y][x]

                if pixel == current_color and run_length < 255:
                    run_length += 1
                else:
                    # Output the current run
                    index_length_pairs.extend([current_color, run_length])
                    current_color = pixel
                    run_length = 1

                # Handle end of row
                if x == self.dat_width - 1:
                    index_length_pairs.extend([current_color, run_length])

        return index_length_pairs

    def create_dat_header(self) -> bytearray:
        """Create the DAT file header.

        Generates the binary header section of the DAT file including dimensions, magic numbers, and other metadata required by the Shima Seiki DAT format specification.

        Returns:
            bytearray: Header as a bytearray of HEADER_SIZE bytes.
        """
        header = bytearray(self.HEADER_SIZE)

        # Write header values in little-endian format
        struct.pack_into('<H', header, 0x00, 0)  # x-min
        struct.pack_into('<H', header, 0x02, 0)  # y-min
        struct.pack_into('<H', header, 0x04, self.dat_width - 1)  # x-max
        struct.pack_into('<H', header, 0x06, self.dat_height - 1)  # y-max
        struct.pack_into('<H', header, 0x08, 1000)  # magic number 1
        struct.pack_into('<H', header, 0x10, 1000)  # magic number 2

        return header

    @staticmethod
    def create_palette_section() -> bytearray:
        """Create the palette section of the DAT file.

        Generates the color palette section using the standard DAT file palette data, padded to the required PALETTE_SIZE.

        Returns:
            bytearray: Palette section as a bytearray (padded to PALETTE_SIZE).
        """
        palette_section = bytearray(Knitout_to_Dat_Converter.PALETTE_SIZE)
        palette_section[:len(Knitout_to_Dat_Converter.PALETTE_BYTES)] = Knitout_to_Dat_Converter.PALETTE_BYTES
        return palette_section

    def _get_startup_rasters(self) -> list[Raster_Carriage_Pass]:
        """Get the list of raster carriage passes for the startup knitting sequences.

        Returns:
            list[Raster_Carriage_Pass]: The list of raster carriage passes for the startup knitting sequences of the pattern width.
        """
        startup_sequence = startup_knit_sequence(self.knitting_width)
        return [Raster_Carriage_Pass(cp, self.machine_specification, min_knitting_slot=self.leftmost_slot, max_knitting_slot=self.rightmost_slot, stitch_number=0)
                for cp in startup_sequence]

    def _get_end_rasters(self) -> list[Raster_Carriage_Pass]:
        """Get the list of raster carriage passes for the ending knitting sequences.

        Creates the ending sequence rasters with the final pass configured for drop sinker operation to properly complete the knitting process.

        Returns:
            list[Raster_Carriage_Pass]: The list of raster carriage passes for the ending knitting sequences.
        """
        ending_sequence = finish_knit_sequence(self.knitting_width)
        rasters = [Raster_Carriage_Pass(cp, self.machine_specification, min_knitting_slot=self.leftmost_slot, max_knitting_slot=self.rightmost_slot, stitch_number=0) for cp in ending_sequence[:-1]]
        sinker_raster = Raster_Carriage_Pass(ending_sequence[-1], self.machine_specification, min_knitting_slot=self.leftmost_slot, max_knitting_slot=self.rightmost_slot, stitch_number=0,
                                             drop_sinker=True)
        rasters.append(sinker_raster)
        return rasters

    def _get_knitting_width_raster(self, pattern_buffer: int = 4, option_buffer: int = 10) -> list[int]:
        """Get the knitting width specification raster row.

        Creates a raster row that specifies the knitting width using WIDTH_SPECIFIER values with appropriate buffering and spacing.

        Args:
            pattern_buffer (int, optional): Buffer space around the pattern. Defaults to 4.
            option_buffer (int, optional): Buffer space around option lines. Defaults to 10.

        Returns:
            list[int]: The raster row specifying the knitting width.

        Raises:
            AssertionError: If the generated raster width doesn't match the expected DAT width.
        """
        option_buffer = Raster_Carriage_Pass.get_option_margin_width(option_buffer)
        raster = [0] * option_buffer  # Left black space of the row
        width_specifier = self.knitting_width + (2 * pattern_buffer) + 2  # Knitting width + left and right buffer + 2 stop markers
        raster.extend([WIDTH_SPECIFIER] * width_specifier)
        raster.extend([0] * option_buffer)
        assert len(raster) == self.dat_width, f"Raster is {len(raster)} pixels wide, but expected {self.dat_width}"
        return raster

    def _get_pattern_rasters(self) -> list[Raster_Carriage_Pass]:
        """Get list of raster carriage passes for each carriage pass in the program.

        Processes each instruction and carriage pass in the knitout execution, handling carrier management, hook operations, pause instructions, and carriage movement optimization.
        Updates carriage move settings based on repeated direction changes.

        Returns:
            list[Raster_Carriage_Pass]: List of raster carriage passes for each carriage pass in the program.

        Raises:
            AssertionError: If inhook operation is attempted on a rightward knitting pass or if a carriage pass cannot be executed on the machine state.
        """
        raster_passes: list[Raster_Carriage_Pass] = []
        inhook_carriers: set[int] = set()
        current_machine_state = Knitting_Machine(self.machine_specification)

        pause_after_next_pass: bool = False
        for execution in self.knitout_executer.process:
            if isinstance(execution, Knitout_Instruction):
                instruction = execution
                if isinstance(instruction, Inhook_Instruction):
                    inhook_carriers.add(instruction.carrier_id)
                elif isinstance(instruction, Releasehook_Instruction):
                    release_passes = self._raster_releasehook(current_machine_state, instruction)
                    raster_passes.extend(release_passes)
                elif isinstance(instruction, Outhook_Instruction):
                    last_raster_pass = raster_passes[-1]
                    if (last_raster_pass.carriage_pass.direction is Carriage_Pass_Direction.Rightward
                            and last_raster_pass.carriage_pass.carrier_set is not None and
                            len(last_raster_pass.carriage_pass.carrier_set.carrier_ids) == 1 and last_raster_pass.carriage_pass.carrier_set.carrier_ids[0] == instruction.carrier_id):
                        last_raster_pass.hook_operation = Hook_Operation_Color.Out_Hook_Operation
                    else:
                        outhook_passes = self._raster_outhook(current_machine_state, instruction)
                        raster_passes.extend(outhook_passes)
                elif isinstance(instruction, Pause_Instruction):
                    pause_after_next_pass = True
                instruction.execute(current_machine_state)  # update machine state as the raster progresses.
            elif isinstance(execution, Carriage_Pass):
                carriage_pass = execution
                hook_operation = Hook_Operation_Color.No_Hook_Operation
                if carriage_pass.carrier_set is not None:
                    for cid in carriage_pass.carrier_set.carrier_ids:
                        if cid in inhook_carriers:
                            hook_operation = Hook_Operation_Color.In_Hook_Operation
                            inhook_carriers.remove(cid)
                raster_pass = Raster_Carriage_Pass(carriage_pass, self.machine_specification, min_knitting_slot=self.leftmost_slot, max_knitting_slot=self.rightmost_slot,
                                                   hook_operation=hook_operation, pause=pause_after_next_pass)
                pause_after_next_pass = False  # reset pause after it has been applied to an instruction.
                raster_passes.append(raster_pass)
                carriage_pass.execute(current_machine_state)  # update teh machine state as the raster progresses
        if pause_after_next_pass:  # if pause after next pass is still set, add it to the last operation.
            raster_passes[-1].pause = True

        if self._leftmost_slot < 0:
            for raster_pass in raster_passes:
                raster_pass.shift_slot_colors(abs(self._leftmost_slot))

        # update carriage move (knit-cancel) values based on carriage pass directions.
        last_color = Carriage_Pass_Direction_Color.Unspecified
        for raster_pass in raster_passes:
            direction_color = raster_pass.direction_color
            if direction_color is not Carriage_Pass_Direction_Color.Unspecified:
                if last_color == direction_color:
                    raster_pass.knit_cancel = Knit_Cancel_Color.Carriage_Move  # Move carriage to return for repeated movement in same direction.
                last_color = direction_color
        return raster_passes

    def _raster_outhook(self, current_machine_state: Knitting_Machine, outhook_instruction: Outhook_Instruction) -> list[Soft_Miss_Raster_Pass]:
        """Create raster passes for outhook operations.

        Generates the necessary raster passes to perform an outhook operation, including an optional preliminary kick pass if the carriage is in the wrong direction.

        Args:
            current_machine_state (Knitting_Machine): The current state of the knitting machine.
            outhook_instruction (Outhook_Instruction): The outhook instruction to convert to raster passes.

        Returns:
            list[Soft_Miss_Raster_Pass]: List of raster passes needed to execute the outhook operation.

        Raises:
            AssertionError: If the carrier to be outhooked has no position.
        """
        outhook_passes = []
        carrier_position = current_machine_state.carrier_system[outhook_instruction.carrier_id].position
        assert isinstance(carrier_position, int), f"Cannot outhook a carrier that has no position: {outhook_instruction.carrier_id}"
        if current_machine_state.carriage.last_direction is Carriage_Pass_Direction.Rightward:  # Need to reset carriage pass so that release is on its own pass.
            kick_for_out = Kick_Instruction(carrier_position, Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set([outhook_instruction.carrier_id]), comment="Kick to outhook rightward on new pass.")
            soft_miss_pass = Soft_Miss_Raster_Pass(kick_for_out, self.machine_specification, min_knitting_slot=self.leftmost_slot, max_knitting_slot=self.rightmost_slot)
            outhook_passes.append(soft_miss_pass)
        outhook_pass = Outhook_Raster_Pass(carrier_position, outhook_instruction.carrier_id, self.machine_specification,
                                           min_knitting_slot=self.leftmost_slot, max_knitting_slot=self.rightmost_slot)
        outhook_passes.append(outhook_pass)
        return outhook_passes

    def _raster_releasehook(self, current_machine_state: Knitting_Machine, release_instruction: Releasehook_Instruction) -> list[Soft_Miss_Raster_Pass]:
        """Create raster passes for releasehook operations.

        Generates the necessary raster passes to perform a releasehook operation.
        Releasehook will be executed in the same direction as the original inhook was executed at the current position of the carrier.
        If the carriage's last move was in the release direction, a Soft-Miss pass is added with knit-cancel for carriage movement.

        Args:
            current_machine_state (Knitting_Machine): The current state of the knitting process that is being rendered. Used to get carrier and carriage position data.
            release_instruction (Releasehook_Instruction): The release hook instruction to raster.

        Returns:
            list[Soft_Miss_Raster_Pass]: The list of 1 or 2 Raster passes used to raster the releasehook operation.

        Raises:
            AssertionError: If the carrier to be released has no position.
        """
        release_passes = []
        release_carrier_position = current_machine_state.carrier_system[release_instruction.carrier_id].position
        assert isinstance(release_carrier_position, int), f"Cannot release a carrier that has no position: {release_instruction.carrier_id}"
        if current_machine_state.carrier_system.hook_input_direction is current_machine_state.carriage.last_direction:  # Add a miss pass to align the carriage for correct release direction.
            kick_to_release = Kick_Instruction(release_carrier_position, ~current_machine_state.carrier_system.hook_input_direction, comment="Kick to set release direction.")
            soft_miss_pass = Soft_Miss_Raster_Pass(kick_to_release, self.machine_specification, min_knitting_slot=self.leftmost_slot, max_knitting_slot=self.rightmost_slot)
            release_passes.append(soft_miss_pass)
        releasehook_pass = Releasehook_Raster_Pass(release_carrier_position, self.machine_specification,
                                                   min_knitting_slot=self.leftmost_slot, max_knitting_slot=self.rightmost_slot)
        release_passes.append(releasehook_pass)
        return release_passes

    def write_dat_file(self) -> None:
        """Write the complete DAT file to disk.

        Creates the complete binary DAT file including header, palette, and run-length encoded raster data. Outputs file information including size and dimensions upon successful completion.

        Raises:
            ValueError: If no raster data exists to write.
        """
        if not self.raster_data:
            raise ValueError("No raster data to write. Create raster data first.")

        # Encode the raster data
        encoded_data = self.run_length_encode()

        # Calculate total file size
        total_size = self.HEADER_SIZE + self.PALETTE_SIZE + len(encoded_data)

        # Create the complete buffer
        buffer = bytearray(total_size)

        # Write header
        header = self.create_dat_header()
        buffer[:self.HEADER_SIZE] = header

        # Write palette
        palette_section = self.create_palette_section()
        buffer[self.HEADER_SIZE:self.HEADER_SIZE + self.PALETTE_SIZE] = palette_section

        # Write encoded data
        data_start = self.DATA_OFFSET
        for i, value in enumerate(encoded_data):
            buffer[data_start + i] = value

        # Write to file
        with open(self.dat_filename, 'wb') as f:
            f.write(buffer)

        print(f"✓ DAT file written: {self.dat_filename}")
        print(f"  File size: {len(buffer)} bytes")
        print(f"  Raster: {self.dat_width} x {self.dat_height}")
        print(f"  Encoded data: {len(encoded_data)} bytes")

    def create_empty_raster(self, width: int, height: int) -> None:
        """Create an empty raster filled with background color (0).

        Args:
            width (int): Width of the raster in pixels.
            height (int): Height of the raster in pixels.
        """
        self.raster_data = [[0 for _ in range(width)] for _ in range(height)]
        print(f"Created empty raster: {width} x {height}")

    def create_empty_dat(self, width: int = 50, height: int = 10) -> None:
        """Create a simple empty DAT file for testing purposes.

        Creates a minimal DAT file with the specified dimensions filled with background color for testing and validation purposes.

        Args:
            width (int, optional): Width of the raster. Defaults to 50.
            height (int, optional): Height of the raster. Defaults to 10.
        """
        self.create_empty_raster(width, height)
        self.write_dat_file()

    def process_knitout_to_dat(self) -> None:
        """Complete workflow: parse knitout file and create DAT file.

        Executes the complete conversion pipeline from knitout parsing through DAT file generation, including raster creation and file writing with progress reporting.
        """
        print("Starting knitout to DAT conversion...")

        # Step 2: Create raster from knitout data
        self.create_raster_from_knitout()

        # Step 3: Write the DAT file
        self.write_dat_file()

        print("✓ Knitout to DAT conversion completed successfully!")
