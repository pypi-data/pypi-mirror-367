"""Tests for malformed AST edge cases in the length checker."""

from .test_utils import run_plugin_on_code


class TestMalformedASTEdgeCases:
    """Test edge cases for malformed AST nodes and syntax errors."""

    def test_incomplete_function_definition(self):
        """Test handling of incomplete function definitions."""
        malformed_codes = [
            "def incomplete_func(",  # Missing closing paren
            "def func():",  # Missing body
            "def func(): ...",  # Valid but minimal
            "def func(a, b,):",  # Trailing comma (valid)
        ]

        for code in malformed_codes:
            errors = run_plugin_on_code(code)
            # Should handle gracefully without crashing
            assert isinstance(errors, list)

    def test_incomplete_class_definition(self):
        """Test handling of incomplete class definitions."""
        malformed_codes = [
            "class IncompleteClass(",  # Missing closing paren
            "class Class():",  # Missing body
            "class Class(): ...",  # Valid but minimal
        ]

        for code in malformed_codes:
            errors = run_plugin_on_code(code)
            # Should handle gracefully without crashing
            assert isinstance(errors, list)

    def test_invalid_indentation_handling(self):
        """Test handling of invalid indentation."""
        malformed_codes = [
            "def func():\n    x = 1\n  y = 2",  # Inconsistent indentation
            "def func():\nx = 1",  # Missing indentation
            "def func():\n        x = 1\n    y = 2",  # Mixed indentation levels
        ]

        for code in malformed_codes:
            errors = run_plugin_on_code(code)
            # Should handle gracefully - either parse successfully or return empty
            assert isinstance(errors, list)

    def test_unicode_and_encoding_edge_cases(self):
        """Test handling of unicode characters and encoding issues."""
        unicode_codes = [
            "def café(): return 'unicode'",  # Unicode in function name
            "def func(): return 'emoji 🚀'",  # Unicode in string
            "def func(): # Comment with ñ",  # Unicode in comment
        ]

        for code in unicode_codes:
            errors = run_plugin_on_code(code)
            # Should handle unicode gracefully
            assert isinstance(errors, list)

    def test_very_long_lines_handling(self):
        """Test handling of extremely long lines."""
        # Create a function with a very long line
        long_string = "'" + "x" * 1000 + "'"
        code = f"""def long_line_func():
    very_long_var = {long_string}
    return very_long_var"""

        errors = run_plugin_on_code(code)
        # Should handle long lines without issues
        assert isinstance(errors, list)

    def test_deeply_nested_structures(self):
        """Test handling of deeply nested code structures."""
        # Create deeply nested if statements
        nested_ifs = ""
        for i in range(20):
            nested_ifs += "    " * (i + 1) + f"if condition_{i}:\n"
        nested_ifs += "    " * 21 + "result = 'deep'"

        code = f"""def deeply_nested():
{nested_ifs}
    return result"""

        errors = run_plugin_on_code(code)
        # Should handle deep nesting without stack overflow
        assert isinstance(errors, list)
