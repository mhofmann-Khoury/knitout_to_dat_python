"""Isolated code for running DAT compiler on windows"""
from nodejs import node


def run_js_compiler_windows(dat_file_name: str, js_compiler_file: str, knitout_file_name: str) -> bool:
    """

    :param dat_file_name: The filename of the DAT file to produce.
    :param js_compiler_file:
    :param knitout_file_name: The file name of the knitout file to compile.
    :return: True if DAT compiled successfully
    """
    file_path = str(js_compiler_file)
    node_process = node.run([file_path, knitout_file_name, dat_file_name])
    if node_process.stdout is not None:
        print(f"DAT Compiler Output:\n\t{node_process.stdout}")
    if node_process.stderr is not None:
        print(f"DAT Compiler Error:\n\t{node_process.stderr}")
    return node_process.stderr is None
