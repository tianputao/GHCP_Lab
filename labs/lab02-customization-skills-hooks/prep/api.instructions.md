---
applyTo: "api/**"
---

# API-Specific Instructions

> Demo Step 1b: Copy into `.github/instructions/api.instructions.md`.
> Layers on top of `.github/copilot-instructions.md` ONLY for files matching `api/**`.

## Handlers
- Every route handler wraps its body in `try/catch` and funnels failures through `sendError(res, err)` (`api/http.ts`).

## Validation
- Validate every input before use following `api/validation.ts` (collect field-level details and throw a single `ValidationError`).
- Never trust `req.body`, `req.params`, or `req.query` without validation.

## HTTP Conventions
- `POST` -> `201` with created resource
- `GET` -> `200` with resource or array
- `PUT` -> `200` with updated resource
- `DELETE` -> `204` with empty body
- Not found -> `404` error envelope; validation error -> `400` with field-level `details`
