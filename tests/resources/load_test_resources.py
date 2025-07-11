"""Module resources for loading knitscript sequences from the package resources."""

from importlib import resources
from pathlib import Path

from knit_script.interpret_knit_script import knit_script_to_knitout, knit_script_to_knitout_to_dat


def load_test_resource(test_resource_filename: str) -> str:
    """
    Load data from a resource file in the resources folder of the current module's package.

    Args:
        test_resource_filename: Name of the resource file to load (e.g., 'resource.txt', 'config.json')

    Returns:
        str: Content of the resource file

    Raises:
        FileNotFoundError: If the resource file doesn't exist
        ImportError: If the resources package structure is invalid
    """
    # Get the current module's package name using __name__
    current_package = __name__.rsplit('.', 1)[0]  # Remove the module name, keep the package
    sequence_resources_path = resources.files(current_package).joinpath(test_resource_filename)

    if not sequence_resources_path.is_file():
        raise FileNotFoundError(f"Resource file '{test_resource_filename}' not found in {current_package}")
    return str(sequence_resources_path)
    # with sequence_resources_path.open('r', encoding=encoding) as f:
    #     content = f.read()
    # return content


def load_test_knitscript_to_knitout(test_knitscript_filename: str, test_knitout_filename: str, **python_variables) -> str:
    """
    Generates a knitout file in the current directory that corresponds to the parameterized run of the given knitscript file.
    Args:
        test_knitscript_filename: The name of the knitscript to run from the test/resources package.
        test_knitout_filename: The name of the knitout file to generate.
        **python_variables: The keyword parameters to pass to the knitscript run.

    Returns:
        The name of the generated knitout file.
    """
    test_knitscript_filename = load_test_resource(test_knitscript_filename)
    _knit_graph, _machine_state = knit_script_to_knitout(test_knitscript_filename, test_knitout_filename, pattern_is_filename=True, **python_variables)
    return test_knitout_filename


def load_test_knitscript_to_knitout_to_old_dat(test_knitscript_filename: str, test_knitout_filename: str, test_dat_name: str, **python_variables) -> tuple[str, str]:
    """
    Generates a knitout file and dat file from the original JS Dat compiler in the current directory that corresponds to the parameterized run of the given knitscript file.
    Args:
        test_dat_name: The name of the dat file to generate with the old js dat compiler.
        test_knitscript_filename: The name of the knitscript to run from the test/resources package.
        test_knitout_filename: The name of the knitout file to generate.
        **python_variables: The keyword parameters to pass to the knitscript run.

    Returns:
        The name of the generated knitout file, the name of the generated dat file.
    """
    test_knitscript_filename = load_test_resource(test_knitscript_filename)
    _knit_graph, _machine_state = knit_script_to_knitout_to_dat(test_knitscript_filename, test_knitout_filename, test_dat_name, pattern_is_filename=True, **python_variables)
    return test_knitout_filename, test_dat_name


def delete_generated_file(filename: str) -> bool:
    """
    Delete a file that was generated in the current package directory.

    This function deletes files relative to where this function is defined,
    not where it's called from. Useful for cleaning up generated files.

    Args:
        filename: Name of the file to delete (e.g., 'output.dat', 'temp.txt')

    Returns:
        bool: True if file was deleted successfully, False if file didn't exist

    Raises:
        PermissionError: If the file cannot be deleted due to permissions
        OSError: If there's an error deleting the file

    Examples:
        # Delete a file in the same directory as this module
        delete_generated_file('output.dat')

        # Delete a file in a subdirectory
        delete_generated_file('temp_file.txt', 'temp')
    """
    # Get the directory where this module is located
    current_module_file = Path(__file__).parent

    # Build the full path to the file
    file_path = current_module_file / filename

    try:
        if file_path.exists() and file_path.is_file():
            file_path.unlink()  # Delete the file
            return True
        else:
            return False  # File didn't exist
    except PermissionError:
        raise PermissionError(f"Permission denied: Cannot delete '{file_path}'")
    except OSError as e:
        raise OSError(f"Error deleting file '{file_path}': {e}")
