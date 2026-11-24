# Copilot Instructions — Lab 05 Enterprise Capstone

## Tech Stack
- Node.js + Express + TypeScript (`"type": "module"`, strict mode ON, no `any`).

## Code Style
- Prefer `async/await` over raw `.then()` chains.
- Use named exports and concise JSDoc comments on exported functions.

## API Conventions
- Validate every input at the route boundary before use.
- Status codes: `201` created, `200` ok, `204` deleted, `400` validation error, `404` not found.
- Never build SQL or shell commands via string concatenation.

## Security
- Never use `eval()`, `Function(...)`, or dynamic code execution on caller input.
- Read secrets from environment variables; never hardcode credentials.

## Testing
- Use `node:test` + `node:assert/strict`.
- Assert against explicit human-verified values; never write tautological assertions.
