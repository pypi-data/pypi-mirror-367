"""Performance tests for multiple public items plugin."""

import ast
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List, Tuple

from src.linters.multiple_public_items.plugin import MultiplePublicItemsPlugin


def run_plugin_on_code(code: str, filename: str = "test.py") -> List[Tuple[int, int, str, str]]:
    """Helper function to run the plugin on code and return error tuples."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    plugin = MultiplePublicItemsPlugin(tree, filename)
    return list(plugin.run())


def generate_large_file_content(num_functions: int = 1000, num_classes: int = 100) -> str:
    """Generate content for a large Python file with many functions and classes."""
    content = ['"""Large file for performance testing."""', ""]

    # Add many functions
    for i in range(num_functions):
        content.extend(
            [f"def function_{i}():", f'    """Function number {i}."""', f"    return {i}", ""]
        )

    # Add many classes
    for i in range(num_classes):
        content.extend(
            [
                f"class Class_{i}:",
                f'    """Class number {i}."""',
                "    ",
                "    def __init__(self):",
                f"        self.value = {i}",
                "    ",
                f"    def method_{i}(self):",
                "        return self.value * 2",
                "",
            ]
        )

    return "\n".join(content)


def generate_deeply_nested_content(depth: int = 10) -> str:
    """Generate content with deeply nested structures."""
    content = ['"""File with deeply nested structures."""', ""]

    # Create nested class structure
    indent = ""
    for i in range(depth):
        content.append(f"{indent}class Level{i}:")
        content.append(f'{indent}    """Class at level {i}."""')
        content.append(f"{indent}    ")
        content.append(f"{indent}    def method_{i}(self):")
        content.append(f"{indent}        return {i}")
        content.append(f"{indent}    ")
        indent += "    "

    # Add public function at module level
    content.extend(
        ["def public_function():", '    """A public function at module level."""', "    return 42"]
    )

    return "\n".join(content)


class TestPerformanceBasic:
    """Basic performance tests."""

    def test_large_file_performance(self):
        """Test plugin performance with large files."""
        # Generate a large file with many functions and classes
        large_content = generate_large_file_content(num_functions=500, num_classes=50)

        # Time the plugin execution
        start_time = time.time()
        errors = run_plugin_on_code(large_content, "large_test.py")
        end_time = time.time()

        execution_time = end_time - start_time

        # Should complete within reasonable time (less than 5 seconds)
        assert execution_time < 5.0, f"Plugin took too long: {execution_time:.2f} seconds"

        # Should detect multiple public items
        assert len(errors) == 1
        assert "EL101" in errors[0][2]

        # Should contain references to multiple items
        error_message = errors[0][2]
        assert "550" in error_message  # Total number of public items (500 functions + 50 classes)

    def test_deeply_nested_performance(self):
        """Test plugin performance with deeply nested structures."""
        # Generate deeply nested content
        nested_content = generate_deeply_nested_content(depth=50)

        # Time the plugin execution
        start_time = time.time()
        errors = run_plugin_on_code(nested_content, "nested_test.py")
        end_time = time.time()

        execution_time = end_time - start_time

        # Should complete within reasonable time (less than 2 seconds)
        assert execution_time < 2.0, f"Plugin took too long: {execution_time:.2f} seconds"

        # Should detect violations (nested classes create one public Level0 class +
        # one public function)
        assert len(errors) == 1
        assert "EL101" in errors[0][2]

    def test_many_small_files_performance(self):
        """Test plugin performance with many small files."""
        # Create many small files with violations
        files_content = []
        for i in range(100):
            content = f"""
def function_{i}_a():
    return {i}

def function_{i}_b():
    return {i} * 2
"""
            files_content.append(content)

        # Time the plugin execution on all files
        start_time = time.time()
        total_errors = 0

        for i, content in enumerate(files_content):
            errors = run_plugin_on_code(content, f"test_{i}.py")
            total_errors += len(errors)

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete within reasonable time (less than 3 seconds)
        assert execution_time < 3.0, f"Plugin took too long: {execution_time:.2f} seconds"

        # Should detect violations in all files
        assert total_errors == 100  # One error per file


class TestPerformanceEdgeCases:
    """Performance tests for edge cases."""

    def test_very_long_function_names(self):
        """Test plugin performance with very long function names."""
        long_name = "a" * 1000  # Very long function name
        content = f"""
def {long_name}_1():
    return 1

def {long_name}_2():
    return 2
