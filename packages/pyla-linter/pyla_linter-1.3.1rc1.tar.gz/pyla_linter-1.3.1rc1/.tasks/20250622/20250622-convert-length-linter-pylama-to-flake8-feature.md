# Feature Specification: Convert Length Linter from Pylama to Flake8 Plugin

## Overview

**Problem Statement:** The current length linter is implemented as a pylama plugin, but the project needs to migrate to flake8 plugin architecture for better integration with standard Python linting workflows and broader ecosystem compatibility.

**Solution Summary:** Convert the existing fully-functional pylama-based length linter to a flake8 plugin while preserving all current functionality, configuration, and smart line counting logic.

**Primary Goals:**
- Maintain identical functionality and behavior of existing length linter
- Adopt flake8 plugin architecture and conventions
- Preserve existing configuration approach for backward compatibility
- Ensure seamless integration with flake8 command line interface

## Functional Requirements

1. **Core Length Checking**: Preserve existing smart line counting logic that excludes docstrings, comments, and empty lines
2. **Function Length Validation**: Check function length against configurable maximum (default: 40 lines)
3. **Class Length Validation**: Check class length against configurable maximum (default: 200 lines)
4. **AST-based Analysis**: Maintain current AST visitor pattern for code element extraction
5. **Nested Element Handling**: Continue supporting nested functions and classes with proper line range calculation
6. **Decorator Support**: Handle decorators correctly in line counting as currently implemented
7. **Configuration Loading**: Read settings from existing `[tool.pyla-linters]` section in pyproject.toml
8. **Command Line Integration**: Work seamlessly with standard flake8 command line interface
9. **Error Reporting**: Generate flake8-compatible error messages with file, line, and column information

## Technical Requirements

**Technology Stack:**
- **Plugin Framework**: flake8 plugin architecture
- **AST Processing**: Continue using Python's built-in `ast` module
- **Configuration**: Maintain `pyproject.toml` reading via existing config.py
- **Testing**: Preserve comprehensive test suite (75 tests) adapted for flake8
- **Dependencies**: Add flake8 as runtime dependency, remove pylama dependency

**Architecture Patterns:**
- **Plugin Interface**: Implement flake8's checker interface instead of pylama's plugin interface
- **Entry Points**: Use flake8 entry point system for plugin discovery
- **Error Codes**: Use custom `EL` prefix for errors (EL001, EL002) with `EW` reserved for future warnings
- **Modular Design**: Maintain current separation of concerns (plugin, ast_visitor, line_counter, config)

**Integration Requirements:**
- **Entry Point Configuration**: Register as `flake8.extension` in pyproject.toml
- **Standard Interface**: Implement flake8's expected `run()` method and error tuple format
- **Version Compatibility**: Support flake8 3.8+ for broad compatibility

## User Stories

1. **As a developer**, I want to run `flake8` and see length violations in the same output as other linting errors
2. **As a CI/CD pipeline**, I want to use standard flake8 commands without changing existing configuration
3. **As a project maintainer**, I want to configure function and class length limits via pyproject.toml
4. **As a code reviewer**, I want consistent error codes (EL001, EL002) that clearly identify length violations

## Acceptance Criteria

1. **Functional Compatibility**: All existing test cases pass with identical behavior
2. **Configuration Preservation**: Existing `[tool.pyla-linters]` configuration continues to work
3. **Error Code Migration**: Function length errors use EL001, class length errors use EL002
4. **Flake8 Integration**: Plugin discovered and executed automatically by flake8
5. **Command Line Interface**: `flake8` command reports length violations alongside other errors
6. **Test Coverage**: All 75 existing tests adapted and passing for flake8 architecture
7. **Dependency Management**: Clean removal of pylama dependency, addition of flake8 dependency
8. **Documentation**: Updated usage instructions reflecting flake8 instead of pylama

## Non-Goals

- **Backward Compatibility**: No requirement to support pylama plugin interface
- **Configuration Migration**: No automatic migration of configuration format
- **Feature Extensions**: No new length checking capabilities beyond current implementation
- **Multiple Plugin Support**: No requirement to support both pylama and flake8 simultaneously

## Technical Considerations

**Dependencies:**
- **Add**: `flake8 >= 3.8.0` as runtime dependency
- **Remove**: Any pylama-related dependencies
- **Preserve**: Current `pyla-logger` dependency for consistent logging

**Migration Strategy:**
- **Plugin Interface**: Convert `LengthCheckerPlugin.run()` to flake8's checker `run()` method
- **Error Format**: Change from pylama error objects to flake8 error tuples `(line, col, message, type)`
- **Entry Points**: Update from `pylama.linter` to `flake8.extension` registration
- **Testing**: Adapt test mocks and assertions for flake8 plugin testing patterns

**Architectural Notes:**
- **Core Logic Preservation**: AST visitor, line counter, and config modules remain largely unchanged
- **Plugin Wrapper**: Only the plugin.py file requires significant changes for flake8 interface
- **Error Codes**: Map LA101 → EL001 (function length), LA102 → EL002 (class length)
- **Configuration Access**: Maintain current config.py approach for reading pyproject.toml

**Integration Points:**
- **Flake8 Discovery**: Plugin must be discoverable via entry points
- **Standard Workflow**: Must integrate with existing flake8 command line and IDE integrations
- **Error Reporting**: Must produce errors in flake8's expected format for proper display

## Success Metrics

1. **Functional Parity**: 100% of existing tests pass with flake8 plugin
2. **Integration Success**: `flake8` command successfully discovers and runs the length checker
3. **Configuration Continuity**: Existing pyproject.toml configurations work without modification
4. **Error Consistency**: Length violations reported with clear EL001/EL002 codes
5. **Performance Maintenance**: No significant performance regression compared to pylama version
6. **Documentation Completeness**: Updated documentation enables easy adoption of flake8 version