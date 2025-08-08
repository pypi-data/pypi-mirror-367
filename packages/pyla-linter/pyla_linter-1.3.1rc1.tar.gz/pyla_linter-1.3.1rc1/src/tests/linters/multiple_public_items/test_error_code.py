# flake8: noqa: EL101
"""Tests to verify EL101 error code is properly assigned and formatted."""

import ast
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

from src.linters.multiple_public_items.plugin import MultiplePublicItemsPlugin


def run_plugin_on_code(code: str, filename: str = "test.py") -> List[Tuple[int, int, str, str]]:
    """Helper function to run the plugin on code and return error tuples."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    plugin = MultiplePublicItemsPlugin(tree, filename)
    return list(plugin.run())


class TestErrorCodeAssignment:
    """Test that EL101 error code is properly assigned."""

    def test_error_code_in_tuple(self):
        """Test that error tuples contain the correct error code."""
        code = """
def function_one():
    return 1

def function_two():
    return 2
"""
        errors = run_plugin_on_code(code)

        assert len(errors) == 1
        error_tuple = errors[0]

        # Error tuple format: (line, column, message, error_code)
        assert len(error_tuple) == 4
        assert error_tuple[3] == "EL101"

    def test_error_code_in_message(self):
        """Test that error messages contain the EL101 code."""
        code = """
class ClassOne:
    pass

class ClassTwo:
    pass
"""
        errors = run_plugin_on_code(code)

        assert len(errors) == 1
        message = errors[0][2]

        # Message should start with EL101
        assert message.startswith("EL101")
        assert "EL101" in message

    def test_error_code_consistency(self):
        """Test that error code is consistent across different violations."""
        test_cases = [
            # Two functions
            """
def func_a():
    return 'a'

def func_b():
    return 'b'
""",
            # Two classes
            """
class ClassA:
    pass

class ClassB:
    pass
""",
            # Mixed function and class
            """
def my_function():
    return 42

class MyClass:
    pass
""",
            # Multiple functions and classes
            """
def func1():
    return 1

def func2():
    return 2

class Class1:
    pass

class Class2:
    pass
""",
        ]

        for i, code in enumerate(test_cases):
            errors = run_plugin_on_code(code, f"test_{i}.py")

            assert len(errors) == 1, f"Test case {i} should produce exactly one error"
            error_tuple = errors[0]

            # Check error code in tuple
            assert error_tuple[3] == "EL101", f"Test case {i} has wrong error code in tuple"

            # Check error code in message
            assert error_tuple[2].startswith(
                "EL101"
            ), f"Test case {i} has wrong error code in message"

    def test_no_error_code_for_valid_files(self):
        """Test that valid files don't produce EL101 errors."""
        valid_cases = [
            # Single function
            """
def single_function():
    return 42
""",
            # Single class
            """
class SingleClass:
    pass
""",
            # Empty file
            "",
            # Only private items
            """
def _private_function():
    return 42

class _PrivateClass:
    pass
""",
            # Only imports and constants
            """
import os
CONSTANT = 42
""",
        ]

        for i, code in enumerate(valid_cases):
            errors = run_plugin_on_code(code, f"valid_{i}.py")

            # Should not produce any EL101 errors
            assert len(errors) == 0, f"Valid case {i} should not produce errors"

    def test_error_code_format_specification(self):
        """Test that error code follows the expected format specification."""
        code = """
def function_one():
    return 1

def function_two():
    return 2
"""
        errors = run_plugin_on_code(code)

        assert len(errors) == 1
        error_tuple = errors[0]

        # Error code should be exactly "EL101"
        error_code = error_tuple[3]
        assert error_code == "EL101"
        assert isinstance(error_code, str)
        assert len(error_code) == 5  # "EL101" is 5 characters
        assert error_code.startswith("EL")
        assert error_code[2:].isdigit()

    def test_error_message_format_specification(self):
        """Test that error message follows the expected format."""
        code = """
def alpha():
    return 'a'

def beta():
    return 'b'

class Gamma:
    pass
"""
        errors = run_plugin_on_code(code)

        assert len(errors) == 1
        message = errors[0][2]

        # Message format: "EL101 File contains X public items: [list]. Only one public item per file is allowed."
        assert message.startswith("EL101 File contains")
        assert "public items:" in message
        assert "Only one public item per file is allowed." in message

        # Should contain specific item information
        assert (
            "function 'alpha'" in message
            and "function 'beta'" in message
            and "class 'Gamma'" in message
        )

        # Should contain line number information
        assert "line 2" in message  # alpha function
        assert "line 5" in message  # beta function
        assert "line 8" in message  # Gamma class


class TestErrorCodeIntegration:
    """Test EL101 error code integration with flake8."""

    def test_flake8_reports_el101(self):
        """Test that flake8 properly reports EL101 errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a file with violations
            test_file = temp_path / "test_el101.py"
            test_file.write_text(
                """
