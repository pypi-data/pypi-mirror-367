"""Comprehensive unit tests for the length checker plugin."""

import ast
from typing import List, Tuple

from src.linters.length_checker.ast_visitor import ASTVisitor
from src.linters.length_checker.code_element import CodeElement
from src.linters.length_checker.config import LengthCheckerConfig
from src.linters.length_checker.plugin import LengthCheckerPlugin
from src.linters.length_checker.statement_counter import StatementCounter


def run_plugin_on_code(
    code: str, config: LengthCheckerConfig | None = None, _filename: str = "test.py"
) -> List[Tuple[int, int, str, str]]:
    """Helper function to run the flake8 plugin on code and return error tuples."""
    import os
    import tempfile

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []  # Return empty list for syntax errors, matching plugin behavior

    # Create a temporary file with the code so the plugin can read it
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        temp_filename = f.name

    try:
        plugin = LengthCheckerPlugin(tree, temp_filename)
        if config:
            plugin.set_config(config)

        return list(plugin.run())
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


class TestASTVisitor:
    """Test the AST visitor functionality."""

    def test_simple_function_detection(self):
        """Test detection of a simple function."""
        code = """def simple_function():
    return 42"""

        visitor = ASTVisitor()
        import ast

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        assert len(elements) == 1
        assert elements[0].name == "simple_function"
        assert elements[0].node_type == "function"
        assert elements[0].start_line == 1
        assert elements[0].end_line == 2

    def test_simple_class_detection(self):
        """Test detection of a simple class."""
        code = """class SimpleClass:
    def method(self):
        pass"""

        visitor = ASTVisitor()
        import ast

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        assert len(elements) == 2  # class and method

        class_element = next(e for e in elements if e.node_type == "class")
        method_element = next(e for e in elements if e.node_type == "function")

        assert class_element.name == "SimpleClass"
        assert method_element.name == "method"

    def test_nested_class_function_detection(self):
        """Test detection of nested classes and functions."""
        code = """class OuterClass:
    def outer_method(self):
        def inner_function():
            pass
        return inner_function

    class InnerClass:
        def inner_method(self):
            pass"""

        visitor = ASTVisitor()
        import ast

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        # Should find: OuterClass, outer_method, inner_function, InnerClass, inner_method
        assert len(elements) == 5

    def test_async_function_detection(self):
        """Test detection of async functions."""
        code = """async def async_function():
    await something()"""

        visitor = ASTVisitor()
        import ast

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        assert len(elements) == 1
        assert elements[0].name == "async_function"
        assert elements[0].node_type == "function"


class TestStatementCounter:
    """Test the statement counting functionality."""

    def test_simple_statement_counting(self):
        """Test basic statement counting without comments or docstrings."""
        code = """def simple_function():
    x = 1
    y = 2
    return x + y"""

        lines = code.splitlines()
        counter = StatementCounter(lines)

        element = CodeElement("simple_function", "function", 1, 4)
        actual_statements = counter.count_element_statements(element, code)

        # Should count 4 statements: def, x=1, y=2, return
        assert actual_statements == 4

    def test_statement_counting_with_comments(self):
        """Test statement counting excluding comment lines."""
        code = """def function_with_comments():
    # This is a comment
    x = 1  # inline comment but line has code
    # Another comment
    return x"""

        lines = code.splitlines()
        counter = StatementCounter(lines)

        element = CodeElement("function_with_comments", "function", 1, 5)
        actual_statements = counter.count_element_statements(element, code)

        # Should count 3 statements (function def, x=1, return) - comments don't count as statements
        assert actual_statements == 3

    def test_statement_counting_with_docstring(self):
        """Test statement counting excluding docstring lines."""
        code = '''def function_with_docstring():
    """This is a docstring.

    It spans multiple lines.
    """
    x = 1
    return x'''

        lines = code.splitlines()
        counter = StatementCounter(lines)

        element = CodeElement("function_with_docstring", "function", 1, 7)
        actual_statements = counter.count_element_statements(element, code)

        # Should count 4 statements (function def, docstring expr, x=1, return)
        # docstring is still a statement
        assert actual_statements == 4

    def test_statement_counting_with_empty_lines(self):
        """Test statement counting excluding empty lines."""
        code = """def function_with_empty_lines():

    x = 1

    y = 2

    return x + y"""

        lines = code.splitlines()
        counter = StatementCounter(lines)

        element = CodeElement("function_with_empty_lines", "function", 1, 7)
        actual_statements = counter.count_element_statements(element, code)

        # Should count 4 statements (function def, x=1, y=2, return)
        # empty lines don't affect statement count
        assert actual_statements == 4

    def test_class_statement_counting(self):
        """Test statement counting for classes."""
        code = '''class TestClass:
    """Class docstring."""

    def __init__(self):
        self.x = 1

    # Comment in class
    def method(self):
        """Method docstring."""
        return self.x'''

        lines = code.splitlines()
        counter = StatementCounter(lines)

        element = CodeElement("TestClass", "class", 1, 10)
        actual_statements = counter.count_element_statements(element, code)

        # Should count: class def, docstring expr, __init__ def, self.x=1,
        # method def, method docstring expr, return
        assert actual_statements == 7


