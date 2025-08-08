"""Tests for warning generation functionality in the length checker."""

from src.linters.length_checker.config import LengthCheckerConfig

from .test_utils import run_plugin_on_code


class TestWarningGeneration:
    """Test the new warning generation functionality."""

    def test_function_warning_at_1x_threshold(self):
        """Test that functions generate warnings when exceeding 1x threshold but under 2x."""
        code = """def warning_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    return line1 + line2 + line3 + line4 + line5"""

        # Set threshold at 5, function has 7 lines (> 5 but < 10)
        config = LengthCheckerConfig(max_function_length=5, max_class_length=50)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 1

        line, col, message, violation_type = violations[0]
        assert violation_type == "WL001"
        assert "WL001" in message
        assert "warning_function" in message
        assert "warning threshold" in message
        assert "recommend refactoring" in message

    def test_class_warning_at_1x_threshold(self):
        """Test that classes generate warnings when exceeding 1x threshold but under 2x."""
        code = """class WarningClass:
    def method1(self):
        return 1

    def method2(self):
        return 2

    def method3(self):
        return 3

    def method4(self):
        return 4"""

        # Set threshold at 8, class has 11 lines (> 8 but < 16)
        config = LengthCheckerConfig(max_function_length=50, max_class_length=8)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 1

        line, col, message, violation_type = violations[0]
        assert violation_type == "WL002"
        assert "WL002" in message
        assert "WarningClass" in message
        assert "warning threshold" in message
        assert "recommend refactoring" in message

    def test_function_warning_message_format(self):
        """Test that function warning messages follow correct format."""
        code = """def test_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    return line1 + line2 + line3 + line4"""

        config = LengthCheckerConfig(max_function_length=4)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 1

        line, col, message, violation_type = violations[0]
        assert line == 1  # Warning reported on function definition line
        assert col == 0
        assert violation_type == "WL001"
        assert message.startswith("WL001")
        assert "test_function" in message
        assert "6 statements long" in message
        assert "exceeds warning threshold of 4" in message
        assert "recommend refactoring" in message

    def test_class_warning_message_format(self):
        """Test that class warning messages follow correct format."""
        code = """class TestClass:
    def method1(self):
        return 1
    def method2(self):
        return 2
    def method3(self):
        return 3"""

        config = LengthCheckerConfig(max_class_length=5)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 1

        line, col, message, violation_type = violations[0]
        assert line == 1  # Warning reported on class definition line
        assert col == 0
        assert violation_type == "WL002"
        assert message.startswith("WL002")
        assert "TestClass" in message
        assert "7 statements long" in message
        assert "exceeds warning threshold of 5" in message
        assert "recommend refactoring" in message

    def test_multiple_function_warnings(self):
        """Test multiple functions generating warnings."""
        code = """def first_warning_function():
    line1 = 1
    line2 = 2
    line3 = 3
    return line1 + line2 + line3

def second_warning_function():
    line1 = 1
    line2 = 2
    line3 = 3
    return line1 + line2 + line3"""

        config = LengthCheckerConfig(max_function_length=3)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 2

        # Both should be warnings (5 lines > 3 but < 6)
        for violation in violations:
            line, col, message, violation_type = violation
            assert violation_type == "WL001"
            assert "warning threshold" in message

    def test_multiple_class_warnings(self):
        """Test multiple classes generating warnings."""
        code = """class FirstWarningClass:
    def method1(self):
        return 1
    def method2(self):
        return 2

class SecondWarningClass:
    def method1(self):
        return 1
    def method2(self):
        return 2"""

        config = LengthCheckerConfig(max_class_length=4)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 2

        # Both should be warnings (5 lines > 4 but < 8)
        for violation in violations:
            line, col, message, violation_type = violation
            assert violation_type == "WL002"
            assert "warning threshold" in message
