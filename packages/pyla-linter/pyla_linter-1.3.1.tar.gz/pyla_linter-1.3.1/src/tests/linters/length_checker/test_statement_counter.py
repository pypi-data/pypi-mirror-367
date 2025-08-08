"""Tests for the statement counting functionality."""

from src.linters.length_checker.code_element import CodeElement
from src.linters.length_checker.statement_counter import StatementCounter


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
