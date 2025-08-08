"""AST visitor to find docstring locations."""

import ast
from typing import List


class DocstringFinder(ast.NodeVisitor):
    """AST visitor to find docstring locations."""

    def __init__(self):
        self.docstring_ranges: List[tuple[int, int]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition and check for docstring."""
        self._check_for_docstring(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition and check for docstring."""
        self._check_for_docstring(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition and check for docstring."""
        self._check_for_docstring(node)
        self.generic_visit(node)

    def visit_Module(self, node: ast.Module) -> None:
        """Visit module and check for module-level docstring."""
        self._check_for_docstring(node)
        self.generic_visit(node)

    def _check_for_docstring(self, node) -> None:
        """Check if a node has a docstring and record its location."""
        if (
            hasattr(node, "body")
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            # This is a docstring
            docstring_node = node.body[0]
            start_line = docstring_node.lineno
            end_line = getattr(docstring_node, "end_lineno", start_line)
            if end_line is None:
                end_line = start_line
            self.docstring_ranges.append((start_line, end_line))
