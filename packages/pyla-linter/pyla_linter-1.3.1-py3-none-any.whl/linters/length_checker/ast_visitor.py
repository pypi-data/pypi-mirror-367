"""AST visitor for analyzing code structure."""

import ast
from typing import List

from .code_element import CodeElement


class ASTVisitor(ast.NodeVisitor):
    """Visits AST nodes to identify classes and functions with their line counts."""

    def __init__(self):
        self.elements: List[CodeElement] = []
        self._element_stack: List[CodeElement] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition."""
        # Include decorators in the line range
        start_line = node.lineno
        if node.decorator_list:
            start_line = min(d.lineno for d in node.decorator_list)

        element = CodeElement(
            name=node.name,
            node_type="class",
            start_line=start_line,
            end_line=node.end_lineno or node.lineno,
        )

        self._add_element(element)
        self._element_stack.append(element)
        self.generic_visit(node)
        self._element_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition."""
        # Include decorators in the line range
        start_line = node.lineno
        if node.decorator_list:
            start_line = min(d.lineno for d in node.decorator_list)

        element = CodeElement(
            name=node.name,
            node_type="function",
            start_line=start_line,
            end_line=node.end_lineno or node.lineno,
        )

        self._add_element(element)
        self._element_stack.append(element)
        self.generic_visit(node)
        self._element_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit an async function definition."""
        # Include decorators in the line range
        start_line = node.lineno
        if node.decorator_list:
            start_line = min(d.lineno for d in node.decorator_list)

        element = CodeElement(
            name=node.name,
            node_type="function",
            start_line=start_line,
            end_line=node.end_lineno or node.lineno,
        )

        self._add_element(element)
        self._element_stack.append(element)
        self.generic_visit(node)
        self._element_stack.pop()

    def _add_element(self, element: CodeElement) -> None:
        """Add element to the appropriate container."""
        if self._element_stack:
            # This is a nested element
            self._element_stack[-1].nested_elements.append(element)
        else:
            # This is a top-level element
            self.elements.append(element)

    def get_all_elements(self) -> List[CodeElement]:
        """Get all code elements found during traversal."""
        result = []

        def collect_elements(elements: List[CodeElement]) -> None:
            for element in elements:
                result.append(element)
                collect_elements(element.nested_elements)

        collect_elements(self.elements)
        return result
