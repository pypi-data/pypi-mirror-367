# CLAUDE.md

## Project Overview

This is a set of Python linting tools to be used by flake8.

Use context7 MCP to access up-to-date documentation for third-party libraries.

## Development Setup

The project uses UV for dependency management and poethepoet for task running. Python 3.12 is required.

### Common Development Commands

```bash
uv sync
uv run poe quality   # Runs all quality checks (linting, type checking, formatting)
uv run pytest                           # Run all tests
```

## Architecture

### Directory Structure

Avoid "kitchen-sink" modules or folders, such as "helpers.py" or "/utils".

- `.circleci/` - CircleCI configuration files
- `.tasks/` - Feature specifications and implementation plans
- `src/` - Module root
- `src/linters/` - Source code for the various linting tools
- `src/tests/` - Unit tests for the linters

### External Integrations

- **OpenAI/LangChain**: AI-powered deck suggestions and content generation
- **PyLa Logger**: Structured logging for API requests and errors
- **CircleCI**: Continuous integration and deployment

## Quality Standards

### Coding Standards

- Document and test all code
- Do not write comments for obvious code
  - Use meaningful variable and function names instead
- Functions should be small and focused (max 40 lines)
  - Refactor large functions into smaller ones
- Classes should have a single responsibility and be small (max 200 lines)
  - Use composition over inheritance where possible
  - Refactor large classes into smaller ones
- One exported item (class, function, etc.) per file (exceptions require user approval)
- Write tests for behaviors and edge cases, not for style or formatting
- If exceptions are required, **STOP and ask for approval** before proceeding
- **Do not** do unrequested work
  - For example, do not add retry logic unless explicitly requested
  - If you think something is missing, **ask for approval** before adding it
- **ASK QUESTIONS** if you are unsure about anything
  - If you are not sure how to implement something, ask for clarification
  - If you are not sure if something is needed, ask for approval

### Naming Conventions
- Use snake_case for variables, functions, and methods
- "Private" variables and methods should start with an underscore (e.g., `_private_method`)
- Use CamelCase for classes and Pydantic models
- Use UPPER_CASE for constants
- File names should be lowercase with underscores (e.g., `create_topic.py`) that match the class or function they contain

### Testing

Write unit tests for all API endpoints and business logic. Use the `src/app/tests/` directory to organize tests by module.

Tests use pytest with async support. Test files follow the pattern `test_*.py` and are organized to mirror the source structure. Create `*.http` files in the `http_requests/` directory for all API endpoints to facilitate testing.

### Type Checking

Use Pyright for type checking. Ensure all code is type-annotated and passes type checks. Run `uv run pyright` to check types.

- Prefer built-in types (`list`, `dict`, etc.) over `typing.List`, `typing.Dict` unless necessary
- Use union operator for optional types (e.g., `str | None` instead of `Optional[str]`)
- FastApi dependencies should be type-annotated with `[Annotated(Type, Depends(...)]` for clarity
  - Do not use a default value of `None` for dependencies unless explicitly required

### Quality Tools

**Always run these tools before completing a task:**
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **Pyright**: Type checking
- **Pytest**: Testing

**NEVER ALLOW FAILING QUALITY CHECKS**
- Fix them
- If you cannot fix them, ask for help - **do not ignore them**
- It does not matter if the code works or if the failures are unrelated to your changes: **DO NOT COMPLETE THE TASK UNTIL ALL QUALITY CHECKS PASS**

## Configuration

Environment variables are documented in README.md. Key configs include Firebase, Google Cloud, and OpenAI credentials, plus optional emulator settings for local development.

## Third-Party Library Documentation

When working with third-party libraries, use the context7 MCP tool to get up-to-date documentation and examples. This ensures you have access to the latest API changes and best practices for libraries like FastAPI, Pydantic, LangChain, Firebase, Google Cloud services, and others used in this project.

## Asking Questions

- **Ask one question at a time**
- **Provide options for each question**

*Example question*
```
In case of multiple variations, should metadata be generated for all variations or only the first one?
- **Options:**
  - A) Generate metadata for all variations
  - B) Generate metadata only for the first variation
  - C) Do not generate metadata at all
```

**Remember to ask one question at a time and provide options for each question.**

## Git Branch Naming

Git branches should follow the naming convention `feature/kebab-case-name-of-feature`. Examples:
- `feature/add-user-authentication`
- `feature/implement-deck-suggestions`

## Prohibited Actions

- ❌ Shared "kitchen-sink" modules
- ❌ Hardcoded secrets (including file paths outside project root)
- ❌ Scope expansion without approval

<rules>
  <critical>NEVER bypass git pre-commit hooks, unit tests or quality checks.</critical>
  <critical>NEVER finish a task with failing unit tests or quality checks.</critical>
  <critical>NEVER, NEVER commit code with failing unit tests or quality checks.</critical>
  <critical>Write tests for new or modified functionality. Do not write tests for style or formatting.</critical>
  <critical>Never hardcode secrets or environment values, including file paths outside project root.</critical>
  <critical>Ensure all quality checks pass before marking a task complete. Do not proceed if any checks or tests fail.</critical>
  <important>Each "public" class or function should be in its own file, unless otherwise approved.</important>
  <important>Use context7 MCP tool to get up-to-date documentation and best practices for all third-party libraries.</important>
  <important>Ask questions for implementation details, clarifications, or when requirements are ambiguous.</important>
  <rule>Do not write comments for obvious code. Use meaningful variable and function names instead.</rule>
</rules>