# Architecture — Task API

A small, layered TypeScript service for managing tasks. Used in the GH-300 Week 7 demo
as a realistic, consistent codebase for Copilot to learn from and extend.

## Layers

```
HTTP (api/)            →  routes, validation, error→envelope translation
  └─ Domain (src/)     →  types, custom errors
       └─ Data (src/)  →  repository pattern over a data store
```

- **`api/`** — the HTTP surface. Route handlers are thin: validate input, call a
  repository, map the result (or error) to an HTTP response. Path-scoped instructions
  (`applyTo: "api/**"`) enforce status-code and validation conventions here.
- **`src/repositories/`** — the only place that touches the database. Each method
  documents its equivalent **parameterized SQL** (`?` placeholders).
- **`src/errors.ts`** — every error extends `AppError` and carries a stable `code` and an
  HTTP `status`, so the API layer can produce a consistent error envelope without leaking
  internals.

## Key decisions (ADR-style)

1. **Repository pattern, always.** Routes never run queries directly. This keeps data
   access testable and makes the "parameterized queries only" rule enforceable in one place.
2. **One error envelope.** All failures serialize to
   `{ "error": { "code", "message", "details?" } }`. No stack traces cross the wire.
3. **No runtime web framework in the demo.** `api/http.ts` defines minimal request/response
   types so the repo type-checks with zero install. Swapping in Express later is mechanical.
4. **Server-assigned identity & time.** `id`, `createdAt`, `status` are set by the server,
   never trusted from the client.

## Request flow (create a task)

1. `POST /tasks` → `validateCreateTask(req.body)` (400 on failure).
2. `TaskRepository.create(input)` assigns id/timestamps, inserts, returns the task.
3. Handler responds `201` with the created task.
4. Any thrown `AppError` → `sendError` → correct status + envelope.
