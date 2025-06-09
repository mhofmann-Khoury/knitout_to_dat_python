"""
Dat_File class for creating Shima Seiki DAT files from knitout files.
Based on the CMU Textile Lab's knitout-to-dat.js functionality.
"""

import os
import struct
import warnings

from knitout_interpreter.knitout_language.Knitout_Context import process_knitout_instructions
from knitout_interpreter.knitout_operations.Header_Line import Knitout_Header_Line, Carriers_Header_Line, Position_Header_Line, Gauge_Header_Line
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line, Knitout_Version_Line, Knitout_Comment_Line
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction
from knitout_interpreter.run_knitout import run_knitout
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Position


class Dat_File:
    """
    A class for creating Shima Seiki DAT files from knitout files.

    DAT files are encoded raster images containing knitting patterns and machine instructions.
    The format consists of a header, color palette, and run-length encoded pixel data.
    """
    POSITION_DESCRIPTIONS: dict[Knitting_Position, str] = {
        Knitting_Position.Center: "center design on needle bed",
        Knitting_Position.Keep: "use needle numbers as written",
        Knitting_Position.Left: "left-justify design on needle bed",
        Knitting_Position.Right: "right-justify design on needle bed"
    }
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

    # Convert palette string to bytes (computed once as class constant)
    PALETTE_BYTES = bytes.fromhex(PALETTE_STR.replace(' ', ''))

    # DAT file structure constants
    HEADER_SIZE = 0x200
    PALETTE_SIZE = 0x400  # 768 bytes palette + padding to 1024 bytes
    DATA_OFFSET = 0x600

    def __init__(self, knitout_file: str, dat_filename: str):
        """
        Initialize a Dat_File instance.

        Args:
            knitout_file: Path to the input knitout file
            dat_filename: Name for the output DAT file
        """

        self.knitout_file = knitout_file
        self.dat_filename = dat_filename

        # Initialize properties derived from parsing the knitout file.
        self.comments: list[Knitout_Comment_Line] = []
        self.instructions: list[Knitout_Instruction] = []
        self.header_lines: list[Knitout_Header_Line] = []
        self.version_line: None | Knitout_Version_Line = None

        # Knitout parsing results
        self.knitout_lines: list[Knitout_Line] = []
        self.knitting_machine_state = None
        self.knitted_knit_graph = None

        # Initialize properties set by the header to their default configuration
        self.position: Knitting_Position = Knitting_Position.Left
        self.needle_bed_width: int = 540
        self.gauge: int = 15

        # Initialize properties that will be set during processing
        self.dat_width: int = 0
        self.dat_height: int = 0
        self.raster_data: list[list[int]] = []
        self.passes: list = []  # Will be defined later when we implement Pass class

        # Pattern positioning info (derived from headers)
        self.min_slot: int = 0
        self.max_slot: int = 0
        self.position_offset: int = 0

        # Validate palette
        if len(self.PALETTE_BYTES) != 768:
            raise ValueError(f"Palette should be 768 bytes, got {len(self.PALETTE_BYTES)}")

        print(f"Initialized Dat_File: {knitout_file} -> {dat_filename}")

    def parse_knitout_file(self) -> None:
        """
        Parse the knitout file using knitout-interpreter library.
        Extracts headers and prepares for conversion to DAT format.
        """
        if not os.path.exists(self.knitout_file):
            raise FileNotFoundError(f"Knitout file not found: {self.knitout_file}")

        print(f"Parsing knitout file: {self.knitout_file}")

        try:
            # Use knitout-interpreter to parse the file
            self.knitout_lines, self.knitting_machine_state, self.knitted_knit_graph = run_knitout(self.knitout_file)
            print(f"Successfully parsed {len(self.knitout_lines)} knitout lines")
            self.version_line, self.header_lines, self.instructions, self.comments = process_knitout_instructions(self.knitout_lines)

            # Extract headers from the parsed results
            self._extract_headers()
            self._calculate_positioning()

        except Exception as e:
            raise RuntimeError(f"Failed to parse knitout file: {str(e)}")

    def _extract_headers(self) -> None:
        """
        Extract header information from the parsed knitout lines.
        Headers are comment lines that start with ';;' and contain ': '.
        """
        set_carriers = False
        set_position = False
        set_width = False
        for header in self.header_lines:
            if isinstance(header, Carriers_Header_Line):
                if header.header_value != 10:
                    warnings.warn(f"Expected 10 carriers in header but got {header}")
                set_carriers = True
            elif isinstance(header, Position_Header_Line):
                self.position = header.header_value
                set_position = True
                # print(f"Will {self.POSITION_DESCRIPTIONS[self.headers['Position']]} as per position header '{self.headers['Position']}'.")
            elif isinstance(header, Gauge_Header_Line):
                if self.gauge != header.header_value:
                    self.gauge = header.header_value
                    self.needle_bed_width = 36 * self.gauge  # Assumes 36 inch bed
                set_width = True

        if not set_carriers:
            warnings.warn("Knitout: Carriers Header not specified. Dat file presumes 10 carriers.")
        if not set_position:
            print(f"Position header not specified. Will center design on needle bed ('Center').")
        print(f"Will {self.POSITION_DESCRIPTIONS[self.position]} as per position header '{self.position}'.")
        if not set_width:
            print(f"Gauge not specified. DAT file assumes gauge of {self.gauge} with {self.needle_bed_width} needles on each bed.")

    def _calculate_positioning(self) -> None:
        """
        Calculate pattern positioning based on headers and needle usage.
        This determines where the pattern will be placed on the machine bed.
        """
        # For now, set default values - this will be updated when we process actual operations
        # to determine min_slot and max_slot from needle usage
        self.min_slot = 0
        self.max_slot = 50  # temporary default

        # Calculate position offset based on Position header (from original JS logic)
        if self.position == 'Center':
            self.position_offset = round((self.needle_bed_width - (self.max_slot - self.min_slot + 1)) / 2)
        elif self.position == 'Keep':
            if self.min_slot > 0 and self.max_slot <= self.needle_bed_width:
                self.position_offset = self.min_slot
            else:
                # This will need to be validated later when we know actual needle range
                print(f"Warning: Position 'Keep' may be invalid for needle range - will validate after processing operations")
                self.position_offset = 0
        elif self.position == 'Right':
            # Let knitPaint auto set for right edge (from original JS comment)
            self.position_offset = 0
        elif self.position == 'Left':
            self.position_offset = 1

    def get_dat_header_info(self) -> dict[str, int]:
        """
        Get current header information.

        Returns:
            Dictionary with header information
        """
        return {
            'min_slot': self.min_slot,
            'max_slot': self.max_slot,
            'position_offset': self.position_offset,
            'pattern_width': self.max_slot - self.min_slot + 1 if self.max_slot > self.min_slot else 0
        }

    def create_raster_from_knitout(self) -> None:
        """
        Create an empty raster filled with background color (0).

        """
        self.raster_data: list[list[int]] = [[0 for _ in range(self.dat_width)] for _ in range(self.dat_height)]

    def run_length_encode(self) -> list[int]:
        """
        Run-length encode the raster data into index-length pairs.

        Returns:
            List of alternating color indices and run lengths
        """
        if not self.raster_data:
            raise ValueError("No raster data to encode. Call create_empty_raster() first.")

        index_length_pairs = []

        for y in range(self.dat_height):
            current_color = self.raster_data[y][0]
            run_length = 0

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

    def create_header(self) -> bytearray:
        """
        Create the DAT file header.

        Returns:
            Header as a bytearray
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
        """
        Create the palette section of the DAT file.

        Returns:
            Palette section as a bytearray (padded to PALETTE_SIZE)
        """
        palette_section = bytearray(Dat_File.PALETTE_SIZE)
        palette_section[:len(Dat_File.PALETTE_BYTES)] = Dat_File.PALETTE_BYTES
        return palette_section

    def write_dat_file(self) -> None:
        """
        Write the complete DAT file to disk.
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
        header = self.create_header()
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
        """
        Create an empty raster filled with background color (0).

        Args:
            width: Width of the raster in pixels
            height: Height of the raster in pixels
        """
        self.dat_width = width
        self.dat_height = height
        self.raster_data = [[0 for _ in range(width)] for _ in range(height)]
        print(f"Created empty raster: {width} x {height}")

    def create_empty_dat(self, width: int = 50, height: int = 10) -> None:
        """
        Create a simple empty DAT file for testing purposes.

        Args:
            width: Width of the raster (default: 50)
            height: Height of the raster (default: 10)
        """
        self.create_empty_raster(width, height)
        self.write_dat_file()

    def get_file_info(self) -> dict:
        """
        Get information about the current DAT file configuration.

        Returns:
            Dictionary with file information
        """
        return {
            'knitout_file': self.knitout_file,
            'dat_filename': self.dat_filename,
            'width': self.dat_width,
            'height': self.dat_height,
            'raster_size': len(self.raster_data) * len(self.raster_data[0]) if self.raster_data else 0,
            'palette_colors': len(self.PALETTE_BYTES) // 3,
            'file_exists': os.path.exists(self.dat_filename),
            'knitout_parsed': len(self.knitout_lines) > 0,
            'min_slot': self.min_slot,
            'max_slot': self.max_slot,
            'position_offset': self.position_offset
        }

    def process_knitout_to_dat(self) -> None:
        """
        Complete workflow: parse knitout file and create DAT file.
        """
        print("Starting knitout to DAT conversion...")

        # Step 1: Parse the knitout file
        self.parse_knitout_file()

        # Step 2: Create raster from knitout data
        self.create_raster_from_knitout()

        # Step 3: Write the DAT file
        self.write_dat_file()

        print("✓ Knitout to DAT conversion completed successfully!")