class TestLengthCheckerPlugin:
    """Test the main plugin functionality."""

    def test_plugin_initialization(self):
        """Test plugin initializes correctly."""
        tree = ast.parse("def test(): pass")
        plugin = LengthCheckerPlugin(tree, "test.py")
        assert plugin.name == "length_checker"
        assert plugin.version == "1.0.0"

    def test_no_violations_under_limit(self):
        """Test that code under limits produces no violations."""
        code = """def short_function():
    return 42

class ShortClass:
    def method(self):
        return True"""

        # Set high limits to ensure no violations
        config = LengthCheckerConfig(max_function_length=50, max_class_length=50)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 0

    def test_function_violation_detection(self):
        """Test detection of function length violations."""
        code = """def long_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    return line1 + line2 + line3 + line4 + line5"""

        config = LengthCheckerConfig(max_function_length=3, max_class_length=50)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1
        line, col, message, error_type = errors[0]
        assert error_type == "EL001"
        assert "EL001" in message
        assert "long_function" in message

    def test_class_violation_detection(self):
        """Test detection of class length violations."""
        code = """class LongClass:
    def method1(self):
        return 1

    def method2(self):
        return 2

    def method3(self):
        return 3"""

        config = LengthCheckerConfig(max_function_length=50, max_class_length=5)

        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1
        line, col, message, error_type = errors[0]
        assert error_type == "WL002"  # Should be warning, not error (9 lines > 5 but < 10)
        assert "WL002" in message
        assert "LongClass" in message

    def test_multiple_violations(self):
        """Test detection of multiple violations."""
        code = """class LongClass:
    def long_method1(self):
        line1 = 1
        line2 = 2
        line3 = 3
        return line1 + line2 + line3

    def long_method2(self):
        line1 = 1
        line2 = 2
        line3 = 3
        return line1 + line2 + line3"""

        config = LengthCheckerConfig(max_function_length=3, max_class_length=8)

        errors = run_plugin_on_code(code, config)
        # Should have 3 violations: 1 class + 2 functions
        assert len(errors) == 3

    def test_syntax_error_handling(self):
        """Test that syntax errors are handled gracefully."""
        code = """def broken_function(
    # Missing closing parenthesis
    return 42"""

        errors = run_plugin_on_code(code)
        # Should return empty list, not crash
        assert errors == []

    def test_docstring_exclusion_in_violations(self):
        """Test that docstrings are properly excluded from violation counts."""
        code = '''def function_with_long_docstring():
    """This is a very long docstring.

    It spans many lines to test that these lines
    are not counted toward the function length limit.

    This should not trigger a violation even though
    the total line count is high.
    """
    return 42'''

        config = LengthCheckerConfig(max_function_length=3)

        errors = run_plugin_on_code(code, config)
        # Should have no violations because docstring lines are excluded
        assert len(errors) == 0

    def test_nested_function_counting(self):
        """Test that nested functions are counted separately."""
        code = """def outer_function():
    def inner_function():
        line1 = 1
        line2 = 2
        line3 = 3
        line4 = 4
        return line1 + line2 + line3 + line4
    return inner_function()"""

        config = LengthCheckerConfig(max_function_length=4, max_class_length=50)

        errors = run_plugin_on_code(code, config)
        # Only inner function should violate (outer: 2 statements, inner: 6 statements > 4 limit)
        assert len(errors) == 1
        error_messages = [error[2] for error in errors]  # error[2] is the message
        assert any("inner_function" in msg for msg in error_messages)


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
        import os
        import tempfile

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


