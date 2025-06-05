"""Tests for CLI functionality."""

from knitout_to_dat_python.cli import main


def test_main_with_no_args():
    """Test CLI with no arguments shows usage."""
    exit_code = main([])
    assert exit_code == 1


def test_main_with_args():
    """Test CLI with arguments processes successfully."""
    exit_code = main(["test_file.knitout"])
    assert exit_code == 0
