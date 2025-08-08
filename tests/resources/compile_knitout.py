"""Used to run js DAT compiler"""
import platform

from tests.resources.load_test_resources import load_test_resource


def compile_knitout(knitout_file_name: str, output_file_name: str | None = None) -> bool:
    """

    :param knitout_file_name: The name of the knitout file to process.
    :param output_file_name: The name of the output file to create. DAT files for Shima Seiki.
    :return: True if the compiler was successful, False otherwise.
    """
    js_compiler_file = load_test_resource('knitout-to-dat.js')
    print(f"\n################Converting {knitout_file_name} to DAT file {output_file_name} ########\n")
    if platform.system() == "Windows":
        from tests.resources.run_js_dat_compilers_windows import run_js_compiler_windows
        return run_js_compiler_windows(output_file_name, js_compiler_file, knitout_file_name)
    else:
        from tests.resources.run_js_dat_compilers_unix import run_js_compiler_unix
        return run_js_compiler_unix(output_file_name, js_compiler_file, knitout_file_name)
