"""AST visitor for counting logical statements within code elements."""

import ast


class StatementVisitor(ast.NodeVisitor):
    """Counts executable statements within a specific scope, excluding nested functions/classes."""

    def __init__(self):
        """Initialize the visitor."""
        self.statement_count = 0
        self._analyzing_class = False
        self._analyzing_function = False

    def count_statements_in_element(self, element_node: ast.AST) -> int:
        """Count statements in a specific code element (function or class).

        Args:
            element_node: The AST node for the function or class to analyze

        Returns:
            Number of statements in the element
        """
        self.statement_count = 0

        # Count the definition itself
        self.statement_count += 1

        # Set context based on what we're analyzing
        if isinstance(element_node, ast.ClassDef):
            self._analyzing_class = True
        else:
            self._analyzing_function = True

        # Visit the body of the element
        if hasattr(element_node, "body"):
            body = getattr(element_node, "body", [])
            for child_node in body:
                self.visit(child_node)

        return self.statement_count

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        # Count the function definition itself
        self.statement_count += 1

        # If we're analyzing a class, visit the method body
        # If we're analyzing a function, skip nested function bodies
        if self._analyzing_class:
            # This is a method in the class, visit its body
            for child_node in node.body:
                self.visit(child_node)
        # If analyzing a function, don't visit nested functions
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition."""
        # Count the function definition itself
        self.statement_count += 1

        # If we're analyzing a class, visit the method body
        # If we're analyzing a function, skip nested function bodies
        if self._analyzing_class:
            # This is a method in the class, visit its body
            for child_node in node.body:
                self.visit(child_node)
        # If analyzing a function, don't visit nested functions
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition - skip nested class content."""
        # Count the class definition itself
        self.statement_count += 1
        # Don't visit nested class bodies regardless of context
        return

    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit assignment statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """Visit augmented assignment statement (+=, -=, etc.)."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Visit annotated assignment statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        """Visit return statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_Yield(self, node: ast.Yield) -> None:
        """Visit yield expression - don't count separately as it's part of an Expr."""
        # Yield expressions are wrapped in Expr nodes, so don't double count
        self.generic_visit(node)

    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:
        """Visit yield from statement - don't count separately as it's part of an Expr."""
        # YieldFrom expressions are wrapped in Expr nodes, so don't double count
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        """Visit expression statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_Pass(self, node: ast.Pass) -> None:
        """Visit pass statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_Break(self, node: ast.Break) -> None:
        """Visit break statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_Continue(self, node: ast.Continue) -> None:
        """Visit continue statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from import statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        """Visit assert statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_Delete(self, node: ast.Delete) -> None:
        """Visit delete statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        """Visit raise statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global) -> None:
        """Visit global statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        """Visit nonlocal statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        """Visit if statement - count as one statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Visit for loop - count as one statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        """Visit async for loop - count as one statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        """Visit while loop - count as one statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        """Visit with statement - count as one statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        """Visit async with statement - count as one statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        """Visit try statement - count as one statement."""
        self.statement_count += 1
        self.generic_visit(node)

    def get_statement_count(self) -> int:
        """Get the total count of statements found."""
        return self.statement_count
