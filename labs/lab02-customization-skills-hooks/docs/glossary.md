# Glossary & Domain Knowledge — Task API

Curated domain context. Paste a few of these lines into a Copilot Space note during Demo 3
to show how Spaces ground answers in *your* vocabulary.

## Terms
- **Task** — a unit of work with a title, optional description, status, and tags.
- **Status** — one of `todo`, `in_progress`, `done`. The only valid lifecycle states.
- **Tag** — a free-form string label on a task; tasks may have many. Filtering uses
  `GET /tasks?tag=<value>`.
- **Repository** — the class that owns all data access for an entity. The *only* place
  queries run.
- **Error envelope** — the single JSON shape all errors serialize to:
  `{ "error": { "code", "message", "details?" } }`.

## Conventions worth knowing
- IDs are server-generated UUID v4 strings; clients never supply an id.
- Timestamps are ISO-8601 strings in **UTC** (`createdAt`, `updatedAt`).
- Titles are 1–200 characters and are trimmed on input.
- "Soft delete" is **not** used — `DELETE` removes the row and returns 204.

## Example questions to ask a Space built on this repo
- "What statuses can a task have, and where is that enforced?"
- "Show me how to add a new field to Task end-to-end, following our conventions."
- "What is our error-handling pattern? Show a compliant route handler."
