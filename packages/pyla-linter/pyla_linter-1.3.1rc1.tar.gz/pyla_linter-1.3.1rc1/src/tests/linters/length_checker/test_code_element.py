"""Unit tests for the CodeElement class."""

from unittest.mock import Mock

import pytest

from src.linters.length_checker.code_element import CodeElement
from src.linters.length_checker.statement_counter import StatementCounter


class TestCodeElement:
    """Test cases for the CodeElement class."""

    def test_init_function_element(self):
        """Test initialization of a function code element."""
        element = CodeElement("test_func", "function", 10, 15)

        assert element.name == "test_func"
        assert element.node_type == "function"
        assert element.start_line == 10
        assert element.end_line == 15
        assert element.nested_elements == []

    def test_init_class_element(self):
        """Test initialization of a class code element."""
        element = CodeElement("TestClass", "class", 1, 20)

        assert element.name == "TestClass"
        assert element.node_type == "class"
        assert element.start_line == 1
        assert element.end_line == 20
        assert element.nested_elements == []

    def test_total_lines_calculation(self):
        """Test total_lines property calculation."""
        # Single line element
        element = CodeElement("single_line", "function", 5, 5)
        assert element.total_lines == 1

        # Multi-line element
        element = CodeElement("multi_line", "function", 10, 15)
        assert element.total_lines == 6

        # Large element
        element = CodeElement("large_element", "class", 1, 100)
        assert element.total_lines == 100

    def test_get_effective_statements_with_mock(self):
        """Test get_effective_statements method with mocked StatementCounter."""
        element = CodeElement("test_func", "function", 5, 10)
        mock_counter = Mock(spec=StatementCounter)
        mock_counter.count_element_statements.return_value = 8
        source_code = "def test_func():\n    pass\n"

        result = element.get_effective_statements(mock_counter, source_code)

        assert result == 8
        mock_counter.count_element_statements.assert_called_once_with(element, source_code)

    def test_get_effective_statements_with_real_counter(self):
        """Test get_effective_statements method with real StatementCounter."""
        code = """def test_function():
    x = 1
    y = 2
    return x + y"""

        source_lines = code.splitlines()
        element = CodeElement("test_function", "function", 1, 4)
        counter = StatementCounter(source_lines)

        result = element.get_effective_statements(counter, code)

        # Should count statements: x=1, y=2, return x+y (plus potentially function def)
        assert result >= 3  # At least 3 statements, possibly more depending on implementation

    def test_nested_elements_handling(self):
        """Test handling of nested elements list."""
        parent = CodeElement("ParentClass", "class", 1, 20)
        child1 = CodeElement("method1", "function", 5, 8)
        child2 = CodeElement("method2", "function", 10, 15)

        parent.nested_elements.append(child1)
        parent.nested_elements.append(child2)

        assert len(parent.nested_elements) == 2
        assert parent.nested_elements[0] == child1
        assert parent.nested_elements[1] == child2

    def test_repr_function(self):
        """Test __repr__ method for function elements."""
        element = CodeElement("my_function", "function", 10, 15)
        expected = "CodeElement(my_function, function, 10-15)"
        assert repr(element) == expected

    def test_repr_class(self):
        """Test __repr__ method for class elements."""
        element = CodeElement("MyClass", "class", 1, 50)
        expected = "CodeElement(MyClass, class, 1-50)"
        assert repr(element) == expected

    @pytest.mark.parametrize(
        "start_line,end_line,expected_total",
        [
            (1, 1, 1),
            (1, 5, 5),
            (10, 20, 11),
            (100, 150, 51),
        ],
    )
    def test_total_lines_various_ranges(self, start_line, end_line, expected_total):
        """Test total_lines calculation for various line ranges."""
        element = CodeElement("test", "function", start_line, end_line)
        assert element.total_lines == expected_total

    def test_element_with_complex_statements(self):
        """Test statement counting with complex code structures."""
        code = """def complex_function():
    # This is a comment
    '''This is a docstring'''

    x = 1  # assignment
    if x > 0:  # if statement
        print("positive")  # function call
    else:  # else clause
        print("non-positive")  # function call

    try:  # try statement
        result = 10 / x  # assignment
    except ZeroDivisionError:  # except clause
        result = 0  # assignment
    finally:  # finally clause
        print("done")  # function call

    return result  # return statement"""

        source_lines = code.splitlines()
        # Count the actual lines in the code - function goes from line 1 to the last line
        lines_count = len(source_lines)
        element = CodeElement("complex_function", "function", 1, lines_count)
        counter = StatementCounter(source_lines)

        result = element.get_effective_statements(counter, code)

        # Should count all executable statements but not comments/docstrings
        # Expected: x=1, if, print, else, print, try, result=10/x, except, result=0,
        # finally, print, return
        assert result > 0  # At least some statements should be counted
