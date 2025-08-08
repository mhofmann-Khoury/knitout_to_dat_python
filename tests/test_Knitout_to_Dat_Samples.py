"""Test cases for the Dat_to_Knitout_Converter class."""
from unittest import TestCase

from knitout_to_dat_python.dat_file_structure.knitout_to_dat_converter import Knitout_to_Dat_Converter
from tests.resources.load_ks_resources import load_test_knitscript_to_knitout_to_old_dat


class TestDat_to_Knitout_Converter(TestCase):

    @staticmethod
    def generate_dats(ks_file: str, output_prefix: str, **ks_kwargs) -> None:
        """
        Generate two dat files that correspond to the given run of knitscript code.
        The first file, "<output_prefix>_js.dat" is generated with the original JS Dat compiler.
        The second file, "<output_prefix>_py.dat" is generated with the python Dat compiler.
        Args:
            ks_file: The knitscript file in the resources folder to execute.
            output_prefix: The prefix for the knitout and dat files.
            **ks_kwargs: The keyword arguments passed to the knitscript compiler.
        """
        original_k_file = f"{output_prefix}.k"
        js_dat_file_name = f"{output_prefix}_js.dat"
        _clean_k_file = load_test_knitscript_to_knitout_to_old_dat(ks_file, original_k_file, js_dat_file_name, **ks_kwargs)

        dat_file_name = f"{output_prefix}_py.dat"
        dat_file = Knitout_to_Dat_Converter(original_k_file, dat_file_name, knitout_in_file=True)
        dat_file.process_knitout_to_dat()

    def test_stst(self):
        self.generate_dats('stst.ks', 'stst',
                           c=3, pattern_width=60, pattern_height=60)

    def test_rib(self):
        self.generate_dats('rib.ks', 'rib',
                           c=3, pattern_width=60, pattern_height=60)

    def test_seed(self):
        self.generate_dats('seed.ks', 'seed',
                           c=3, pattern_width=60, pattern_height=60)

    def test_tube(self):
        self.generate_dats('tube.ks', 'tube',
                           c=3, pattern_width=60, pattern_height=60)

    def test_all_needle_jacquard(self):
        self.generate_dats('all_needle.ks', 'all_needle',
                           c=3, pattern_width=60, pattern_height=60)

    def test_short_rows(self):
        self.generate_dats('short_rows.ks', 'short_rows',
                           c=3, pattern_width=60, pattern_height=60, base=6, shorts=2)

    def test_jacquard_stripe(self):
        self.generate_dats('jacquard_stripes.ks', 'jacquard_stripes',
                           white=3, black=4, pattern_width=60, pattern_height=60)

    def test_lace(self):
        self.generate_dats('lace.ks', 'lace',
                           c=3, pattern_width=60, pattern_height=60)

    def test_cable(self):
        self.generate_dats('cable.ks', 'cable',
                           c=3, pattern_width=60, pattern_height=60)

    def test_intarsia(self):
        self.generate_dats('intarsia_float_block.ks', 'intarsia',
                           white=3, black=4, border=10, block_width=40, block_height=40)

    def test_plating(self):
        self.generate_dats('plating.ks', 'plating',
                           white=3, black=4, stripe_size=10, stripes=6, pattern_height=60)

    def test_shift(self):
        self.generate_dats('shift.ks', 'shift',
                           c=3, pattern_width=60, pattern_height=30, shift=2)

    def test_half_gauge(self):
        self.generate_dats('half_gauge.ks', 'half_gauge',
                           c=3, pattern_width=60, pattern_height=60)

    def test_splits(self):
        self.generate_dats('splits.ks', 'splits',
                           c=3, pattern_width=60, pattern_height=60)

    def test_all_needle_racked(self):
        self.generate_dats('all_needle_racked.ks', 'all_needle_racked',
                           c=3, pattern_width=60, pattern_height=20)
