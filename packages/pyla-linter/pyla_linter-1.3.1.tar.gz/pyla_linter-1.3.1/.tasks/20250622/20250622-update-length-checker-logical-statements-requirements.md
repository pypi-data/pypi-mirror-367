# Feature

Update the length checker linter to count logical statements of code instead of physical lines in the file.

## Requirements:

- Replace line counting logic in `LineCounter` class with AST-based logical statement counting
- Count logical statements including assignments, function calls, control structures, and expressions
- Exclude comments, docstrings, and empty lines from logical statement counting (maintain current exclusion behavior)
- Include decorators in logical statement count as they represent executable code
- Maintain existing warning (WL001/WL002) and error (EL001/EL002) violation levels with same thresholds
- Update error messages to reference "statements" instead of "lines" for clarity
- Preserve existing configuration options (`--length-max-function`, `--length-max-class`) with same default values
- Support nested functions and classes with accurate statement counting for each scope
- Handle compound statements (if/elif/else, try/except/finally) as separate logical units
- Count import statements, class definitions, and function definitions as single logical statements
- Update comprehensive test suite to validate logical statement counting instead of line counting
- Maintain backward compatibility with existing `pyproject.toml` configuration format
- Ensure flake8 integration continues to work without breaking changes

## See Also:
- `src/linters/length_checker/line_counter.py` - Core counting logic to be updated
- `src/linters/length_checker/plugin.py` - Main plugin class that uses the counter
- `src/tests/test_length_checker/` - Comprehensive test suite requiring updates