"""Test suite for adding kickbacks to a knitout execution - converted to unittest."""
import unittest

from tests.resources.load_test_resources import load_test_knitscript_to_knitout_to_old_dat


class Test_Original_Dat_Samples(unittest.TestCase):
    """Generates a series of dats using the original compiler as examples of correct outputs."""

    def test_stst(self):
        _k_file, _dat_file = load_test_knitscript_to_knitout_to_old_dat('stst.ks',
                                                                        'stst.k', 'stst_js.dat',
                                                                        c=1, pattern_width=10, pattern_height=10)

    def test_rib(self):
        _k_file, _dat_file = load_test_knitscript_to_knitout_to_old_dat('rib.ks',
                                                                        'rib.k', 'rib_js.dat',
                                                                        c=1, pattern_width=10, pattern_height=10)

    def test_seed(self):
        _k_file, _dat_file = load_test_knitscript_to_knitout_to_old_dat('seed.ks',
                                                                        'seed.k', 'seed_js.dat',
                                                                        c=1, pattern_width=10, pattern_height=10)

    def test_jacquard_stripes(self):
        _k_file, _dat_file = load_test_knitscript_to_knitout_to_old_dat('jacquard_stripes.ks',
                                                                        'jacquard_stripes.k', 'jacquard_stripes_js.dat',
                                                                        white=1, black=2, pattern_width=10, pattern_height=10)

    def test_tuck_lines(self):
        _k_file, _dat_file = load_test_knitscript_to_knitout_to_old_dat('tuck_line.ks',
                                                                        'tuck_lines.k', 'tuck_lines_js.dat',
                                                                        c=1, pattern_width=10)

    def test_tuck_2_lines(self):
        _k_file, _dat_file = load_test_knitscript_to_knitout_to_old_dat('tuck_2_lines.ks',
                                                                        'tuck_2_lines.k', 'tuck_2_lines_js.dat',
                                                                        c=1, pattern_width=10)
