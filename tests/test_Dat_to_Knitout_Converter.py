"""Test cases for the Dat_to_Knitout_Converter class."""
import os
from unittest import TestCase

from knitout_interpreter.knitout_compilers.compile_knitout import compile_knitout
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from knitout_interpreter.knitout_operations.Rack_Instruction import Rack_Instruction

from knitout_to_dat_python.dat_file_structure.Dat_to_Knitout_Converter import Dat_to_Knitout_Converter
from knitout_to_dat_python.dat_file_structure.knitout_to_dat_converter import Knitout_to_Dat_Converter
from tests.resources.knitout_diff import diff_knitout_files, Knitout_Diff_Result, KnitoutDiffer
from tests.resources.load_test_resources import load_test_knitscript_to_knitout_to_old_dat


class TestDat_to_Knitout_Converter(TestCase):

    @staticmethod
    def compare_dats_by_knitout(ks_file: str, output_prefix: str, **ks_kwargs) -> tuple[Knitout_Diff_Result, Knitout_Diff_Result, Knitout_Diff_Result]:
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
            A tuple of the three knitout diff-results for: the original knitout to python, original knitout to javascript, and python to javascript.
        """
        original_k_file, js_dat_file_name = load_test_knitscript_to_knitout_to_old_dat(ks_file, f"{output_prefix}.k", f"{output_prefix}_js.dat", **ks_kwargs)
        if not os.path.exists(js_dat_file_name):
            print(f"JS Dat file {js_dat_file_name} Failed to Compile. Attempting to fix negative all needle rackings")
            k_file_lines = parse_knitout(original_k_file, pattern_is_file=True)
            fixed_rack_lines = [Rack_Instruction(line.rack + 0.25, line.comment) if isinstance(line, Rack_Instruction) and line.rack < 0 and line.all_needle_rack
                                else line
                                for line in k_file_lines]
            with open(original_k_file, 'w') as f:
                f.writelines([str(l) for l in fixed_rack_lines])
            compile_knitout(original_k_file, js_dat_file_name)

        dat_file_name = f"{output_prefix}.dat"
        dat_file = Knitout_to_Dat_Converter(original_k_file, dat_file_name, knitout_in_file=True)
        dat_file.process_knitout_to_dat()
        js_dat_converter = Dat_to_Knitout_Converter(js_dat_file_name)
        js_k_file = f"{output_prefix}_js.k"
        js_dat_converter.write_knitout(js_k_file)
        py_dat_converter = Dat_to_Knitout_Converter(dat_file_name)
        py_k_file = f"{output_prefix}_from_py.k"
        py_dat_converter.write_knitout(py_k_file)

        print(f"# Compare Original {original_k_file} with Python->Dat->Knitout Output")
        original_to_py_result = diff_knitout_files(original_k_file, py_k_file)
        if original_to_py_result.are_functionally_equivalent:
            original_to_py_result.simple_report()
        else:
            original_to_py_result.verbose_report()

        print(f"\n# Compare Original {original_k_file} with JS->Dat->Knitout Output")
        original_to_js_result = diff_knitout_files(original_k_file, js_k_file)
        if original_to_js_result.are_functionally_equivalent:
            original_to_js_result.simple_report()
        else:
            original_to_js_result.verbose_report()

        print(f"\n# Compare PY->Dat->Knitout with JS->Dat->Knitout Output")
        py_to_js_result = diff_knitout_files(py_k_file, js_k_file)
        if py_to_js_result.are_functionally_equivalent:
            py_to_js_result.simple_report()
        else:
            py_to_js_result.verbose_report()

        return original_to_py_result, original_to_js_result, py_to_js_result

    def test_stst(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('stst.ks', 'stst',
                                                         c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_rib(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('rib.ks', 'rib',
                                                         c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_seed(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('seed.ks', 'seed',
                                                         c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_tube(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('tube.ks', 'tube',
                                                         c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_all_needle_jacquard(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('all_needle.ks', 'all_needle',
                                                         c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert len(py_js.significant_diffs) <= 1, "Javascript and Python code only differ by final rack line"

    def test_short_rows(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('short_rows.ks', 'shorts',
                                                         c=1, pattern_width=10, pattern_height=10, base=2, shorts=2)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_jacquard_stripe(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('jacquard_stripes.ks', 'jacquard_stripes',
                                                         white=1, black=2, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_lace(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('lace.ks', 'lace',
                                                         c=1, pattern_width=10, pattern_height=10)
        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_equivalent, "Javascript and Python code differ"

    def test_xfer_rackings(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('xfer_rackings.ks', 'xfer_rackings')
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
        o_py, o_js, py_js = self.compare_dats_by_knitout('cable.ks', 'cable',
                                                         c=1, pattern_width=12, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_intarsia(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('intarsia_float_block.ks', 'intarsia',
                                                         white=1, black=2,
                                                         border=4, block_width=4, block_height=6)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_plating(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('plating.ks', 'plating',
                                                         white=1, black=2,
                                                         stripe_size=4, stripes=4,
                                                         pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_shift(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('shift.ks', 'shift',
                                                         c=1, pattern_width=10, pattern_height=10,
                                                         shift=2)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_half_gauge(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('half_gauge.ks', 'half_gauge',
                                                         c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_gauged_sheets(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('gauged_sheets.ks', 'gauged_sheets',
                                                         c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_splits(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('splits.ks', 'splits',
                                                         c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_pauses(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('pauses.ks', 'pauses',
                                                         c=1, pattern_width=10, pattern_height=10)

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_all_needle_racked(self):
        test_name = 'all_needle_racked'
        o_py, o_js, py_js = self.compare_dats_by_knitout('all_needle_racked.ks', '%s' % test_name,
                                                         c=1, pattern_width=10, pattern_height=10)
        print(f"# Compare Shift Original {test_name}.k with Python->Dat->Knitout Output")
        differ = KnitoutDiffer(f'{test_name}.k', f'{test_name}_from_py.k', shift_file2=1)
        original_to_py_result = differ.get_diff_results()
        if original_to_py_result.are_functionally_equivalent:
            original_to_py_result.simple_report()
        else:
            original_to_py_result.verbose_report()

        print(f"\n# Compare Original {test_name}.k with JS->Dat->Knitout Output")
        differ = KnitoutDiffer(f'{test_name}.k', f'{test_name}_js.k', shift_file2=1)
        original_to_js_result = differ.get_diff_results()
        if original_to_js_result.are_functionally_equivalent:
            original_to_js_result.simple_report()
        else:
            original_to_js_result.verbose_report()
        assert py_js.are_equivalent, "Javascript and Python code differ"

    def test_weird_carriage_moves(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('weird_carriage_moves.ks', 'carriage_moves')

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_plate_row(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('plate_row.ks', 'plate_row')

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"
