---
name: sdd-apply-tdd
description: "Implement an approved OpenSpec change strictly following spec-driven TDD: read proposal/spec/design/tasks, write REQ-tagged failing tests first, implement minimal compliant code, and verify against the acceptance suite. Use when implementing an approved SDD change."
---

# SDD Apply with TDD Discipline

## Workflow
1. **Load Approved Artifacts**: Read `proposal.md`, `specs/**/spec.md`, `design.md`, and `tasks.md` under `openspec/changes/<change>/`. Confirm all `REQ-XX` requirements and explicit Non-Goals.
2. **Red Phase (Tests from Spec)**: Write tests referencing each `REQ-XX` ID directly from the `WHEN / THEN` scenarios in `spec.md` BEFORE implementing business logic.
3. **Green Phase (Minimal Compliant Implementation)**: Follow `design.md` decisions and existing brownfield conventions (e.g., standard error envelope, integer cents). Do not add unrequested features outside `proposal.md`.
4. **Verify**: Run:
   ```bash
   uv run mypy playground
   uv run python -m evaluator.evaluate_playground   # when working inside SDD/playground
   ```
5. **Report Traceability**: Output a table mapping every `REQ-XX` -> modified file -> passing test -> verification status.
