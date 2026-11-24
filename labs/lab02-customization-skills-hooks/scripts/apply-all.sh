#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Applying all Lab 02 2026 customizations from prep/ into .github/..."
mkdir -p .github/instructions .github/skills/scaffold-feature .github/agents .github/hooks

cp prep/copilot-instructions.md .github/copilot-instructions.md
cp prep/api.instructions.md .github/instructions/api.instructions.md
cp prep/skills/scaffold-feature/SKILL.md .github/skills/scaffold-feature/SKILL.md
cp prep/skills/scaffold-feature/check-conventions.mjs .github/skills/scaffold-feature/check-conventions.mjs
cp prep/security-reviewer.agent.md .github/agents/security-reviewer.agent.md
cp prep/hooks/guardrails.json .github/hooks/guardrails.json
cp prep/hooks/guard-tools.mjs .github/hooks/guard-tools.mjs

echo "✅ Applied:"
echo "  - .github/copilot-instructions.md"
echo "  - .github/instructions/api.instructions.md"
echo "  - .github/skills/scaffold-feature/{SKILL.md,check-conventions.mjs}"
echo "  - .github/agents/security-reviewer.agent.md"
echo "  - .github/hooks/{guardrails.json,guard-tools.mjs}"
echo
echo "Tip: Open this folder in VS Code and run 'Chat: Open Customizations' to inspect all loaded layers."
