"""Tests for error generation functionality in the length checker."""

from src.linters.length_checker.config import LengthCheckerConfig

from .test_utils import run_plugin_on_code


class TestErrorGeneration:
    """Test error generation at 2x threshold."""

    def test_function_error_at_2x_threshold(self):
        """Test that functions generate errors when exceeding 2x threshold."""
        code = """def error_function():
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
    return sum([line1, line2, line3, line4, line5, line6, line7, line8, line9, line10, line11])"""

        # Set threshold at 5, function has 13 lines (> 10 which is 2x threshold)
        config = LengthCheckerConfig(max_function_length=5, max_class_length=50)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 1

        line, col, message, violation_type = violations[0]
        assert violation_type == "EL001"
        assert "EL001" in message
        assert "error_function" in message
        assert "error threshold" in message
        assert "recommend refactoring" in message

    def test_class_error_at_2x_threshold(self):
        """Test that classes generate errors when exceeding 2x threshold."""
        code = """class ErrorClass:
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
        return 9
    def method10(self):
        return 10
    def method11(self):
        return 11"""

        # Set threshold at 8, class has 17 lines (> 16 which is 2x threshold)
        config = LengthCheckerConfig(max_function_length=50, max_class_length=8)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 1

        line, col, message, violation_type = violations[0]
        assert violation_type == "EL002"
        assert "EL002" in message
        assert "ErrorClass" in message
        assert "error threshold" in message
        assert "recommend refactoring" in message

    def test_function_error_message_format(self):
        """Test that function error messages follow correct format."""
        code = """def test_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    line8 = 8
    line9 = 9
    return sum([line1, line2, line3, line4, line5, line6, line7, line8, line9])"""

        config = LengthCheckerConfig(max_function_length=4)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 1

        line, col, message, violation_type = violations[0]
        assert line == 1  # Error reported on function definition line
        assert col == 0
        assert violation_type == "EL001"
        assert message.startswith("EL001")
        assert "test_function" in message
        assert "11 statements long" in message
        assert "exceeds error threshold of 8" in message  # 2x threshold
        assert "recommend refactoring" in message

    def test_class_error_message_format(self):
        """Test that class error messages follow correct format."""
        code = """class TestClass:
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
        return 9
    def method10(self):
        return 10
    def method11(self):
        return 11"""

        config = LengthCheckerConfig(max_class_length=5)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 1

        line, col, message, violation_type = violations[0]
        assert line == 1  # Error reported on class definition line
        assert col == 0
        assert violation_type == "EL002"
        assert message.startswith("EL002")
        assert "TestClass" in message
        assert "23 statements long" in message
        assert "exceeds error threshold of 10" in message  # 2x threshold
        assert "recommend refactoring" in message

    def test_multiple_function_errors(self):
        """Test multiple functions generating errors."""
        code = """def first_error_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    return sum([line1, line2, line3, line4, line5, line6, line7])

def second_error_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    return sum([line1, line2, line3, line4, line5, line6, line7])"""

        config = LengthCheckerConfig(max_function_length=3)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 2

        # Both should be errors (8 lines > 6 which is 2x threshold)
        for violation in violations:
            line, col, message, violation_type = violation
            assert violation_type == "EL001"
            assert "error threshold" in message

    def test_multiple_class_errors(self):
        """Test multiple classes generating errors."""
        code = """class FirstErrorClass:
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

class SecondErrorClass:
    def method1(self):
        return 1
    def method2(self):
        return 2
    def method3(self):
        return 3
    def method4(self):
        return 4
    def method5(self):
        return 5"""

        config = LengthCheckerConfig(max_class_length=4)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 2

        # Both should be errors (9 lines > 8 which is 2x threshold)
        for violation in violations:
            line, col, message, violation_type = violation
            assert violation_type == "EL002"
            assert "error threshold" in message
