# Copilot Instructions — Task API

> Demo Step 1: Copy into `.github/copilot-instructions.md` to activate repo-wide standards.

## Architecture
- TypeScript project. Domain logic lives in `src/`; the HTTP layer lives in `api/`.
- Data access uses the **repository pattern** (`src/repositories/`). Routes never touch the database directly.

## Coding Standards
- TypeScript strict mode — never use `any`.
- Use `const` by default; use `let` only when reassignment is required; never `var`.
- Every exported function has an explicit return type.
- Use `async/await` — never raw `.then()` chains or callbacks.

## Database
- Use **parameterized queries only** (`?` placeholders) — never string concatenation.
- All database access goes through a repository class, never inline in a route handler.

## Error Handling
- Throw the custom error classes in `src/errors.ts` (extend `AppError`) — never bare `Error` or strings.
- API responses use one consistent envelope:
  `{ "error": { "code": "ERROR_CODE", "message": "Human readable message" } }`
- Never expose stack traces or internal details to clients.

## Documentation & Testing
- Exported functions need JSDoc with `@param`, `@returns`, and `@throws` where relevant.
- Follow Arrange-Act-Assert. Never write tautological assertions that compare a function's output against itself.
