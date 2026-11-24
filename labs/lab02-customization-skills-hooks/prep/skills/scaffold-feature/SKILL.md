---
name: scaffold-feature
description: "Scaffold a new Task API feature (types, repository, routes, tests) following repository standards and verify compliance with the bundled convention checker script. Use when asked to scaffold or add a new resource/feature to Task API."
---

# Scaffold Feature Skill (2026 Agent Skill Standard)

> Replaces legacy `.github/prompts/new-feature.prompt.md` with a portable, cross-harness Agent Skill (works in VS Code Copilot harness, Copilot CLI, GitHub Copilot App, and Copilot Cloud Agent).

## Workflow

When the user asks to scaffold a new feature `<feature_name>` (e.g., `comments` or `tags`):

1. **Inspect existing references first**:
   - Read `src/models.py`, `src/errors.py`, `src/repositories/task_repository.py`, `api/validation.py`, and `api/routes/task_routes.py`.
2. **Generate 4 aligned artifacts**:
   - **Models**: Add or create `src/<feature_name>.py` (or extend `src/models.py`) with strict entity + Create/Update dataclasses.
   - **Repository**: Create `src/repositories/<feature_name>_repository.py` using `InMemoryTable`, parameterized SQL docstring remarks, and `NotFoundError`.
   - **Routes**: Create `api/routes/<feature_name>_routes.py` with `try/except`, `send_error`, field validation, and standard HTTP status codes (`201/200/204/400/404`).
   - **Tests**: Add deterministic `pytest` tests using Arrange-Act-Assert with hard-coded expected values.
3. **Run bundled verification script** from this skill directory:
   ```bash
   uv run python .github/skills/scaffold-feature/check_conventions.py src api
   uv run mypy src api tests
   ```
4. **Report**: Summarize created/updated files and exact verification output. Do not claim compliance without running the checker and `uv run mypy src api tests`.