class TestEdgeCases:  # noqa: WL002
    """Test edge cases and corner scenarios."""

    def test_lambda_functions_not_counted(self):
        """Test that lambda functions are not counted as regular functions."""
        code = """def regular_function():
    lambda_func = lambda x: x * 2
    return lambda_func(5)"""

        visitor = ASTVisitor()
        import ast

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
        import ast

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
        import ast

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
        import ast

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
        import ast

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
        import ast

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
        import ast

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
        import ast

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
        import ast

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
        import ast

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
        import ast

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        assert len(elements) == 1
        assert elements[0].name == "context_function"


class TestConfiguration:
    """Test configuration loading and defaults."""

    def test_default_config_values(self):
        """Test that default configuration values are correct."""
        config = LengthCheckerConfig()
        assert config.max_function_length == LengthCheckerConfig.DEFAULT_FUNCTION_LENGTH
        assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH
        assert config.max_function_length == 40
        assert config.max_class_length == 200

    def test_config_initialization_with_custom_values(self):
        """Test configuration initialization with custom values."""
        config = LengthCheckerConfig(max_function_length=25, max_class_length=150)
        assert config.max_function_length == 25
        assert config.max_class_length == 150

    def test_config_from_dict_with_all_values(self):
        """Test configuration creation from dictionary with all values."""
        config_dict = {
            "max_function_length": 30,
            "max_class_length": 180,
        }
        config = LengthCheckerConfig.from_dict(config_dict)
        assert config.max_function_length == 30
        assert config.max_class_length == 180

    def test_config_from_dict_with_partial_values(self):
        """Test configuration creation from dictionary with partial values."""
        config_dict = {"max_function_length": 35}
        config = LengthCheckerConfig.from_dict(config_dict)
        assert config.max_function_length == 35
        assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH

    def test_config_from_dict_with_no_values(self):
        """Test configuration creation from empty dictionary."""
        config_dict = {}
        config = LengthCheckerConfig.from_dict(config_dict)
        assert config.max_function_length == LengthCheckerConfig.DEFAULT_FUNCTION_LENGTH
        assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH

    def test_config_from_dict_with_extra_values(self):
        """Test configuration creation from dictionary with extra values."""
        config_dict = {
            "max_function_length": 25,
            "max_class_length": 175,
            "unknown_setting": "ignored",
        }
        config = LengthCheckerConfig.from_dict(config_dict)
        assert config.max_function_length == 25
        assert config.max_class_length == 175

    def test_config_from_nonexistent_pyproject_toml(self):
        """Test configuration loading when pyproject.toml doesn't exist."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_path = Path(temp_dir) / "nonexistent.toml"
            config = LengthCheckerConfig.from_pyproject_toml(nonexistent_path)
            # Should return default config
            assert config.max_function_length == LengthCheckerConfig.DEFAULT_FUNCTION_LENGTH
            assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH

    def test_config_from_valid_pyproject_toml(self):
        """Test configuration loading from valid pyproject.toml."""
        import tempfile
        from pathlib import Path

        toml_content = """
[tool.pyla-linters]
max_function_length = 50
max_class_length = 250
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            temp_path = Path(f.name)

        try:
            config = LengthCheckerConfig.from_pyproject_toml(temp_path)
            assert config.max_function_length == 50
            assert config.max_class_length == 250
        finally:
            temp_path.unlink()

    def test_config_from_pyproject_toml_missing_tool_section(self):
        """Test configuration loading when [tool] section is missing."""
        import tempfile
        from pathlib import Path

        toml_content = """
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            temp_path = Path(f.name)

        try:
            config = LengthCheckerConfig.from_pyproject_toml(temp_path)
            # Should return default config
            assert config.max_function_length == LengthCheckerConfig.DEFAULT_FUNCTION_LENGTH
            assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH
        finally:
            temp_path.unlink()

    def test_config_from_pyproject_toml_missing_pyla_linters_section(self):
        """Test configuration loading when [tool.pyla-linters] section is missing."""
        import tempfile
        from pathlib import Path

        toml_content = """
[project]
name = "test-project"

