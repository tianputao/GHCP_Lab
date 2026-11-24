# SDD Constitution — GitHub Copilot Instructions

You are working in a **Specification-Driven Development (SDD)** workspace.

## Spec-First Rules (Non-Negotiable)
1. **Specification is the single source of truth**: Before writing or editing implementation code, read the approved OpenSpec change artifacts under `openspec/changes/<change>/` (`proposal.md`, `specs/**/spec.md`, `design.md`, `tasks.md`).
2. **Never silently guess ambiguous rules**: If a requirement, error code, rounding rule, or approval policy is unspecified, stop and run `/grill-me` to clarify with a human BEFORE coding.
3. **Preserve Brownfield Invariants**: Never alter existing error envelopes (`{ error: { code, message, details? } }`) or break existing endpoints unless explicitly approved in a modified spec delta.
4. **Integer Cents Only**: Financial values must be integer cents; never use floating-point subtraction on money.
5. **Traceability Required**: Every new test must reference its `REQ-XX` requirement ID from `specs/**/spec.md`.
6. **Verify Before Declaring Done**: Run `npm run typecheck`, unit/compliance tests, and `npm run evaluate:playground` (when working in `playground/`).
