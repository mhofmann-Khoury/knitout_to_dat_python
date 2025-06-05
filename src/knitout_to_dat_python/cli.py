"""Command-line interface for knitout-to-dat converter."""

import sys


def main(args: list | None = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        args: Command line arguments (defaults to sys.argv)

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    if args is None:
        args = sys.argv[1:]

    print("Knitout to DAT Converter v0.1.0")
    print("This tool is under development.")

    if not args:
        print("Usage: knitout-to-dat <input_file> [output_file]")
        return 1

    print(f"Would process file: {args[0]}")
    print("Conversion functionality coming soon!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