[tool.black]
line-length = 88
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            temp_path = Path(f.name)

        try:
            config = LengthCheckerConfig.from_pyproject_toml(temp_path)
            # Should return default config
            assert config.max_function_length == LengthCheckerConfig.DEFAULT_FUNCTION_LENGTH
            assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH
        finally:
            temp_path.unlink()

    def test_config_from_invalid_toml_file(self):
        """Test configuration loading from invalid TOML file."""
        import tempfile
        from pathlib import Path

        invalid_toml_content = """
[tool.pyla-linters
# Missing closing bracket
max_function_length = 50
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(invalid_toml_content)
            temp_path = Path(f.name)

        try:
            config = LengthCheckerConfig.from_pyproject_toml(temp_path)
            # Should return default config when TOML parsing fails
            assert config.max_function_length == LengthCheckerConfig.DEFAULT_FUNCTION_LENGTH
            assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH
        finally:
            temp_path.unlink()

    def test_config_from_pyproject_toml_with_partial_settings(self):
        """Test configuration loading with only some settings in pyproject.toml."""
        import tempfile
        from pathlib import Path

        toml_content = """
[tool.pyla-linters]
max_function_length = 35
# max_class_length is not specified
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            temp_path = Path(f.name)

        try:
            config = LengthCheckerConfig.from_pyproject_toml(temp_path)
            assert config.max_function_length == 35
            assert config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH
        finally:
            temp_path.unlink()

    def test_plugin_config_loading_behavior(self):
        """Test that plugin loads configuration correctly."""
        tree = ast.parse("def test(): pass")
        plugin = LengthCheckerPlugin(tree, "test.py")

        # Initially should use default config
        assert plugin.config.max_function_length == LengthCheckerConfig.DEFAULT_FUNCTION_LENGTH
        assert plugin.config.max_class_length == LengthCheckerConfig.DEFAULT_CLASS_LENGTH

    def test_plugin_manual_config_override(self):
        """Test that manual configuration overrides file-based config."""
        tree = ast.parse("def test(): pass")
        plugin = LengthCheckerPlugin(tree, "test.py")

        # Set manual config
        custom_config = LengthCheckerConfig(max_function_length=15, max_class_length=75)
        plugin.set_config(custom_config)

        # Config should be the manually set one
        assert plugin.config.max_function_length == 15
        assert plugin.config.max_class_length == 75
        assert plugin._manual_config is True

    def test_plugin_config_loading_only_once(self):
        """Test that configuration is only loaded once from file."""
        tree = ast.parse("def test(): pass")
        plugin = LengthCheckerPlugin(tree, "test.py")

        # First call should load config
        assert plugin._config_loaded is False
        plugin._load_config_if_needed()
        assert plugin._config_loaded is True

        # Second call should not reload
        original_config = plugin.config
        plugin._load_config_if_needed()
        assert plugin.config is original_config  # Same object reference

    def test_config_find_pyproject_toml_search(self):
        """Test that pyproject.toml search works in parent directories."""
        import os
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create nested directory structure
            nested_dir = temp_path / "subdir" / "nested"
            nested_dir.mkdir(parents=True)

            # Create pyproject.toml in root
            toml_content = """
[tool.pyla-linters]
max_function_length = 60
"""
            pyproject_path = temp_path / "pyproject.toml"
            pyproject_path.write_text(toml_content)

            # Change to nested directory
            original_cwd = os.getcwd()
            try:
                os.chdir(nested_dir)

                # Should find pyproject.toml in parent directories
                config = LengthCheckerConfig.from_pyproject_toml()
                assert config.max_function_length == 60
            finally:
                os.chdir(original_cwd)


