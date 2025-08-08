"""Comprehensive unit tests for the multiple public items plugin."""

import ast
from typing import List, Tuple

from src.linters.multiple_public_items.ast_visitor import PublicItemsVisitor
from src.linters.multiple_public_items.plugin import MultiplePublicItemsPlugin


def run_plugin_on_code(code: str, filename: str = "test.py") -> List[Tuple[int, int, str, str]]:
    """Helper function to run the flake8 plugin on code and return error tuples."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []  # Return empty list for syntax errors, matching plugin behavior

    plugin = MultiplePublicItemsPlugin(tree, filename)
    return list(plugin.run())


class TestPluginInitialization:
    """Test the plugin initialization and basic functionality."""

    def test_plugin_initialization(self):
        """Test plugin initializes correctly."""
        tree = ast.parse("def test(): pass")
        plugin = MultiplePublicItemsPlugin(tree, "test.py")
        assert plugin.name == "multiple_public_items"
        assert plugin.version == "1.0.0"
        assert plugin.tree is tree
        assert plugin.filename == "test.py"

    def test_plugin_with_default_filename(self):
        """Test plugin works with default filename."""
        tree = ast.parse("def test(): pass")
        plugin = MultiplePublicItemsPlugin(tree)
        assert plugin.filename == "<stdin>"


class TestNoViolations:
    """Test cases that should not produce violations."""

    def test_empty_file_no_violations(self):
        """Test that empty files produce no violations."""
        code = ""
        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_single_public_function_no_violations(self):
        """Test that single public function produces no violations."""
        code = """def public_function():
    return 42"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_single_public_class_no_violations(self):
        """Test that single public class produces no violations."""
        code = """class PublicClass:
    def method(self):
        pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_single_async_function_no_violations(self):
        """Test that single async function produces no violations."""
        code = """async def async_function():
    await something()"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_only_private_items_no_violations(self):
        """Test that files with only private items produce no violations."""
        code = """def _private_function():
    return 42

class _PrivateClass:
    def method(self):
        pass

async def _private_async():
    await something()"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_imports_and_constants_no_violations(self):
        """Test that imports and constants don't count as public items."""
        code = """import os
from typing import List

CONSTANT = 42
_PRIVATE_CONSTANT = "private"

def public_function():
    return CONSTANT"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_nested_items_no_violations(self):
        """Test that nested classes and functions don't count as violations."""
        code = """class PublicClass:
    def method(self):
        def nested_function():
            return 42

        class NestedClass:
            pass

        return nested_function()"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 0


class TestViolationDetection:
    """Test cases that should produce violations."""

    def test_two_public_functions_violation(self):
        """Test that two public functions produce a violation."""
        code = """def first_function():
    return 1

def second_function():
    return 2"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1

        line, col, message, error_code = errors[0]
        assert error_code == "EL101"
        assert "2 public items" in message
        assert "first_function" in message
        assert "second_function" in message

    def test_two_public_classes_violation(self):
        """Test that two public classes produce a violation."""
        code = """class FirstClass:
    pass

class SecondClass:
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1

        line, col, message, error_code = errors[0]
        assert error_code == "EL101"
        assert "2 public items" in message
        assert "FirstClass" in message
        assert "SecondClass" in message

    def test_mixed_class_and_function_violation(self):
        """Test that a class and function together produce a violation."""
        code = """def public_function():
    return 42

class PublicClass:
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1

        line, col, message, error_code = errors[0]
        assert error_code == "EL101"
        assert "2 public items" in message
        assert "function 'public_function'" in message
        assert "class 'PublicClass'" in message

    def test_async_function_and_regular_function_violation(self):
        """Test that async and regular functions together produce a violation."""
        code = """def regular_function():
    return 42

async def async_function():
    await something()"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1

        line, col, message, error_code = errors[0]
        assert error_code == "EL101"
        assert "2 public items" in message
        assert "regular_function" in message
        assert "async_function" in message

    def test_multiple_public_items_violation(self):
        """Test that multiple public items produce a violation."""
        code = """def first_function():
    return 1

class FirstClass:
    pass

def second_function():
    return 2

async def async_function():
    await something()

class SecondClass:
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1

        line, col, message, error_code = errors[0]
        assert error_code == "EL101"
        assert "5 public items" in message
        assert "first_function" in message
        assert "FirstClass" in message
        assert "second_function" in message
        assert "async_function" in message
        assert "SecondClass" in message


class TestErrorMessageFormat:
    """Test error message format and content."""

    def test_error_message_contains_required_elements(self):
        """Test that error messages contain all required elements."""
        code = """def func1():
    pass

def func2():
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1

        line, col, message, error_code = errors[0]
        assert error_code == "EL101"
        assert message.startswith("EL101")
        assert "2 public items" in message
        assert "Only one public item per file is allowed" in message

    def test_error_message_line_numbers_included(self):
        """Test that error messages include line numbers for each item."""
        code = """def first_function():
    pass

