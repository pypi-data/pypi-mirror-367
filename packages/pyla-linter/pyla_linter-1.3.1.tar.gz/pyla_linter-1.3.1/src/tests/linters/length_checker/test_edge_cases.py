"""Tests for edge cases and corner scenarios in the length checker."""

import ast

from src.linters.length_checker.ast_visitor import ASTVisitor
from src.linters.length_checker.config import LengthCheckerConfig

from .test_utils import run_plugin_on_code


class TestEdgeCases:  # noqa: WL002
    """Test edge cases and corner scenarios."""

    def test_lambda_functions_not_counted(self):
        """Test that lambda functions are not counted as regular functions."""
        code = """def regular_function():
    lambda_func = lambda x: x * 2
    return lambda_func(5)"""

        visitor = ASTVisitor()

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        # Should only find the regular function, not the lambda
        assert len(elements) == 1
        assert elements[0].name == "regular_function"

    def test_empty_class(self):
        """Test handling of empty class."""
        code = """class EmptyClass:
    pass"""

        config = LengthCheckerConfig(max_class_length=1)

        errors = run_plugin_on_code(code, config)
        # Should have 1 violation (2 lines > 1 limit)
        assert len(errors) == 1

    def test_empty_function(self):
        """Test handling of empty function."""
        code = """def empty_function():
    pass"""

        config = LengthCheckerConfig(max_function_length=1)

        errors = run_plugin_on_code(code, config)
        # Should have 1 violation (2 lines > 1 limit)
        assert len(errors) == 1

    def test_decorator_handling(self):
        """Test that decorators are included in function line count."""
        code = """@decorator1
@decorator2
def decorated_function():
    return 42"""

        visitor = ASTVisitor()

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        assert len(elements) == 1
        # Decorators should be included in the line range
        assert elements[0].start_line == 1  # Starts at first decorator
        assert elements[0].end_line == 4

    def test_multiple_decorators_on_class(self):
        """Test that decorators are included in class line count."""
        code = """@dataclass
@decorator2
class DecoratedClass:
    def method(self):
        return 42"""

        visitor = ASTVisitor()

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        class_element = next(e for e in elements if e.node_type == "class")
        # Decorators should be included in the class line range
        assert class_element.start_line == 1  # Starts at first decorator
        assert class_element.end_line == 5

    def test_property_decorators(self):
        """Test handling of property decorators."""
        code = """class TestClass:
    @property
    def prop(self):
        return self._value

    @prop.setter
    def prop(self, value):
        self._value = value"""

        visitor = ASTVisitor()

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        # Should find class and both property methods
        assert len(elements) == 3
        prop_methods = [e for e in elements if e.node_type == "function"]
        assert len(prop_methods) == 2

    def test_nested_decorators(self):
        """Test handling of nested functions with decorators."""
        code = """def outer():
    @decorator
    def inner():
        return 42
    return inner"""

        visitor = ASTVisitor()

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        assert len(elements) == 2  # outer and inner functions
        inner_func = next(e for e in elements if e.name == "inner")
        # Decorator should be included in inner function range
        assert inner_func.start_line == 2  # Starts at decorator line

    def test_class_with_only_pass(self):
        """Test empty class with only pass statement."""
        code = """class EmptyClass:
    pass"""

        config = LengthCheckerConfig(max_class_length=1)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1
        _, _, message, _ = errors[0]
        assert "2 statements long" in message

    def test_function_with_only_ellipsis(self):
        """Test function with only ellipsis (...)."""
        code = """def placeholder_function():
    ..."""

        config = LengthCheckerConfig(max_function_length=1)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1
        line, col, message, error_type = errors[0]
        assert "2 statements long" in message

    def test_class_with_class_variables(self):
        """Test class with only class variables."""
        code = """class ConfigClass:
    CONSTANT1 = "value1"
    CONSTANT2 = "value2"
    CONSTANT3 = "value3\""""

        config = LengthCheckerConfig(max_class_length=3)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1  # 4 lines > 3 limit

    def test_generator_function(self):
        """Test generator functions are counted normally."""
        code = """def generator_function():
    yield 1
    yield 2
    yield 3"""

        visitor = ASTVisitor()

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        assert len(elements) == 1
        assert elements[0].name == "generator_function"
        assert elements[0].node_type == "function"

    def test_comprehensions_not_counted_as_functions(self):
        """Test that comprehensions are not counted as separate functions."""
        code = """def test_function():
    list_comp = [x for x in range(10) if x > 5]
    dict_comp = {x: x*2 for x in range(5)}
    set_comp = {x for x in range(10)}
    return list_comp, dict_comp, set_comp"""

        visitor = ASTVisitor()

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        # Should only find the main function, not the comprehensions
        assert len(elements) == 1
        assert elements[0].name == "test_function"

    def test_lambda_in_decorator(self):
        """Test lambda functions in decorators are not counted."""
        code = """@lambda_decorator(lambda x: x * 2)
def decorated_function():
    return 42"""

        visitor = ASTVisitor()

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        # Should only find the decorated function, not the lambda
        assert len(elements) == 1
        assert elements[0].name == "decorated_function"

    def test_method_with_complex_signature(self):
        """Test methods with complex signatures including annotations."""
        code = '''class ComplexClass:
    def complex_method(
        self,
        param1: str,
        param2: int = 42,
        *args: tuple,
        **kwargs: dict
    ) -> bool:
        """Method with complex signature."""
        return True'''

        visitor = ASTVisitor()

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        assert len(elements) == 2  # class and method
        method_element = next(e for e in elements if e.node_type == "function")
        assert method_element.name == "complex_method"

    def test_metaclass_definition(self):
        """Test metaclass definitions are counted properly."""
        code = """class MetaClass(type):
    def __new__(cls, name, bases, attrs):
        return super().__new__(cls, name, bases, attrs)

class UsingMeta(metaclass=MetaClass):
    pass"""

        visitor = ASTVisitor()

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        # Should find MetaClass, __new__ method, and UsingMeta
        assert len(elements) == 3
        class_names = [e.name for e in elements if e.node_type == "class"]
        assert "MetaClass" in class_names
        assert "UsingMeta" in class_names

    def test_try_except_finally_blocks(self):
        """Test functions with try/except/finally blocks."""
        code = """def error_handling_function():
    try:
        risky_operation()
    except ValueError as e:
        handle_value_error(e)
    except Exception:
        handle_generic_error()
    finally:
        cleanup()
    return True"""

        config = LengthCheckerConfig(max_function_length=5)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1  # Function should exceed 5 lines

    def test_context_manager_function(self):
        """Test functions using context managers."""
        code = """def context_function():
    with open('file.txt') as f:
        content = f.read()
    with another_context():
        process_data()
    return content"""

        visitor = ASTVisitor()

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        assert len(elements) == 1
        assert elements[0].name == "context_function"
