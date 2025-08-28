"""Test cases for the Dat_to_Knitout_Converter class."""
from unittest import TestCase

from knitout_to_dat_python.knitout_to_dat import dat_to_knitout, knitout_to_dat
from tests.resources.knitout_diff import (
    Knitout_Diff_Result,
    KnitoutDiffer,
    diff_knitout_files,
)
from tests.resources.load_ks_resources import load_test_knitscript_to_knitout_to_old_dat


class TestDat_to_Knitout_Converter(TestCase):

    @staticmethod
    def compare_dats_by_knitout(ks_file: str, output_prefix: str, **ks_kwargs) -> tuple[Knitout_Diff_Result, Knitout_Diff_Result, Knitout_Diff_Result, Knitout_Diff_Result]:
        """
        Generate two dat files that correspond to the given run of knitscript code.
        The first file, "<output_prefix>_js.dat" is generated with the original JS Dat compiler.
        The second file, "<output_prefix>.dat" is generated with the python Dat compiler.
        Both dat files are then converted back into knitout codes which can be compared to the original knitout generated from knitscript
        Args:
            ks_file: The knitscript file in the resources folder to execute.
            output_prefix: The prefix for the knitout and dat files.
            **ks_kwargs: The keyword arguments passed to the knitscript compiler.
        Returns:
            A tuple of the three knitout diff-results for: the original knitout to python, clean knitout to python,  original knitout to javascript, and python to javascript.
        """
        original_k_file = f"{output_prefix}.k"
        js_dat_file_name = f"{output_prefix}_js.dat"
        clean_k_file = load_test_knitscript_to_knitout_to_old_dat(ks_file, original_k_file, js_dat_file_name, **ks_kwargs)
        # Convert original k file (not cleaned) to a DAT File using this python library
        dat_file_name = f"{output_prefix}_py.dat"
        knitout_to_dat(original_k_file, dat_file_name)

        # Convert the JS made dat file back to knitout
        js_k_file = f"{output_prefix}_js.k"
        dat_to_knitout(js_dat_file_name, js_k_file)

        # Convert the Python made dat file back to knitout
        py_k_file = f"{output_prefix}_from_py.k"
        dat_to_knitout(dat_file_name, py_k_file)

        print("\n#############################################################################")
        print(f"Compare KnitScript Generated Knitout <{original_k_file}> with Python->Dat->Knitout <{py_k_file}>")
        original_to_py_result = diff_knitout_files(original_k_file, py_k_file)
        if original_to_py_result.are_functionally_equivalent:
            original_to_py_result.simple_report()
        else:
            original_to_py_result.verbose_report()

        print("\n#############################################################################")
        print(f"Compare Cleaned KnitScript Generated Knitout <{clean_k_file}> with Python->Dat->Knitout <{py_k_file}>")
        clean_to_py_result = diff_knitout_files(clean_k_file, py_k_file)
        if clean_to_py_result.are_functionally_equivalent:
            clean_to_py_result.simple_report()
        else:
            clean_to_py_result.verbose_report()

        print("\n#############################################################################")
        print(f"Compare KnitScript Generated Knitout <{original_k_file}>  with JS->Dat->Knitout <{js_k_file}>")
        original_to_js_result = diff_knitout_files(original_k_file, js_k_file)
        if original_to_js_result.are_functionally_equivalent:
            original_to_js_result.simple_report()
        else:
            original_to_js_result.verbose_report()

        print("\n#############################################################################")
        print(f"Compare PY->Dat->Knitout <{py_k_file}> with JS->Dat->Knitout <{js_k_file}>")
        py_to_js_result = diff_knitout_files(py_k_file, js_k_file)
        if py_to_js_result.are_functionally_equivalent:
            py_to_js_result.simple_report()
        else:
            py_to_js_result.verbose_report()

        return original_to_py_result, clean_to_py_result, original_to_js_result, py_to_js_result

    def test_stst(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('stst.ks', 'stst',
                                                               c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_rib(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('rib.ks', 'rib',
                                                               c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_seed(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('seed.ks', 'seed',
                                                               c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_tube(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('tube.ks', 'tube',
                                                               c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_all_needle_jacquard(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('all_needle.ks', 'all_needle',
                                                               c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert len(py_js.significant_diffs) <= 1, "Javascript and Python code only differ by final rack line"

    def test_short_rows(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('short_rows.ks', 'shorts',
                                                               c=1, pattern_width=10, pattern_height=10, base=2, shorts=2)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_jacquard_stripe(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('jacquard_stripes.ks', 'jacquard_stripes',
                                                               white=1, black=2, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_lace(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('lace.ks', 'lace',
                                                               c=1, pattern_width=10, pattern_height=10)
        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_equivalent, "Javascript and Python code differ"

    def test_xfer_rackings(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('xfer_rackings.ks', 'xfer_rackings')
        print(f"# Compare Shift Original xfer_rackings.k with Python->Dat->Knitout Output")
        differ = KnitoutDiffer('xfer_rackings.k', 'xfer_rackings_from_py.k', shift_file2=1)
        original_to_py_result = differ.get_diff_results()
        if original_to_py_result.are_functionally_equivalent:
            original_to_py_result.simple_report()
        else:
            original_to_py_result.verbose_report()

        print(f"\n# Compare Original xfer_rackings.k with JS->Dat->Knitout Output")
        differ = KnitoutDiffer('xfer_rackings.k', 'xfer_rackings_js.k', shift_file2=1)
        original_to_js_result = differ.get_diff_results()
        if original_to_js_result.are_functionally_equivalent:
            original_to_js_result.simple_report()
        else:
            original_to_js_result.verbose_report()
        assert py_js.are_equivalent, "Javascript and Python code differ"

    def test_cable(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('cable.ks', 'cable',
                                                               c=1, pattern_width=12, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_intarsia(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('intarsia_float_block.ks', 'intarsia',
                                                               white=1, black=2,
                                                               border=4, block_width=4, block_height=6)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_plating(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('plating.ks', 'plating',
                                                               white=1, black=2,
                                                               stripe_size=4, stripes=4,
                                                               pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_shift(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('shift.ks', 'shift',
                                                               c=1, pattern_width=10, pattern_height=10,
                                                               shift=2)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_half_gauge(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('half_gauge.ks', 'half_gauge',
                                                               c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_gauged_sheets(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('gauged_sheets.ks', 'gauged_sheets',
                                                               c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_splits(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('splits.ks', 'splits',
                                                               c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_pauses(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('pauses.ks', 'pauses',
                                                               c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_all_needle_racked(self):
        test_name = 'all_needle_racked'
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('all_needle_racked.ks', '%s' % test_name,
                                                               c=1, pattern_width=10, pattern_height=10)
        print(f"# Compare Shift Original xfer_rackings.k with Python->Dat->Knitout Output")
        differ = KnitoutDiffer('all_needle_racked.k', 'all_needle_racked_from_py.k', shift_file2=1)
        original_to_py_result = differ.get_diff_results()
        if original_to_py_result.are_functionally_equivalent:
            original_to_py_result.simple_report()
        else:
            original_to_py_result.verbose_report()

        print(f"\n# Compare Original xfer_rackings.k with JS->Dat->Knitout Output")
        differ = KnitoutDiffer('all_needle_racked.k', 'all_needle_racked_js.k', shift_file2=1)
        original_to_js_result = differ.get_diff_results()
        if original_to_js_result.are_functionally_equivalent:
            original_to_js_result.simple_report()
        else:
            original_to_js_result.verbose_report()
        assert py_js.are_equivalent, "Javascript and Python code differ"

    def test_weird_carriage_moves(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('weird_carriage_moves.ks', 'carriage_moves')

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_plate_row(self):
        o_py, c_py, o_js, py_js = self.compare_dats_by_knitout('plate_row.ks', 'plate_row')

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"
