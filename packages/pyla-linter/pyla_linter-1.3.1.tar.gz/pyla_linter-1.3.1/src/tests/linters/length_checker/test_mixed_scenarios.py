"""Tests for mixed scenarios with warnings and errors in the same file."""

from src.linters.length_checker.config import LengthCheckerConfig

from .test_utils import run_plugin_on_code


class TestMixedScenarios:
    """Test mixed scenarios with warnings and errors in same file."""

    def test_mixed_function_warnings_and_errors(self):
        """Test file with both function warnings and errors."""
        code = """def warning_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    return line1 + line2 + line3 + line4

def error_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    return sum([line1, line2, line3, line4, line5, line6, line7])"""

        # Threshold 4: warning_function = 6 lines (warning), error_function = 8 lines (error)
        config = LengthCheckerConfig(max_function_length=4, max_class_length=50)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 2

        # Should have one warning and one error
        violation_types = [v[3] for v in violations]
        assert "WL001" in violation_types
        assert "EL001" in violation_types

    def test_mixed_class_warnings_and_errors(self):
        """Test file with both class warnings and errors."""
        code = """class WarningClass:
    def method1(self):
        return 1
    def method2(self):
        return 2
    def method3(self):
        return 3

class ErrorClass:
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
        return 6
    def method7(self):
        return 7
    def method8(self):
        return 8
    def method9(self):
        return 9"""

        # Threshold 5: WarningClass = 7 lines (warning), ErrorClass = 13 lines (error)
        config = LengthCheckerConfig(max_function_length=50, max_class_length=5)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 2

        # Should have one warning and one error
        violation_types = [v[3] for v in violations]
        assert "WL002" in violation_types
        assert "EL002" in violation_types

    def test_mixed_functions_and_classes(self):
        """Test file with mixed function and class violations."""
        code = """def warning_function():
    line1 = 1
    line2 = 2
    line3 = 3
    return line1 + line2 + line3

class ErrorClass:
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
        return 6
    def method7(self):
        return 7"""

        # Function threshold 3: warning_function = 5 lines (warning)
        # Class threshold 5: ErrorClass = 11 lines (error)
        config = LengthCheckerConfig(max_function_length=3, max_class_length=5)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 2

        # Should have function warning and class error
        violation_types = [v[3] for v in violations]
        assert "WL001" in violation_types
        assert "EL002" in violation_types

    def test_violation_ordering_source_order(self):
        """Test that violations are reported in source code order."""
        code = """def first_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    return line1 + line2 + line3 + line4

class MiddleClass:
    def method1(self):
        return 1
    def method2(self):
        return 2
    def method3(self):
        return 3

def last_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    return line1 + line2 + line3 + line4 + line5"""

        config = LengthCheckerConfig(max_function_length=3, max_class_length=4)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 3

        # Check violations are in source order by line number
        line_numbers = [v[0] for v in violations]
        assert line_numbers == sorted(line_numbers)

        # Check specific ordering
        assert line_numbers[0] == 1  # first_function
        assert line_numbers[1] == 8  # MiddleClass
        assert line_numbers[2] == 16  # last_function
