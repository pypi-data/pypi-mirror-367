"""Tests for new edge cases and boundary conditions for the warning system."""

from src.linters.length_checker.config import LengthCheckerConfig

from .test_utils import run_plugin_on_code


class TestNewEdgeCases:
    """Test edge cases and boundary conditions for the new warning system."""

    def test_function_exactly_at_2x_threshold(self):
        """Test function exactly at 2x threshold generates error."""
        code = """def exact_2x_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    return line1 + line2 + line3 + line4 + line5"""

        # Threshold 3, function = 6 lines (exactly 2x threshold)
        config = LengthCheckerConfig(max_function_length=3, max_class_length=50)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 1
        assert violations[0][3] == "EL001"  # Should be error

    def test_class_exactly_at_2x_threshold(self):
        """Test class exactly at 2x threshold generates error."""
        code = """class Exact2xClass:
    def method1(self):
        return 1
    def method2(self):
        return 2
    def method3(self):
        return 3"""

        # Threshold 3, class = 6 lines (exactly 2x threshold)
        config = LengthCheckerConfig(max_function_length=50, max_class_length=3)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 1
        assert violations[0][3] == "EL002"  # Should be error

    def test_function_one_over_2x_threshold(self):
        """Test function one line over 2x threshold generates error."""
        code = """def over_2x_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    return line1 + line2 + line3 + line4 + line5 + line6"""

        # Threshold 3, function = 7 lines (> 6 which is 2x threshold)
        config = LengthCheckerConfig(max_function_length=3, max_class_length=50)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 1
        assert violations[0][3] == "EL001"  # Should be error

    def test_class_one_over_2x_threshold(self):
        """Test class one line over 2x threshold generates error."""
        code = """class Over2xClass:
    def method1(self):
        return 1
    def method2(self):
        return 2
    def method3(self):
        return 3
    def method4(self):
        return 4"""

        # Threshold 3, class = 7 lines (> 6 which is 2x threshold)
        config = LengthCheckerConfig(max_function_length=50, max_class_length=3)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 1
        assert violations[0][3] == "EL002"  # Should be error

    def test_warning_codes_generation(self):
        """Test that warning codes WL001 and WL002 are generated correctly."""
        code = """def warning_function():
    line1 = 1
    line2 = 2
    line3 = 3
    return line1 + line2 + line3

class WarningClass:
    def method(self):
        return 1
    def method2(self):
        return 2"""

        config = LengthCheckerConfig(max_function_length=3, max_class_length=4)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 2

        violation_codes = [v[3] for v in violations]
        assert "WL001" in violation_codes  # Function warning
        assert "WL002" in violation_codes  # Class warning

        # Check specific messages
        for line, col, message, code in violations:
            if code == "WL001":
                assert "warning_function" in message
                assert "warning threshold" in message
            elif code == "WL002":
                assert "WarningClass" in message
                assert "warning threshold" in message

    def test_message_format_consistency(self):  # noqa: WL001
        """Test that all message formats include required elements."""
        code = """def warning_function():
    line1 = 1
    line2 = 2
    line3 = 3
    return line1 + line2 + line3

def error_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    return sum([line1, line2, line3, line4, line5, line6])

class WarningClass:
    def method(self):
        return 1
    def method2(self):
        return 2

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

        config = LengthCheckerConfig(max_function_length=3, max_class_length=4)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 4

        for line, col, message, violation_type in violations:
            # All messages should contain these elements
            assert "statements long" in message
            assert "threshold" in message
            assert "recommend refactoring" in message

            # Check specific format based on type
            if violation_type in ["WL001", "WL002"]:
                assert "warning threshold" in message
            elif violation_type in ["EL001", "EL002"]:
                assert "error threshold" in message
