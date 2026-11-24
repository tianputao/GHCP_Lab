---
name: scaffold-feature
description: "Scaffold a new Task API feature (types, repository, routes, tests) following repository standards and verify compliance with the bundled convention checker script. Use when asked to scaffold or add a new resource/feature to Task API."
---

# Scaffold Feature Skill (2026 Agent Skill Standard)

> Replaces legacy `.github/prompts/new-feature.prompt.md` with a portable, cross-harness Agent Skill (works in VS Code Copilot harness, Copilot CLI, GitHub Copilot App, and Copilot Cloud Agent).

## Workflow

When the user asks to scaffold a new feature `<feature_name>` (e.g., `comments` or `tags`):

1. **Inspect existing references first**:
   - Read `src/types.ts`, `src/errors.ts`, `src/repositories/task-repository.ts`, `api/validation.ts`, and `api/routes/task-routes.ts`.
2. **Generate 4 aligned artifacts**:
   - **Types**: Add or create `src/<feature_name>.ts` (or extend `src/types.ts`) with strict entity + Create/Update input interfaces.
   - **Repository**: Create `src/repositories/<feature_name>-repository.ts` using `InMemoryTable`, parameterized SQL JSDoc remarks, and `NotFoundError`.
   - **Routes**: Create `api/routes/<feature_name>-routes.ts` with `try/catch`, `sendError`, field validation, and standard HTTP status codes (`201/200/204/400/404`).
   - **Tests**: Add deterministic tests using Arrange-Act-Assert with hard-coded expected values.
3. **Run bundled verification script** from this skill directory:
   ```bash
   node .github/skills/scaffold-feature/check-conventions.mjs src api
   npm run typecheck
   ```
4. **Report**: Summarize created/updated files and exact verification output. Do not claim compliance without running the checker and `npm run typecheck`.
