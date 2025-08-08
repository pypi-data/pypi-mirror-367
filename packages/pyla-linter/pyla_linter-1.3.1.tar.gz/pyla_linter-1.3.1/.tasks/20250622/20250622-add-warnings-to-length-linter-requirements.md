# Feature

Update the length checker linter to support warnings for function and class length violations, in addition to existing error reporting.

## Requirements:

- If function or class length exceeds the configured limit, report a warning instead of an error.
  - Use new warning codes WL001 and WL002 for these checks.
  - Update message to recommend refactoring to smaller functions or classes.
- If function or class length exceeds the double the configured limit, report an error.
  - Use existing error codes EL001 and EL002 for these checks.
  - Update message to recommend refactoring to smaller functions or classes.
- It's not necessary to maintain backward compatibility

## See Also:
- `src/linters/length_checker/` - Existing length checker implementation
- `src/linters/length_checker/config.py` - Current configuration system
- `src/linters/length_checker/plugin.py` - Pylama plugin integration