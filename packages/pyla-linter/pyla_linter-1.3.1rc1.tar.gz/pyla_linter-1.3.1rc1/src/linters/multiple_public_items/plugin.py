"""Main plugin class implementing flake8 interface."""

import ast
from typing import Iterator, Tuple

from .ast_visitor import PublicItemsVisitor


class MultiplePublicItemsPlugin:
    """Flake8 plugin for checking multiple public items per file."""

    name = "multiple_public_items"
    version = "1.0.0"

    def __init__(self, tree: ast.AST, filename: str = "<stdin>"):
        """Initialize the plugin with AST tree and filename."""
        self.tree = tree
        self.filename = filename

    def run(self) -> Iterator[Tuple[int, int, str, str]]:
        """Run the multiple public items checker and yield flake8 errors."""
        try:
            yield from self._analyze_ast()
        except (SyntaxError, Exception):
            # Skip files with syntax errors or other processing issues
            pass

    def _analyze_ast(self) -> Iterator[Tuple[int, int, str, str]]:
        """Analyze the AST tree and yield flake8 errors."""
        visitor = PublicItemsVisitor()
        visitor.visit(self.tree)

        public_items = visitor.get_public_items()

        # Check if there are multiple public items (violation)
        if len(public_items) > 1:
            yield self._create_violation(public_items)

    def _create_violation(self, public_items) -> Tuple[int, int, str, str]:
        """Create a multiple public items error tuple for flake8."""
        # Sort items by line number for consistent output
        sorted_items = sorted(public_items, key=lambda item: item.line_number)

        # Create list of items for error message
        item_descriptions = []
        for item in sorted_items:
            item_descriptions.append(f"{item.item_type} '{item.name}' (line {item.line_number})")

        items_list = ", ".join(item_descriptions)

        message = (
            f"EL101 File contains {len(public_items)} public items: {items_list}. "
            f"Only one public item per file is allowed."
        )

        # Report error at the first line of the first public item
        first_item = sorted_items[0]
        return (first_item.line_number, 0, message, "EL101")
