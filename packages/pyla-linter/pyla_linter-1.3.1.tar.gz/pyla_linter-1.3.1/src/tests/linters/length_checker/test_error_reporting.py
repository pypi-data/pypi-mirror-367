"""Tests for the length checker error reporting functionality."""

import ast
import os
import tempfile

from src.linters.length_checker.config import LengthCheckerConfig
from src.linters.length_checker.plugin import LengthCheckerPlugin

from .test_utils import run_plugin_on_code


class TestErrorReporting:
    """Test comprehensive error reporting functionality."""

    def test_error_message_format_function(self):
        """Test that function error messages follow correct format."""
        code = """def long_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    return line1 + line2 + line3 + line4 + line5 + line6"""

        config = LengthCheckerConfig(max_function_length=3)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1

        line, col, message, error_type = errors[0]
        assert line == 1  # Error reported on function definition line
        assert col == 0  # Column should be 0
        assert error_type == "EL001"
        assert message.startswith("EL001")
        assert "long_function" in message
        assert "8 statements long" in message
        assert "exceeds error threshold of 6" in message

    def test_error_message_format_class(self):
        """Test that class error messages follow correct format."""
        code = """class LongClass:
    def method1(self):
        return 1
    def method2(self):
        return 2
    def method3(self):
        return 3
    def method4(self):
        return 4
    def method5(self):
        return 5
    def method6(self):
        return 6"""

        config = LengthCheckerConfig(max_class_length=5)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1

        line, col, message, error_type = errors[0]
        assert line == 1  # Error reported on class definition line
        assert col == 0  # Column should be 0
        assert error_type == "EL002"
        assert message.startswith("EL002")
        assert "LongClass" in message
        assert "13 statements long" in message
        assert "exceeds error threshold of 10" in message

    def test_error_codes_are_unique(self):
        """Test that class and function violations have different error codes."""
        code = """class TooLongClass:
    def too_long_function(self):
        line1 = 1
        line2 = 2
        line3 = 3
        line4 = 4
        line5 = 5
        line6 = 6
        return line1 + line2 + line3 + line4 + line5 + line6

    def another_method(self):
        return 1

    def third_method(self):
        return 2

    def fourth_method(self):
        return 3"""

        config = LengthCheckerConfig(max_function_length=3, max_class_length=5)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 2

        error_types = [error[3] for error in errors]  # error[3] is the error type
        assert "EL002" in error_types  # Class error
        assert "EL001" in error_types  # Function error

    def test_error_line_positioning(self):
        """Test that errors are reported on correct line numbers."""
        code = """# First line comment

class FirstClass:
    def method1(self):
        return 1
    def method2(self):
        return 2

def first_function():
    line1 = 1
    line2 = 2
    line3 = 3

class SecondClass:
    def method1(self):
        return 1
    def method2(self):
        return 2
    def method3(self):
        return 3"""

        config = LengthCheckerConfig(max_function_length=2, max_class_length=3)

        errors = run_plugin_on_code(code, config)
        # Should have violations for first_function, FirstClass, and SecondClass
        assert len(errors) == 3

        # Check that line numbers are correct
        error_lines = [error[0] for error in errors]  # error[0] is the line number
        assert 3 in error_lines  # FirstClass starts at line 3
        assert 9 in error_lines  # first_function starts at line 9
        assert 14 in error_lines  # SecondClass starts at line 14

    def test_configuration_threshold_exact_match(self):
        """Test behavior when code length exactly matches configured limits."""
        code = """def exact_limit_function():
    line1 = 1
    line2 = 2
    return line1 + line2"""

        config = LengthCheckerConfig(max_function_length=4)  # Exactly 4 lines

        errors = run_plugin_on_code(code, config)
        # Should have no violations when exactly at limit
        assert len(errors) == 0

    def test_configuration_threshold_one_over_limit(self):
        """Test behavior when code length is one line over configured limits."""
        code = """def one_over_limit_function():
    line1 = 1
    line2 = 2
    line3 = 3
    return line1 + line2 + line3"""

        config = LengthCheckerConfig(max_function_length=4)  # 5 lines > 4 limit

        errors = run_plugin_on_code(code, config)
        # Should have exactly 1 violation (warning, not error)
        assert len(errors) == 1
        line, col, message, error_type = errors[0]
        assert error_type == "WL001"  # Should be warning
        assert "5 statements long, exceeds warning threshold of 4" in message

    def test_multiple_error_ordering(self):
        """Test that multiple errors are reported in source code order."""
        code = """def first_function():
    line1 = 1
    line2 = 2
    line3 = 3
    return line1 + line2 + line3

def second_function():
    line1 = 1
    line2 = 2
    line3 = 3
    return line1 + line2 + line3"""

        config = LengthCheckerConfig(max_function_length=3)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 2

        # Errors should be in source order
        line1, col1, message1, error_type1 = errors[0]
        line2, col2, message2, error_type2 = errors[1]
        assert line1 < line2  # First error line < second error line
        assert "first_function" in message1
        assert "second_function" in message2

    def test_error_message_includes_actual_and_max_lengths(self):
        """Test that error messages include both actual and maximum lengths."""
        code = """def test_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    return line1 + line2 + line3 + line4 + line5 + line6"""

        config = LengthCheckerConfig(max_function_length=5)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1

        line, col, message, error_type = errors[0]
        assert "8 statements long" in message  # Actual length
        assert "exceeds warning threshold of 5" in message  # Configured limit

    def test_error_reporting_with_file_reading(self):
        """Test error reporting when plugin reads file from disk."""
        code = """def file_function():
    line1 = 1
    line2 = 2
    line3 = 3
    return line1 + line2 + line3"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            tree = ast.parse(code)
            plugin = LengthCheckerPlugin(tree, temp_path)
            config = LengthCheckerConfig(max_function_length=3)
            plugin.set_config(config)

            # Test with the real file path for filename
            errors = list(plugin.run())
            assert len(errors) == 1
            line, col, message, error_type = errors[0]
            assert "WL001" in message
            assert "file_function" in message
        finally:
            os.unlink(temp_path)

    def test_error_reporting_resilience_to_invalid_files(self):
        """Test that error reporting handles invalid files gracefully."""
        # Test with non-existent file - plugin constructor will receive parsed AST
        # so this doesn't apply directly
        # but we test with broken syntax code

        # Test with invalid code that would cause processing errors
        invalid_code = """def broken_function(
    # This is broken syntax
    return 42"""

        errors = run_plugin_on_code(invalid_code)
        assert errors == []  # Should handle gracefully, not crash