def main() -> None:
    """Example usage of the Dat_File class."""

    # Example 1: Create a simple empty DAT file
    print("=== Creating Empty DAT File ===")
    dat_file = Dat_File("example.knitout", "test_output.dat")
    dat_file.create_empty_dat(width=60, height=15)

    # Display file information
    info = dat_file.get_file_info()
    print("\nEmpty DAT File Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")

    # Example 2: Process a real knitout file (if it exists)
    print("\n=== Processing Knitout File ===")
    knitout_file = "sample.knitout"  # Replace with actual file path

    if os.path.exists(knitout_file):
        dat_file2 = Dat_File(knitout_file, "from_knitout.dat")
        try:
            dat_file2.process_knitout_to_dat()

            # Display header information
            dat_header_info = dat_file2.get_dat_header_info()
            print("\nHeader Information:")
            for key, value in dat_header_info.items():
                print(f"  {key}: {value}")

            # Display final file information
            final_info = dat_file2.get_file_info()
            print("\nFinal DAT File Information:")
            for key, value in final_info.items():
                print(f"  {key}: {value}")

        except Exception as e:
            print(f"Error processing knitout file: {e}")
    else:
        print(f"Sample knitout file '{knitout_file}' not found. Skipping knitout processing example.")
        print("To test knitout processing, create a valid knitout file and update the file path.")


if __name__ == "__main__":
    main()
