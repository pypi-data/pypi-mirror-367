"""Unit tests for the StatementVisitor class."""

import ast

from src.linters.length_checker.statement_visitor import StatementVisitor


class TestStatementVisitor:
    """Test the AST statement counting functionality."""

    def test_simple_assignment_statements(self):
        """Test counting simple assignment statements."""
        code = """def test_function():
    x = 1
    y = 2
    z = x + y
    return z"""

        tree = ast.parse(code)
        function_def = tree.body[0]  # The function definition

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, x=1, y=2, z=x+y, return z = 5 statements
        assert count == 5

    def test_augmented_assignment_statements(self):
        """Test counting augmented assignment statements."""
        code = """def test_function():
    x = 10
    x += 5
    x -= 2
    x *= 3
    return x"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, x=10, x+=5, x-=2, x*=3, return x = 6 statements
        assert count == 6

    def test_annotated_assignment_statements(self):
        """Test counting annotated assignment statements."""
        code = """def test_function():
    x: int = 1
    y: str = "hello"
    z: list = []
    return x, y, z"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, x:int=1, y:str="hello", z:list=[], return = 5 statements
        assert count == 5

    def test_expression_statements(self):
        """Test counting expression statements."""
        code = """def test_function():
    print("hello")
    len([1, 2, 3])
    "docstring"
    42
    return None"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, print(), len(), "docstring", 42, return = 6 statements
        assert count == 6

    def test_control_flow_statements(self):
        """Test counting control flow statements."""
        code = """def test_function():
    pass
    break
    continue
    return 42"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, pass, break, continue, return = 5 statements
        assert count == 5

    def test_import_statements(self):
        """Test counting import statements."""
        code = """def test_function():
    import os
    from sys import path
    import json, ast
    return os.getcwd()"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, import os, from sys import path, import json,ast, return = 5 statements
        assert count == 5

    def test_other_statements(self):
        """Test counting assert, delete, raise, global, nonlocal statements."""
        code = """def test_function():
    global x
    nonlocal y
    assert True
    del some_var
    raise ValueError("test")"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, global, nonlocal, assert, del, raise = 6 statements
        assert count == 6

    def test_compound_statements_count_as_one(self):
        """Test that compound statements (if, for, while, etc.) count as one statement each."""
        code = """def test_function():
    if True:
        print("true")
    else:
        print("false")

    for i in range(10):
        print(i)

    while True:
        break

    with open("file") as f:
        content = f.read()

    try:
        risky_operation()
    except Exception:
        handle_error()
    finally:
        cleanup()

    return True"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, if, print("true"), print("false"), for, print(i), while, break,
        # with, content=f.read(), try, risky_operation(), handle_error(), cleanup(), return
        # = 15 statements total
        assert count == 15

    def test_nested_function_exclusion(self):
        """Test that statements inside nested functions are not counted."""
        code = """def outer_function():
    x = 1

    def inner_function():
        y = 2
        z = 3
        return y + z

    result = inner_function()
    return result"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count only outer function statements: def outer, x=1, def inner,
        # result=inner(), return result = 5
        # Inner function definition counts as 1 statement, its contents should not be counted
        assert count == 5

    def test_nested_class_exclusion(self):
        """Test that statements inside nested classes are not counted."""
        code = """class OuterClass:
    x = 1

    class InnerClass:
        y = 2
        z = 3

        def inner_method(self):
            return self.y + self.z

    def outer_method(self):
        return self.x"""

        tree = ast.parse(code)
        class_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(class_def)

        # Should count only outer class statements: class def, x=1, class inner,
        # def outer_method, return self.x = 5
        # Inner class and its contents should not be counted
        assert count == 5

    def test_scope_boundary_handling(self):
        """Test that only the target function's statements are counted."""
        code = """def function_before():
    return 1

def target_function():
    x = 1
    y = 2
    return x + y

def function_after():
    return 3"""

        tree = ast.parse(code)
        target_function = tree.body[1]  # The middle function

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(target_function)

        # Should count only target function statements: def, x=1, y=2, return = 4
        assert count == 4

    def test_class_scope_boundary_handling(self):
        """Test scope boundary handling for classes."""
        code = """class TargetClass:
    class_var = 1

    def method1(self):
        return self.class_var

    def method2(self):
        x = 2
        return x

class OtherClass:
    other_var = 3"""

        tree = ast.parse(code)
        target_class = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(target_class)

        # Should count: class def, class_var=1, def method1, return self.class_var,
        # def method2, x=2, return x = 7 statements
        assert count == 7

    def test_multiple_statements_on_same_line(self):
        """Test handling of multiple statements on the same line."""
        code = """def test_function():
    x = 1; y = 2
    return x + y"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, x=1, y=2, return = 4 statements
        # Even though x=1 and y=2 are on the same line, they are separate AST nodes
        assert count == 4

    def test_empty_function(self):
        """Test counting statements in empty function."""
        code = """def empty_function():
    pass"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, pass = 2 statements
        assert count == 2

    def test_empty_class(self):
        """Test counting statements in empty class."""
        code = """class EmptyClass:
    pass"""

        tree = ast.parse(code)
        class_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(class_def)

        # Should count: class def, pass = 2 statements
        assert count == 2

    def test_async_functions(self):
        """Test counting statements in async functions."""
        code = """async def async_function():
    await some_operation()
    async for item in async_generator():
        process(item)
    async with async_context() as ctx:
        await ctx.do_something()
    return result"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: async def, await, async for, process(), async with, await, return = 7
        assert count == 7

    def test_complex_nested_structure(self):
        """Test complex nested structure with multiple levels."""
        code = """def complex_function():
    x = 1

    if x > 0:
        y = 2

        def nested_func():
            nested_var = 42
            return nested_var

        z = nested_func()
    else:
        z = 0

    class NestedClass:
        attr = "value"

        def nested_method(self):
            return self.attr

    return z"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def complex_function, x=1, if, y=2, def nested_func,
        # z=nested_func(), z=0, class NestedClass, return z = 9
        # Nested function and class contents should not be counted
        assert count == 9

    def test_generator_functions(self):
        """Test counting statements in generator functions."""
        code = """def generator_function():
    yield 1
    yield 2
    yield from [3, 4, 5]
    return"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, yield 1, yield 2, yield from, return = 5 statements
        assert count == 5

    def test_comprehensions_not_counted_separately(self):
        """Test that comprehensions are counted as expression statements, not separate functions."""
        code = """def test_function():
    list_comp = [x for x in range(10)]
    dict_comp = {x: x*2 for x in range(5)}
    set_comp = {x for x in range(10)}
    gen_comp = (x for x in range(10))
    return list_comp, dict_comp, set_comp, gen_comp"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, list_comp=, dict_comp=, set_comp=, gen_comp=, return = 6 statements
        # Comprehensions are expressions, not separate functions
        assert count == 6

    def test_lambda_functions_counted_as_expressions(self):
        """Test that lambda functions are counted as expression statements."""
        code = """def test_function():
    func = lambda x: x * 2
    result = func(5)
    return result"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, func=lambda, result=func(5), return = 4 statements
        assert count == 4

    def test_decorator_handling(self):
        """Test that decorators are not counted as separate statements."""
        code = """@decorator1
