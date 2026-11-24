#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
fail=0

echo "[1/5] Node.js version (>= 22.5 recommended)..."
node -v

echo "[2/5] Prep answer-key files present..."
for f in \
  prep/copilot-instructions.md \
  prep/api.instructions.md \
  prep/skills/scaffold-feature/SKILL.md \
  prep/skills/scaffold-feature/check-conventions.mjs \
  prep/security-reviewer.agent.md \
  prep/hooks/guardrails.json \
  prep/hooks/guard-tools.mjs \
  prep/insecure-example.ts; do
  if [ -f "$f" ]; then echo "      ✓ $f"; else echo "      ❌ missing $f"; fail=1; fi
done

echo "[3/5] Clean BEFORE state check..."
if [ -d .github ]; then
  echo "      ⚠️  .github/ is currently populated (run 'npm run reset' for Before->After demo)."
else
  echo "      ✓ clean starting state — ready for Before -> After demo"
fi

echo "[4/5] TypeScript + Smoke test..."
npm run --silent typecheck && npm run --silent demo:smoke

echo "[5/5] Hook guardrail & Skill checker unit tests..."
npm run --silent test:hooks && npm run --silent test:skill-check

if [ "$fail" -eq 0 ]; then
  echo -e "\n✅ Lab 02 environment verified."
else
  exit 1
fi
