---
name: sdd-verify
description: "Audit Spec-to-Code and Spec-to-Test compliance for an OpenSpec change, flagging missing requirements, architectural drift, tautological tests, or out-of-scope edits. Use before opening a PR or archiving a change."
---

# SDD Reverse Verification Auditor

## Checklist
1. Run `uv run python scripts/validate_openspec.py` (optionally add `--use-npx` if Node.js is installed) to verify OpenSpec schema validity.
2. Read every `REQ-XX` in `openspec/changes/<change>/specs/**/spec.md`.
3. For each `REQ-XX`, verify:
   - Exact code location enforcing the invariant;
   - At least one non-tautological test asserting the exact expected HTTP status, error code, and state change;
   - No drift from `design.md` (error envelope, monetary units, state machine).
4. Flag any code changes that violate **Non-Goals** in `proposal.md`.
5. Output a **PASS / FAIL Compliance Matrix** (never pass if any requirement lacks an executed test).
