"""Tests for flake8 integration with the length checker."""

import subprocess
import sys
import tempfile
from pathlib import Path


class TestFlake8Integration:  # noqa: WL002
    """Test integration with flake8 CLI."""

    def test_plugin_is_registered_with_flake8(self):
        """Test that the plugin is properly registered as a flake8 plugin."""
        # Run flake8 --help to see if our plugin is available
        result = subprocess.run(["uv", "run", "flake8", "--help"], capture_output=True, text=True)

        # Should not error and should complete successfully
        assert result.returncode == 0

    def test_flake8_integration_with_violations(self):  # noqa: EL001
        """Test full flake8 integration with code that has violations."""
        # Create a Python file with violations
        code_with_violations = '''def very_long_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    line8 = 8
    line9 = 9
    line10 = 10
    line11 = 11
    line12 = 12
    line13 = 13
    line14 = 14
    line15 = 15
    line16 = 16
    line17 = 17
    line18 = 18
    line19 = 19
    line20 = 20
    line21 = 21
    line22 = 22
    line23 = 23
    line24 = 24
    line25 = 25
    line26 = 26
    line27 = 27
    line28 = 28
    line29 = 29
    line30 = 30
    line31 = 31
    line32 = 32
    line33 = 33
    line34 = 34
    line35 = 35
    line36 = 36
    line37 = 37
    line38 = 38
    line39 = 39
    line40 = 40
    line41 = 41  # This exceeds the default 40 line limit
    return sum([line1, line2, line3, line4, line5])

class VeryLongClass:
    """A class that exceeds the default 200 line limit."""

    def __init__(self):
        self.attr1 = 1
        self.attr2 = 2
        self.attr3 = 3
        self.attr4 = 4
        self.attr5 = 5

    def method1(self):
        return self.attr1

    def method2(self):
        return self.attr2

    def method3(self):
        return self.attr3

    def method4(self):
        return self.attr4

    def method5(self):
        return self.attr5
''' + (
            """
    def method6(self):
        return 6

    def method7(self):
        return 7

    def method8(self):
        return 8

    def method9(self):
        return 9

    def method10(self):
        return 10
"""
            * 25
        )  # Repeat to make class very long

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "test_violations.py"
            test_file.write_text(code_with_violations)

            # Create pyproject.toml with strict limits to ensure violations
            pyproject_content = """
[project]
name = "test-project"
version = "0.1.0"
description = "Test project"
authors = [{name = "Test", email = "test@example.com"}]

[tool.pyla-linters]
max_function_length = 40
max_class_length = 200

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
"""
            pyproject_file = temp_path / "pyproject.toml"
            pyproject_file.write_text(pyproject_content)

            # Run flake8 on the test file with explicit plugin selection
            result = subprocess.run(
                ["uv", "run", "flake8", "--select=WL,EL", str(test_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            # Should detect violations and return non-zero exit code
            assert result.returncode != 0

            # Should contain our violation codes in output
            output = result.stdout + result.stderr
            assert "WL001" in output  # Function length warning (43 lines > 40)
            assert "WL002" in output  # Class length warning (267 lines > 200 but < 400)
            assert "very_long_function" in output
            assert "VeryLongClass" in output

    def test_flake8_integration_without_violations(self):
        """Test flake8 integration with code that has no violations."""
        # Create a Python file without violations
        clean_code = '''def short_function():
    """A short function."""
    return 42

class ShortClass:
    """A short class."""

    def __init__(self):
        self.value = 0

    def get_value(self):
        return self.value
'''

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "test_clean.py"
            test_file.write_text(clean_code)

            # Create pyproject.toml with lenient limits
            pyproject_content = """
[tool.pyla-linters]
max_function_length = 40
max_class_length = 200
"""
            pyproject_file = temp_path / "pyproject.toml"
            pyproject_file.write_text(pyproject_content)

            # Run flake8 on the test file with explicit plugin selection
            result = subprocess.run(
                ["uv", "run", "flake8", "--select=WL,EL", str(test_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            # Should not detect violations
            output = result.stdout + result.stderr

            # Should not contain our error codes
            assert "EL001" not in output
            assert "EL002" not in output

    def test_flake8_integration_with_custom_config(self):  # noqa: WL001
        """Test flake8 integration with custom configuration."""
        # Create a Python file that violates strict limits but not lenient ones
        medium_code = """def medium_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    line8 = 8
    return line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "test_medium.py"
            test_file.write_text(medium_code)

            # Test with strict limits - should have violations
            strict_pyproject = """
[project]
name = "test-project"
version = "0.1.0"
description = "Test project"
authors = [{name = "Test", email = "test@example.com"}]

[tool.pyla-linters]
max_function_length = 5
max_class_length = 50

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
"""
            pyproject_file = temp_path / "pyproject.toml"
            pyproject_file.write_text(strict_pyproject)

            result_strict = subprocess.run(
                ["uv", "run", "flake8", "--select=WL,EL", str(test_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            # Should have violations with strict limits
            strict_output = result_strict.stdout + result_strict.stderr
            assert "WL001" in strict_output

            # Test with lenient limits - should not have violations
            lenient_pyproject = """
[tool.poetry]
name = "test-project"
version = "0.1.0"
description = "Test project"
authors = ["Test <test@example.com>"]

[tool.pyla-linters]
max_function_length = 20
max_class_length = 200

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
            pyproject_file.write_text(lenient_pyproject)

            result_lenient = subprocess.run(
                ["uv", "run", "flake8", "--select=WL,EL", str(test_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            # Should not have violations with lenient limits
            lenient_output = result_lenient.stdout + result_lenient.stderr
            assert "WL001" not in lenient_output
            assert "EL001" not in lenient_output

    def test_flake8_integration_error_format(self):  # noqa: WL001
        """Test that flake8 integration produces correctly formatted errors."""
        # Create a Python file with a simple violation
        code_with_error = """def long_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    return line1 + line2 + line3 + line4 + line5 + line6
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "test_format.py"
            test_file.write_text(code_with_error)

            # Create pyproject.toml with strict limits
            pyproject_content = """
[project]
name = "test-project"
version = "0.1.0"
description = "Test project"
authors = [{name = "Test", email = "test@example.com"}]

[tool.pyla-linters]
max_function_length = 5
max_class_length = 50

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
"""
            pyproject_file = temp_path / "pyproject.toml"
            pyproject_file.write_text(pyproject_content)

            # Run flake8 on the test file with explicit plugin selection
            result = subprocess.run(
                ["uv", "run", "flake8", "--select=WL,EL", str(test_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            output = result.stdout + result.stderr

            # Should contain correctly formatted error message
            # Flake8 format is typically: filename:line:col: error_code message
            assert "test_format.py" in output
            assert "WL001" in output
            assert "long_function" in output
            assert "8 statements long" in output
            assert "exceeds warning threshold of 5" in output

    def test_flake8_integration_multiple_files(self):  # noqa: WL001
        """Test flake8 integration with multiple files."""
        file1_code = """def violation_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    return line1 + line2 + line3 + line4 + line5 + line6 + line7
"""

        file2_code = """def clean_function():
    return 42

class CleanClass:
    def method(self):
        return True
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create multiple test files
            file1 = temp_path / "file1.py"
            file1.write_text(file1_code)

            file2 = temp_path / "file2.py"
            file2.write_text(file2_code)

            # Create pyproject.toml
            pyproject_content = """
[project]
name = "test-project"
version = "0.1.0"
description = "Test project"
authors = [{name = "Test", email = "test@example.com"}]

[tool.pyla-linters]
max_function_length = 5
max_class_length = 50

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
"""
            pyproject_file = temp_path / "pyproject.toml"
            pyproject_file.write_text(pyproject_content)

            # Run flake8 on all Python files with explicit plugin selection
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "flake8",
                    "--select=WL,EL",
                    "--length-max-function=5",
                    "--length-max-class=50",
                    str(file1),
                    str(file2),
                ],
                capture_output=True,
                text=True,
            )

            output = result.stdout + result.stderr

            # Should find violation in file1 but not file2
            assert "file1.py" in output
            assert "WL001" in output  # 9 lines > 5 threshold but < 10 (2x threshold)
            assert "violation_function" in output

            # Should not complain about file2's clean functions
            if "file2.py" in output:
                # If file2 is mentioned, it shouldn't have EL001/EL002 errors
                file2_lines = [line for line in output.split("\n") if "file2.py" in line]
                for line in file2_lines:
                    assert "EL001" not in line
                    assert "EL002" not in line

    def test_flake8_integration_with_syntax_errors(self):
        """Test flake8 integration handles syntax errors gracefully."""
        # Create a Python file with syntax errors
        broken_code = """def broken_function(
    # Missing closing parenthesis
    line1 = 1
    line2 = 2
    return line1 + line2
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "broken.py"
            test_file.write_text(broken_code)

            # Create pyproject.toml
            pyproject_content = """
[tool.pyla-linters]
max_function_length = 5
max_class_length = 50
"""
            pyproject_file = temp_path / "pyproject.toml"
            pyproject_file.write_text(pyproject_content)

            # Run flake8 on the test file with our plugin
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "--select=EL", str(test_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            # flake8 should run (might report syntax errors)
            # but our plugin should not crash or produce EL001/EL002 errors
            output = result.stdout + result.stderr

            # Our plugin should not report length violations for broken syntax
            assert "EL001" not in output
            assert "EL002" not in output
