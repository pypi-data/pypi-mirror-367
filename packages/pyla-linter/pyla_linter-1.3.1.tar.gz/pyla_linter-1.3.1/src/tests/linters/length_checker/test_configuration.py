"""Tests for the length checker configuration functionality."""

import ast
import os
import tempfile
from pathlib import Path

from src.linters.length_checker.config import LengthCheckerConfig
from src.linters.length_checker.plugin import LengthCheckerPlugin


class TestConfiguration:
    """Test configuration loading and defaults."""

    def test_default_config_values(self):
        """Test that default configuration values are correct."""
        config = LengthCheckerConfig()
        assert config.max_function_length == LengthCheckerConfig.DEFAULT_FUNCTION_LENGTH
        assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH
        assert config.max_function_length == 40
        assert config.max_class_length == 200

    def test_config_initialization_with_custom_values(self):
        """Test configuration initialization with custom values."""
        config = LengthCheckerConfig(max_function_length=25, max_class_length=150)
        assert config.max_function_length == 25
        assert config.max_class_length == 150

    def test_config_from_dict_with_all_values(self):
        """Test configuration creation from dictionary with all values."""
        config_dict = {
            "max_function_length": 30,
            "max_class_length": 180,
        }
        config = LengthCheckerConfig.from_dict(config_dict)
        assert config.max_function_length == 30
        assert config.max_class_length == 180

    def test_config_from_dict_with_partial_values(self):
        """Test configuration creation from dictionary with partial values."""
        config_dict = {"max_function_length": 35}
        config = LengthCheckerConfig.from_dict(config_dict)
        assert config.max_function_length == 35
        assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH

    def test_config_from_dict_with_no_values(self):
        """Test configuration creation from empty dictionary."""
        config_dict = {}
        config = LengthCheckerConfig.from_dict(config_dict)
        assert config.max_function_length == LengthCheckerConfig.DEFAULT_FUNCTION_LENGTH
        assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH

    def test_config_from_dict_with_extra_values(self):
        """Test configuration creation from dictionary with extra values."""
        config_dict = {
            "max_function_length": 25,
            "max_class_length": 175,
            "unknown_setting": "ignored",
        }
        config = LengthCheckerConfig.from_dict(config_dict)
        assert config.max_function_length == 25
        assert config.max_class_length == 175

    def test_config_from_nonexistent_pyproject_toml(self):
        """Test configuration loading when pyproject.toml doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_path = Path(temp_dir) / "nonexistent.toml"
            config = LengthCheckerConfig.from_pyproject_toml(nonexistent_path)
            # Should return default config
            assert config.max_function_length == LengthCheckerConfig.DEFAULT_FUNCTION_LENGTH
            assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH

    def test_config_from_valid_pyproject_toml(self):
        """Test configuration loading from valid pyproject.toml."""
        toml_content = """
[tool.pyla-linters]
max_function_length = 50
max_class_length = 250
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            temp_path = Path(f.name)

        try:
            config = LengthCheckerConfig.from_pyproject_toml(temp_path)
            assert config.max_function_length == 50
            assert config.max_class_length == 250
        finally:
            temp_path.unlink()

    def test_config_from_pyproject_toml_missing_tool_section(self):
        """Test configuration loading when [tool] section is missing."""
        toml_content = """
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            temp_path = Path(f.name)

        try:
            config = LengthCheckerConfig.from_pyproject_toml(temp_path)
            # Should return default config
            assert config.max_function_length == LengthCheckerConfig.DEFAULT_FUNCTION_LENGTH
            assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH
        finally:
            temp_path.unlink()

    def test_config_from_pyproject_toml_missing_pyla_linters_section(self):
        """Test configuration loading when [tool.pyla-linters] section is missing."""
        toml_content = """
[project]
name = "test-project"

[tool.black]
line-length = 88
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            temp_path = Path(f.name)

        try:
            config = LengthCheckerConfig.from_pyproject_toml(temp_path)
            # Should return default config
            assert config.max_function_length == LengthCheckerConfig.DEFAULT_FUNCTION_LENGTH
            assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH
        finally:
            temp_path.unlink()

    def test_config_from_invalid_toml_file(self):
        """Test configuration loading from invalid TOML file."""
        invalid_toml_content = """
[tool.pyla-linters
# Missing closing bracket
max_function_length = 50
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(invalid_toml_content)
            temp_path = Path(f.name)

        try:
            config = LengthCheckerConfig.from_pyproject_toml(temp_path)
            # Should return default config when TOML parsing fails
            assert config.max_function_length == LengthCheckerConfig.DEFAULT_FUNCTION_LENGTH
            assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH
        finally:
            temp_path.unlink()

    def test_config_from_pyproject_toml_with_partial_settings(self):
        """Test configuration loading with only some settings in pyproject.toml."""
        toml_content = """
[tool.pyla-linters]
max_function_length = 35
# max_class_length is not specified
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            temp_path = Path(f.name)

        try:
            config = LengthCheckerConfig.from_pyproject_toml(temp_path)
            assert config.max_function_length == 35
            assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH
        finally:
            temp_path.unlink()

    def test_plugin_config_loading_behavior(self):
        """Test that plugin loads configuration correctly."""
        tree = ast.parse("def test(): pass")
        plugin = LengthCheckerPlugin(tree, "test.py")

        # Initially should use default config
        assert plugin.config.max_function_length == LengthCheckerConfig.DEFAULT_FUNCTION_LENGTH
        assert plugin.config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH

    def test_plugin_manual_config_override(self):
        """Test that manual configuration overrides file-based config."""
        tree = ast.parse("def test(): pass")
        plugin = LengthCheckerPlugin(tree, "test.py")

        # Set manual config
        custom_config = LengthCheckerConfig(max_function_length=15, max_class_length=75)
        plugin.set_config(custom_config)

        # Config should be the manually set one
        assert plugin.config.max_function_length == 15
        assert plugin.config.max_class_length == 75
        assert plugin._manual_config is True

    def test_plugin_config_loading_only_once(self):
        """Test that configuration is only loaded once from file."""
        tree = ast.parse("def test(): pass")
        plugin = LengthCheckerPlugin(tree, "test.py")

        # First call should load config
        assert plugin._config_loaded is False
        plugin._load_config_if_needed()
        assert plugin._config_loaded is True

        # Second call should not reload
        original_config = plugin.config
        plugin._load_config_if_needed()
        assert plugin.config is original_config  # Same object reference

    def test_config_find_pyproject_toml_search(self):
        """Test that pyproject.toml search works in parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create nested directory structure
            nested_dir = temp_path / "subdir" / "nested"
            nested_dir.mkdir(parents=True)

            # Create pyproject.toml in root
            toml_content = """
[tool.pyla-linters]
max_function_length = 60
"""
            pyproject_path = temp_path / "pyproject.toml"
            pyproject_path.write_text(toml_content)

            # Change to nested directory
            original_cwd = os.getcwd()
            try:
                os.chdir(nested_dir)

                # Should find pyproject.toml in parent directories
                config = LengthCheckerConfig.from_pyproject_toml()
                assert config.max_function_length == 60
            finally:
                os.chdir(original_cwd)
