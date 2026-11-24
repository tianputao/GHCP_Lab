---
applyTo: "api/**"
---

# API-Specific Instructions

> Demo Step 1b: Copy into `.github/instructions/api.instructions.md`.
> Layers on top of `.github/copilot-instructions.md` ONLY for files matching `api/**`.

## Handlers
- Every route handler wraps its body in `try/except` and funnels failures through `send_error(res, err)` (`api/http.py`).

## Validation
- Validate every input before use following `api/validation.py` (collect field-level details and raise a single `ValidationError`).
- Never trust `req.body`, `req.params`, or `req.query` without validation.

## HTTP Conventions
- `POST` -> `201` with created resource
- `GET` -> `200` with resource or array
- `PUT` -> `200` with updated resource
- `DELETE` -> `204` with empty body
- Not found -> `404` error envelope; validation error -> `400` with field-level `details`
