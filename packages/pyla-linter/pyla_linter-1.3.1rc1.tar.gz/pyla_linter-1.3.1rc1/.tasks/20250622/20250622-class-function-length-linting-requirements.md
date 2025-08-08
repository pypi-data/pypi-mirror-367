# Feature

Add a pylama linting script that checks and enforces maximum length limits for classes and functions in Python code.

## Requirements:

- Implement a custom pylama linter plugin that analyzes Python class definitions
- Check that class definitions do not exceed 200 lines (configurable)
- Check that function/method definitions do not exceed 40 lines (configurable)
- Report violations with clear error messages including file path, line number, and actual line count
- Support configuration options to customize the maximum allowed lines for classes and functions
- Integrate seamlessly with existing pylama workflow and configuration
- Follow pylama plugin architecture and conventions
- Include proper error codes for class length violations (e.g., LA101) and function length violations (e.g., LA102)
- Support exclusion patterns for specific files or directories
- Handle nested classes and functions appropriately
- Count only actual code lines, excluding docstrings and comments from the line count
- Create new folder under `src/linters/` for the custom plugin and supporting code
- add to root module
