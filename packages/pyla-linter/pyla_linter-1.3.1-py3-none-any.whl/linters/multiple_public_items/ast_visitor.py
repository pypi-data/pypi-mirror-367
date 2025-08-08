"""AST visitor for collecting public classes and functions at module level."""

import ast
from typing import List

from .public_item import PublicItem


class PublicItemsVisitor(ast.NodeVisitor):
    """Visits AST nodes to identify public classes and functions at module level."""

    def __init__(self):
        self.public_items: List[PublicItem] = []
        self._depth = 0

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition."""
        # Only collect public classes at module level (depth 0)
        if self._depth == 0 and not node.name.startswith("_"):
            item = PublicItem(name=node.name, item_type="class", line_number=node.lineno)
            self.public_items.append(item)

        # Continue traversing nested structures
        self._depth += 1
        self.generic_visit(node)
        self._depth -= 1

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition."""
        # Only collect public functions at module level (depth 0)
        if self._depth == 0 and not node.name.startswith("_"):
            item = PublicItem(name=node.name, item_type="function", line_number=node.lineno)
            self.public_items.append(item)

        # Continue traversing nested structures
        self._depth += 1
        self.generic_visit(node)
        self._depth -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit an async function definition."""
        # Only collect public async functions at module level (depth 0)
        if self._depth == 0 and not node.name.startswith("_"):
            item = PublicItem(name=node.name, item_type="function", line_number=node.lineno)
            self.public_items.append(item)

        # Continue traversing nested structures
        self._depth += 1
        self.generic_visit(node)
        self._depth -= 1

    def get_public_items(self) -> List[PublicItem]:
        """Get all public items found at module level."""
        return self.public_items
