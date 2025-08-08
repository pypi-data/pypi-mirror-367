# Feature Specification: Update Length Checker to Count Logical Statements

## Overview

**Problem Statement:** The current length checker linter counts physical lines of code, which can be misleading when evaluating code complexity. A function with many short lines may be flagged as too long, while a function with fewer but more complex logical statements may pass undetected.

**Solution Summary:** Replace the line-based counting mechanism with AST-based logical statement counting that focuses on executable statements, providing a more accurate measure of code complexity.

**Primary Goals:**
- Improve accuracy of code complexity measurement
- Maintain backward compatibility with existing configuration
- Preserve flake8 integration without breaking changes
- Provide clearer feedback to developers about code structure

## Functional Requirements

1. **AST-Based Statement Counting:** Replace `LineCounter.count_element_lines()` method to traverse AST nodes and count executable statements instead of physical lines

2. **Executable Statement Types:** Count only these AST node types as logical statements:
   - Assignment statements (`ast.Assign`, `ast.AnnAssign`, `ast.AugAssign`)
   - Expression statements (`ast.Expr` containing function calls, method calls, etc.)
   - Control flow statements (`ast.Return`, `ast.Break`, `ast.Continue`, `ast.Pass`, `ast.Raise`)
   - Import statements (`ast.Import`, `ast.ImportFrom`)
   - Delete statements (`ast.Delete`)
   - Assert statements (`ast.Assert`)
   - Context management (`ast.With`, `ast.AsyncWith`)
   - Exception handling (`ast.Try` block and each handler/finally clause counted separately)
   - Conditional statements (`ast.If`, `ast.Elif`, `ast.Else` each counted as separate logical units)
   - Loop statements (`ast.For`, `ast.AsyncFor`, `ast.While`)

3. **Exclusion Rules:** Continue excluding from counts:
   - Comments and docstrings (maintain current behavior)
   - Empty lines and whitespace-only lines
   - Class and function definition headers (not executable statements)
   - Decorator lines (not executable statements)

4. **Nested Scope Handling:** Accurately count statements within each function/class scope without double-counting statements in nested functions/classes

5. **Compound Statement Logic:** Handle compound statements correctly:
   - `if/elif/else` chains: count each branch as separate logical statement
   - `try/except/finally`: count try block, each except handler, and finally block separately
   - Loop bodies: count the loop statement itself, not the iteration

6. **Error Message Updates:** Update violation messages to reference "statements" instead of "lines":
   - `EL001`: "Function 'X' has Y statements, exceeds error threshold of Z statements"
   - `WL001`: "Function 'X' has Y statements, exceeds warning threshold of Z statements"
   - `EL002`: "Class 'X' has Y statements, exceeds error threshold of Z statements"
   - `WL002`: "Class 'X' has Y statements, exceeds warning threshold of Z statements"

7. **Configuration Preservation:** Maintain all existing configuration options with same names and default values:
   - `max_function_length: 40` (now means 40 statements instead of 40 lines)
   - `max_class_length: 200` (now means 200 statements instead of 200 lines)
   - Command line overrides: `--length-max-function`, `--length-max-class`

## Technical Requirements

1. **Core Architecture Changes:**
   - Replace line counting logic in `src/linters/length_checker/line_counter.py`
   - Rename class from `LineCounter` to `StatementCounter` for clarity
   - Update method name from `count_element_lines()` to `count_element_statements()`

2. **AST Traversal Implementation:**
   - Create new AST visitor specifically for statement counting within code elements
   - Handle scope boundaries correctly to avoid counting nested function/class statements
   - Implement statement type detection using isinstance checks on AST nodes

3. **Integration Points:**
   - Update `plugin.py` to use new `StatementCounter` class
   - Modify error message generation in plugin violation methods
   - Ensure flake8 interface remains unchanged (same error codes and format)

4. **Backward Compatibility:**
   - Maintain existing `pyproject.toml` configuration section `[tool.pyla-linters]`
   - Preserve command line argument names and behavior
   - Keep same error codes (EL001, EL002, WL001, WL002)

5. **Dependencies:**
   - Continue using Python's built-in `ast` module
   - Maintain existing dependency on `tomllib`/`tomli` for configuration
   - No new external dependencies required

## User Stories

1. **As a developer**, I want the linter to accurately measure code complexity so that I can identify truly complex functions that need refactoring, not just functions with many short lines.

2. **As a team lead**, I want consistent complexity measurement across the codebase so that code review standards are based on logical complexity rather than formatting style.

3. **As a CI/CD maintainer**, I want the linter to continue working with existing flake8 configurations without requiring migration or setup changes.

## Acceptance Criteria

1. **Functional Correctness:**
   - ✅ Statement counting accurately identifies executable statements using AST analysis
   - ✅ Nested functions and classes are handled correctly with proper scope isolation
   - ✅ Compound statements (if/elif/else, try/except/finally) are counted as separate logical units
   - ✅ Comments, docstrings, and decorators are excluded from statement counts

2. **Integration Stability:**
   - ✅ All existing flake8 integration points continue to work unchanged
   - ✅ Error codes and message format remain consistent with current implementation
   - ✅ Configuration loading from `pyproject.toml` and command line works identically

3. **Performance:**
   - ✅ Statement counting performance is comparable to or better than line counting
   - ✅ Memory usage remains within acceptable bounds for large files

4. **Test Coverage:**
   - ✅ All existing tests updated to validate statement counting instead of line counting
   - ✅ New test cases cover edge cases specific to statement counting (compound statements, nested scopes)
   - ✅ Test suite maintains 100% coverage of modified code paths

## Non-Goals

- **Not changing default thresholds:** Keep 40/200 defaults even though they now represent statements
- **Not adding new error codes:** Maintain existing EL001, EL002, WL001, WL002 codes
- **Not supporting mixed counting modes:** No option to switch between line and statement counting
- **Not changing configuration format:** No new configuration options or sections required

## Technical Considerations

1. **AST Node Scope Management:** Implement careful tracking of current function/class context to avoid counting statements from nested definitions in parent scope counts

2. **Error Handling:** Maintain existing error handling patterns for syntax errors and file access issues, ensuring graceful degradation

3. **Testing Strategy:** Update the comprehensive existing test suite (2,500+ lines) to validate statement counting behavior while preserving all existing test scenarios

4. **Performance Optimization:** AST traversal may be slightly more expensive than line counting, but should remain negligible for typical file sizes

5. **Edge Cases:** Handle malformed AST nodes, incomplete statement constructs, and Python version compatibility gracefully

## Success Metrics

1. **Accuracy Improvement:** Statement-based violations should better correlate with actual code complexity compared to line-based violations

2. **Backward Compatibility:** Zero breaking changes for existing users - all current configurations and integrations continue working

3. **Test Suite Coverage:** 100% test coverage maintained with all edge cases covered

4. **Performance:** Statement counting completes within 110% of current line counting performance

5. **Developer Adoption:** Clear, understandable error messages that help developers identify truly complex code sections for refactoring