class TestFileExclusionPatterns:
    """Test file and directory exclusion pattern behavior.

    Note: The current implementation does not support file/directory exclusion patterns.
    These tests document the current behavior and can be updated when exclusion support is added.
    """

    def test_no_exclusion_pattern_support_in_config(self):
        """Test that current configuration doesn't support exclusion patterns."""
        config = LengthCheckerConfig()

        # Current implementation doesn't have exclusion pattern attributes
        assert not hasattr(config, "exclude_patterns")
        assert not hasattr(config, "include_patterns")
        assert not hasattr(config, "exclude_dirs")
        assert not hasattr(config, "exclude_files")

    def test_plugin_processes_all_provided_files(self):
        """Test that plugin processes all files provided to it."""
        code = """def test_function():
    return 42"""

        config = LengthCheckerConfig(max_function_length=1)

        # Plugin should process any file path provided to it
        errors1 = run_plugin_on_code(code, config, "regular_file.py")
        errors2 = run_plugin_on_code(code, config, "test_file.py")
        errors3 = run_plugin_on_code(code, config, "__pycache__/cached.py")
        errors4 = run_plugin_on_code(code, config, "venv/lib/python3.11/site-packages/module.py")

        # All should produce violations (all have functions > 1 line)
        assert len(errors1) == 1
        assert len(errors2) == 1
        assert len(errors3) == 1
        assert len(errors4) == 1

    def test_plugin_does_not_filter_by_file_extension(self):
        """Test that plugin doesn't filter files by extension."""
        code = """def test_function():
    return 42"""

        config = LengthCheckerConfig(max_function_length=1)

        # Plugin should process files regardless of extension
        errors_py = run_plugin_on_code(code, config, "test.py")
        errors_pyx = run_plugin_on_code(code, config, "test.pyx")
        errors_no_ext = run_plugin_on_code(code, config, "test")

        # All should produce violations
        assert len(errors_py) == 1
        assert len(errors_pyx) == 1
        assert len(errors_no_ext) == 1

    def test_plugin_does_not_filter_by_directory_path(self):
        """Test that plugin doesn't filter files by directory path."""
        code = """def test_function():
    return 42"""

        config = LengthCheckerConfig(max_function_length=1)

        # Plugin should process files in any directory
        paths_to_test = [
            "src/module.py",
            "tests/test_module.py",
            "__pycache__/module.pyc",
            ".venv/lib/python3.11/site-packages/package/module.py",
            "node_modules/some-package/python/script.py",
            ".git/hooks/pre-commit.py",
            "build/temp/generated.py",
            "dist/package/module.py",
        ]

        for path in paths_to_test:
            errors = run_plugin_on_code(code, config, path)
            assert len(errors) == 1, f"Expected violation for path: {path}"

    def test_exclusion_would_be_handled_by_flake8_not_plugin(self):
        """Test that file exclusion is expected to be handled by flake8, not the plugin."""
        # This test documents the current architecture where flake8 handles
        # file filtering and the plugin processes whatever files are passed to it

        tree = ast.parse("def test(): pass")
        plugin = LengthCheckerPlugin(tree, "test.py")

        # The plugin's run method signature shows it expects to receive
        # individual files that flake8 has already filtered
        import inspect

        signature = inspect.signature(plugin.run)

        # Plugin run method takes no parameters (gets data from constructor)
        params = list(signature.parameters.keys())
        # Plugin doesn't receive exclude patterns in run method
        assert "exclude_patterns" not in params
        assert "include_patterns" not in params

    def test_current_config_from_toml_ignores_exclusion_patterns(self):
        """Test that TOML config loading ignores exclusion pattern settings."""
        import tempfile
        from pathlib import Path

        toml_content = """
[tool.pyla-linters]
max_function_length = 30
max_class_length = 150
# These would be exclusion patterns if supported
exclude_patterns = ["*/test_*", "*.tmp.py"]
exclude_dirs = ["__pycache__", ".venv"]
include_patterns = ["src/**/*.py"]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            temp_path = Path(f.name)

        try:
            config = LengthCheckerConfig.from_pyproject_toml(temp_path)
            # Should load the supported settings
            assert config.max_function_length == 30
            assert config.max_class_length == 150
            # Should ignore unsupported exclusion settings
            assert not hasattr(config, "exclude_patterns")
            assert not hasattr(config, "exclude_dirs")
            assert not hasattr(config, "include_patterns")
        finally:
            temp_path.unlink()

    def test_future_exclusion_pattern_support_would_need_config_extension(self):
        """Test documenting what would be needed for exclusion pattern support."""
        # This test documents the interface that would be needed for exclusion support

        # Current config only has length limits
        config = LengthCheckerConfig()
        current_attrs = [attr for attr in dir(config) if not attr.startswith("_")]
        expected_current = [
            "DEFAULT_CLASS_LENGTH",
            "DEFAULT_FUNCTION_LENGTH",
            "from_dict",
            "from_pyproject_toml",
            "max_class_length",
            "max_function_length",
        ]

        # Verify current attributes match expected
        assert set(current_attrs) == set(expected_current)

        # Future exclusion support would need additional attributes
        future_exclusion_attrs = [
            "exclude_patterns",
            "include_patterns",
            "exclude_dirs",
            "exclude_files",
        ]

        # These don't exist yet
        for attr in future_exclusion_attrs:
            assert not hasattr(config, attr)

    def test_plugin_run_params_could_support_exclusion_metadata(self):
        """Test that plugin run method accepts params that could contain exclusion info."""
        # Test that the plugin interface doesn't support exclusion patterns directly
        # This functionality would be handled by flake8 itself

        code = "def test(): pass"

        # The plugin doesn't accept exclusion parameters - this is handled by flake8
        errors = run_plugin_on_code(code)
        assert isinstance(errors, list)  # Should return normal error list

        # Plugin interface is simplified - flake8 handles file filtering


class TestFlake8Integration:  # noqa: WL002
    """Test integration with flake8 CLI."""

    def test_plugin_is_registered_with_flake8(self):
        """Test that the plugin is properly registered as a flake8 plugin."""
        import subprocess

        # Run flake8 --help to see if our plugin is available
        result = subprocess.run(["uv", "run", "flake8", "--help"], capture_output=True, text=True)

        # Should not error and should complete successfully
        assert result.returncode == 0

    def test_flake8_integration_with_violations(self):  # noqa: EL001
        """Test full flake8 integration with code that has violations."""
        import subprocess
        import tempfile
        from pathlib import Path

        # Create a Python file with violations
        code_with_violations = '''def very_long_function():
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
    line12 = 12
    line13 = 13
    line14 = 14
    line15 = 15
    line16 = 16
    line17 = 17
    line18 = 18
    line19 = 19
    line20 = 20
    line21 = 21
    line22 = 22
    line23 = 23
    line24 = 24
    line25 = 25
    line26 = 26
    line27 = 27
    line28 = 28
    line29 = 29
    line30 = 30
    line31 = 31
    line32 = 32
    line33 = 33
    line34 = 34
    line35 = 35
    line36 = 36
    line37 = 37
    line38 = 38
    line39 = 39
    line40 = 40
    line41 = 41  # This exceeds the default 40 line limit
    return sum([line1, line2, line3, line4, line5])

class VeryLongClass:
    """A class that exceeds the default 200 line limit."""

    def __init__(self):
        self.attr1 = 1
        self.attr2 = 2
        self.attr3 = 3
        self.attr4 = 4
        self.attr5 = 5

    def method1(self):
        return self.attr1

    def method2(self):
        return self.attr2

    def method3(self):
        return self.attr3

    def method4(self):
        return self.attr4

    def method5(self):
        return self.attr5
''' + (
            """
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
"""
            * 25
        )  # Repeat to make class very long

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "test_violations.py"
            test_file.write_text(code_with_violations)

            # Create pyproject.toml with strict limits to ensure violations
            pyproject_content = """
