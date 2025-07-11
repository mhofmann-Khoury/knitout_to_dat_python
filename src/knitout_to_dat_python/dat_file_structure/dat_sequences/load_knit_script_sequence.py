"""Module resources for loading knitscript sequences from the package resources."""

from importlib import resources
from pathlib import Path


def get_knit_script_sequence(sequence_knitout_filename: str, encoding: str = 'utf-8') -> str:
    """
    Load data from a resource file in the resources folder of the current module's package.

    Args:
        sequence_knitout_filename: Name of the resource file to load (e.g., 'resource.txt', 'config.json')
        encoding: Text encoding to use when reading the file (default: 'utf-8')

    Returns:
        str: Content of the resource file

    Raises:
        FileNotFoundError: If the resource file doesn't exist
        ImportError: If the resources package structure is invalid
    """
    # Get the current module's package name using __name__
    current_package = __name__.rsplit('.', 1)[0]  # Remove the module name, keep the package

    try:
        # Python 3.9+ approach
        sequence_resources_package = resources.files(current_package).joinpath('resources')
        sequence_resources_path = sequence_resources_package.joinpath(sequence_knitout_filename)

        if not sequence_resources_path.is_file():
            raise FileNotFoundError(f"Resource file '{sequence_knitout_filename}' not found in {current_package}.resources/")

        with sequence_resources_path.open('r', encoding=encoding) as f:
            content = f.read()
        return content

    except AttributeError:
        # Python 3.7-3.8 fallback
        try:
            resources_package = f"{current_package}.resources"
            with resources.open_text(resources_package, sequence_knitout_filename, encoding=encoding) as f:
                content = f.read()
            return content
        except (ImportError, FileNotFoundError):
            raise FileNotFoundError(f"Resource file '{sequence_knitout_filename}' not found in {current_package}.resources/")


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
