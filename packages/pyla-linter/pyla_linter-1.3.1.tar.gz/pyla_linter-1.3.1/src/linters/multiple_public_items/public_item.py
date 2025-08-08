"""Represents a public class or function at module level."""


class PublicItem:
    """Represents a public class or function at module level."""

    def __init__(self, name: str, item_type: str, line_number: int):
        self.name = name
        self.item_type = item_type  # "class" or "function"
        self.line_number = line_number

    def __repr__(self) -> str:
        return f"PublicItem({self.name}, {self.item_type}, line {self.line_number})"
