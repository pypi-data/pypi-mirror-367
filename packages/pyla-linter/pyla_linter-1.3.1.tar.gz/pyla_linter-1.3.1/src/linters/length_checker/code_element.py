"""Represents a code element (class or function) with location and statement counting."""

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .statement_counter import StatementCounter


class CodeElement:
    """Represents a code element with location and statement counting capability.

    This class stores the position and type of a code element and provides
    methods to count executable statements within that element using AST analysis.
    """

    def __init__(self, name: str, node_type: str, start_line: int, end_line: int) -> None:
        """Initialize a code element with its name, type, and location.

        Args:
            name: The name of the code element (function or class name)
            node_type: The type of code element ("class" or "function")
            start_line: The line number where the element starts (1-based)
            end_line: The line number where the element ends (1-based)
        """
        self.name = name
        self.node_type = node_type  # "class" or "function"
        self.start_line = start_line
        self.end_line = end_line
        self.nested_elements: List["CodeElement"] = []

    @property
    def total_lines(self) -> int:
        """Get the total number of physical lines spanned by this code element.

        Note: This returns the physical line span, not the statement count.
        For statement counting, use get_effective_statements().

        Returns:
            The total physical line count from start_line to end_line (inclusive)
        """
        return self.end_line - self.start_line + 1

    def get_effective_statements(
        self, statement_counter: "StatementCounter", source_code: str
    ) -> int:
        """Count the number of effective executable statements in this code element.

        Uses AST-based statement counting to exclude docstrings, comments, and empty lines.
        Only counts statements that are directly within this element's scope, excluding
        nested function and class definitions.

        Args:
            statement_counter: The StatementCounter instance to use for counting
            source_code: The full source code of the file containing this element

        Returns:
            The number of executable statements in this code element
        """
        return statement_counter.count_element_statements(self, source_code)

    def __repr__(self) -> str:
        return f"CodeElement({self.name}, {self.node_type}, {self.start_line}-{self.end_line})"
