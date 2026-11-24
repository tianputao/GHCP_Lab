# Coding Standards — Task API

These are the team conventions Copilot should follow. They mirror
`.github/copilot-instructions.md` and are included here so they can also be added to a
**Copilot Space** as curated context.

## TypeScript
- Strict mode. **No `any`** — use precise types or `unknown` with narrowing.
- `const` by default; `let` only when reassignment is required; never `var`.
- Explicit return types on every exported function.
- `async/await` only — no `.then()` chains or callbacks.

## Data access
- **Parameterized queries only** (`?` placeholders). Never build SQL with string
  concatenation or template literals.
- All queries live in a repository class under `src/repositories/`. No inline queries
  in route handlers.

## Errors
- Throw the classes in `src/errors.ts` (`NotFoundError`, `ValidationError`, `ConflictError`).
- Never throw bare `Error` or strings.
- Client responses use the envelope `{ "error": { "code", "message", "details?" } }`.
- Never leak stack traces, secrets, or internal messages to clients.

## HTTP (api/)
- `POST` → 201, `GET` → 200, `PUT` → 200, `DELETE` → 204.
- Not found → 404. Validation failure → 400 with field-level `details`.
- Handlers are async with `try/catch`; failures go through `sendError`.

## Documentation
- JSDoc on every exported function: `@param`, `@returns`, and `@throws` where relevant.

## Tests
- Arrange-Act-Assert.
- Cover happy path, error case, and at least one edge case per function.
- Assert against human-verified expected values — never assert a function equals its own
  output (tautological tests always pass and prove nothing).
