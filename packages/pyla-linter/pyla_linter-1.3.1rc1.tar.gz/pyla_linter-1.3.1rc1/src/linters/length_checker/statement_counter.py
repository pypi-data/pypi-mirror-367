"""Logic for counting logical statements excluding docstrings and comments."""

import ast
from typing import Sequence, Set

from .code_element import CodeElement
from .docstring_finder import DocstringFinder
from .statement_visitor import StatementVisitor


class StatementCounter:
    """Counts logical statements, excluding docstrings and comments."""

    def __init__(self, source_lines: Sequence[str]):
        self.source_lines = source_lines
        self._comment_lines = self._find_comment_lines()
        self._docstring_lines = set()

    def count_element_statements(self, element: CodeElement, source_code: str) -> int:
        """Count statements for a code element, excluding docstrings and comments.

        Args:
            element: The code element to count statements for
            source_code: The full source code of the file

        Returns:
            Number of logical statements (excluding docstrings and comments)
        """
        try:
            # Parse the source code to get AST
            tree = ast.parse(source_code)

            # Find the AST node that corresponds to this element
            element_node = self._find_element_node(tree, element)
            if element_node is None:
                return 0

            # Use StatementVisitor to count statements
            visitor = StatementVisitor()
            statement_count = visitor.count_statements_in_element(element_node)

            # Find docstring lines for this element
            self._find_docstring_lines(element, source_code)

            # Subtract statements that are in docstring or comment lines
            adjusted_count = self._adjust_for_excluded_lines(
                statement_count, element, element_node, source_code
            )

            return adjusted_count

        except (SyntaxError, ValueError):
            # If parsing fails, fall back to simple line counting
            return self._fallback_line_count(element)

    def _find_element_node(self, tree: ast.AST, element: CodeElement) -> ast.AST | None:
        """Find the AST node corresponding to the given code element."""
        for node in ast.walk(tree):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                lineno = getattr(node, "lineno", None)
                end_lineno = getattr(node, "end_lineno", None)
                if lineno == element.start_line and end_lineno == element.end_line:
                    if (element.node_type == "class" and isinstance(node, ast.ClassDef)) or (
                        element.node_type == "function"
                        and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ):
                        return node
        return None

    def _adjust_for_excluded_lines(
        self, statement_count: int, element: CodeElement, element_node: ast.AST, source_code: str
    ) -> int:
        """Adjust statement count to exclude statements on comment/docstring lines."""
        # This is a simplified approach - in practice, most statements
        # won't be on comment/docstring lines, so we return the raw count
        # The StatementVisitor already handles AST-level exclusions
        return statement_count

    def _fallback_line_count(self, element: CodeElement) -> int:
        """Fallback method that counts non-empty, non-comment lines when AST parsing fails.

        Note: This is a simplified approximation used only when proper AST-based
        statement counting cannot be performed.
        """
        actual_lines = 0
        for line_num in range(element.start_line, element.end_line + 1):
            if self._is_code_line(line_num):
                actual_lines += 1
        return actual_lines

    def _find_comment_lines(self) -> Set[int]:
        """Find all lines that are comments or contain only comments."""
        comment_lines = set()

        for i, line in enumerate(self.source_lines, 1):
            stripped = line.strip()
            # Check if line is a comment or starts with comment after whitespace
            if stripped.startswith("#") or (not stripped):
                comment_lines.add(i)
            else:
                # Check for inline comments - but only if they're the only content
                # We want to keep lines with code + comments as they contain actual code
                pass

        return comment_lines

    def _find_docstring_lines(self, element: CodeElement, source_code: str) -> None:
        """Find docstring lines for a specific code element."""
        try:
            # Parse the source to find docstrings
            tree = ast.parse(source_code)
            docstring_finder = DocstringFinder()
            docstring_finder.visit(tree)

            # Find docstrings that belong to this element
            for start_line, end_line in docstring_finder.docstring_ranges:
                if start_line >= element.start_line and end_line <= element.end_line:
                    for line_num in range(start_line, end_line + 1):
                        self._docstring_lines.add(line_num)

        except (SyntaxError, ValueError):
            # If parsing fails, don't exclude any docstring lines
            pass

    def _is_code_line(self, line_num: int) -> bool:
        """Check if a line number represents actual code."""
        # Line is code if it's not a comment line and not a docstring line
        if line_num in self._comment_lines or line_num in self._docstring_lines:
            return False

        # Also check if the line is just whitespace
        if line_num <= len(self.source_lines):
            line_content = self.source_lines[line_num - 1].strip()
            return bool(line_content)

        return False