class SomeClass:
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1

        line, col, message, error_code = errors[0]
        assert "line 1" in message  # first_function is on line 1
        assert "line 4" in message  # SomeClass is on line 4 (after empty line)

    def test_error_reported_at_first_public_item_line(self):
        """Test that error is reported at the line of the first public item."""
        code = """# Comment
# Another comment

def first_function():
    pass

def second_function():
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1

        line, col, message, error_code = errors[0]
        assert line == 4  # first_function is on line 4
        assert col == 0

    def test_error_message_sorted_by_line_number(self):
        """Test that items in error message are sorted by line number."""
        code = """def second_function():
    pass

def first_function():
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1

        line, col, message, error_code = errors[0]
        # Message should list items in line order (second_function line 1, first_function line 4)
        # So second_function should appear first in the message
        first_pos = message.find("first_function")
        second_pos = message.find("second_function")
        assert second_pos < first_pos  # second_function appears first because it's on line 1

    def test_error_message_item_type_labels(self):
        """Test that error message includes correct item type labels."""
        code = """async def async_func():
    await something()

class MyClass:
    pass

def regular_func():
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1

        line, col, message, error_code = errors[0]
        assert "function 'async_func'" in message
        assert "class 'MyClass'" in message
        assert "function 'regular_func'" in message


class TestPrivateItemFiltering:
    """Test that private items are properly filtered out."""

    def test_private_function_ignored(self):
        """Test that private functions don't count as public items."""
        code = """def public_function():
    return 1

def _private_function():
    return 2"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_private_class_ignored(self):
        """Test that private classes don't count as public items."""
        code = """class PublicClass:
    pass

class _PrivateClass:
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 0

    def test_mixed_private_and_public_items(self):
        """Test that only public items are counted in violations."""
        code = """def public_function():
    return 1

def _private_function():
    return 2

class PublicClass:
    pass

