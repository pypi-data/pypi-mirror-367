"""Tests for flake8 configuration integration with multiple public items plugin."""

import subprocess
import tempfile
from pathlib import Path


class TestFlake8ConfigIntegration:
    """Test flake8 configuration integration."""

    def test_exclude_configuration(self):
        """Test that files can be excluded via flake8 CLI option."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a Python file with multiple public items
            test_file = temp_path / "test_excluded.py"
            test_file.write_text(
                """def function_one():
    return 1


def function_two():
    return 2
"""
            )

            # Run flake8 with exclude option
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "flake8",
                    "--exclude=test_excluded.py",
                    "--select=EL101",
                    str(temp_path),
                ],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # Should not report any errors because file is excluded
            assert result.returncode == 0
            assert "EL101" not in result.stdout

    def test_per_file_ignores_configuration(self):
        """Test that specific errors can be ignored per file using CLI option."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a Python file with multiple public items
            test_file = temp_path / "test_ignore.py"
            test_file.write_text(
                """def function_one():
    return 1


def function_two():
    return 2
"""
            )

            # Run flake8 with per-file-ignores CLI option
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "flake8",
                    f"--per-file-ignores={test_file.name}:EL101",
                    "--select=EL101",
                    str(test_file),
                ],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # Should not report EL101 errors because they're ignored for this file
            assert result.returncode == 0
            assert "EL101" not in result.stdout

    def test_select_configuration(self):
        """Test that plugin can be explicitly selected."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a Python file with multiple public items
            test_file = temp_path / "test_select.py"
            test_file.write_text(
                """def function_one():
    return 1


def function_two():
    return 2
"""
            )

            # Create flake8 config that only selects our plugin
            config_file = temp_path / "setup.cfg"
            config_file.write_text(
                """
[flake8]
select = EL101
"""
            )

            # Run flake8 with our plugin
            result = subprocess.run(
                ["uv", "run", "flake8", "--config", str(config_file), str(test_file)],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # Should report EL101 error
            assert result.returncode != 0
            assert "EL101" in result.stdout
            assert "function_one" in result.stdout
            assert "function_two" in result.stdout

    def test_ignore_configuration(self):
        """Test that plugin errors can be globally ignored via CLI."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a Python file with multiple public items
            test_file = temp_path / "test_ignore_global.py"
            test_file.write_text(
                """def function_one():
    return 1


def function_two():
    return 2
"""
            )

            # Run flake8 with ignore CLI option
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "flake8",
                    "--ignore=EL101",
                    "--select=EL101",
                    str(test_file),
                ],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # Should not report any errors because EL101 is ignored
            assert result.returncode == 0
            assert "EL101" not in result.stdout

    def test_extend_ignore_configuration(self):
        """Test that plugin errors can be added to existing ignores via CLI."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a Python file with multiple public items and other style issues
            test_file = temp_path / "test_extend_ignore.py"
            test_file.write_text(
                """def function_one():
    return 1


def function_two():
    return 2
"""
            )

            # Run flake8 with extend-ignore CLI option
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "flake8",
                    "--extend-ignore=EL101",
                    "--select=EL101",
                    str(test_file),
                ],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # Should not report EL101 errors
            assert result.returncode == 0
            assert "EL101" not in result.stdout

    def test_multiple_files_with_config(self):
        """Test per-file ignore configuration with multiple files via CLI."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create first file with violations
            file1 = temp_path / "file1.py"
            file1.write_text(
                """def function_one():
    return 1


def function_two():
    return 2
"""
            )

            # Create second file with violations
            file2 = temp_path / "file2.py"
            file2.write_text(
                """class ClassOne:
    pass


class ClassTwo:
    pass
"""
            )

            # Create third file without violations
            file3 = temp_path / "file3.py"
            file3.write_text(
                """def single_function():
    return 1
"""
            )

            # Run flake8 on all files with per-file ignores for file1
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "flake8",
                    f"--per-file-ignores={file1.name}:EL101",
                    "--select=EL101",
                    str(file1),
                    str(file2),
                    str(file3),
                ],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # Should report error for file2 but not file1 or file3
            assert result.returncode != 0
            assert file1.name not in result.stdout  # Ignored
            assert file2.name in result.stdout  # Should have error
            assert file3.name not in result.stdout  # No violations
            assert "EL101" in result.stdout

    def test_pyproject_toml_configuration(self):
        """Test that pyproject.toml configuration works."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a Python file with multiple public items
            test_file = temp_path / "test_pyproject.py"
            test_file.write_text(
                """def function_one():
    return 1


def function_two():
    return 2
"""
            )

            # Create pyproject.toml config that ignores EL101
            config_file = temp_path / "pyproject.toml"
            config_file.write_text(
                """
[tool.flake8]
ignore = ["EL101"]
"""
            )

            # Run flake8 with our plugin (note: flake8 doesn't natively support pyproject.toml)
            # This test documents the expected behavior if pyproject.toml support is added
            result = subprocess.run(
                ["uv", "run", "flake8", str(test_file)],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # This should report errors since flake8 doesn't read pyproject.toml by default
            # but documents expected behavior
            assert result.returncode != 0
            assert "EL101" in result.stdout


class TestFlake8CliOptions:
    """Test flake8 command line options integration."""

    def test_select_cli_option(self):
        """Test --select command line option."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a Python file with multiple public items
            test_file = temp_path / "test_cli_select.py"
            test_file.write_text(
                """
def function_one():
    return 1

def function_two():
    return 2
"""
            )

            # Run flake8 with --select option
            result = subprocess.run(
                ["uv", "run", "flake8", "--select=EL101", str(test_file)],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # Should report EL101 error
            assert result.returncode != 0
            assert "EL101" in result.stdout

    def test_ignore_cli_option(self):
        """Test --ignore command line option."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a Python file with multiple public items
            test_file = temp_path / "test_cli_ignore.py"
            test_file.write_text(
                """def function_one():
    return 1


def function_two():
    return 2
"""
            )

            # Run flake8 with --ignore option, but also select only EL101 to test specifically
            result = subprocess.run(
                ["uv", "run", "flake8", "--ignore=EL101", "--select=EL101", str(test_file)],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # Should not report any errors (ignore overrides select)
            assert result.returncode == 0
            assert "EL101" not in result.stdout

    def test_extend_ignore_cli_option(self):
        """Test --extend-ignore command line option."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a Python file with multiple public items
            test_file = temp_path / "test_cli_extend_ignore.py"
            test_file.write_text(
                """def function_one():
    return 1


def function_two():
    return 2
"""
            )

            # Run flake8 with --extend-ignore option
            result = subprocess.run(
                ["uv", "run", "flake8", "--extend-ignore=EL101", str(test_file)],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            # Should not report EL101 errors
            assert result.returncode == 0 or "EL101" not in result.stdout
