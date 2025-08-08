"""Tests for ensuring no violations when code is under thresholds."""

from src.linters.length_checker.config import LengthCheckerConfig

from .test_utils import run_plugin_on_code


class TestNoViolationsUnderThreshold:
    """Test that no violations are generated when under 1x threshold."""

    def test_function_under_1x_threshold_no_violations(self):
        """Test that functions under 1x threshold generate no violations."""
        code = """def short_function():
    line1 = 1
    line2 = 2
    return line1 + line2"""

        # Set threshold at 5, function has 4 lines (< 5)
        config = LengthCheckerConfig(max_function_length=5, max_class_length=50)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 0

    def test_class_under_1x_threshold_no_violations(self):
        """Test that classes under 1x threshold generate no violations."""
        code = """class ShortClass:
    def method1(self):
        return 1
    def method2(self):
        return 2"""

        # Set threshold at 8, class has 5 lines (< 8)
        config = LengthCheckerConfig(max_function_length=50, max_class_length=8)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 0

    def test_function_exactly_at_1x_threshold_no_violations(self):
        """Test that functions exactly at 1x threshold generate no violations."""
        code = """def exact_threshold_function():
    line1 = 1
    line2 = 2
    line3 = 3
    return line1 + line2 + line3"""

        # Set threshold at 5, function has exactly 5 lines
        config = LengthCheckerConfig(max_function_length=5, max_class_length=50)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 0

    def test_class_exactly_at_1x_threshold_no_violations(self):
        """Test that classes exactly at 1x threshold generate no violations."""
        code = """class ExactThresholdClass:
    def method1(self):
        return 1
    def method2(self):
        return 2
    def method3(self):
        return 3"""

        # Set threshold at 7, class has exactly 7 lines
        config = LengthCheckerConfig(max_function_length=50, max_class_length=7)

        violations = run_plugin_on_code(code, config)
        assert len(violations) == 0