def function_one():
    return 1

def function_two():
    return 2
"""
            )

            # Run flake8
            result = subprocess.run(
                ["uv", "run", "flake8", "--select=EL101", str(test_file)],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # Should report EL101 error
            assert result.returncode != 0
            assert "EL101" in result.stdout
            assert str(test_file) in result.stdout

    def test_flake8_select_only_el101(self):
        """Test that flake8 can select only EL101 errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a file with violations and other style issues
            test_file = temp_path / "test_select_el101.py"
            test_file.write_text(
                """
def function_one():
    return 1

def function_two():
    return 2
"""
            )

            # Run flake8 with only EL101 selected
            result = subprocess.run(
                ["uv", "run", "flake8", "--select=EL101", str(test_file)],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # Should only report EL101 errors
            lines = result.stdout.strip().split("\n")
            for line in lines:
                if line.strip():  # Skip empty lines
                    assert "EL101" in line

    def test_flake8_ignore_el101(self):
        """Test that flake8 can ignore EL101 errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a file with violations
            test_file = temp_path / "test_ignore_el101.py"
            test_file.write_text(
                """
def function_one():
    return 1

def function_two():
    return 2
"""
            )

            # Run flake8 with EL101 ignored
            result = subprocess.run(
                ["uv", "run", "flake8", "--ignore=EL101", str(test_file)],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # Should not report EL101 errors
            assert "EL101" not in result.stdout

    def test_error_code_in_flake8_output_format(self):
        """Test that EL101 appears correctly in flake8 output format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a file with violations
            test_file = temp_path / "format_test.py"
            test_file.write_text(
                """
def first_function():
    return 1

def second_function():
    return 2
"""
            )

            # Run flake8
            result = subprocess.run(
                ["uv", "run", "flake8", "--select=EL101", str(test_file)],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # Parse the output format: filename:line:column: error_code message
            lines = result.stdout.strip().split("\n")
            assert len(lines) >= 1

            for line in lines:
                if line.strip():
                    parts = line.split(":", 3)  # Split on first 3 colons
                    assert len(parts) >= 4

                    # Check filename
                    assert str(test_file) in parts[0]

                    # Check line number is numeric
                    assert parts[1].strip().isdigit()

                    # Check column number is numeric
                    assert parts[2].strip().isdigit()

                    # Check error code and message
                    error_part = parts[3].strip()
                    assert error_part.startswith("EL101")

    def test_multiple_files_with_el101(self):
        """Test EL101 reporting across multiple files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create multiple files with violations
            files_with_violations = []
            for i in range(3):
                test_file = temp_path / f"multi_test_{i}.py"
                test_file.write_text(
                    f"""
def function_{i}_a():
    return {i}

def function_{i}_b():
    return {i} * 2
"""
                )
                files_with_violations.append(test_file)

            # Create one file without violations
            clean_file = temp_path / "clean_file.py"
            clean_file.write_text(
                """
def single_function():
    return 42
"""
            )

            # Run flake8 on the directory
            result = subprocess.run(
                ["uv", "run", "flake8", "--select=EL101", str(temp_path)],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # Should report EL101 for files with violations
            assert result.returncode != 0

            lines = result.stdout.strip().split("\n")
            el101_lines = [line for line in lines if "EL101" in line]

            # Should have one EL101 error per file with violations
            assert len(el101_lines) == 3

            # Each violation file should be mentioned
            for violation_file in files_with_violations:
                assert any(str(violation_file) in line for line in el101_lines)

            # Clean file should not be mentioned
            assert not any(str(clean_file) in line for line in el101_lines)


class TestErrorCodeEdgeCases:
    """Test edge cases for EL101 error code assignment."""

    def test_error_code_with_syntax_errors(self):
        """Test that syntax errors don't produce EL101 codes."""
        invalid_code = """
def invalid_syntax(
    # Missing closing parenthesis
    return 42
"""
        errors = run_plugin_on_code(invalid_code)

        # Should not produce any errors (including EL101)
        assert len(errors) == 0

    def test_error_code_consistency_across_runs(self):
        """Test that error codes are consistent across multiple runs."""
        code = """
def function_a():
    return 'a'

def function_b():
    return 'b'
"""

        # Run multiple times
        all_errors = []
        for _ in range(5):
            errors = run_plugin_on_code(code)
            all_errors.extend(errors)

        # All errors should have the same code
        for error in all_errors:
            assert error[3] == "EL101"
            assert error[2].startswith("EL101")

    def test_error_code_with_unicode_names(self):
        """Test that EL101 works correctly with unicode function/class names."""
        code = """
def função_um():
    return 1

def función_dos():
    return 2
"""

        errors = run_plugin_on_code(code)

        assert len(errors) == 1
        assert errors[0][3] == "EL101"
        assert "EL101" in errors[0][2]
        assert "função_um" in errors[0][2]
        assert "función_dos" in errors[0][2]
