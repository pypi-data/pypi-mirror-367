"""Tests for file exclusion patterns behavior in the length checker."""

import ast
import inspect
import tempfile
from pathlib import Path

from src.linters.length_checker.config import LengthCheckerConfig
from src.linters.length_checker.plugin import LengthCheckerPlugin

from .test_utils import run_plugin_on_code


class TestFileExclusionPatterns:
    """Test file and directory exclusion pattern behavior.

    Note: The current implementation does not support file/directory exclusion patterns.
    These tests document the current behavior and can be updated when exclusion support is added.
    """

    def test_no_exclusion_pattern_support_in_config(self):
        """Test that current configuration doesn't support exclusion patterns."""
        config = LengthCheckerConfig()

        # Current implementation doesn't have exclusion pattern attributes
        assert not hasattr(config, "exclude_patterns")
        assert not hasattr(config, "include_patterns")
        assert not hasattr(config, "exclude_dirs")
        assert not hasattr(config, "exclude_files")

    def test_plugin_processes_all_provided_files(self):
        """Test that plugin processes all files provided to it."""
        code = """def test_function():
    return 42"""

        config = LengthCheckerConfig(max_function_length=1)

        # Plugin should process any file path provided to it
        errors1 = run_plugin_on_code(code, config, "regular_file.py")
        errors2 = run_plugin_on_code(code, config, "test_file.py")
        errors3 = run_plugin_on_code(code, config, "__pycache__/cached.py")
        errors4 = run_plugin_on_code(code, config, "venv/lib/python3.11/site-packages/module.py")

        # All should produce violations (all have functions > 1 line)
        assert len(errors1) == 1
        assert len(errors2) == 1
        assert len(errors3) == 1
        assert len(errors4) == 1

    def test_plugin_does_not_filter_by_file_extension(self):
        """Test that plugin doesn't filter files by extension."""
        code = """def test_function():
    return 42"""

        config = LengthCheckerConfig(max_function_length=1)

        # Plugin should process files regardless of extension
        errors_py = run_plugin_on_code(code, config, "test.py")
        errors_pyx = run_plugin_on_code(code, config, "test.pyx")
        errors_no_ext = run_plugin_on_code(code, config, "test")

        # All should produce violations
        assert len(errors_py) == 1
        assert len(errors_pyx) == 1
        assert len(errors_no_ext) == 1

    def test_plugin_does_not_filter_by_directory_path(self):
        """Test that plugin doesn't filter files by directory path."""
        code = """def test_function():
    return 42"""

        config = LengthCheckerConfig(max_function_length=1)

        # Plugin should process files in any directory
        paths_to_test = [
            "src/module.py",
            "tests/test_module.py",
            "__pycache__/module.pyc",
            ".venv/lib/python3.11/site-packages/package/module.py",
            "node_modules/some-package/python/script.py",
            ".git/hooks/pre-commit.py",
            "build/temp/generated.py",
            "dist/package/module.py",
        ]

        for path in paths_to_test:
            errors = run_plugin_on_code(code, config, path)
            assert len(errors) == 1, f"Expected violation for path: {path}"

    def test_exclusion_would_be_handled_by_flake8_not_plugin(self):
        """Test that file exclusion is expected to be handled by flake8, not the plugin."""
        # This test documents the current architecture where flake8 handles
        # file filtering and the plugin processes whatever files are passed to it

        tree = ast.parse("def test(): pass")
        plugin = LengthCheckerPlugin(tree, "test.py")

        # The plugin's run method signature shows it expects to receive
        # individual files that flake8 has already filtered
        signature = inspect.signature(plugin.run)

        # Plugin run method takes no parameters (gets data from constructor)
        params = list(signature.parameters.keys())
        # Plugin doesn't receive exclude patterns in run method
        assert "exclude_patterns" not in params
        assert "include_patterns" not in params

    def test_current_config_from_toml_ignores_exclusion_patterns(self):
        """Test that TOML config loading ignores exclusion pattern settings."""
        toml_content = """
[tool.pyla-linters]
max_function_length = 30
max_class_length = 150
# These would be exclusion patterns if supported
exclude_patterns = ["*/test_*", "*.tmp.py"]
exclude_dirs = ["__pycache__", ".venv"]
include_patterns = ["src/**/*.py"]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            temp_path = Path(f.name)

        try:
            config = LengthCheckerConfig.from_pyproject_toml(temp_path)
            # Should load the supported settings
            assert config.max_function_length == 30
            assert config.max_class_length == 150
            # Should ignore unsupported exclusion settings
            assert not hasattr(config, "exclude_patterns")
            assert not hasattr(config, "exclude_dirs")
            assert not hasattr(config, "include_patterns")
        finally:
            temp_path.unlink()

    def test_future_exclusion_pattern_support_would_need_config_extension(self):
        """Test documenting what would be needed for exclusion pattern support."""
        # This test documents the interface that would be needed for exclusion support

        # Current config only has length limits
        config = LengthCheckerConfig()
        current_attrs = [attr for attr in dir(config) if not attr.startswith("_")]
        expected_current = [
            "DEFAULT_CLASS_LENGTH",
            "DEFAULT_FUNCTION_LENGTH",
            "from_dict",
            "from_pyproject_toml",
            "max_class_length",
            "max_function_length",
        ]

        # Verify current attributes match expected
        assert set(current_attrs) == set(expected_current)

        # Future exclusion support would need additional attributes
        future_exclusion_attrs = [
            "exclude_patterns",
            "include_patterns",
            "exclude_dirs",
            "exclude_files",
        ]

        # These don't exist yet
        for attr in future_exclusion_attrs:
            assert not hasattr(config, attr)

    def test_plugin_run_params_could_support_exclusion_metadata(self):
        """Test that plugin run method accepts params that could contain exclusion info."""
        # Test that the plugin interface doesn't support exclusion patterns directly
        # This functionality would be handled by flake8 itself

        code = "def test(): pass"

        # The plugin doesn't accept exclusion parameters - this is handled by flake8
        errors = run_plugin_on_code(code)
        assert isinstance(errors, list)  # Should return normal error list

        # Plugin interface is simplified - flake8 handles file filtering
