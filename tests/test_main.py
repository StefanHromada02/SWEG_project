"""
Tests for the main module.
"""

import pytest
from sweg_project.main import example_function, main


def test_example_function():
    """Test the example_function."""
    result = example_function("World")
    assert result == "Hello, World! Welcome to the SWEG project."


def test_example_function_with_empty_string():
    """Test the example_function with empty string."""
    result = example_function("")
    assert result == "Hello, ! Welcome to the SWEG project."


def test_main_function(capsys):
    """Test the main function output."""
    main()
    captured = capsys.readouterr()
    assert "Hello from SWEG Project!" in captured.out
    assert "This is your Python project template." in captured.out