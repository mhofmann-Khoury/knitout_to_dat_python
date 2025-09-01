"""Test cases for the Dat_to_Knitout_Converter class."""
from unittest import TestCase

from knitout_to_dat_python.knitout_to_dat import dat_to_knitout, knitout_to_dat
from tests.resources.knitout_diff import Knitout_Diff_Result, diff_knitout_files
from tests.resources.load_ks_resources import load_test_knitout_to_dat


class TestDat_to_Knitout_Converter(TestCase):

    @staticmethod
    def compare_dats_by_knitout(k_file: str, output_prefix: str) -> tuple[Knitout_Diff_Result, Knitout_Diff_Result, Knitout_Diff_Result]:
        """
        Generate two dat files that correspond to the given run of knitout code.
        The first file, "<output_prefix>_js.dat" is generated with the original JS Dat compiler.
        The second file, "<output_prefix>.dat" is generated with the python Dat compiler.
        Both dat files are then converted back into knitout codes which can be compared to the original knitout.

        Args:
            k_file: The knitout file in the resources folder to execute.
            output_prefix: The prefix for the knitout and dat files.
        Returns:
            A tuple of the three knitout diff-results for: original knitout to python, original knitout to javascript, and python to javascript.
        """
        js_dat_file_name = f"{output_prefix}_js.dat"
        original_k_file, clean_k_file = load_test_knitout_to_dat(k_file, js_dat_file_name)
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

        return original_to_py_result, original_to_js_result, py_to_js_result

    def test_jacquard_merge(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('jacquard_merge.k', 'jacquard_merge')

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_seed_jacquard(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('seed_jacquard.k', 'seed_jacquard')

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"

    def test_jacquard_seed(self):
        o_py, o_js, py_js = self.compare_dats_by_knitout('jacquard_seed.k', 'jacquard_seed')

        assert o_py.are_functionally_equivalent, "Original and Python code differ"
        assert o_js.are_functionally_equivalent, "Original and Javascript code differ"
        assert py_js.are_functionally_equivalent, "Javascript and Python code differ"
