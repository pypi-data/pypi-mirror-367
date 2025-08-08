"""Common utilities for length checker tests."""

import ast
from typing import List, Tuple

from src.linters.length_checker.config import LengthCheckerConfig
from src.linters.length_checker.plugin import LengthCheckerPlugin


def run_plugin_on_code(
    code: str, config: LengthCheckerConfig | None = None, _filename: str = "test.py"
) -> List[Tuple[int, int, str, str]]:
    """Helper function to run the flake8 plugin on code and return error tuples."""
    import os
    import tempfile

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []  # Return empty list for syntax errors, matching plugin behavior

    # Create a temporary file with the code so the plugin can read it
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        temp_filename = f.name

    try:
        plugin = LengthCheckerPlugin(tree, temp_filename)
        if config:
            plugin.set_config(config)

        return list(plugin.run())
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)