@decorator2
def decorated_function():
    return 42"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def (decorators are part of function definition), return = 2 statements
        assert count == 2

    def test_property_methods(self):
        """Test counting statements in property methods."""
        code = """class TestClass:
    @property
    def prop(self):
        return self._value

    @prop.setter
    def prop(self, value):
        self._value = value"""

        tree = ast.parse(code)
        class_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(class_def)

        # Should count: class def, def prop, return, def prop (setter), self._value = 5 statements
        assert count == 5

    def test_exception_handling_statements(self):
        """Test counting statements in exception handling blocks."""
        code = """def test_function():
    try:
        risky_operation()
        another_operation()
    except ValueError as e:
        handle_value_error(e)
        log_error(e)
    except Exception:
        handle_generic_error()
    finally:
        cleanup()
    return True"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, try, risky_operation(), another_operation(),
        # handle_value_error(e), log_error(e), handle_generic_error(), cleanup(), return = 9
        assert count == 9

    def test_context_manager_statements(self):
        """Test counting statements in context managers."""
        code = """def test_function():
    with open('file.txt') as f:
        content = f.read()
        lines = content.splitlines()

    with open('out.txt', 'w') as out, open('log.txt', 'a') as log:
        out.write(content)
        log.write("processed")

    return lines"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def, with, content=f.read(), lines=content.splitlines(),
        # with (multiple contexts), out.write(), log.write(), return = 8
        assert count == 8

    def test_performance_with_large_function(self):
        """Test performance with a function containing many statements."""
        # Generate a large function with many assignment statements
        statements = ["    x{} = {}".format(i, i) for i in range(100)]
        code = (
            "def large_function():\n"
            + "\n".join(statements)
            + "\n    return sum([{}])".format(", ".join("x{}".format(i) for i in range(100)))
        )

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def + 100 assignments + return = 102 statements
        assert count == 102

    def test_edge_case_function_with_only_nested_definitions(self):
        """Test function that only contains nested definitions."""
        code = """def container_function():
    def nested_func1():
        return 1

    class NestedClass:
        value = 42

    def nested_func2():
        return 2"""

        tree = ast.parse(code)
        function_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(function_def)

        # Should count: def container, def nested_func1, class NestedClass,
        # def nested_func2 = 4 statements
        assert count == 4

    def test_class_with_only_nested_definitions(self):
        """Test class that only contains nested definitions."""
        code = """class ContainerClass:
    class InnerClass1:
        pass

    def method1(self):
        pass

    class InnerClass2:
        value = 1"""

        tree = ast.parse(code)
        class_def = tree.body[0]

        visitor = StatementVisitor()
        count = visitor.count_statements_in_element(class_def)

        # Should count: class def, class InnerClass1, def method1, pass (in method1),
        # class InnerClass2 = 5 statements
        # Note: We count statements inside methods when analyzing a class,
        # but not inside nested classes
        assert count == 5
