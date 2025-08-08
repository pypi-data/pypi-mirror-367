# Feature

Add a new linter that detects multiple classes or public functions (without leading underscore) in a single Python file.

## Requirements:

- Detect when a Python file contains more than one class definition
- Identify public functions (functions without leading underscore) in module scope
- Report violation when a file contains multiple public items (classes or functions combined)
- Allow configuration to exclude certain patterns or files from this check
- Provide clear error messages indicating which items violate the one-item-per-file rule
- Support whitelisting specific files that are allowed to have multiple public items
- Integrate with flake8 as a custom linter plugin
- Follow existing linter patterns and architecture in the codebase
- Include line numbers and item names in violation reports

## See Also:
- `/src/linters/` - Existing linter implementations
- `CLAUDE.md` - Project coding standards mentioning one exported item per file rule