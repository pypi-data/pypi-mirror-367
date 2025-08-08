# Feature Specification: Add Warnings to Length Linter

## Overview

The length linter currently only reports errors when functions or classes exceed configured maximum lengths. This feature adds a warning level that triggers at the current threshold, while errors now trigger at double the threshold. This provides graduated feedback to developers, allowing them to receive early warnings before violations become errors.

**Problem Statement:** Current length linter provides binary feedback (pass/fail), making it difficult for developers to receive early warnings about approaching length limits.

**Solution Summary:** Implement a two-tier violation system with warnings at configured thresholds and errors at double those thresholds.

**Primary Goals:**
- Provide early warnings when functions/classes approach problematic lengths
- Maintain error reporting for severely oversized code elements
- Use existing configuration values for warning thresholds

## Functional Requirements

1. **Warning Detection**: When function or class length exceeds configured limit, report warning instead of error
   - Use warning codes WL001 (functions) and WL002 (classes)
   - Include actual length, threshold, and refactoring recommendation in message

2. **Error Detection**: When function or class length exceeds double the configured limit, report error
   - Use existing error codes EL001 (functions) and EL002 (classes)
   - Include actual length, threshold, and refactoring recommendation in message

3. **Message Format**: Both warnings and errors should use format:
   - `"[CODE] [Type] '[name]' is X lines long, exceeds [warning/error] threshold of Y, recommend refactoring"`

4. **Configuration Compatibility**: Current configuration values (max_function_length, max_class_length) become warning thresholds
   - Error thresholds automatically calculated as 2x warning thresholds
   - Existing command-line options control warning thresholds
   - No new configuration options required

## Technical Requirements

**Technology Stack:**
- Python 3.12+ with existing AST parsing and flake8 integration
- Current tomllib/tomli configuration loading
- Existing line counting logic with docstring/comment exclusion

**Integration Points:**
- Flake8 plugin interface for warning/error reporting
- Pylama compatibility for linting pipeline
- pyproject.toml configuration system

**Code Quality:**
- Maintain existing test coverage patterns
- Follow current naming conventions and file organization
- Use existing LineCounter and ASTVisitor components

## User Stories

**Story 1: Developer receives early warning**
- As a developer writing a function approaching 40 lines
- When I run the linter on a 45-line function
- Then I receive WL001 warning recommending refactoring
- And I can address the issue before it becomes an error

**Story 2: Developer receives error for severely long code**
- As a developer with an 85-line function (threshold 40)
- When I run the linter
- Then I receive EL001 error indicating severe length violation
- And I understand this requires immediate attention

**Story 3: Team maintains existing configuration**
- As a team with existing max_function_length=50 configuration
- When I upgrade to the new version
- Then warnings trigger at 50 lines and errors at 100 lines
- And no configuration changes are required

## Acceptance Criteria

1. **Warning Generation**: Functions/classes exceeding configured limits generate warnings with correct codes (WL001/WL002)

2. **Error Generation**: Functions/classes exceeding 2x configured limits generate errors with existing codes (EL001/EL002)

3. **Message Format**: All messages include element name, actual length, threshold type, threshold value, and refactoring recommendation

4. **Configuration Backward Compatibility**: Existing pyproject.toml configurations work without changes, with current limits becoming warning thresholds

5. **Command Line Compatibility**: Existing --length-max-function and --length-max-class options control warning thresholds

6. **Test Coverage**: All new warning/error logic covered by unit tests matching existing test patterns

## Non-Goals

- Adding new configuration options for separate warning/error thresholds
- Maintaining backward compatibility (as specified in requirements)
- Supporting custom warning/error threshold ratios other than 2:1
- Adding new command-line options beyond existing ones

## Technical Considerations

**Dependencies:**
- No new external dependencies required
- Existing AST parsing, line counting, and configuration systems sufficient

**Architecture Notes:**
- Modify `_check_element_violations` method in plugin.py to implement two-tier checking
- Update violation creation methods to support both warning and error generation
- Line counting logic remains unchanged
- Configuration loading logic remains unchanged

**Constraints:**
- Must maintain flake8 plugin interface compatibility
- Warning codes must follow W[L]### pattern for flake8 compatibility
- Error codes must remain EL001/EL002 for consistency

**Integration Points:**
- Flake8 expects tuple format: (line, column, message, code)
- Pylama processes flake8-compatible output
- Configuration system uses existing pyproject.toml structure

## Success Metrics

1. **Functional Success**: 
   - All functions/classes 1x-2x threshold generate warnings only
   - All functions/classes >2x threshold generate errors only
   - Message format matches specification exactly

2. **Compatibility Success**:
   - Existing configurations work without modification
   - Existing command-line options function correctly
   - All existing tests continue to pass

3. **Quality Success**:
   - New functionality covered by comprehensive unit tests
   - Code quality tools (black, isort, pylama, pyright) pass
   - No regressions in existing functionality