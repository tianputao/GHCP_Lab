# Coding Standards — Task API

These are the team conventions Copilot should follow. They mirror
`.github/copilot-instructions.md` and are included here so they can also be added to a
**Copilot Space** as curated context.

## Python
- Strict typing (`mypy --strict`). **No explicit `Any`** — use precise types or `object` with `isinstance()` narrowing.
- Complete type annotations on all public function parameters and return values.
- Never use `eval()`, `exec()`, or `subprocess(..., shell=True)`.

## Data access
- **Parameterized queries only** (`?` placeholders). Never build SQL with string
  concatenation or f-strings.
- All queries live in a repository class under `src/repositories/`. No inline queries
  in route handlers.

## Errors
- Raise the classes in `src/errors.py` (`NotFoundError`, `ValidationError`, `ConflictError`).
- Never raise bare `Exception` or strings.
- Client responses use the envelope `{ "error": { "code", "message", "details?" } }`.
- Never leak tracebacks, secrets, or internal messages to clients.

## HTTP (api/)
- `POST` → 201, `GET` → 200, `PUT` → 200, `DELETE` → 204.
- Not found → 404. Validation failure → 400 with field-level `details`.
- Handlers wrap logic in `try/except`; failures go through `send_error`.

## Documentation
- Google-style docstrings on every public function (`Args:`, `Returns:`, `Raises:`).

## Tests
- Arrange-Act-Assert.
- Cover happy path, error case, and at least one edge case per function.
- Assert against human-verified expected values — never assert a function equals its own
  output (tautological tests always pass and prove nothing).