"""

        start_time = time.time()
        errors = run_plugin_on_code(content, "long_names.py")
        end_time = time.time()

        execution_time = end_time - start_time

        # Should complete quickly even with long names
        assert execution_time < 1.0, f"Plugin took too long: {execution_time:.2f} seconds"

        # Should detect violation
        assert len(errors) == 1
        assert "EL101" in errors[0][2]

    def test_many_empty_functions(self):
        """Test plugin performance with many empty functions."""
        content = []
        for i in range(1000):
            content.extend([f"def empty_function_{i}():", "    pass", ""])

        code = "\n".join(content)

        start_time = time.time()
        errors = run_plugin_on_code(code, "empty_functions.py")
        end_time = time.time()

        execution_time = end_time - start_time

        # Should complete within reasonable time
        assert execution_time < 3.0, f"Plugin took too long: {execution_time:.2f} seconds"

        # Should detect violation
        assert len(errors) == 1
        assert "EL101" in errors[0][2]

    def test_mixed_large_content(self):
        """Test plugin performance with mixed large content."""
        content = ['"""Mixed large content for performance testing."""', ""]

        # Add many imports
        for i in range(100):
            content.append(f"import module_{i}")

        content.append("")

        # Add many constants
        for i in range(200):
            content.append(f"CONSTANT_{i} = {i}")

        content.append("")

        # Add some public functions
        for i in range(50):
            content.extend(
                [
                    f"def public_function_{i}():",
                    f'    """Public function {i}."""',
                    f"    return CONSTANT_{i} if {i} < 200 else 0",
                    "",
                ]
            )

        # Add some private functions
        for i in range(100):
            content.extend(
                [
                    f"def _private_function_{i}():",
                    f'    """Private function {i}."""',
                    f"    return {i}",
                    "",
                ]
            )

        # Add some classes with many methods
        for i in range(10):
            content.extend([f"class LargeClass_{i}:", f'    """Large class {i}."""', "    "])

            # Add many methods to each class
            for j in range(20):
                content.extend([f"    def method_{j}(self):", f"        return {i} * {j}", "    "])

            content.append("")

        code = "\n".join(content)

        start_time = time.time()
        errors = run_plugin_on_code(code, "mixed_large.py")
        end_time = time.time()

        execution_time = end_time - start_time

        # Should complete within reasonable time
        assert execution_time < 5.0, f"Plugin took too long: {execution_time:.2f} seconds"

        # Should detect violation (50 functions + 10 classes = 60 public items)
        assert len(errors) == 1
        assert "EL101" in errors[0][2]
        assert "60" in errors[0][2]


class TestPerformanceRegression:
    """Regression tests to ensure performance doesn't degrade."""

    def test_baseline_performance(self):
        """Establish baseline performance for small files."""
        simple_content = """
def function_one():
    return 1

def function_two():
    return 2
"""

        # Run multiple times to get average
        times = []
        errors = None
        for _ in range(10):
            start_time = time.time()
            errors = run_plugin_on_code(simple_content, "baseline.py")
            end_time = time.time()
            times.append(end_time - start_time)

        average_time = sum(times) / len(times)

        # Should be very fast for simple files
        assert average_time < 0.1, f"Baseline performance too slow: {average_time:.4f} seconds"

        # Should detect violation
        assert errors is not None and len(errors) == 1

    def test_scaling_performance(self):
        """Test that performance scales reasonably with file size."""
        # Test with increasing file sizes
        sizes = [10, 50, 100, 200, 500]
        times = []

        for size in sizes:
            content = generate_large_file_content(num_functions=size, num_classes=0)

            start_time = time.time()
            errors = run_plugin_on_code(content, f"scale_{size}.py")
            end_time = time.time()

            times.append(end_time - start_time)

            # Should always detect violation
            assert len(errors) == 1

        # Performance should scale reasonably (not exponentially)
        # Largest file should not take more than 50x the smallest file
        # (allowing for timing variance). All times should be reasonable (< 0.1 seconds)
        assert times[-1] < 0.1, f"Performance too slow for largest file: {times[-1]:.4f} seconds"
        assert times[-1] < times[0] * 50, f"Performance scaling issue: {times}"

    def test_memory_usage_reasonable(self):
        """Test that memory usage is reasonable for large files."""
        # This is a basic test - in a real scenario you might use memory profiling tools
        large_content = generate_large_file_content(num_functions=1000, num_classes=100)

        # Plugin should not crash or cause memory issues
        errors = run_plugin_on_code(large_content, "memory_test.py")

        # Should complete successfully
        assert len(errors) == 1
        assert "EL101" in errors[0][2]


class TestPerformanceIntegration:
    """Integration performance tests with flake8."""

    def test_flake8_integration_performance(self):
        """Test performance when running through flake8."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a large file
            large_content = generate_large_file_content(num_functions=200, num_classes=20)
            test_file = temp_path / "large_integration.py"
            test_file.write_text(large_content)

            # Time flake8 execution
            start_time = time.time()
            result = subprocess.run(
                ["uv", "run", "flake8", "--select=EL101", str(test_file)],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )
            end_time = time.time()

            execution_time = end_time - start_time

            # Should complete within reasonable time
            assert (
                execution_time < 10.0
            ), f"Flake8 integration took too long: {execution_time:.2f} seconds"

            # Should detect violation
            assert result.returncode != 0
            assert "EL101" in result.stdout
