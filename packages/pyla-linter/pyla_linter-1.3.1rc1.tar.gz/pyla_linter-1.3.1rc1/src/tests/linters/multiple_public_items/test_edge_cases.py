"""Comprehensive edge case tests for multiple public items plugin."""

import ast
from typing import List, Tuple

from src.linters.multiple_public_items.plugin import MultiplePublicItemsPlugin


def run_plugin_on_code(code: str, filename: str = "test.py") -> List[Tuple[int, int, str, str]]:
    """Helper function to run the plugin on code and return error tuples."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    plugin = MultiplePublicItemsPlugin(tree, filename)
    return list(plugin.run())


class TestEmptyFiles:
    """Test edge cases with empty files."""

    def test_completely_empty_file(self):
        """Test that completely empty files produce no violations."""
        code = ""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_file_with_only_whitespace(self):
        """Test that files with only whitespace produce no violations."""
        code = "   \n\n\t  \n  "
        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_file_with_only_comments(self):
        """Test that files with only comments produce no violations."""
        code = """
# This is a comment
# Another comment
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_file_with_only_docstring(self):
        """Test that files with only module docstring produce no violations."""
        code = '''"""This is a module docstring."""'''
        errors = run_plugin_on_code(code)
        assert len(errors) == 0


class TestPrivateItemsOnly:
    """Test edge cases with only private functions/classes."""

    def test_file_with_only_private_functions(self):
        """Test that files with only private functions produce no violations."""
        code = """
def _private_function():
    return 42

def __double_underscore_function():
    return 24
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_file_with_only_private_classes(self):
        """Test that files with only private classes produce no violations."""
        code = """
class _PrivateClass:
    def method(self):
        pass

class __DoubleUnderscoreClass:
    def method(self):
        pass
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_file_with_mixed_private_items(self):
        """Test that files with mixed private items produce no violations."""
        code = """
def _private_function():
    return 42

class _PrivateClass:
    def method(self):
        pass

def __another_private_function():
    return 24
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0


class TestNestedClasses:
    """Test edge cases with nested classes and functions."""

    def test_nested_classes_not_counted(self):
        """Test that nested classes are not counted as public items."""
        code = """
class OuterClass:
    class InnerClass:
        def method(self):
            pass

    def method(self):
        pass
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_nested_functions_not_counted(self):
        """Test that nested functions are not counted as public items."""
        code = """
def outer_function():
    def inner_function():
        return 42

    class LocalClass:
        def method(self):
            pass

    return inner_function()
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_deeply_nested_items_not_counted(self):
        """Test that deeply nested items are not counted."""
        code = """
class Level1:
    class Level2:
        class Level3:
            def method(self):
                def level4_function():
                    return 42
                return level4_function()
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_mixed_public_and_nested_items(self):
        """Test that only top-level public items are counted."""
        code = """
def public_function():
    def nested_function():
        return 42
    return nested_function()

class PublicClass:
    class NestedClass:
        def method(self):
            pass

    def method(self):
        pass
"""
        # Should produce violation because we have 2 public items at module level
        errors = run_plugin_on_code(code)
        assert len(errors) == 1
        assert "EL101" in errors[0][2]
        assert "public_function" in errors[0][2]
        assert "PublicClass" in errors[0][2]


class TestSpecialMethods:
    """Test edge cases with special methods and magic methods."""

    def test_magic_methods_not_counted(self):
        """Test that magic methods are not counted as public items."""
        code = """
def __init__(self):
    pass

def __str__(self):
    return "test"

def __repr__(self):
    return "test"
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_dunder_methods_not_counted(self):
        """Test that dunder methods are not counted as public items."""
        code = """
def __name__():
    pass

def __file__():
    pass

def __all__():
    pass
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0


class TestImportsAndConstants:
    """Test edge cases with imports and constants."""

    def test_imports_not_counted(self):
        """Test that imports are not counted as public items."""
        code = """
import os
from typing import List
import ast as ast_module

def public_function():
    return 42
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_constants_not_counted(self):
        """Test that constants are not counted as public items."""
        code = """
CONSTANT = 42
ANOTHER_CONSTANT = "hello"
_PRIVATE_CONSTANT = "private"

def public_function():
    return CONSTANT
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_all_declaration_not_counted(self):
        """Test that __all__ declaration is not counted as public item."""
        code = """
__all__ = ['public_function']

def public_function():
    return 42

def _private_function():
    return 24
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0


class TestComplexStructures:
    """Test edge cases with complex code structures."""

    def test_decorators_not_affecting_detection(self):
        """Test that decorators don't affect public item detection."""
        code = """
@property
def decorated_function():
    return 42

@staticmethod
@classmethod
def multi_decorated_function():
    return 24
"""
        # Should produce violation because we have 2 public functions
        errors = run_plugin_on_code(code)
        assert len(errors) == 1
        assert "EL101" in errors[0][2]

    def test_async_functions_detected(self):
        """Test that async functions are properly detected."""
        code = """
async def async_function():
    return 42

def sync_function():
    return 24
"""
        # Should produce violation because we have 2 public functions
        errors = run_plugin_on_code(code)
        assert len(errors) == 1
        assert "EL101" in errors[0][2]
        assert "async_function" in errors[0][2]
        assert "sync_function" in errors[0][2]

    def test_with_statements_not_counted(self):
        """Test that with statements are not counted as public items."""
        code = """
def public_function():
    with open("file.txt") as f:
        return f.read()
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_try_except_not_counted(self):
        """Test that try/except blocks are not counted as public items."""
        code = """
def public_function():
    try:
        return 42
    except Exception:
        return 0
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0


class TestSyntaxErrors:
    """Test plugin behavior with syntax errors."""

    def test_syntax_error_handling(self):
        """Test that syntax errors are handled gracefully."""
        code = """
def invalid_syntax(
    # Missing closing parenthesis
    return 42
"""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0  # Should not crash, just return no errors

    def test_invalid_ast_handling(self):
        """Test handling of invalid AST structures."""
        # Create a plugin with empty AST
        empty_tree = ast.parse("")
        plugin = MultiplePublicItemsPlugin(empty_tree, "test.py")
        errors = list(plugin.run())
        assert len(errors) == 0  # Should handle gracefully
