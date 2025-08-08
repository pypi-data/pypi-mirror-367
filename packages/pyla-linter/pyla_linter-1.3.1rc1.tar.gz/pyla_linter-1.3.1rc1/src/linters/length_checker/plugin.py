"""Main plugin class implementing flake8 interface."""

import ast
from typing import Iterator, Optional, Tuple

from .ast_visitor import ASTVisitor
from .config import LengthCheckerConfig
from .statement_counter import StatementCounter


class LengthCheckerPlugin:
    """Flake8 plugin for checking function and class length."""

    name = "length_checker"
    version = "1.0.0"

    def __init__(self, tree: ast.AST, filename: str = "<stdin>"):
        """Initialize the plugin with AST tree and filename."""
        self.tree = tree
        self.filename = filename
        self.config = LengthCheckerConfig()
        self._config_loaded = False
        self._manual_config = False

    @classmethod
    def add_options(cls, option_manager):
        """Add command line options for the plugin."""
        option_manager.add_option(
            "--length-max-function",
            type=int,
            help="Maximum allowed function length (overrides config file)",
            parse_from_config=True,
        )
        option_manager.add_option(
            "--length-max-class",
            type=int,
            help="Maximum allowed class length (overrides config file)",
            parse_from_config=True,
        )

    @classmethod
    def parse_options(cls, options):
        """Parse command line options."""
        cls.max_function_length_override = getattr(options, "length_max_function", None)
        cls.max_class_length_override = getattr(options, "length_max_class", None)

    def set_config(self, config: LengthCheckerConfig) -> None:
        """Set configuration manually (prevents loading from pyproject.toml)."""
        self.config = config
        self._manual_config = True

    def run(self) -> Iterator[Tuple[int, int, str, str]]:
        """Run the length checker and yield flake8 errors."""
        self._load_config_if_needed()

        # Apply command line overrides if available
        if (
            hasattr(self.__class__, "max_function_length_override")
            and self.__class__.max_function_length_override
        ):
            self.config.max_function_length = self.__class__.max_function_length_override
        if (
            hasattr(self.__class__, "max_class_length_override")
            and self.__class__.max_class_length_override
        ):
            self.config.max_class_length = self.__class__.max_class_length_override

        try:
            yield from self._analyze_ast()
        except (SyntaxError, Exception):
            # Skip files with syntax errors or other processing issues
            pass

    def _analyze_ast(self) -> Iterator[Tuple[int, int, str, str]]:
        """Analyze the AST tree and yield flake8 errors."""
        visitor = ASTVisitor()
        visitor.visit(self.tree)

        # Get the source code to count statements
        source_code = self._get_source_code()
        if source_code is None:
            return

        source_lines = source_code.splitlines()
        statement_counter = StatementCounter(source_lines)

        for element in visitor.get_all_elements():
            yield from self._check_element_violations(element, statement_counter, source_code)

    def _load_config_if_needed(self) -> None:
        """Load configuration from pyproject.toml if not manually configured."""
        if not self._config_loaded and not self._manual_config:
            self.config = LengthCheckerConfig.from_pyproject_toml()
            self._config_loaded = True

    def _get_source_code(self) -> Optional[str]:
        """Get source code from filename."""
        if self.filename == "<stdin>":
            return None

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None

    def _check_element_violations(
        self, element, statement_counter, code: str
    ) -> Iterator[Tuple[int, int, str, str]]:
        """Check a single element for length violations and yield flake8 warnings and errors."""
        effective_statements = statement_counter.count_element_statements(element, code)

        if element.node_type == "class":
            threshold = self.config.max_class_length
            if effective_statements > threshold * 2:
                # Error at 2x threshold
                yield self._create_class_violation(element, effective_statements)
            elif effective_statements > threshold:
                # Warning at 1x threshold
                yield self._create_class_warning(element, effective_statements)
        elif element.node_type == "function":
            threshold = self.config.max_function_length
            if effective_statements > threshold * 2:
                # Error at 2x threshold
                yield self._create_function_violation(element, effective_statements)
            elif effective_statements > threshold:
                # Warning at 1x threshold
                yield self._create_function_warning(element, effective_statements)

    def _create_class_violation(
        self, element, effective_statements: int
    ) -> Tuple[int, int, str, str]:
        """Create a class length error tuple for flake8."""
        message = (
            f"EL002 Class '{element.name}' is {effective_statements} statements long, "
            f"exceeds error threshold of {self.config.max_class_length * 2}, recommend refactoring"
        )
        return (element.start_line, 0, message, "EL002")

    def _create_function_violation(
        self, element, effective_statements: int
    ) -> Tuple[int, int, str, str]:
        """Create a function length error tuple for flake8."""
        message = (
            f"EL001 Function '{element.name}' is {effective_statements} statements long, "
            f"exceeds error threshold of {self.config.max_function_length * 2}, "
            f"recommend refactoring"
        )
        return (element.start_line, 0, message, "EL001")

    def _create_class_warning(
        self, element, effective_statements: int
    ) -> Tuple[int, int, str, str]:
        """Create a class length warning tuple for flake8."""
        message = (
            f"WL002 Class '{element.name}' is {effective_statements} statements long, "
            f"exceeds warning threshold of {self.config.max_class_length}, recommend refactoring"
        )
        return (element.start_line, 0, message, "WL002")

    def _create_function_warning(
        self, element, effective_statements: int
    ) -> Tuple[int, int, str, str]:
        """Create a function length warning tuple for flake8."""
        message = (
            f"WL001 Function '{element.name}' is {effective_statements} statements long, "
            f"exceeds warning threshold of {self.config.max_function_length}, recommend refactoring"
        )
        return (element.start_line, 0, message, "WL001")
