---
description: "[LEGACY Local Harness Format] Scaffold a new feature — kept for migration comparison with Agent Skills"
agent: "agent"
---

# Legacy Prompt File Comparison

> Note (2026-11): Prompt files (`.github/prompts/*.prompt.md`) were designed for the legacy Local harness.
> For new workflows across VS Code Copilot Agent Host, Copilot CLI, and Cloud Agent, migrate to
> **Agent Skills** (`.github/skills/<name>/SKILL.md`), which also support bundled scripts like `check_conventions.py`.

Scaffold a feature named `{{ feature_name }}` following `.github/copilot-instructions.md` and `.github/instructions/api.instructions.md`.
