# Multiple Public Items Per File Linter Feature Specification

## Overview

This feature adds a new flake8 linter plugin that enforces the project's coding standard of having only one public item (class or function) per Python file. The linter will detect violations where multiple public classes or functions exist in a single file and report them as a single error per file, listing all violating items. This helps maintain clean, focused modules that are easier to understand, test, and maintain.

## Functional Requirements

1. **Detect Multiple Public Classes**: The linter shall identify when a Python file contains more than one class definition at the module level.

2. **Detect Multiple Public Functions**: The linter shall identify when a Python file contains more than one public function (functions without leading underscore) at the module level.

3. **Combined Violation Reporting**: The linter shall report a single error per file when multiple public items (classes and/or functions combined) are detected.

4. **Clear Error Messages**: Error messages shall list all violating public items with their names in the format: "File contains X public items: ClassName1, ClassName2, function_name1, function_name2"

5. **Line Number Reporting**: Errors shall be reported on line 1 of the file to indicate it's a file-level violation.

6. **Ignore Private Items**: The linter shall ignore any functions or methods with leading underscores (e.g., `_private_function`).

7. **Module-Level Scope Only**: The linter shall only check items at the module level, not nested classes or functions within classes.

8. **Error Code Assignment**: The linter shall use error code "EL101" (Multiple Public Functions) for violations.

## Technical Requirements

1. **Flake8 Integration**: Implement as a flake8 plugin following the established plugin interface pattern.

2. **AST-Based Analysis**: Use Python's Abstract Syntax Tree (AST) to analyze file structure and identify classes and functions.

3. **Configuration**: Rely on flake8's built-in configuration mechanisms (`exclude`, `per-file-ignores`) for file exclusions and whitelisting.

4. **Python Compatibility**: Support Python 3.8+ (matching project requirements).

5. **Architecture Consistency**: Follow the existing linter architecture pattern established by the length_checker plugin.

6. **No External Dependencies**: Use only Python standard library and flake8 for implementation.

## User Stories

1. **As a developer**, I want to be notified when I accidentally place multiple public classes or functions in a single file, so I can refactor them into separate modules.

2. **As a code reviewer**, I want automated detection of multiple public items per file violations, so I don't have to manually check each file during reviews.

3. **As a team lead**, I want to enforce the one-public-item-per-file standard across the codebase to maintain consistent code organization.

4. **As a developer**, I want to exclude certain files (like `__init__.py` or test files) from this check using standard flake8 configuration.

## Acceptance Criteria

1. The linter correctly identifies files with multiple public classes and reports them as violations.

2. The linter correctly identifies files with multiple public functions and reports them as violations.

3. The linter correctly identifies files with mixed public items (classes and functions) and reports them as violations.

4. Files with one or zero public items do not trigger any violations.

5. Private functions (with leading underscore) are not counted as public items.

6. Nested classes and functions within classes are not counted as module-level items.

7. Error messages clearly list all violating items with their names.

8. The plugin integrates seamlessly with flake8 and respects standard flake8 configuration options.

9. The plugin can be disabled for specific files using flake8's `per-file-ignores` configuration.

## Non-Goals

1. **Custom Configuration Options**: This linter will not implement its own exclusion patterns or whitelist mechanisms, relying instead on flake8's built-in configuration.

2. **Inline Suppression Comments**: The linter will not support custom inline comments for suppression beyond flake8's standard `# noqa` comments.

3. **Variable Detection**: The linter will not check for multiple public variables or constants at the module level.

4. **Import Analysis**: The linter will not analyze or report on import statements or their organization.

5. **Automatic Refactoring**: The linter will not provide automatic fixes or refactoring suggestions.

6. **Severity Levels**: Unlike the length checker, this linter will not have warning/error thresholds - all violations are errors.

## Technical Considerations

1. **AST Visitor Pattern**: Implement an AST visitor similar to the length_checker to traverse the syntax tree and collect public items.

2. **Error Reporting**: Follow flake8's error tuple format: `(line_number, column, message, error_code)`.

3. **Performance**: Single-pass AST traversal should be sufficient for detecting all public items.

4. **Testing**: Create comprehensive unit tests covering various file structures and edge cases.

5. **Plugin Registration**: Register the plugin with flake8 using the standard entry point mechanism.

6. **Code Organization**: Create a new subdirectory `src/linters/multiple_public_items/` following the existing pattern.

## Success Metrics

1. **Detection Accuracy**: 100% detection rate for files violating the one-public-item-per-file rule.

2. **False Positive Rate**: Zero false positives for compliant files.

3. **Performance Impact**: Negligible impact on flake8 execution time (< 5% increase).

4. **Integration Success**: Plugin works seamlessly with existing flake8 configurations and other linters.

5. **Error Clarity**: Developers can immediately understand violations and required actions from error messages.