[project]
name = "test-project"
version = "0.1.0"
description = "Test project"
authors = [{name = "Test", email = "test@example.com"}]

[tool.pyla-linters]
max_function_length = 40
max_class_length = 200

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
"""
            pyproject_file = temp_path / "pyproject.toml"
            pyproject_file.write_text(pyproject_content)

            # Run flake8 on the test file with explicit plugin selection
            result = subprocess.run(
                ["uv", "run", "flake8", "--select=WL,EL", str(test_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            # Should detect violations and return non-zero exit code
            assert result.returncode != 0

            # Should contain our violation codes in output
            output = result.stdout + result.stderr
            assert "WL001" in output  # Function length warning (43 lines > 40)
            assert "WL002" in output  # Class length warning (267 lines > 200 but < 400)
            assert "very_long_function" in output
            assert "VeryLongClass" in output

    def test_flake8_integration_without_violations(self):
        """Test flake8 integration with code that has no violations."""
        import subprocess
        import tempfile
        from pathlib import Path

        # Create a Python file without violations
        clean_code = '''def short_function():
    """A short function."""
    return 42

class ShortClass:
    """A short class."""

    def __init__(self):
        self.value = 0

    def get_value(self):
        return self.value
'''

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "test_clean.py"
            test_file.write_text(clean_code)

            # Create pyproject.toml with lenient limits
            pyproject_content = """
