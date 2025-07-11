"""Module of tests that render example DAT files using the original JS Dat compiler."""
from unittest import TestCase

from knitout_to_dat_python.dat_file_structure.knitout_to_dat_converter import Knitout_to_Dat_Converter
from tests.resources.load_test_resources import load_test_knitscript_to_knitout_to_old_dat


class TestDat_File(TestCase):
    @staticmethod
    def make_comparison_dats(ks_file: str, output_prefix: str, **ks_kwargs):
        """
        Generate two dat files that correspond to the given run of knitscript code.
        The first file, "<output_prefix>_js.dat" is generated with the original JS Dat compiler.
        The second file, "<output_prefix>.dat" is generated with the python Dat compiler.
        Args:
            ks_file: The knitscript file in the resources folder to execute.
            output_prefix: The prefix for the knitout and dat files.
            **ks_kwargs: The keyword arguments passed to the knitscript compiler.
        """
        k_file, js_dat_file_name = load_test_knitscript_to_knitout_to_old_dat(ks_file, f"{output_prefix}.k", f"{output_prefix}_js.dat", **ks_kwargs)
        dat_file_name = f"{output_prefix}.dat"
        dat_file = Knitout_to_Dat_Converter(k_file, dat_file_name, knitout_in_file=True)
        dat_file.process_knitout_to_dat()

    def test_one_line_knitout_to_dat(self):
        self.make_comparison_dats('tuck_line.ks', 'tuck_line',
                                  c=1, pattern_width=10)

    def test_stst(self):
        self.make_comparison_dats('stst.ks', 'stst', c=1,
                                  pattern_width=10, pattern_height=10)

    def test_rib(self):
        self.make_comparison_dats('rib.ks', 'rib',
                                  c=1, pattern_width=10, pattern_height=10)

    def test_seed(self):
        self.make_comparison_dats('seed.ks', 'seed',
                                  c=1, pattern_width=10, pattern_height=10)

    def test_tube(self):
        self.make_comparison_dats('tube.ks', 'tube',
                                  c=1, pattern_width=10, pattern_height=10)

    def test_all_needle_jacquard(self):
        self.make_comparison_dats('all_needle.ks', 'all_needle',
                                  c=1, pattern_width=10, pattern_height=10)

    def test_short_rows(self):
        self.make_comparison_dats('short_rows.ks', 'shorts',
                                  c=1, pattern_width=10, pattern_height=10, base=2, shorts=2)

    def test_jacquard_stripe(self):
        self.make_comparison_dats('jacquard_stripes.ks', 'jacquard_stripes',
                                  white=1, black=2, pattern_width=10, pattern_height=10)

    def test_lace(self):
        self.make_comparison_dats('lace.ks', 'lace',
                                  c=1, pattern_width=10, pattern_height=10)

    def test_cable(self):
        self.make_comparison_dats('cable.ks', 'cable',
                                  c=1, pattern_width=12, pattern_height=10)

    def test_intarsia(self):
        self.make_comparison_dats('intarsia_float_block.ks', 'intarsia',
                                  white=1, black=2,
                                  border=4, block_width=4, block_height=6)

    def test_plating(self):
        self.make_comparison_dats('plating.ks', 'plating',
                                  white=1, black=2,
                                  stripe_size=4, stripes=4,
                                  pattern_height=10)

    def test_shift(self):
        self.make_comparison_dats('shift.ks', 'shift',
                                  c=1, pattern_width=10, pattern_height=10,
                                  shift=2)

    def test_half_gauge(self):
        self.make_comparison_dats('half_gauge.ks', 'half_gauge',
                                  c=1, pattern_width=10, pattern_height=10)

    def test_gauged_sheets(self):
        self.make_comparison_dats('gauged_sheets.ks', 'gauged_sheets',
                                  c=1, pattern_width=10, pattern_height=10)
