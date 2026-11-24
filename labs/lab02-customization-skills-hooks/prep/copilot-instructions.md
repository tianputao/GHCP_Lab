# Copilot Instructions — Task API

> Demo Step 1: Copy into `.github/copilot-instructions.md` to activate repo-wide standards.

## Architecture
- Python 3.11+ project managed with `uv`. Domain logic lives in `src/`; the HTTP layer lives in `api/`.
- Data access uses the **repository pattern** (`src/repositories/`). Routes never touch the database directly.

## Coding Standards
- Strict static typing (`mypy --strict`) — never use explicit `Any`; use precise types or `object` with `isinstance()` narrowing.
- Every public function and method must have complete parameter and return type annotations.
- Never use `eval()`, `exec()`, or `subprocess(..., shell=True)`.

## Database
- Use **parameterized queries only** (`?` placeholders) — never f-strings or string concatenation.
- All database access goes through a repository class, never inline in a route handler.

## Error Handling
- Raise the custom error classes in `src/errors.py` (subclass `AppError`) — never bare `Exception` or strings.
- API responses use one consistent envelope:
  `{ "error": { "code": "ERROR_CODE", "message": "Human readable message" } }`
- Never expose tracebacks or internal details to clients.

## Documentation & Testing
- Public functions need Google-style docstrings with `Args:`, `Returns:`, and `Raises:` where relevant.
- Follow Arrange-Act-Assert with `pytest`. Never write tautological assertions that compare a function's output against itself.