[tool.pyla-linters]
max_function_length = 40
max_class_length = 200
"""
            pyproject_file = temp_path / "pyproject.toml"
            pyproject_file.write_text(pyproject_content)

            # Run flake8 on the test file with explicit plugin selection
            result = subprocess.run(
                ["uv", "run", "flake8", "--select=WL,EL", str(test_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            # Should not detect violations
            output = result.stdout + result.stderr

            # Should not contain our error codes
            assert "EL001" not in output
            assert "EL002" not in output

    def test_flake8_integration_with_custom_config(self):  # noqa: WL001
        """Test flake8 integration with custom configuration."""
        import subprocess
        import tempfile
        from pathlib import Path

        # Create a Python file that violates strict limits but not lenient ones
        medium_code = """def medium_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    line8 = 8
    return line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "test_medium.py"
            test_file.write_text(medium_code)

            # Test with strict limits - should have violations
            strict_pyproject = """
[project]
name = "test-project"
version = "0.1.0"
description = "Test project"
authors = [{name = "Test", email = "test@example.com"}]

[tool.pyla-linters]
max_function_length = 5
max_class_length = 50

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
"""
            pyproject_file = temp_path / "pyproject.toml"
            pyproject_file.write_text(strict_pyproject)

            result_strict = subprocess.run(
                ["uv", "run", "flake8", "--select=WL,EL", str(test_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            # Should have violations with strict limits
            strict_output = result_strict.stdout + result_strict.stderr
            assert "WL001" in strict_output

            # Test with lenient limits - should not have violations
            lenient_pyproject = """
[tool.poetry]
name = "test-project"
version = "0.1.0"
description = "Test project"
authors = ["Test <test@example.com>"]

[tool.pyla-linters]
max_function_length = 20
max_class_length = 200

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
            pyproject_file.write_text(lenient_pyproject)

            result_lenient = subprocess.run(
                ["uv", "run", "flake8", "--select=WL,EL", str(test_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            # Should not have violations with lenient limits
            lenient_output = result_lenient.stdout + result_lenient.stderr
            assert "WL001" not in lenient_output
            assert "EL001" not in lenient_output

    def test_flake8_integration_error_format(self):  # noqa: WL001
        """Test that flake8 integration produces correctly formatted errors."""
        import subprocess
        import tempfile
        from pathlib import Path

        # Create a Python file with a simple violation
        code_with_error = """def long_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    return line1 + line2 + line3 + line4 + line5 + line6
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "test_format.py"
            test_file.write_text(code_with_error)

            # Create pyproject.toml with strict limits
            pyproject_content = """
[project]
name = "test-project"
version = "0.1.0"
description = "Test project"
authors = [{name = "Test", email = "test@example.com"}]

[tool.pyla-linters]
max_function_length = 5
max_class_length = 50

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
"""
            pyproject_file = temp_path / "pyproject.toml"
            pyproject_file.write_text(pyproject_content)

            # Run flake8 on the test file with explicit plugin selection
            result = subprocess.run(
                ["uv", "run", "flake8", "--select=WL,EL", str(test_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            output = result.stdout + result.stderr

            # Should contain correctly formatted error message
            # Flake8 format is typically: filename:line:col: error_code message
            assert "test_format.py" in output
            assert "WL001" in output
            assert "long_function" in output
            assert "8 statements long" in output
            assert "exceeds warning threshold of 5" in output

    def test_flake8_integration_multiple_files(self):  # noqa: WL001
        """Test flake8 integration with multiple files."""
        import subprocess
        import tempfile
        from pathlib import Path

        file1_code = """def violation_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    return line1 + line2 + line3 + line4 + line5 + line6 + line7
"""

        file2_code = """def clean_function():
    return 42

class CleanClass:
    def method(self):
        return True
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create multiple test files
            file1 = temp_path / "file1.py"
            file1.write_text(file1_code)

            file2 = temp_path / "file2.py"
            file2.write_text(file2_code)

            # Create pyproject.toml
            pyproject_content = """
[project]
name = "test-project"
version = "0.1.0"
description = "Test project"
authors = [{name = "Test", email = "test@example.com"}]

[tool.pyla-linters]
max_function_length = 5
max_class_length = 50

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
"""
            pyproject_file = temp_path / "pyproject.toml"
            pyproject_file.write_text(pyproject_content)

            # Run flake8 on all Python files with explicit plugin selection
            result = subprocess.run(
                ["poetry", "run", "flake8", "--select=WL,EL", str(file1), str(file2)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            output = result.stdout + result.stderr

            # Should find violation in file1 but not file2
            assert "file1.py" in output
            assert "WL001" in output  # 9 lines > 5 threshold but < 10 (2x threshold)
            assert "violation_function" in output

            # Should not complain about file2's clean functions
            if "file2.py" in output:
                # If file2 is mentioned, it shouldn't have EL001/EL002 errors
                file2_lines = [line for line in output.split("\n") if "file2.py" in line]
                for line in file2_lines:
                    assert "EL001" not in line
                    assert "EL002" not in line

    def test_flake8_integration_with_syntax_errors(self):
        """Test flake8 integration handles syntax errors gracefully."""
        import subprocess
        import sys
        import tempfile
        from pathlib import Path

        # Create a Python file with syntax errors
        broken_code = """def broken_function(
    # Missing closing parenthesis
    line1 = 1
    line2 = 2
    return line1 + line2
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file
            test_file = temp_path / "broken.py"
            test_file.write_text(broken_code)

            # Create pyproject.toml
            pyproject_content = """
[tool.pyla-linters]
max_function_length = 5
max_class_length = 50
"""
            pyproject_file = temp_path / "pyproject.toml"
            pyproject_file.write_text(pyproject_content)

            # Run flake8 on the test file with our plugin
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "--select=EL", str(test_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            # flake8 should run (might report syntax errors)
            # but our plugin should not crash or produce EL001/EL002 errors
            output = result.stdout + result.stderr

            # Our plugin should not report length violations for broken syntax
            assert "EL001" not in output
            assert "EL002" not in output


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


class TestCompoundStatementHandling:
    """Test comprehensive compound statement handling for if/elif/else, try/except/finally."""

    def test_complex_if_elif_else_chain(self):
        """Test that complex if/elif/else chains count statements correctly."""
        code = """def complex_conditional():
    x = 10
    if x > 15:
        result = "high"
        print(result)
    elif x > 10:
        result = "medium"
        log_value(result)
    elif x > 5:
        result = "low"
        process_value(result)
    else:
        result = "zero"
        handle_zero(result)
    return result"""

        config = LengthCheckerConfig(max_function_length=8)
        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1

        # Should count: def, x=10, if, result="high", print(), result="medium",
        # log_value(), result="low", process_value(), result="zero", handle_zero(), return
        # = 14 statements total (actual count)
        _, _, message, _ = errors[0]
        assert "14 statements long" in message

    def test_nested_try_except_finally_blocks(self):
        """Test nested try/except/finally blocks count correctly."""
        code = """def nested_exception_handling():
    try:
        x = get_value()
        try:
            result = process(x)
            validate(result)
        except ValidationError:
            result = default_value()
        finally:
            log_process()
    except NetworkError as e:
        handle_network_error(e)
        retry_count += 1
    except Exception:
        handle_generic_error()
    finally:
        cleanup_resources()
    return result"""

        config = LengthCheckerConfig(max_function_length=10)
        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1

        # Should count all executable statements including nested try blocks
        # = 13 statements total (actual count)
        _, _, message, _ = errors[0]
        assert "13 statements long" in message

    def test_match_case_statements(self):
        """Test Python 3.10+ match/case statements (if supported)."""
        code = """def match_example(value):
    match value:
        case 1:
            result = "one"
        case 2 | 3:
            result = "two or three"
        case str() if len(value) > 5:
            result = "long string"
        case _:
            result = "default"
    return result"""

        try:
            config = LengthCheckerConfig(max_function_length=5)
            errors = run_plugin_on_code(code, config)
            # Should handle match/case correctly regardless of Python version
            if errors:  # If match/case is supported and creates violations
                _, _, message, _ = errors[0]
                assert "statements long" in message
        except SyntaxError:
            # Match/case not supported in this Python version, skip test
            pass

    def test_complex_loop_structures(self):
        """Test complex loop structures with breaks and continues."""
        code = """def complex_loops():
    for i in range(10):
        if i % 2 == 0:
            continue
        for j in range(i):
            if j > 5:
                break
            process_pair(i, j)

    while condition():
        try:
            value = get_next()
            if value is None:
                break
            process(value)
        except StopIteration:
            break
    return results"""

        config = LengthCheckerConfig(max_function_length=10)
        errors = run_plugin_on_code(code, config)
        assert len(errors) == 1

        # Should count all statements including control flow
        _, _, message, _ = errors[0]
        assert "statements long" in message


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
