"""Tests for the AST visitor that collects public items."""

import ast

from src.linters.multiple_public_items.ast_visitor import PublicItemsVisitor
from src.linters.multiple_public_items.public_item import PublicItem


class TestPublicItemsVisitor:
    """Test cases for PublicItemsVisitor."""

    def test_single_public_class(self):
        """Test detection of a single public class."""
        code = """
class MyClass:
    def method(self):
        pass
"""
        tree = ast.parse(code)
        visitor = PublicItemsVisitor()
        visitor.visit(tree)

        items = visitor.get_public_items()
        assert len(items) == 1
        assert items[0].name == "MyClass"
        assert items[0].item_type == "class"
        assert items[0].line_number == 2

    def test_single_public_function(self):
        """Test detection of a single public function."""
        code = """
def my_function():
    return 42
"""
        tree = ast.parse(code)
        visitor = PublicItemsVisitor()
        visitor.visit(tree)

        items = visitor.get_public_items()
        assert len(items) == 1
        assert items[0].name == "my_function"
        assert items[0].item_type == "function"
        assert items[0].line_number == 2

    def test_single_public_async_function(self):
        """Test detection of a single public async function."""
        code = """
async def my_async_function():
    return 42
"""
        tree = ast.parse(code)
        visitor = PublicItemsVisitor()
        visitor.visit(tree)

        items = visitor.get_public_items()
        assert len(items) == 1
        assert items[0].name == "my_async_function"
        assert items[0].item_type == "function"
        assert items[0].line_number == 2

    def test_multiple_public_items(self):
        """Test detection of multiple public items."""
        code = """
class FirstClass:
    pass

def first_function():
    pass

class SecondClass:
    pass

async def second_function():
    pass
"""
        tree = ast.parse(code)
        visitor = PublicItemsVisitor()
        visitor.visit(tree)

        items = visitor.get_public_items()
        assert len(items) == 4

        # Check first class
        assert items[0].name == "FirstClass"
        assert items[0].item_type == "class"
        assert items[0].line_number == 2

        # Check first function
        assert items[1].name == "first_function"
        assert items[1].item_type == "function"
        assert items[1].line_number == 5

        # Check second class
        assert items[2].name == "SecondClass"
        assert items[2].item_type == "class"
        assert items[2].line_number == 8

        # Check second async function
        assert items[3].name == "second_function"
        assert items[3].item_type == "function"
        assert items[3].line_number == 11

    def test_private_items_ignored(self):
        """Test that private items (starting with _) are ignored."""
        code = """
class _PrivateClass:
    pass

def _private_function():
    pass

class PublicClass:
    pass

def public_function():
    pass

async def _private_async():
    pass
"""
        tree = ast.parse(code)
        visitor = PublicItemsVisitor()
        visitor.visit(tree)

        items = visitor.get_public_items()
        assert len(items) == 2
        assert items[0].name == "PublicClass"
        assert items[1].name == "public_function"

    def test_nested_items_ignored(self):
        """Test that nested classes and functions are ignored."""
        code = """
class OuterClass:
    class InnerClass:
        pass

    def inner_method(self):
        def nested_function():
            pass
        return nested_function

def outer_function():
    class LocalClass:
        pass

    def local_function():
        pass

    return LocalClass
"""
        tree = ast.parse(code)
        visitor = PublicItemsVisitor()
        visitor.visit(tree)

        items = visitor.get_public_items()
        assert len(items) == 2
        assert items[0].name == "OuterClass"
        assert items[0].item_type == "class"
        assert items[1].name == "outer_function"
        assert items[1].item_type == "function"

    def test_empty_file(self):
        """Test that empty files produce no public items."""
        code = ""
        tree = ast.parse(code)
        visitor = PublicItemsVisitor()
        visitor.visit(tree)

        items = visitor.get_public_items()
        assert len(items) == 0

    def test_only_imports_and_constants(self):
        """Test files with only imports and constants."""
        code = """
import os
from typing import List

CONSTANT = 42
_PRIVATE_CONSTANT = "private"
"""
        tree = ast.parse(code)
        visitor = PublicItemsVisitor()
        visitor.visit(tree)

        items = visitor.get_public_items()
        assert len(items) == 0

    def test_mixed_public_and_private(self):
        """Test files with mix of public and private items."""
        code = """
_private_var = "private"

class PublicClass:
    def _private_method(self):
        pass

    def public_method(self):
        pass

def _private_function():
    pass

PUBLIC_CONSTANT = 42

def public_function():
    pass

class _PrivateClass:
    pass
"""
        tree = ast.parse(code)
        visitor = PublicItemsVisitor()
        visitor.visit(tree)

        items = visitor.get_public_items()
        assert len(items) == 2
        assert items[0].name == "PublicClass"
        assert items[0].item_type == "class"
        assert items[1].name == "public_function"
        assert items[1].item_type == "function"

    def test_public_item_representation(self):
        """Test the string representation of PublicItem."""
        item = PublicItem("TestClass", "class", 10)
        assert str(item) == "PublicItem(TestClass, class, line 10)"
