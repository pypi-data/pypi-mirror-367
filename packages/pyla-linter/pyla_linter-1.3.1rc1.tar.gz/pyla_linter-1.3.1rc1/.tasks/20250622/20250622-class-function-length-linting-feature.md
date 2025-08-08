# Class and Function Length Linting Feature Specification

## Overview

This feature adds a standalone pylama plugin that enforces maximum length limits for Python classes and functions. The plugin will analyze Python source files to ensure that class definitions do not exceed 200 lines and function/method definitions do not exceed 40 lines (both configurable). This helps maintain code readability and encourages developers to write more modular, maintainable code by breaking down large classes and functions into smaller, focused components.

## Functional Requirements

1. **Line Counting Logic**
   - Count actual code lines in class and function definitions
   - Exclude all docstrings (module, class, and function/method level) from line counts
   - Exclude comment lines from line counts
   - Include nested classes and functions in their parent's line count
   - Count from the definition line (e.g., `class MyClass:`) to the last line of the class/function body

2. **Violation Detection**
   - Check all class definitions against a configurable maximum (default: 200 lines)
   - Check all function/method definitions against a configurable maximum (default: 40 lines)
   - Report each violation with standardized error codes (LA101 for classes, LA102 for functions)

3. **Error Reporting**
   - Generate clear error messages in the format: `error_code: Class/Function 'name' exceeds maximum length at filename:line_number (X/Y lines)`
   - Include the actual line count and configured maximum in error messages
   - Report violations at the line where the class/function is defined

4. **Configuration Support**
   - Allow users to configure maximum lines for classes via settings
   - Allow users to configure maximum lines for functions via settings
   - Support configuration through standard pylama configuration files (.pylama, setup.cfg, tox.ini, pyproject.toml)
   - Use sensible defaults when no configuration is provided (200 for classes, 40 for functions)

5. **File/Directory Exclusions**
   - Support pylama's standard exclusion patterns
   - Allow users to exclude specific files or directories from length checking
   - Respect .gitignore patterns if configured

6. **Plugin Integration**
   - Integrate seamlessly with existing pylama workflow
   - Support all pylama command-line options
   - Work with other pylama linters without conflicts
   - Provide proper plugin metadata (name, version, description)

## Technical Requirements

1. **Architecture**
   - Implement as a standalone pylama plugin installable via pip
   - Follow pylama's plugin architecture and conventions
   - Use Python AST (Abstract Syntax Tree) for accurate code analysis
   - Package name: `pylama-length` or similar

2. **Dependencies**
   - Python 3.12+ (matching the project's Python version)
   - pylama 8.4.1+ (for plugin compatibility)
   - No additional third-party dependencies if possible

3. **Code Organization**
   - Create plugin package structure following Python packaging standards
   - Include proper setup.py/pyproject.toml for pip installation
   - Implement plugin discovery mechanism for pylama
   - Follow Python naming conventions and best practices

4. **Performance**
   - Efficiently parse Python files using AST
   - Minimize memory usage for large codebases
   - Process files in parallel when possible (leverage pylama's capabilities)

## User Stories

1. **As a developer**, I want to be warned when my classes exceed 200 lines so that I can refactor them into smaller, more manageable components.

2. **As a developer**, I want to be warned when my functions exceed 40 lines so that I can break them down into smaller, more focused functions.

3. **As a team lead**, I want to configure custom line limits for our project to match our team's coding standards.

4. **As a developer**, I want to exclude certain files (e.g., generated code, migrations) from length checking while still checking the rest of my codebase.

5. **As a developer**, I want clear error messages that tell me exactly which class/function is too long and by how much, so I know how much refactoring is needed.

## Acceptance Criteria

1. Plugin correctly identifies classes exceeding the configured line limit
2. Plugin correctly identifies functions/methods exceeding the configured line limit
3. Line counting excludes all docstrings and comments as specified
4. Nested classes and functions count toward their parent's line total
5. Configuration options work correctly from all supported config file formats
6. Default values (200/40) are used when no configuration is provided
7. Error messages follow the specified format
8. Plugin integrates seamlessly with pylama command-line usage
9. Exclusion patterns work correctly for files and directories
10. Plugin can be installed via pip as a standalone package

## Non-Goals

1. **Not** implementing automatic refactoring suggestions
2. **Not** providing IDE integration (beyond what pylama already provides)
3. **Not** analyzing code complexity or other metrics (only line length)
4. **Not** supporting Python versions below 3.12
5. **Not** creating a general-purpose linting framework (specific to line length only)

## Technical Considerations

1. **AST Parsing**: Use Python's `ast` module for accurate parsing and line counting
2. **Configuration Loading**: Leverage pylama's existing configuration mechanisms
3. **Plugin Registration**: Follow pylama's plugin registration pattern using entry points
4. **Error Code Namespacing**: Use LA-prefixed codes to avoid conflicts with other linters
5. **Testing**: Include comprehensive unit tests for various Python code patterns
6. **Distribution**: Package as a standard Python package for PyPI distribution

## Success Metrics

1. Plugin successfully installs via pip and is discovered by pylama
2. All acceptance criteria pass in testing
3. Plugin processes Python files without significant performance impact
4. Error messages provide actionable information for developers
5. Configuration works intuitively across different file formats
6. No conflicts with existing pylama linters