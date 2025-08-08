"""Tests for the AST visitor functionality."""

import ast

from src.linters.length_checker.ast_visitor import ASTVisitor


class TestASTVisitor:
    """Test the AST visitor functionality."""

    def test_simple_function_detection(self):
        """Test detection of a simple function."""
        code = """def simple_function():
    return 42"""

        visitor = ASTVisitor()

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

        tree = ast.parse(code)
        visitor.visit(tree)

        elements = visitor.get_all_elements()
        assert len(elements) == 1
        assert elements[0].name == "async_function"
        assert elements[0].node_type == "function"
