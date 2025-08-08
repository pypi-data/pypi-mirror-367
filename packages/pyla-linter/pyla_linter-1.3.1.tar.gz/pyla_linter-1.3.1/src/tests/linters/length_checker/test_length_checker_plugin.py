"""Tests for the length checker plugin main functionality."""

import ast

from src.linters.length_checker.config import LengthCheckerConfig
from src.linters.length_checker.plugin import LengthCheckerPlugin

from .test_utils import run_plugin_on_code


class TestLengthCheckerPlugin:
    """Test the main plugin functionality."""

    def test_plugin_initialization(self):
        """Test plugin initializes correctly."""
        tree = ast.parse("def test(): pass")
        plugin = LengthCheckerPlugin(tree, "test.py")
        assert plugin.name == "length_checker"
        assert plugin.version == "1.0.0"

    def test_no_violations_under_limit(self):
        """Test that code under limits produces no violations."""
        code = """def short_function():
    return 42

class ShortClass:
    def method(self):
        return True"""

        # Set high limits to ensure no violations
        config = LengthCheckerConfig(max_function_length=50, max_class_length=50)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 0

    def test_function_violation_detection(self):
        """Test detection of function length violations."""
        code = """def long_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    return line1 + line2 + line3 + line4 + line5"""

        config = LengthCheckerConfig(max_function_length=3, max_class_length=50)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1
        line, col, message, error_type = errors[0]
        assert error_type == "EL001"
        assert "EL001" in message
        assert "long_function" in message

    def test_class_violation_detection(self):
        """Test detection of class length violations."""
        code = """class LongClass:
    def method1(self):
        return 1

    def method2(self):
        return 2

    def method3(self):
        return 3"""

        config = LengthCheckerConfig(max_function_length=50, max_class_length=5)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1
        line, col, message, error_type = errors[0]
        assert error_type == "WL002"  # Should be warning, not error (9 lines > 5 but < 10)
        assert "WL002" in message
        assert "LongClass" in message

    def test_multiple_violations(self):
        """Test detection of multiple violations."""
        code = """class LongClass:
    def long_method1(self):
        line1 = 1
        line2 = 2
        line3 = 3
        return line1 + line2 + line3

    def long_method2(self):
        line1 = 1
        line2 = 2
        line3 = 3
        return line1 + line2 + line3"""

        config = LengthCheckerConfig(max_function_length=3, max_class_length=8)

        errors = run_plugin_on_code(code, config)
        # Should have 3 violations: 1 class + 2 functions
        assert len(errors) == 3

    def test_syntax_error_handling(self):
        """Test that syntax errors are handled gracefully."""
        code = """def broken_function(
    # Missing closing parenthesis
    return 42"""

        errors = run_plugin_on_code(code)
        # Should return empty list, not crash
        assert errors == []

    def test_docstring_exclusion_in_violations(self):
        """Test that docstrings are properly excluded from violation counts."""
        code = '''def function_with_long_docstring():
    """This is a very long docstring.

    It spans many lines to test that these lines
    are not counted toward the function length limit.

    This should not trigger a violation even though
    the total line count is high.
    """
    return 42'''

        config = LengthCheckerConfig(max_function_length=3)

        errors = run_plugin_on_code(code, config)
        # Should have no violations because docstring lines are excluded
        assert len(errors) == 0

    def test_nested_function_counting(self):
        """Test that nested functions are counted separately."""
        code = """def outer_function():
    def inner_function():
        line1 = 1
        line2 = 2
        line3 = 3
        line4 = 4
        return line1 + line2 + line3 + line4
    return inner_function()"""

        config = LengthCheckerConfig(max_function_length=4, max_class_length=50)

        errors = run_plugin_on_code(code, config)
        # Only inner function should violate (outer: 2 statements, inner: 6 statements > 4 limit)
        assert len(errors) == 1
        error_messages = [error[2] for error in errors]  # error[2] is the message
        assert any("inner_function" in msg for msg in error_messages)
