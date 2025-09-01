"""Module provides helper functions to convert Knit Script resources into knitout and dat files for testing."""
from knit_graphs.Knit_Graph import Knit_Graph
from knit_script.interpret_knit_script import knit_script_to_knitout
from knit_script.knit_script_interpreter.Knit_Script_Interpreter import (
    Knit_Script_Interpreter,
)
from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Comment_Line
from knitout_interpreter.run_knitout import run_knitout
from resources.compile_knitout import compile_knitout
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from tests.resources.load_test_resources import load_test_resource


def _clean_knitout(executer: Knitout_Executer):
    clean_instructions = []
    for instruction in executer.executed_instructions:
        instruction.comment = None
        if not isinstance(instruction, Knitout_Comment_Line):
            clean_instructions.append(instruction)
    executer.executed_instructions = clean_instructions


def knit_script_to_knitout_to_dat(pattern: str, knitout_name: str, dat_name: str | None = None, pattern_is_filename: bool = False, **python_variables) -> tuple[Knit_Graph, Knitting_Machine]:
    """
    Processes a knit script pattern into knitout and a dat file for shima seiki machines and returns the resulting knit graph from the operations.
    :param pattern_is_filename: If true, the pattern is a filename.
    :param dat_name: Output location for dat file.
    If none, dat file shares the name with knitout.
    :param knitout_name: The output location for knitout.
    :param pattern: The knit script pattern or a file containing it.
    :param python_variables: Python variables to load into scope.
    :return: The KnitGraph constructed during parsing on a virtual machine
    """
    knit_graph, machine_state = knit_script_to_knitout(pattern, knitout_name, pattern_is_filename=pattern_is_filename, **python_variables)
    success = compile_knitout(knitout_name, dat_name)
    assert success, f"Dat file could not be produced from {knitout_name}"
    return knit_graph, machine_state


def load_test_knitout_to_dat(k_name: str, dat_name: str) -> tuple[str, str]:
    """
    Executes the knitout in the given resource file and generates a cleaned version without comments.
    Args:
        k_name (str): The name of the knitout file in the test resources' folder.
        dat_name (str): The name of the dat file to generate from the cleaned knitout instructions.

    Returns:
        tuple[str, str]: A tuple of the name with the file path information of the knitout resource file and the name of the generated cleaned knitout file.
    """
    test_k_name = load_test_resource(k_name)
    knitout, _machine, _graph = run_knitout(test_k_name)
    knitout_executer = Knitout_Executer(knitout)
    _clean_knitout(knitout_executer)
    clean_k_name = f"{test_k_name[0:-2]}_clean.k"
    knitout_executer.write_executed_instructions(clean_k_name)
    success = compile_knitout(clean_k_name, dat_name)
    assert success, f"Dat file could not be produced from {clean_k_name}"
    return test_k_name, clean_k_name


def load_test_knitscript_to_knitout(test_knitscript_filename: str, test_knitout_filename: str, **python_variables) -> str:
    """
    Generates a knitout file in the current directory that corresponds to the parameterized run of the given knitscript file.
    Args:
        test_knitscript_filename: The name of the knitscript to run from the test/resources package.
        test_knitout_filename: The name of the knitout file to generate.
        **python_variables: The keyword parameters to pass to the knitscript run.

    Returns: The name of the cleaned knitout file (removing comments and semicolons).
    """
    test_knitscript_filename = load_test_resource(test_knitscript_filename)
    interpreter = Knit_Script_Interpreter()
    knitout, knit_graph, machine_state = interpreter.write_knitout(test_knitscript_filename, test_knitout_filename, pattern_is_file=True, **python_variables)
    knitout_executer = Knitout_Executer(knitout)
    clean_k_name = f"{test_knitout_filename[0:-2]}_clean.k"
    _clean_knitout(knitout_executer)
    knitout_executer.write_executed_instructions(clean_k_name)
    return clean_k_name


def load_test_knitscript_to_knitout_to_old_dat(test_knitscript_filename: str, test_knitout_filename: str, test_dat_name: str, **python_variables) -> str:
    """
    Generates a knitout file and dat file from the original JS Dat compiler in the current directory that corresponds to the parameterized run of the given knitscript file.
    Args:
        test_dat_name: The name of the dat file to generate with the old js dat compiler.
        test_knitscript_filename: The name of the knitscript to run from the test/resources package.
        test_knitout_filename: The name of the knitout file to generate.
        **python_variables: The keyword parameters to pass to the knitscript run.

    Returns:
        The name of the cleaned knitscript generated knitout file.
    """
    clean_k_name = load_test_knitscript_to_knitout(test_knitscript_filename, test_knitout_filename, **python_variables)
    success = compile_knitout(test_knitout_filename, test_dat_name)
    assert success, f"Dat file could not be produced from {test_knitout_filename}"
    return clean_k_name
