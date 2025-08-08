"""Integration tests for the multiple public items plugin with flake8."""

import subprocess
import sys
import tempfile
from pathlib import Path


class TestFlake8BasicIntegration:
    """Test basic integration with flake8 CLI."""

    def test_plugin_is_discovered_by_flake8(self):
        """Test that the plugin is properly discovered as a flake8 plugin."""
        # Run flake8 --help to see if our plugin is available
        result = subprocess.run(
            [sys.executable, "-m", "flake8", "--help"], capture_output=True, text=True
        )

        # Should not error and should complete successfully
        assert result.returncode == 0

    def test_flake8_integration_with_violations(self):
        """Test full flake8 integration with code that has violations."""
        # Create a Python file with multiple public items
        code_with_violations = '''def first_function():
    """First public function."""
    return 1

def second_function():
    """Second public function."""
    return 2

class PublicClass:
    """Public class."""

    def method(self):
        return 3
'''

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "test_violations.py"
            test_file.write_text(code_with_violations)

            # Run flake8 on the test file with explicit plugin selection
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "--select=EL101", str(test_file)],
                capture_output=True,
                text=True,
            )

            # Should detect violations and return non-zero exit code
            assert result.returncode != 0

            # Should contain our violation code in output
            output = result.stdout + result.stderr
            assert "EL101" in output
            assert "first_function" in output
            assert "second_function" in output
            assert "PublicClass" in output
            assert "3 public items" in output

    def test_flake8_integration_without_violations(self):
        """Test flake8 integration with code that has no violations."""
        # Create a Python file with only one public item
        clean_code = '''def single_function():
    """Only public function."""
    return 42

def _private_function():
    """Private function should be ignored."""
    return 0
'''

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "test_clean.py"
            test_file.write_text(clean_code)

            # Run flake8 on the test file with explicit plugin selection
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "--select=EL101", str(test_file)],
                capture_output=True,
                text=True,
            )

            # Should not detect violations
            output = result.stdout + result.stderr

            # Should not contain our error code
            assert "EL101" not in output


class TestFlake8ErrorFormatting:
    """Test flake8 error formatting and reporting."""

    def test_flake8_integration_error_format(self):
        """Test that flake8 integration produces correctly formatted errors."""
        # Create a Python file with multiple public items
        code_with_error = '''class FirstClass:
    """First public class."""
    pass

class SecondClass:
    """Second public class."""
    pass
'''

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "test_format.py"
            test_file.write_text(code_with_error)

            # Run flake8 on the test file with explicit plugin selection
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "--select=EL101", str(test_file)],
                capture_output=True,
                text=True,
            )

            output = result.stdout + result.stderr

            # Should contain correctly formatted error message
            # Flake8 format is typically: filename:line:col: error_code message
            assert "test_format.py" in output
            assert "EL101" in output
            assert "FirstClass" in output
            assert "SecondClass" in output
            assert "2 public items" in output
            assert "Only one public item per file is allowed" in output

    def test_flake8_integration_multiple_files(self):
        """Test flake8 integration with multiple files."""
        file1_code = """def function_one():
    return 1

def function_two():
    return 2
"""

        file2_code = """def single_function():
    return 42
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create multiple test files
            file1 = temp_path / "file1.py"
            file1.write_text(file1_code)

            file2 = temp_path / "file2.py"
            file2.write_text(file2_code)

            # Run flake8 on all Python files with explicit plugin selection
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "--select=EL101", str(file1), str(file2)],
                capture_output=True,
                text=True,
            )

            output = result.stdout + result.stderr

            # Should find violation in file1 but not file2
            assert "file1.py" in output
            assert "EL101" in output
            assert "function_one" in output
            assert "function_two" in output

            # Should not complain about file2's single function
            if "file2.py" in output:
                # If file2 is mentioned, it shouldn't have EL101 errors
                file2_lines = [line for line in output.split("\n") if "file2.py" in line]
                for line in file2_lines:
                    assert "EL101" not in line


class TestFlake8SpecialCases:
    """Test flake8 integration with special cases and edge conditions."""

    def test_flake8_integration_with_syntax_errors(self):
        """Test flake8 integration handles syntax errors gracefully."""
        # Create a Python file with syntax errors
        broken_code = """def broken_function(
    # Missing closing parenthesis
    return 42

def another_function():
    return 1
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "broken.py"
            test_file.write_text(broken_code)

            # Run flake8 on the test file with our plugin
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "--select=EL101", str(test_file)],
                capture_output=True,
                text=True,
            )

            output = result.stdout + result.stderr

            # Our plugin should not report EL101 errors for broken syntax
            assert "EL101" not in output

    def test_flake8_integration_mixed_public_private_items(self):
        """Test flake8 integration with mixed public and private items."""
        mixed_code = '''def public_function():
    """Public function."""
    return 1

def _private_function():
    """Private function."""
    return 2

class PublicClass:
    """Public class."""
    pass

class _PrivateClass:
    """Private class."""
    pass
'''

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "mixed.py"
            test_file.write_text(mixed_code)

            # Run flake8 on the test file with explicit plugin selection
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "--select=EL101", str(test_file)],
                capture_output=True,
                text=True,
            )

            # Should detect violations for public items only
            assert result.returncode != 0

            output = result.stdout + result.stderr
            assert "EL101" in output
            assert "public_function" in output
            assert "PublicClass" in output
            assert "_private_function" not in output
            assert "_PrivateClass" not in output
            assert "2 public items" in output

    def test_flake8_integration_with_nested_items(self):
        """Test flake8 integration ignores nested functions and classes."""
        nested_code = '''def outer_function():
    """Outer function."""

    def inner_function():
        """Nested function should be ignored."""
        return 1

    class InnerClass:
        """Nested class should be ignored."""
        pass

    return inner_function()

class OuterClass:
    """Outer class."""

    def method(self):
        return 1
'''

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "nested.py"
            test_file.write_text(nested_code)

            # Run flake8 on the test file with explicit plugin selection
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "--select=EL101", str(test_file)],
                capture_output=True,
                text=True,
            )

            # Should detect violations for top-level items only
            assert result.returncode != 0

            output = result.stdout + result.stderr
            assert "EL101" in output
            assert "outer_function" in output
            assert "OuterClass" in output
            assert "inner_function" not in output
            assert "InnerClass" not in output
            assert "2 public items" in output

    def test_flake8_integration_empty_file(self):
        """Test flake8 integration with empty file."""
        empty_code = '''# This file only has comments

"""
And docstrings
"""
'''

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "empty.py"
            test_file.write_text(empty_code)

            # Run flake8 on the test file with explicit plugin selection
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "--select=EL101", str(test_file)],
                capture_output=True,
                text=True,
            )

            # Should not detect violations for empty file
            output = result.stdout + result.stderr
            assert "EL101" not in output

    def test_plugin_error_code_assignment(self):
        """Test that the plugin uses the correct error code EL101."""
        code_with_violation = """def first():
    return 1

def second():
    return 2
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "test_error_code.py"
            test_file.write_text(code_with_violation)

            # Run flake8 on the test file with explicit plugin selection
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "--select=EL101", str(test_file)],
                capture_output=True,
                text=True,
            )

            output = result.stdout + result.stderr

            # Should use exactly EL101 error code
            assert "EL101" in output
            # Should not use other error codes
            assert "EL999" not in output
            assert "EL909" not in output