class _PrivateClass:
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1

        line, col, message, error_code = errors[0]
        assert "2 public items" in message
        assert "public_function" in message
        assert "PublicClass" in message
        assert "_private_function" not in message
        assert "_PrivateClass" not in message

    def test_dunder_methods_ignored(self):
        """Test that dunder methods/classes are considered private."""
        code = """def public_function():
    return 1

def __dunder_function__():
    return 2

class __DunderClass__:
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 0


class TestNestedItemFiltering:
    """Test that nested items are properly filtered out."""

    def test_nested_function_ignored(self):
        """Test that nested functions don't count as public items."""
        code = """def outer_function():
    def inner_function():
        return 42
    return inner_function()

def another_function():
    return 1"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1

        line, col, message, error_code = errors[0]
        assert "2 public items" in message
        assert "outer_function" in message
        assert "another_function" in message
        assert "inner_function" not in message

    def test_nested_class_ignored(self):
        """Test that nested classes don't count as public items."""
        code = """class OuterClass:
    class InnerClass:
        pass

    def method(self):
        pass

class AnotherClass:
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1

        line, col, message, error_code = errors[0]
        assert "2 public items" in message
        assert "OuterClass" in message
        assert "AnotherClass" in message
        assert "InnerClass" not in message

    def test_method_in_class_ignored(self):
        """Test that methods inside classes don't count as separate public items."""
        code = """class MyClass:
    def public_method(self):
        pass

    def another_method(self):
        pass

    def _private_method(self):
        pass

def standalone_function():
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1

        line, col, message, error_code = errors[0]
        assert "2 public items" in message
        assert "MyClass" in message
        assert "standalone_function" in message
        assert "public_method" not in message
        assert "another_method" not in message


class TestEdgeCases:
    """Test edge cases and corner scenarios."""

    def test_syntax_error_handling(self):
        """Test that syntax errors are handled gracefully."""
        code = """def broken_function(
    # Missing closing parenthesis
    return 42"""

        errors = run_plugin_on_code(code)
        assert errors == []  # Should return empty list, not crash

    def test_empty_function_body(self):
        """Test functions with empty bodies."""
        code = """def empty_function():
    pass

def another_empty():
    ..."""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1
        assert "2 public items" in errors[0][2]

    def test_decorators_on_functions(self):
        """Test that decorators don't affect public item detection."""
        code = """@decorator
def decorated_function():
    pass

@another_decorator
@multiple_decorators
def multi_decorated():
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1
        assert "2 public items" in errors[0][2]

    def test_decorators_on_classes(self):
        """Test that decorators don't affect public class detection."""
        code = """@dataclass
class DecoratedClass:
    pass

@decorator
class AnotherClass:
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1
        assert "2 public items" in errors[0][2]

    def test_lambda_functions_ignored(self):
        """Test that lambda functions are not counted as public items."""
        code = """def regular_function():
    lambda_func = lambda x: x * 2
    return lambda_func(5)

# Module level lambda - should also be ignored
module_lambda = lambda x: x + 1

def another_function():
    return 42"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1
        assert "2 public items" in errors[0][2]
        assert "regular_function" in errors[0][2]
        assert "another_function" in errors[0][2]

    def test_generator_functions(self):
        """Test that generator functions are counted as public items."""
        code = """def generator_function():
    yield 1
    yield 2

def regular_function():
    return 42"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1
        assert "2 public items" in errors[0][2]

    def test_property_methods(self):
        """Test that property methods inside classes don't count separately."""
        code = """class PropertyClass:
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

def standalone_function():
    pass"""

        errors = run_plugin_on_code(code)
        assert len(errors) == 1
        assert "2 public items" in errors[0][2]


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_realistic_module_structure(self):
        """Test a realistic module with mixed content."""
        code = '''"""Module docstring."""

import os
from typing import List

# Constants
DEFAULT_VALUE = 42
_PRIVATE_CONSTANT = "internal"

def public_utility_function(data: List[str]) -> str:
    """A public utility function."""
    def _internal_helper(item: str) -> str:
        return item.upper()

    return ", ".join(_internal_helper(item) for item in data)

class PublicDataProcessor:
    """A public data processing class."""

    def __init__(self, config: dict):
        self.config = config

    def process(self, data: List[str]) -> List[str]:
        """Process the data."""
        return [item.strip() for item in data]

    def _validate(self, data: List[str]) -> bool:
        """Private validation method."""
        return all(isinstance(item, str) for item in data)

def _private_helper_function():
    """A private helper function."""
    pass'''

        errors = run_plugin_on_code(code)
        assert len(errors) == 1
        assert "2 public items" in errors[0][2]
        assert "public_utility_function" in errors[0][2]
        assert "PublicDataProcessor" in errors[0][2]

    def test_file_with_main_guard(self):
        """Test file with if __name__ == '__main__' guard."""
        code = '''def main_function():
    """Main function."""
    print("Hello, world!")

class UtilityClass:
    """Utility class."""
    pass

if __name__ == "__main__":
    main_function()'''

        errors = run_plugin_on_code(code)
        assert len(errors) == 1
        assert "2 public items" in errors[0][2]

    def test_file_with_only_main_function(self):
        """Test file with only a main function."""
        code = '''def main():
    """Main entry point."""
    pass

if __name__ == "__main__":
    main()'''

        errors = run_plugin_on_code(code)
        assert len(errors) == 0  # Only one public item

    def test_abstract_base_class_scenario(self):
        """Test abstract base class with multiple inheritance."""
        code = '''from abc import ABC, abstractmethod

class AbstractProcessor(ABC):
    """Abstract base class for processors."""

    @abstractmethod
    def process(self, data):
        """Process the data."""
        pass

class ConcreteProcessor(AbstractProcessor):
    """Concrete implementation of processor."""

    def process(self, data):
        """Process the data concretely."""
        return data.upper()'''

        errors = run_plugin_on_code(code)
        assert len(errors) == 1
        assert "2 public items" in errors[0][2]


class TestASTVisitorIntegration:
    """Test integration with the AST visitor."""

    def test_visitor_integration(self):
        """Test that plugin correctly uses AST visitor."""
        code = """def func1():
    pass

class Class1:
    pass

def func2():
    pass"""

        # Test that plugin creates and uses visitor correctly
        tree = ast.parse(code)
        plugin = MultiplePublicItemsPlugin(tree, "test.py")

        # Plugin should use visitor internally
        errors = list(plugin.run())
        assert len(errors) == 1

        # Verify the visitor would find the same items
        visitor = PublicItemsVisitor()
        visitor.visit(tree)
        public_items = visitor.get_public_items()

        assert len(public_items) == 3
        assert public_items[0].name == "func1"
        assert public_items[1].name == "Class1"
        assert public_items[2].name == "func2"

    def test_empty_visitor_result(self):
        """Test plugin behavior when visitor finds no public items."""
        code = """# Just comments
_private_var = 42"""

        tree = ast.parse(code)
        plugin = MultiplePublicItemsPlugin(tree, "test.py")
        errors = list(plugin.run())

        assert len(errors) == 0

    def test_visitor_exception_handling(self):
        """Test that plugin handles visitor exceptions gracefully."""
        # Test with malformed AST (this is more of a theoretical test)
        tree = ast.parse("def test(): pass")
        plugin = MultiplePublicItemsPlugin(tree, "test.py")

        # Should not raise exceptions
        errors = list(plugin.run())
        assert isinstance(errors, list)


class TestFilenameHandling:
    """Test filename parameter handling."""

    def test_different_filenames(self):
        """Test that plugin works with different filename parameters."""
        code = """def func1():
    pass

def func2():
    pass"""

        # Test various filename formats
        filenames = [
            "test.py",
            "module/test.py",
            "/absolute/path/test.py",
            "test_module.py",
            "<stdin>",
            "temp_file.py",
        ]

        for filename in filenames:
            errors = run_plugin_on_code(code, filename)
            assert len(errors) == 1
            assert "2 public items" in errors[0][2]

    def test_filename_in_error_context(self):
        """Test that filename doesn't affect error detection."""
        code = """def only_function():
    pass"""

        errors1 = run_plugin_on_code(code, "file1.py")
        errors2 = run_plugin_on_code(code, "file2.py")

        # Both should have no errors (single public item)
        assert len(errors1) == 0
        assert len(errors2) == 0
